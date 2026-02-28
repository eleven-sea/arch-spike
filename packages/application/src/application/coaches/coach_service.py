
import json

from application.core.events import IEventDispatcher
from application.core.logger import ILogger
from application.core.ports import ICache
from domain.coaches.coach import Coach
from domain.coaches.repositories import ICoachRepository
from domain.coaches.value_objects import CoachTier, Specialization
from domain.members.repositories import IMemberRepository
from domain.services.coach_matching import CoachMatchingService

_CACHE_TTL = 300


class CoachService:
    def __init__(
            self,
            coach_repo: ICoachRepository,
            member_repo: IMemberRepository,
            cache: ICache,
            dispatcher: IEventDispatcher,
            app_logger: ILogger,
    ) -> None:
        self._repo = coach_repo
        self._member_repo = member_repo
        self._cache = cache
        self._dispatcher = dispatcher
        self._logger = app_logger.get_logger(__name__)

    async def register(
            self,
            first_name: str,
            last_name: str,
            email: str,
            bio: str,
            tier: str,
            specializations: list[str],
            max_clients: int,
    ) -> Coach:
        if await self._repo.get_by_email(email) is not None:
            raise ValueError(f"Email {email!r} already registered")

        coach = Coach.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            bio=bio,
            tier=CoachTier(tier),
            specializations=frozenset(Specialization(s) for s in specializations),
            max_clients=max_clients,
        )

        saved = await self._repo.save(coach)

        self._logger.info("Coach registered: %s (id=%s)", saved.email.value, saved.id)

        for spec in saved.specializations:
            await self._cache.delete(f"coaches:available:{spec.value}")

        for event in coach.pull_events():
            self._dispatcher.run_in_background(event)

        return saved

    async def find_available(self, specialization: str | None = None) -> list[Coach]:
        """Return coaches, using Redis cache keyed by specialization."""
        cache_key = f"coaches:available:{specialization or 'ALL'}"
        cached = await self._cache.get(cache_key)
        if cached is not None:
            return self._deserialize_coaches(cached)

        if specialization:
            coaches = await self._repo.find_by_specialization(Specialization(specialization))
        else:
            coaches = await self._repo.get_all()

        await self._cache.set(cache_key, self._serialize_coaches(coaches), _CACHE_TTL)
        return coaches

    async def get(self, coach_id: int) -> Coach | None:
        return await self._repo.get_by_id(coach_id)

    async def find_best_for_member(self, member_id: int) -> Coach | None:
        """Return the best matching coach for a member based on their goals and tier."""
        member = await self._member_repo.get_by_id(member_id)
        if member is None:
            raise ValueError(f"Member {member_id} not found")
        coaches = await self._repo.get_all()
        return CoachMatchingService.find_best_coach(member, coaches)

    async def delete(self, coach_id: int) -> None:
        coach = await self._repo.get_by_id(coach_id)
        if coach:
            for spec in coach.specializations:
                await self._cache.delete(f"coaches:available:{spec.value}")
            await self._cache.delete("coaches:available:ALL")
        await self._repo.delete(coach_id)

    @staticmethod
    def _serialize_coaches(coaches: list[Coach]) -> str:
        return json.dumps([c.model_dump(mode="json") for c in coaches])

    @staticmethod
    def _deserialize_coaches(data: str) -> list[Coach]:
        return [Coach.model_validate(item) for item in json.loads(data)]

from __future__ import annotations

import json

from domain.coaches.coach import Coach
from domain.coaches.repositories import ICoachRepository
from domain.coaches.value_objects import CoachTier, Specialization
from domain.members.repositories import IMemberRepository
from domain.services.coach_matching import CoachMatchingService
from application.core.events import IEventDispatcher
from application.core.logger import ILogger
from application.core.ports import ICache


_CACHE_TTL = 300  # 5 minutes


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

        coach2 = Coach.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            bio=bio,
            tier=CoachTier(tier),
            specializations=frozenset(Specialization(s) for s in specializations),
            max_clients=max_clients,
        )

        # some changes
        saved = await self._repo.save(coach)
        saved2 = await self._repo.save(coach2)


        self._logger.info("Coach registered: %s (id=%s)", saved.email.value, saved.id)

        # Invalidate relevant caches
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

    # ------------------------------------------------------------------
    # Serialisation helpers (simple JSON, no heavy dependencies)
    # ------------------------------------------------------------------
    @staticmethod
    def _serialize_coaches(coaches: list[Coach]) -> str:
        return json.dumps(
            [
                {
                    "id": c.id,
                    "first_name": c.name.first_name,
                    "last_name": c.name.last_name,
                    "email": c.email.value,
                    "bio": c.bio,
                    "tier": c.tier.value,
                    "specializations": [s.value for s in c.specializations],
                    "max_clients": c.max_clients,
                    "current_client_count": c.current_client_count,
                }
                for c in coaches
            ]
        )

    @staticmethod
    def _deserialize_coaches(data: str) -> list[Coach]:
        from domain.shared.value_objects import Email, FullName

        items = json.loads(data)
        coaches = []
        for item in items:
            coach = Coach(
                id=item["id"],
                name=FullName(item["first_name"], item["last_name"]),
                email=Email(item["email"]),
                bio=item["bio"],
                tier=CoachTier(item["tier"]),
                specializations=frozenset(Specialization(s) for s in item["specializations"]),
                max_clients=item["max_clients"],
                current_client_count=item["current_client_count"],
            )
            coaches.append(coach)
        return coaches

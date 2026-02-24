from __future__ import annotations

import json
from datetime import date

from domain.members.repositories import IMemberRepository
from domain.plans.entities import WorkoutSession
from domain.plans.repositories import ITrainingPlanRepository
from domain.plans.training_plan import TrainingPlan
from domain.plans.value_objects import PlannedExercise
from domain.services.plan_progress import PlanProgressService
from application.core.events import IEventDispatcher
from application.core.logger import ILogger
from application.core.ports import ICache, IExerciseClient

_EXERCISE_TTL = 3600  # 1 hour


class TrainingPlanService:
    def __init__(
        self,
        plan_repo: ITrainingPlanRepository,
        member_repo: IMemberRepository,
        cache: ICache,
        exercise_client: IExerciseClient,
        dispatcher: IEventDispatcher,
        app_logger: ILogger,
    ) -> None:
        self._plan_repo = plan_repo
        self._member_repo = member_repo
        self._cache = cache
        self._exercise_client = exercise_client
        self._dispatcher = dispatcher
        self._logger = app_logger

    async def create_plan(
        self,
        member_id: int,
        coach_id: int,
        name: str,
        starts_at: str,
        ends_at: str,
    ) -> TrainingPlan:
        logger = self._logger.get_logger(__name__)

        member = await self._member_repo.get_by_id(member_id)
        if member is None:
            raise ValueError(f"Member {member_id} not found")
        if member.active_plan_id is not None:
            raise ValueError(
                f"Member {member_id} already has an active plan ({member.active_plan_id})"
            )

        plan = TrainingPlan.create(
            member_id=member_id,
            coach_id=coach_id,
            name=name,
            starts_at=date.fromisoformat(starts_at),
            ends_at=date.fromisoformat(ends_at),
        )
        saved = await self._plan_repo.save(plan)
        logger.info("Plan created: %s (id=%s)", saved.name, saved.id)

        for event in plan.pull_events():
            self._dispatcher.run_in_background(event)

        return saved

    async def activate_plan(self, plan_id: int) -> TrainingPlan:
        plan = await self._plan_repo.get_by_id(plan_id)
        if plan is None:
            raise ValueError(f"Plan {plan_id} not found")

        plan.activate()
        saved = await self._plan_repo.save(plan)

        # Update member's active_plan_id
        member = await self._member_repo.get_by_id(plan.member_id)
        if member:
            member.assign_plan(plan_id)
            await self._member_repo.save(member)

        for event in saved.pull_events():
            self._dispatcher.run_in_background(event)

        return saved

    async def add_session(
        self,
        plan_id: int,
        session_name: str,
        scheduled_date: str,
        exercises: list[dict],
    ) -> TrainingPlan:
        """Add a workout session with exercises (looked up / cached from wger)."""
        plan = await self._plan_repo.get_by_id(plan_id)
        if plan is None:
            raise ValueError(f"Plan {plan_id} not found")

        planned_exercises: list[PlannedExercise] = []
        for ex in exercises:
            ex_name = ex.get("name", "Unknown")
            cache_key = f"exercise:{ex_name.lower()}"
            cached = await self._cache.get(cache_key)
            if cached is not None:
                ex_data = json.loads(cached)
            else:
                results = await self._exercise_client.search_exercises(ex_name)
                ex_data = results[0] if results else {"exercise_id": "0", "name": ex_name}
                await self._cache.set(cache_key, json.dumps(ex_data), _EXERCISE_TTL)

            planned_exercises.append(
                PlannedExercise(
                    exercise_id=str(ex_data.get("exercise_id", ex.get("exercise_id", "0"))),
                    name=ex_data.get("name", ex_name),
                    sets=ex.get("sets", 3),
                    reps=ex.get("reps", 10),
                    rest_seconds=ex.get("rest_seconds", 60),
                )
            )

        session = WorkoutSession(
            name=session_name,
            scheduled_date=date.fromisoformat(scheduled_date),
            exercises=planned_exercises,
        )
        plan.add_session(session)
        saved = await self._plan_repo.save(plan)
        return saved

    async def complete_session(
        self,
        plan_id: int,
        session_id: int,
        notes: str | None = None,
    ) -> TrainingPlan:
        logger = self._logger.get_logger(__name__)

        plan = await self._plan_repo.get_by_id(plan_id)
        if plan is None:
            raise ValueError(f"Plan {plan_id} not found")

        plan.complete_session(session_id, notes)
        saved = await self._plan_repo.save(plan)
        logger.info("Session %s completed on plan %s", session_id, plan_id)

        events = saved.pull_events()
        for event in events:
            self._dispatcher.run_in_background(event)

        return saved

    async def get(self, plan_id: int) -> TrainingPlan | None:
        return await self._plan_repo.get_by_id(plan_id)

    async def get_by_member(self, member_id: int) -> list[TrainingPlan]:
        return await self._plan_repo.get_by_member(member_id)

    async def get_progress(self, plan_id: int) -> float:
        plan = await self._plan_repo.get_by_id(plan_id)
        if plan is None:
            raise ValueError(f"Plan {plan_id} not found")
        return PlanProgressService.completion_pct(plan)

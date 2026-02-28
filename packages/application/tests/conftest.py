
import logging
from unittest.mock import AsyncMock, MagicMock

import pytest

from application.core.logger import ILogger
from domain.coaches.coach import Coach
from domain.coaches.repositories import ICoachRepository
from domain.coaches.value_objects import Specialization
from domain.members.member import Member
from domain.members.repositories import IMemberRepository
from domain.plans.repositories import ITrainingPlanRepository
from domain.plans.training_plan import TrainingPlan


class InMemoryMemberRepository(IMemberRepository):
    def __init__(self) -> None:
        self._store: dict[int, Member] = {}
        self._next_id = 1

    async def save(self, member: Member) -> Member:
        if member.id is None:
            member.id = self._next_id
            self._next_id += 1
            for goal in member.goals:
                if goal.id is None:
                    goal.id = self._next_id
                    self._next_id += 1
        self._store[member.id] = member
        return member

    async def get_by_id(self, id: int) -> Member | None:
        return self._store.get(id)

    async def get_by_email(self, email: str) -> Member | None:
        return next((m for m in self._store.values() if m.email.value == email), None)

    async def get_all(self) -> list[Member]:
        return list(self._store.values())

    async def delete(self, id: int) -> None:
        self._store.pop(id, None)


class InMemoryCoachRepository(ICoachRepository):
    def __init__(self) -> None:
        self._store: dict[int, Coach] = {}
        self._next_id = 1

    async def save(self, coach: Coach) -> Coach:
        if coach.id is None:
            coach.id = self._next_id
            self._next_id += 1
        self._store[coach.id] = coach
        return coach

    async def get_by_id(self, id: int) -> Coach | None:
        return self._store.get(id)

    async def get_by_email(self, email: str) -> Coach | None:
        return next((c for c in self._store.values() if c.email.value == email), None)

    async def find_by_specialization(self, spec: Specialization) -> list[Coach]:
        return [c for c in self._store.values() if spec in c.specializations]

    async def get_all(self) -> list[Coach]:
        return list(self._store.values())

    async def delete(self, id: int) -> None:
        self._store.pop(id, None)


class InMemoryPlanRepository(ITrainingPlanRepository):
    def __init__(self) -> None:
        self._store: dict[int, TrainingPlan] = {}
        self._next_id = 1

    async def save(self, plan: TrainingPlan) -> TrainingPlan:
        if plan.id is None:
            plan.id = self._next_id
            self._next_id += 1
            for session in plan.sessions:
                if session.id is None:
                    session.id = self._next_id
                    self._next_id += 1
        else:
            for session in plan.sessions:
                if session.id is None:
                    session.id = self._next_id
                    self._next_id += 1
        self._store[plan.id] = plan
        return plan

    async def get_by_id(self, id: int) -> TrainingPlan | None:
        return self._store.get(id)

    async def get_by_member(self, member_id: int) -> list[TrainingPlan]:
        return [p for p in self._store.values() if p.member_id == member_id]

    async def delete(self, id: int) -> None:
        self._store.pop(id, None)


@pytest.fixture()
def member_repo() -> InMemoryMemberRepository:
    return InMemoryMemberRepository()


@pytest.fixture()
def coach_repo() -> InMemoryCoachRepository:
    return InMemoryCoachRepository()


@pytest.fixture()
def plan_repo() -> InMemoryPlanRepository:
    return InMemoryPlanRepository()


@pytest.fixture()
def fake_dispatcher():
    mock = MagicMock()
    mock.run_in_background = MagicMock()
    mock.register = MagicMock()
    return mock


@pytest.fixture()
def fake_cache():
    mock = AsyncMock()
    mock.get.return_value = None
    mock.set.return_value = None
    mock.delete.return_value = None
    return mock


@pytest.fixture()
def fake_exercise_client():
    mock = AsyncMock()
    mock.search_exercises.return_value = [{"exercise_id": "42", "name": "Squat"}]
    mock.get_exercise.return_value = {"id": "42", "name": "Squat"}
    return mock


@pytest.fixture()
def fake_broker():
    mock = AsyncMock()
    mock.publish.return_value = None
    return mock


@pytest.fixture()
def fake_task_dispatcher():
    mock = AsyncMock()
    mock.dispatch.return_value = None
    return mock


@pytest.fixture()
def fake_logger():
    mock = MagicMock(spec=ILogger)
    mock.get_logger.return_value = logging.getLogger("test")
    return mock

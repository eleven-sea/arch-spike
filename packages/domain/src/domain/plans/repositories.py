from __future__ import annotations

from abc import ABC, abstractmethod

from domain.plans.training_plan import TrainingPlan


class ITrainingPlanRepository(ABC):
    @abstractmethod
    async def get_by_id(self, id: int) -> TrainingPlan | None: ...

    @abstractmethod
    async def get_by_member(self, member_id: int) -> list[TrainingPlan]: ...

    @abstractmethod
    async def save(self, plan: TrainingPlan) -> TrainingPlan: ...

    @abstractmethod
    async def delete(self, id: int) -> None: ...

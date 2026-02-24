from __future__ import annotations

from sqlalchemy import select

from domain.plans.repositories import ITrainingPlanRepository
from domain.plans.training_plan import TrainingPlan
from infrastructure.database.base_repository import BaseRepository
from infrastructure.database.mappers.plan_mapper import PlanMapper
from infrastructure.database.models.plan_models import TrainingPlanORM


class PostgresTrainingPlanRepository(BaseRepository[TrainingPlanORM, int], ITrainingPlanRepository):
    def __init__(self, session_factory) -> None:
        super().__init__(TrainingPlanORM, session_factory)

    async def get_by_id(self, id: int) -> TrainingPlan | None:
        orm = await self.find_by_id(id)
        return PlanMapper.to_domain(orm) if orm else None

    async def get_by_member(self, member_id: int) -> list[TrainingPlan]:
        async with self._session_factory() as session:
            result = await session.execute(
                select(TrainingPlanORM).where(TrainingPlanORM.member_id == member_id)
            )
            orms = result.scalars().all()
            return [PlanMapper.to_domain(o) for o in orms]

    async def save(self, plan: TrainingPlan) -> TrainingPlan:
        async with self._session_factory() as session:
            orm = PlanMapper.to_orm(plan)
            merged = await session.merge(orm)
            await session.flush()
            await session.refresh(merged, attribute_names=["sessions"])
            return PlanMapper.to_domain(merged)

    async def delete(self, id: int) -> None:
        await super().delete(id)

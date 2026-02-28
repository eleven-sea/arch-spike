from typing import override

from sqlalchemy import select

from domain.plans.repositories import ITrainingPlanRepository
from domain.plans.training_plan import TrainingPlan
from infrastructure.database.base_repository import BaseRepository, SessionFactory
from infrastructure.database.mappers.plan_mapper import PlanMapper
from infrastructure.database.models.plan_models import TrainingPlanORM


class PostgresTrainingPlanRepository(BaseRepository[TrainingPlanORM, int]):
    def __init__(self, session_factory: SessionFactory) -> None:
        super().__init__(TrainingPlanORM, session_factory)

    async def find_by_member(self, member_id: int) -> list[TrainingPlanORM]:
        async with self._session_factory() as session:
            result = await session.execute(
                select(TrainingPlanORM).where(TrainingPlanORM.member_id == member_id)
            )
            return list(result.scalars().all())


class TrainingPlanRepository(ITrainingPlanRepository):
    def __init__(self, repo: PostgresTrainingPlanRepository) -> None:
        self._repo = repo

    @override
    async def get_by_id(self, id: int) -> TrainingPlan:
        orm = await self._repo.get_by_id(id)
        return PlanMapper.to_domain(orm)

    @override
    async def get_by_member(self, member_id: int) -> list[TrainingPlan]:
        orms = await self._repo.find_by_member(member_id)
        return [PlanMapper.to_domain(o) for o in orms]

    @override
    async def save(self, plan: TrainingPlan) -> TrainingPlan:
        orm = await self._repo.save(PlanMapper.to_orm(plan))
        return PlanMapper.to_domain(orm)

    @override
    async def delete(self, id: int) -> None:
        await self._repo.delete(id)

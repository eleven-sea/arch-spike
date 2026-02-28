
from typing import override

from sqlalchemy import select

from domain.coaches.coach import Coach
from domain.coaches.repositories import ICoachRepository
from domain.coaches.value_objects import Specialization
from infrastructure.database.base_repository import BaseRepository, SessionFactory
from infrastructure.database.mappers.coach_mapper import CoachMapper
from infrastructure.database.models.coach_models import CoachORM, CoachSpecializationORM


class PostgresCoachRepository(BaseRepository[CoachORM, int], ICoachRepository):
    def __init__(self, session_factory: SessionFactory) -> None:
        super().__init__(CoachORM, session_factory)

    @override
    async def get_by_id(self, id: int) -> Coach | None:
        orm = await self.find_by_id(id)
        return CoachMapper.to_domain(orm) if orm else None

    @override
    async def get_by_email(self, email: str) -> Coach | None:
        async with self._session_factory() as session:
            result = await session.execute(
                select(CoachORM).where(CoachORM.email == email)
            )
            orm = result.scalar_one_or_none()
            return CoachMapper.to_domain(orm) if orm else None

    @override
    async def find_by_specialization(self, spec: Specialization) -> list[Coach]:
        async with self._session_factory() as session:
            result = await session.execute(
                select(CoachORM)
                .join(CoachSpecializationORM, CoachORM.id == CoachSpecializationORM.coach_id)
                .where(CoachSpecializationORM.specialization == spec.value)
                .distinct()
            )
            orms = result.scalars().all()
            return [CoachMapper.to_domain(o) for o in orms]

    @override
    async def get_all(self) -> list[Coach]:
        orms = await self.find_all()
        return [CoachMapper.to_domain(o) for o in orms]

    @override
    async def save(self, coach: Coach) -> Coach:  # pyright: ignore[reportIncompatibleMethodOverride]
        async with self._session_factory() as session:
            orm = CoachMapper.to_orm(coach)
            merged = await session.merge(orm)
            await session.flush()
            await session.refresh(merged, attribute_names=["certifications", "available_slots", "specializations"])
            return CoachMapper.to_domain(merged)

    @override
    async def delete(self, id: int) -> None:
        await super().delete(id)

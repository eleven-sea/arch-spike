from typing import override

from sqlalchemy import select

from domain.coaches.coach import Coach
from domain.coaches.repositories import ICoachRepository
from domain.coaches.value_objects import Specialization
from infrastructure.database.base_repository import BaseRepository, SessionFactory
from infrastructure.database.mappers.coach_mapper import CoachMapper
from infrastructure.database.models.coach_models import CoachORM, CoachSpecializationORM


class PostgresCoachRepository(BaseRepository[CoachORM, int]):
    def __init__(self, session_factory: SessionFactory) -> None:
        super().__init__(CoachORM, session_factory)

    async def find_by_email(self, email: str) -> CoachORM | None:
        async with self._session_factory() as session:
            result = await session.execute(select(CoachORM).where(CoachORM.email == email))
            return result.scalar_one_or_none()

    async def find_by_specialization(self, spec: Specialization) -> list[CoachORM]:
        async with self._session_factory() as session:
            result = await session.execute(
                select(CoachORM)
                .join(CoachSpecializationORM, CoachORM.id == CoachSpecializationORM.coach_id)
                .where(CoachSpecializationORM.specialization == spec.value)
                .distinct()
            )
            return list(result.scalars().all())


class CoachRepository(ICoachRepository):
    def __init__(self, repo: PostgresCoachRepository) -> None:
        self._repo = repo

    @override
    async def get_by_id(self, id: int) -> Coach:
        orm = await self._repo.get_by_id(id)
        return CoachMapper.to_domain(orm)

    @override
    async def get_by_email(self, email: str) -> Coach | None:
        orm = await self._repo.find_by_email(email)
        return CoachMapper.to_domain(orm) if orm else None

    @override
    async def find_by_specialization(self, spec: Specialization) -> list[Coach]:
        orms = await self._repo.find_by_specialization(spec)
        return [CoachMapper.to_domain(o) for o in orms]

    @override
    async def get_all(self) -> list[Coach]:
        orms = await self._repo.find_all()
        return [CoachMapper.to_domain(o) for o in orms]

    @override
    async def save(self, coach: Coach) -> Coach:
        orm = await self._repo.save(CoachMapper.to_orm(coach))
        return CoachMapper.to_domain(orm)

    @override
    async def delete(self, id: int) -> None:
        await self._repo.delete(id)

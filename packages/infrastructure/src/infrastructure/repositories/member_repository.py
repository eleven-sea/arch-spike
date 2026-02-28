
from typing import override

from sqlalchemy import select

from domain.members.member import Member
from domain.members.repositories import IMemberRepository
from infrastructure.database.base_repository import BaseRepository, SessionFactory
from infrastructure.database.mappers.member_mapper import MemberMapper
from infrastructure.database.models.member_models import MemberORM


class PostgresMemberRepository(BaseRepository[MemberORM, int], IMemberRepository):
    def __init__(self, session_factory: SessionFactory) -> None:
        super().__init__(MemberORM, session_factory)

    @override
    async def get_by_id(self, id: int) -> Member | None:
        orm = await self.find_by_id(id)
        return MemberMapper.to_domain(orm) if orm else None

    @override
    async def get_by_email(self, email: str) -> Member | None:
        async with self._session_factory() as session:
            result = await session.execute(
                select(MemberORM).where(MemberORM.email == email)
            )
            orm = result.scalar_one_or_none()
            return MemberMapper.to_domain(orm) if orm else None

    @override
    async def get_all(self) -> list[Member]:
        orms = await self.find_all()
        return [MemberMapper.to_domain(o) for o in orms]

    @override
    async def save(self, member: Member) -> Member:  # pyright: ignore[reportIncompatibleMethodOverride]
        async with self._session_factory() as session:
            orm = MemberMapper.to_orm(member)
            merged = await session.merge(orm)
            await session.flush()
            await session.refresh(merged, attribute_names=["goals"])
            return MemberMapper.to_domain(merged)

    @override
    async def delete(self, id: int) -> None:
        await super().delete(id)

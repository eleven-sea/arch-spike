from typing import override

from sqlalchemy import select

from domain.members.member import Member
from domain.members.repositories import IMemberRepository
from infrastructure.database.base_repository import BaseRepository, SessionFactory
from infrastructure.database.mappers.member_mapper import MemberMapper
from infrastructure.database.models.member_models import MemberORM


class PostgresMemberRepository(BaseRepository[MemberORM, int]):
    def __init__(self, session_factory: SessionFactory) -> None:
        super().__init__(MemberORM, session_factory)

    async def find_by_email(self, email: str) -> MemberORM | None:
        async with self._session_factory() as session:
            result = await session.execute(select(MemberORM).where(MemberORM.email == email))
            return result.scalar_one_or_none()


class MemberRepository(IMemberRepository):
    def __init__(self, repo: PostgresMemberRepository) -> None:
        self._repo = repo

    @override
    async def get_by_id(self, id: int) -> Member:
        orm = await self._repo.get_by_id(id)
        return MemberMapper.to_domain(orm)

    @override
    async def get_by_email(self, email: str) -> Member | None:
        orm = await self._repo.find_by_email(email)
        return MemberMapper.to_domain(orm) if orm else None

    @override
    async def get_all(self) -> list[Member]:
        orms = await self._repo.find_all()
        return [MemberMapper.to_domain(o) for o in orms]

    @override
    async def save(self, member: Member) -> Member:
        orm = await self._repo.save(MemberMapper.to_orm(member))
        return MemberMapper.to_domain(orm)

    @override
    async def delete(self, id: int) -> None:
        await self._repo.delete(id)

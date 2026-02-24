from typing import Generic, TypeVar

from sqlalchemy import func, select

from infrastructure.database.base import Base

T = TypeVar("T", bound=Base)
ID = TypeVar("ID")


class BaseRepository(Generic[T, ID]):
    def __init__(self, model: type[T], session_factory):
        self._model = model
        self._session_factory = session_factory

    async def find_by_id(self, id: ID) -> T | None:
        async with self._session_factory() as session:
            return await session.get(self._model, id)

    async def find_all(self) -> list[T]:
        async with self._session_factory() as session:
            result = await session.execute(select(self._model))
            return list(result.scalars().all())

    async def save(self, entity: T) -> T:
        async with self._session_factory() as session:
            merged = await session.merge(entity)
            await session.flush()
            return merged

    async def save_all(self, entities: list[T]) -> list[T]:
        async with self._session_factory() as session:
            merged = [await session.merge(e) for e in entities]
            await session.flush()
            return merged

    async def delete(self, id: ID) -> None:
        async with self._session_factory() as session:
            entity = await session.get(self._model, id)
            if entity:
                await session.delete(entity)

    async def delete_all(self) -> None:
        async with self._session_factory() as session:
            result = await session.execute(select(self._model))
            for entity in result.scalars().all():
                await session.delete(entity)

    async def count(self) -> int:
        async with self._session_factory() as session:
            result = await session.execute(
                select(func.count()).select_from(self._model)
            )
            return result.scalar_one()

    async def exists(self, id: ID) -> bool:
        return await self.find_by_id(id) is not None

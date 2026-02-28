from collections.abc import Callable
from contextlib import AbstractAsyncContextManager

from sqlalchemy import func
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from infrastructure.database.base import Base
from infrastructure.database.exceptions import EntityNotFoundException

type SessionFactory = Callable[[], AbstractAsyncContextManager[AsyncSession]]


class BaseRepository[T: Base, ID]:
    def __init__(self, model: type[T], session_factory: SessionFactory) -> None:
        self._model = model
        self._session_factory = session_factory

    async def find_by_id(self, id: ID) -> T | None:
        async with self._session_factory() as session:
            return await session.get(self._model, id)

    async def find_all(self) -> list[T]:
        async with self._session_factory() as session:
            result = await session.exec(select(self._model))
            return list(result.all())

    async def get_by_id(self, id: ID) -> T:
        r = await self.find_by_id(id)
        if r is None:
            raise EntityNotFoundException(self._model.__name__, id)
        return r

    async def save(self, entity: T) -> T:
        async with self._session_factory() as session:
            if entity.is_new:
                session.add(entity)
            else:
                entity = await session.merge(entity)
            await session.flush()
            return entity

    async def save_all(self, entities: list[T]) -> list[T]:
        async with self._session_factory() as session:
            result: list[T] = []
            for entity in entities:
                if entity.is_new:
                    session.add(entity)
                    result.append(entity)
                else:
                    result.append(await session.merge(entity))
            await session.flush()
            return result

    async def delete(self, id: ID) -> None:
        async with self._session_factory() as session:
            entity = await session.get(self._model, id)
            if entity:
                await session.delete(entity)

    async def delete_all(self) -> None:
        async with self._session_factory() as session:
            result = await session.exec(select(self._model))
            for entity in result.all():
                await session.delete(entity)

    async def count(self) -> int:
        async with self._session_factory() as session:
            result = await session.exec(
                select(func.count()).select_from(self._model)
            )
            return result.one()

    async def exists(self, id: ID) -> bool:
        return await self.find_by_id(id) is not None

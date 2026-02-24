from contextlib import asynccontextmanager
from typing import AsyncIterator

from infrastructure.database.session import Database


class TransactionManager:
    def __init__(self, database: Database):
        self._database = database

    @asynccontextmanager
    async def transaction(self) -> AsyncIterator[None]:
        async with self._database.transaction():
            yield

import logging
from contextlib import asynccontextmanager
from contextvars import ContextVar

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine, AsyncEngine

_current_session: ContextVar[AsyncSession | None] = ContextVar("_current_session", default=None)
_logger = logging.getLogger(__name__)


class Database:
    def __init__(
        self,
        db_url: str,
        pool_size: int = 5,
        max_overflow: int = 10,
        pool_timeout: float = 30.0,
        pool_recycle: int = 1800,
    ):
        self._engine: AsyncEngine = create_async_engine(
            db_url,
            pool_size=pool_size,
            max_overflow=max_overflow,
            pool_timeout=pool_timeout,
            pool_recycle=pool_recycle,
        )
        self._session_factory = async_sessionmaker(
            bind=self._engine, expire_on_commit=False
        )

    @asynccontextmanager
    async def session(self):
        existing = _current_session.get()
        if existing is not None:
            _logger.debug("Reusing existing session %s", id(existing))
            yield existing
            return

        async with self._session_factory() as session:
            _logger.debug("Session opened %s", id(session))
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                _logger.debug("Session closed %s", id(session))

    @asynccontextmanager
    async def transaction(self, new: bool = False):
        existing = _current_session.get()
        if existing is not None and not new:
            _logger.debug("Reusing existing transaction session %s", id(existing))
            yield existing
            return

        async with self._session_factory() as session:
            _logger.debug("Transaction session opened %s", id(session))
            token = _current_session.set(session)
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                _current_session.reset(token)
                _logger.debug("Transaction session closed %s", id(session))

    @property
    def engine(self) -> AsyncEngine:
        return self._engine

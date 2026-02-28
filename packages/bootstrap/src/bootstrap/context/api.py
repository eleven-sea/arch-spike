
import asyncio
import logging
from typing import override

from bootstrap.context.base import BaseApplicationContext
from infrastructure.database.migrations import run_migrations
from infrastructure.redis.redis_client import RedisClient

logger = logging.getLogger(__name__)


async def _pubsub_listener(redis_client: RedisClient) -> None:
    """Background listener for Redis pub/sub channels."""
    pubsub = redis_client.pubsub()
    await pubsub.subscribe("member.registered", "plan.completed")  # pyright: ignore[reportUnknownMemberType]
    logger.info("Pub/Sub listener started — subscribed to member.registered + plan.completed")
    try:
        while True:
            msg = await pubsub.get_message(ignore_subscribe_messages=True, timeout=0.1)  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
            if msg and msg.get("type") == "message":  # pyright: ignore[reportUnknownMemberType]
                logger.info(
                    "Received pub/sub [%s]: %s",
                    msg.get("channel"),  # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType]
                    msg.get("data"),  # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType]
                )
            await asyncio.sleep(0.05)
    except asyncio.CancelledError:
        logger.info("Pub/Sub listener shutting down")
        await pubsub.unsubscribe()  # pyright: ignore[reportUnknownMemberType]
        raise


class ApiApplicationContext(BaseApplicationContext):
    def __init__(self) -> None:
        super().__init__()
        self._pubsub_task: asyncio.Task[None] | None = None

    @override
    async def _before_start(self) -> None:
        await run_migrations(self._container.database().engine)

    @override
    async def _after_start(self) -> None:
        redis_client = await self._container.redis_client.async_()
        self._pubsub_task = asyncio.create_task(
            _pubsub_listener(redis_client),
            name="pubsub-listener",
        )

    @override
    async def _before_stop(self) -> None:
        if self._pubsub_task is not None:
            self._pubsub_task.cancel()
            try:
                await self._pubsub_task
            except asyncio.CancelledError:
                pass

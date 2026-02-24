from __future__ import annotations

import asyncio
import logging

from bootstrap.containers import Container
from infrastructure.database.migrations import run_migrations

logger = logging.getLogger(__name__)


async def _pubsub_listener(redis_client) -> None:
    """Background listener for Redis pub/sub channels."""
    pubsub = redis_client._redis.pubsub()
    await pubsub.subscribe("member.registered", "plan.completed")
    logger.info("Pub/Sub listener started — subscribed to member.registered + plan.completed")
    try:
        while True:
            msg = await pubsub.get_message(ignore_subscribe_messages=True, timeout=0.1)
            if msg and msg.get("type") == "message":
                logger.info(
                    "Received pub/sub [%s]: %s",
                    msg.get("channel"),
                    msg.get("data"),
                )
            await asyncio.sleep(0.05)
    except asyncio.CancelledError:
        logger.info("Pub/Sub listener shutting down")
        await pubsub.unsubscribe()
        raise


class ApplicationContext:
    def __init__(self) -> None:
        self._container = Container()
        self._pubsub_task: asyncio.Task | None = None
        self._logger = self._container.app_logger().get_logger(__name__)

    @property
    def container(self) -> Container:
        return self._container

    async def start(self) -> None:
        await run_migrations(self._container.database().engine)

        result = self._container.init_resources()
        if result is not None:
            await result

        await self._register_event_handlers()

        redis_client = await self._container.redis_client.async_()
        self._pubsub_task = asyncio.create_task(
            _pubsub_listener(redis_client),
            name="pubsub-listener",
        )

    async def stop(self) -> None:
        if self._pubsub_task is not None:
            self._pubsub_task.cancel()
            try:
                await self._pubsub_task
            except asyncio.CancelledError:
                pass

        result = self._container.shutdown_resources()
        if result is not None:
            await result

        await self._container.database().engine.dispose()

    async def _register_event_handlers(self) -> None:
        """Wire domain events to application handlers."""
        import inspect
        from domain.members.events import MemberRegistered
        from domain.coaches.events import CoachRegistered
        from domain.plans.events import SessionCompleted, PlanCompleted

        async def resolve(provider):
            result = provider()
            return await result if inspect.isawaitable(result) else result

        dispatcher = self._container.event_dispatcher()
        dispatcher.register(MemberRegistered, (await resolve(self._container.member_registered_handler)).handle)
        dispatcher.register(CoachRegistered,  (await resolve(self._container.coach_registered_handler)).handle)
        dispatcher.register(SessionCompleted, (await resolve(self._container.session_completed_handler)).handle)
        dispatcher.register(PlanCompleted,    (await resolve(self._container.plan_completed_handler)).handle)

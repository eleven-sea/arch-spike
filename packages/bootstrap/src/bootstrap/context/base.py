
from abc import ABC, abstractmethod
from typing import Any

from bootstrap.containers import Container


class BaseApplicationContext(ABC):
    def __init__(self) -> None:
        self._container = Container()
        self._logger = self._container.app_logger().get_logger(__name__)

    @property
    def container(self) -> Container:
        return self._container

    async def start(self) -> None:
        await self._before_start()

        result = self._container.init_resources()
        if result is not None:
            await result

        await self._register_event_handlers()
        await self._after_start()

    async def stop(self) -> None:
        await self._before_stop()

        result = self._container.shutdown_resources()
        if result is not None:
            await result

        await self._container.database().engine.dispose()

    @abstractmethod
    async def _before_start(self) -> None: ...

    @abstractmethod
    async def _after_start(self) -> None: ...

    @abstractmethod
    async def _before_stop(self) -> None: ...

    async def _register_event_handlers(self) -> None:
        import inspect

        from domain.coaches.events import CoachRegistered
        from domain.members.events import MemberRegistered
        from domain.plans.events import PlanCompleted, SessionCompleted

        async def resolve(provider: Any) -> Any:
            result = provider()
            return await result if inspect.isawaitable(result) else result

        dispatcher = self._container.event_dispatcher()
        dispatcher.register(MemberRegistered, (await resolve(self._container.member_registered_handler)).handle)
        dispatcher.register(CoachRegistered,  (await resolve(self._container.coach_registered_handler)).handle)
        dispatcher.register(SessionCompleted, (await resolve(self._container.session_completed_handler)).handle)
        dispatcher.register(PlanCompleted,    (await resolve(self._container.plan_completed_handler)).handle)

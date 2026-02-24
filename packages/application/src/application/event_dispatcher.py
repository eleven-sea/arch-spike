import asyncio
from collections import defaultdict
from typing import Callable, Awaitable

from domain.shared.events import ApplicationEvent
from application.core.events import IEventDispatcher
from application.core.logger import ILogger

Handler = Callable[[ApplicationEvent], Awaitable[None]]


class EventDispatcher(IEventDispatcher):
    def __init__(self, app_logger: ILogger) -> None:
        self._logger = app_logger.get_logger(__name__)
        self._handlers: dict[type[ApplicationEvent], list[Handler]] = defaultdict(list)

    def register(self, event_type: type[ApplicationEvent], handler: Handler) -> None:
        self._handlers[event_type].append(handler)
        handler_name = (
            f"{type(handler.__self__).__name__}.{handler.__name__}"
            if hasattr(handler, "__self__")
            else getattr(handler, "__name__", None)
            or getattr(getattr(handler, "func", None), "__name__", repr(handler))
        )
        self._logger.debug("Registered handler '%s' for %s", handler_name, event_type.__name__)

    async def run(self, event: ApplicationEvent) -> None:
        handlers = self._handlers[type(event)]
        self._logger.debug("Running %d handler(s) for %s", len(handlers), type(event).__name__)
        for handler in handlers:
            await handler(event)

    def run_in_background(self, event: ApplicationEvent) -> None:
        handlers = self._handlers[type(event)]
        self._logger.debug(
            "Scheduling %d background handler(s) for %s", len(handlers), type(event).__name__
        )
        for handler in handlers:
            task = asyncio.create_task(handler(event))
            task.add_done_callback(self._on_task_done)

    def _on_task_done(self, task: asyncio.Task) -> None:
        exc = task.exception()
        if exc:
            self._logger.error(
                "Background event handler raised an exception: %s",
                exc,
                exc_info=exc,
            )

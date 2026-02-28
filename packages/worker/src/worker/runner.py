"""
Worker entry point.

Run with:
    taskiq worker worker.runner:broker
"""

from taskiq import TaskiqEvents, TaskiqState

import worker.tasks.member_tasks  # noqa: F401  # pyright: ignore[reportUnusedImport]
from bootstrap.context import WorkerApplicationContext
from infrastructure.taskiq.broker import broker

_ctx: WorkerApplicationContext | None = None


@broker.on_event(TaskiqEvents.WORKER_STARTUP)
async def on_startup(state: TaskiqState) -> None:
    global _ctx
    _ctx = WorkerApplicationContext()
    await _ctx.start()
    _ctx.container.wire(packages=["worker.tasks"])


@broker.on_event(TaskiqEvents.WORKER_SHUTDOWN)
async def on_shutdown(state: TaskiqState) -> None:
    if _ctx is not None:
        await _ctx.stop()

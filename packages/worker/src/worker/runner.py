"""
Worker entry point.

Run with:
    taskiq worker worker.runner:broker
"""

from taskiq import TaskiqEvents, TaskiqState

from bootstrap.broker import broker
from bootstrap.context import WorkerApplicationContext

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

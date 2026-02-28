
from typing import override

from taskiq import AsyncBroker

from application.core.ports import IAsyncTaskDispatcher


class TaskiqTaskDispatcher(IAsyncTaskDispatcher):
    def __init__(self, broker: AsyncBroker) -> None:
        self._broker = broker

    @override
    async def dispatch(self, task_name: str, /, **kwargs: object) -> None:
        task = self._broker.find_task(task_name)
        if task is None:
            raise ValueError(f"Task {task_name!r} not registered in broker")
        await task.kiq(**kwargs)

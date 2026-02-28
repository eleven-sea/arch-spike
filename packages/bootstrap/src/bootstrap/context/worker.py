
from typing import override

from bootstrap.context.base import BaseApplicationContext


class WorkerApplicationContext(BaseApplicationContext):
    @override
    async def _before_start(self) -> None:
        pass

    @override
    async def _after_start(self) -> None:
        pass

    @override
    async def _before_stop(self) -> None:
        pass

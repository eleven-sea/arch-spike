from abc import ABC, abstractmethod
from typing import Generic, TypeVar

# ApplicationEvent lives in domain so that domain events can inherit it
# without creating a dependency from domain → application.
from domain.shared.events import ApplicationEvent  # noqa: F401 — re-exported

E = TypeVar("E", bound=ApplicationEvent)


class IApplicationEventHandler(ABC, Generic[E]):
    @abstractmethod
    async def handle(self, event: E) -> None: ...


class IEventDispatcher(ABC):
    @abstractmethod
    async def run(self, event: ApplicationEvent) -> None: ...

    @abstractmethod
    def run_in_background(self, event: ApplicationEvent) -> None: ...

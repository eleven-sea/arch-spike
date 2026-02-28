from abc import ABC, abstractmethod

from domain.shared.events import ApplicationEvent


class IApplicationEventHandler[E: ApplicationEvent](ABC):
    @abstractmethod
    async def handle(self, event: E) -> None: ...


class IEventDispatcher(ABC):
    @abstractmethod
    async def run(self, event: ApplicationEvent) -> None: ...

    @abstractmethod
    def run_in_background(self, event: ApplicationEvent) -> None: ...

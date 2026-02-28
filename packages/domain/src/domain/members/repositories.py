
from abc import ABC, abstractmethod

from domain.members.member import Member


class IMemberRepository(ABC):
    @abstractmethod
    async def get_by_id(self, id: int) -> Member: ...

    @abstractmethod
    async def get_by_email(self, email: str) -> Member | None: ...

    @abstractmethod
    async def save(self, member: Member) -> Member: ...

    @abstractmethod
    async def delete(self, id: int) -> None: ...

    @abstractmethod
    async def get_all(self) -> list[Member]: ...

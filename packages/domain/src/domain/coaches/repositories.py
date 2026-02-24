from __future__ import annotations

from abc import ABC, abstractmethod

from domain.coaches.coach import Coach
from domain.coaches.value_objects import Specialization


class ICoachRepository(ABC):
    @abstractmethod
    async def get_by_id(self, id: int) -> Coach | None: ...

    @abstractmethod
    async def get_by_email(self, email: str) -> Coach | None: ...

    @abstractmethod
    async def find_by_specialization(self, spec: Specialization) -> list[Coach]: ...

    @abstractmethod
    async def get_all(self) -> list[Coach]: ...

    @abstractmethod
    async def save(self, coach: Coach) -> Coach: ...

    @abstractmethod
    async def delete(self, id: int) -> None: ...

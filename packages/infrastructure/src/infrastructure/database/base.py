from abc import abstractmethod

from sqlmodel import SQLModel


class Base(SQLModel):
    @property
    @abstractmethod
    def is_new(self) -> bool: ...

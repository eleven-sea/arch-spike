from abc import abstractmethod

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    @property
    @abstractmethod
    def is_new(self) -> bool: ...

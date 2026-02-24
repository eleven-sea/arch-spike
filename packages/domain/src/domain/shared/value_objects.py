from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class FullName:
    first_name: str
    last_name: str

    def __post_init__(self) -> None:
        if not self.first_name.strip():
            raise ValueError("first_name cannot be blank")
        if not self.last_name.strip():
            raise ValueError("last_name cannot be blank")

    @property
    def full(self) -> str:
        return f"{self.first_name} {self.last_name}"


@dataclass(frozen=True)
class Email:
    value: str

    _PATTERN: re.Pattern = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

    def __post_init__(self) -> None:
        if not self._PATTERN.match(self.value):
            raise ValueError(f"Invalid email: {self.value!r}")


@dataclass(frozen=True)
class PhoneNumber:
    value: str

    _PATTERN: re.Pattern = re.compile(r"^\+?[1-9]\d{6,14}$")

    def __post_init__(self) -> None:
        if not self._PATTERN.match(self.value):
            raise ValueError(f"Invalid phone number: {self.value!r}")

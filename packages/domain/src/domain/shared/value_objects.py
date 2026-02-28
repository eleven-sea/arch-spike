
import re
from typing import ClassVar

from pydantic import BaseModel, ConfigDict, field_validator


class FullName(BaseModel):
    model_config = ConfigDict(frozen=True)

    first_name: str
    last_name: str

    @field_validator("first_name", "last_name")
    @classmethod
    def not_blank(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("cannot be blank")
        return v

    @property
    def full(self) -> str:
        return f"{self.first_name} {self.last_name}"


class Email(BaseModel):
    model_config = ConfigDict(frozen=True)

    _PATTERN: ClassVar[re.Pattern[str]] = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

    value: str

    @field_validator("value")
    @classmethod
    def valid_email(cls, v: str) -> str:
        if not cls._PATTERN.match(v):
            raise ValueError(f"Invalid email: {v!r}")
        return v


class PhoneNumber(BaseModel):
    model_config = ConfigDict(frozen=True)

    _PATTERN: ClassVar[re.Pattern[str]] = re.compile(r"^\+?[1-9]\d{6,14}$")

    value: str

    @field_validator("value")
    @classmethod
    def valid_phone(cls, v: str) -> str:
        if not cls._PATTERN.match(v):
            raise ValueError(f"Invalid phone number: {v!r}")
        return v

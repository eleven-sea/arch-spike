
from datetime import date
from typing import Self

from pydantic import BaseModel, model_validator

from domain.coaches.value_objects import CertId, SlotId, Weekday


class Certification(BaseModel):
    name: str
    issuing_body: str
    issued_at: date
    expires_at: date | None = None
    id: CertId | None = None

    def is_valid(self, as_of: date | None = None) -> bool:
        if self.expires_at is None:
            return True
        check = as_of or date.today()
        return self.expires_at >= check


class AvailabilitySlot(BaseModel):
    day: Weekday
    start_hour: int
    end_hour: int
    id: SlotId | None = None

    @model_validator(mode="after")
    def valid_hours(self) -> Self:
        if not (0 <= self.start_hour < self.end_hour <= 24):
            raise ValueError(
                f"Invalid slot hours: start={self.start_hour}, end={self.end_hour}"
            )
        return self

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from domain.coaches.value_objects import CertId, SlotId, Weekday


@dataclass
class Certification:
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


@dataclass
class AvailabilitySlot:
    day: Weekday
    start_hour: int
    end_hour: int
    id: SlotId | None = None

    def __post_init__(self) -> None:
        if not (0 <= self.start_hour < self.end_hour <= 24):
            raise ValueError(
                f"Invalid slot hours: start={self.start_hour}, end={self.end_hour}"
            )

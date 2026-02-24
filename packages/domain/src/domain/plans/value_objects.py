from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

PlanId = int
SessionId = int


class PlanStatus(str, Enum):
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class SessionStatus(str, Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    SKIPPED = "SKIPPED"


@dataclass(frozen=True)
class PlannedExercise:
    exercise_id: str
    name: str
    sets: int
    reps: int
    rest_seconds: int

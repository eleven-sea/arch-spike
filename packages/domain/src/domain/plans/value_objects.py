
from enum import StrEnum

from pydantic import BaseModel, ConfigDict

PlanId = int
SessionId = int


class PlanStatus(StrEnum):
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class SessionStatus(StrEnum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    SKIPPED = "SKIPPED"


class PlannedExercise(BaseModel):
    model_config = ConfigDict(frozen=True)

    exercise_id: str
    name: str
    sets: int
    reps: int
    rest_seconds: int

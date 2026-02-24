from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime

from domain.plans.value_objects import PlannedExercise, SessionId, SessionStatus


@dataclass
class WorkoutSession:
    name: str
    scheduled_date: date
    exercises: list[PlannedExercise] = field(default_factory=list)
    status: SessionStatus = SessionStatus.PENDING
    completed_at: datetime | None = None
    notes: str | None = None
    id: SessionId | None = None

    def complete(self, notes: str | None = None) -> None:
        if self.status != SessionStatus.PENDING:
            raise ValueError(
                f"Cannot complete session with status {self.status.value}"
            )
        self.status = SessionStatus.COMPLETED
        self.completed_at = datetime.utcnow()
        if notes is not None:
            self.notes = notes

    def skip(self) -> None:
        if self.status != SessionStatus.PENDING:
            raise ValueError(
                f"Cannot skip session with status {self.status.value}"
            )
        self.status = SessionStatus.SKIPPED

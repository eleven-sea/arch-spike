
from datetime import UTC, date, datetime

from pydantic import BaseModel

from domain.plans.value_objects import PlannedExercise, SessionId, SessionStatus


class WorkoutSession(BaseModel):
    name: str
    scheduled_date: date
    exercises: list[PlannedExercise] = []
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
        self.completed_at = datetime.now(UTC)
        if notes is not None:
            self.notes = notes

    def skip(self) -> None:
        if self.status != SessionStatus.PENDING:
            raise ValueError(
                f"Cannot skip session with status {self.status.value}"
            )
        self.status = SessionStatus.SKIPPED

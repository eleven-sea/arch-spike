from datetime import date, datetime
from typing import ClassVar, override

from sqlalchemy import Column, DateTime
from sqlmodel import Field, Relationship

from infrastructure.database.base import Base


class PlannedExerciseORM(Base, table=True):
    __tablename__: ClassVar[str] = "planned_exercises"  # pyright: ignore[reportIncompatibleVariableOverride]
    id: int | None = Field(default=None, primary_key=True)
    session_id: int = Field(foreign_key="workout_sessions.id")
    exercise_id: str = Field(max_length=100)
    name: str = Field(max_length=200)
    sets: int
    reps: int
    rest_seconds: int

    @property
    @override
    def is_new(self) -> bool:
        return self.id is None


class WorkoutSessionORM(Base, table=True):
    __tablename__: ClassVar[str] = "workout_sessions"  # pyright: ignore[reportIncompatibleVariableOverride]
    id: int | None = Field(default=None, primary_key=True)
    plan_id: int = Field(foreign_key="training_plans.id")
    name: str = Field(max_length=200)
    scheduled_date: date
    status: str = Field(default="PENDING", max_length=20)
    completed_at: datetime | None = Field(
        default=None, sa_column=Column(DateTime(timezone=True), nullable=True)
    )
    notes: str | None = Field(default=None)
    exercises: list[PlannedExerciseORM] = Relationship(
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "lazy": "selectin"}
    )

    @property
    @override
    def is_new(self) -> bool:
        return self.id is None


class TrainingPlanORM(Base, table=True):
    __tablename__: ClassVar[str] = "training_plans"  # pyright: ignore[reportIncompatibleVariableOverride]
    id: int | None = Field(default=None, primary_key=True)
    member_id: int
    coach_id: int
    name: str = Field(max_length=200)
    status: str = Field(default="DRAFT", max_length=20)
    starts_at: date
    ends_at: date
    sessions: list[WorkoutSessionORM] = Relationship(
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "lazy": "selectin"}
    )

    @property
    @override
    def is_new(self) -> bool:
        return self.id is None

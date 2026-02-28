from datetime import date, datetime
from typing import override

from sqlalchemy import BigInteger, Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from infrastructure.database.base import Base


class PlannedExerciseORM(Base):
    __tablename__ = "planned_exercises"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("workout_sessions.id", ondelete="CASCADE"), nullable=False
    )
    exercise_id: Mapped[str] = mapped_column(String(100), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    sets: Mapped[int] = mapped_column(Integer, nullable=False)
    reps: Mapped[int] = mapped_column(Integer, nullable=False)
    rest_seconds: Mapped[int] = mapped_column(Integer, nullable=False)

    @property
    @override
    def is_new(self) -> bool:
        return self.id is None  # pyright: ignore[reportUnnecessaryComparison]


class WorkoutSessionORM(Base):
    __tablename__ = "workout_sessions"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    plan_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("training_plans.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    scheduled_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="PENDING")
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    exercises: Mapped[list[PlannedExerciseORM]] = relationship(
        "PlannedExerciseORM",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    @property
    @override
    def is_new(self) -> bool:
        return self.id is None  # pyright: ignore[reportUnnecessaryComparison]


class TrainingPlanORM(Base):
    __tablename__ = "training_plans"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    member_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    coach_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="DRAFT")
    starts_at: Mapped[date] = mapped_column(Date, nullable=False)
    ends_at: Mapped[date] = mapped_column(Date, nullable=False)

    sessions: Mapped[list[WorkoutSessionORM]] = relationship(
        "WorkoutSessionORM",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    @property
    @override
    def is_new(self) -> bool:
        return self.id is None  # pyright: ignore[reportUnnecessaryComparison]

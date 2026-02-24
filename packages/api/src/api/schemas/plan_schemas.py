from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel


class ExerciseInput(BaseModel):
    name: str
    sets: int = 3
    reps: int = 10
    rest_seconds: int = 60
    exercise_id: str = "0"


class SessionCreate(BaseModel):
    name: str
    scheduled_date: str  # ISO date string
    exercises: list[ExerciseInput] = []


class CompleteSession(BaseModel):
    notes: Optional[str] = None


class PlanCreate(BaseModel):
    member_id: int
    coach_id: int
    name: str
    starts_at: str  # ISO date string
    ends_at: str    # ISO date string


class PlannedExerciseResponse(BaseModel):
    exercise_id: str
    name: str
    sets: int
    reps: int
    rest_seconds: int


class WorkoutSessionResponse(BaseModel):
    id: Optional[int]
    name: str
    scheduled_date: date
    status: str
    completed_at: Optional[datetime]
    notes: Optional[str]
    exercises: list[PlannedExerciseResponse]


class PlanProgressResponse(BaseModel):
    plan_id: int
    completion_pct: float


class PlanResponse(BaseModel):
    id: Optional[int]
    member_id: int
    coach_id: int
    name: str
    status: str
    starts_at: date
    ends_at: date
    sessions: list[WorkoutSessionResponse]

    @classmethod
    def from_domain(cls, p) -> "PlanResponse":
        return cls(
            id=p.id,
            member_id=p.member_id,
            coach_id=p.coach_id,
            name=p.name,
            status=p.status.value,
            starts_at=p.starts_at,
            ends_at=p.ends_at,
            sessions=[
                WorkoutSessionResponse(
                    id=s.id,
                    name=s.name,
                    scheduled_date=s.scheduled_date,
                    status=s.status.value,
                    completed_at=s.completed_at,
                    notes=s.notes,
                    exercises=[
                        PlannedExerciseResponse(
                            exercise_id=e.exercise_id,
                            name=e.name,
                            sets=e.sets,
                            reps=e.reps,
                            rest_seconds=e.rest_seconds,
                        )
                        for e in s.exercises
                    ],
                )
                for s in p.sessions
            ],
        )

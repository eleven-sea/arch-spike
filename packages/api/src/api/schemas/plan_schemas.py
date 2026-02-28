
from datetime import date, datetime
from typing import Self

from pydantic import BaseModel

from domain.plans.training_plan import TrainingPlan


class ExerciseInput(BaseModel):
    name: str
    sets: int = 3
    reps: int = 10
    rest_seconds: int = 60
    exercise_id: str = "0"


class SessionCreate(BaseModel):
    name: str
    scheduled_date: str
    exercises: list[ExerciseInput] = []


class CompleteSession(BaseModel):
    notes: str | None = None


class PlanCreate(BaseModel):
    member_id: int
    coach_id: int
    name: str
    starts_at: str
    ends_at: str


class PlannedExerciseResponse(BaseModel):
    exercise_id: str
    name: str
    sets: int
    reps: int
    rest_seconds: int


class WorkoutSessionResponse(BaseModel):
    id: int | None
    name: str
    scheduled_date: date
    status: str
    completed_at: datetime | None
    notes: str | None
    exercises: list[PlannedExerciseResponse]


class PlanProgressResponse(BaseModel):
    plan_id: int
    completion_pct: float


class PlanResponse(BaseModel):
    id: int | None
    member_id: int
    coach_id: int
    name: str
    status: str
    starts_at: date
    ends_at: date
    sessions: list[WorkoutSessionResponse]

    @classmethod
    def from_domain(cls, p: TrainingPlan) -> Self:
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

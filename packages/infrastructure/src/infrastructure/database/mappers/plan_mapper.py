from __future__ import annotations

from domain.plans.entities import WorkoutSession
from domain.plans.training_plan import TrainingPlan
from domain.plans.value_objects import PlannedExercise, PlanStatus, SessionStatus
from infrastructure.database.models.plan_models import (
    PlannedExerciseORM,
    TrainingPlanORM,
    WorkoutSessionORM,
)


class PlanMapper:
    @staticmethod
    def to_domain(orm: TrainingPlanORM) -> TrainingPlan:
        sessions = [
            WorkoutSession(
                id=s.id,
                name=s.name,
                scheduled_date=s.scheduled_date,
                status=SessionStatus(s.status),
                completed_at=s.completed_at,
                notes=s.notes,
                exercises=[
                    PlannedExercise(
                        exercise_id=e.exercise_id,
                        name=e.name,
                        sets=e.sets,
                        reps=e.reps,
                        rest_seconds=e.rest_seconds,
                    )
                    for e in (s.exercises or [])
                ],
            )
            for s in (orm.sessions or [])
        ]
        return TrainingPlan(
            id=orm.id,
            member_id=orm.member_id,
            coach_id=orm.coach_id,
            name=orm.name,
            status=PlanStatus(orm.status),
            starts_at=orm.starts_at,
            ends_at=orm.ends_at,
            sessions=sessions,
        )

    @staticmethod
    def to_orm(plan: TrainingPlan) -> TrainingPlanORM:
        pid = plan.id or 0
        sessions = [
            WorkoutSessionORM(
                id=s.id,
                plan_id=pid,
                name=s.name,
                scheduled_date=s.scheduled_date,
                status=s.status.value,
                completed_at=s.completed_at,
                notes=s.notes,
                exercises=[
                    PlannedExerciseORM(
                        session_id=s.id or 0,
                        exercise_id=e.exercise_id,
                        name=e.name,
                        sets=e.sets,
                        reps=e.reps,
                        rest_seconds=e.rest_seconds,
                    )
                    for e in s.exercises
                ],
            )
            for s in plan.sessions
        ]
        return TrainingPlanORM(
            id=plan.id,
            member_id=plan.member_id,
            coach_id=plan.coach_id,
            name=plan.name,
            status=plan.status.value,
            starts_at=plan.starts_at,
            ends_at=plan.ends_at,
            sessions=sessions,
        )

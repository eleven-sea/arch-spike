"""Unit tests for the TrainingPlan aggregate."""

from datetime import date, timedelta

import pytest

from domain.plans.entities import WorkoutSession
from domain.plans.events import (
    PlanActivated,
    PlanCompleted,
    PlanCreated,
    SessionCompleted,
)
from domain.plans.training_plan import TrainingPlan
from domain.plans.value_objects import PlannedExercise, PlanStatus, SessionStatus


def _plan(member_id: int = 1, coach_id: int = 1) -> TrainingPlan:
    return TrainingPlan.create(
        member_id=member_id,
        coach_id=coach_id,
        name="Test Plan",
        starts_at=date.today(),
        ends_at=date.today() + timedelta(weeks=4),
    )


def _session(name: str = "Leg Day", days_ahead: int = 1) -> WorkoutSession:
    return WorkoutSession(
        name=name,
        scheduled_date=date.today() + timedelta(days=days_ahead),
        exercises=[
            PlannedExercise(
                exercise_id="1",
                name="Squat",
                sets=3,
                reps=10,
                rest_seconds=60,
            )
        ],
    )


class TestPlanCreate:
    def test_starts_as_draft(self):
        plan = _plan()
        assert plan.status == PlanStatus.DRAFT

    def test_emits_plan_created_event(self):
        plan = _plan()
        events = plan.pull_events()
        assert len(events) == 1
        assert isinstance(events[0], PlanCreated)


class TestActivate:
    def test_activate_draft_plan(self):
        plan = _plan()
        plan.id = 1
        plan.activate()
        assert plan.status == PlanStatus.ACTIVE

    def test_activate_emits_event(self):
        plan = _plan()
        plan.id = 1
        plan.pull_events()  # clear PlanCreated
        plan.activate()
        events = plan.pull_events()
        assert len(events) == 1
        assert isinstance(events[0], PlanActivated)

    def test_cannot_activate_non_draft(self):
        plan = _plan()
        plan.id = 1
        plan.activate()
        with pytest.raises(ValueError, match="DRAFT"):
            plan.activate()


class TestAddSession:
    def test_add_session_to_draft(self):
        plan = _plan()
        plan.add_session(_session())
        assert len(plan.sessions) == 1

    def test_cannot_add_session_to_active_plan(self):
        plan = _plan()
        plan.id = 1
        plan.activate()
        with pytest.raises(ValueError, match="DRAFT"):
            plan.add_session(_session())


class TestCompleteSession:
    def _active_plan_with_session(self) -> tuple[TrainingPlan, WorkoutSession]:
        plan = _plan()
        plan.id = 10
        s = _session()
        s.id = 100
        plan.sessions.append(s)
        plan.status = PlanStatus.ACTIVE
        return plan, s

    def test_complete_session(self):
        plan, session = self._active_plan_with_session()
        plan.pull_events()  # clear
        plan.complete_session(session.id)
        assert session.status == SessionStatus.COMPLETED

    def test_complete_session_emits_event(self):
        plan, session = self._active_plan_with_session()
        plan.pull_events()
        plan.complete_session(session.id)
        events = plan.pull_events()
        assert any(isinstance(e, SessionCompleted) for e in events)

    def test_all_sessions_done_auto_completes_plan(self):
        plan, session = self._active_plan_with_session()
        plan.pull_events()
        plan.complete_session(session.id)
        assert plan.status == PlanStatus.COMPLETED

    def test_auto_complete_emits_plan_completed(self):
        plan, session = self._active_plan_with_session()
        plan.pull_events()
        plan.complete_session(session.id)
        events = plan.pull_events()
        assert any(isinstance(e, PlanCompleted) for e in events)

    def test_cannot_complete_session_on_draft_plan(self):
        plan = _plan()
        plan.id = 1
        s = _session()
        s.id = 1
        plan.sessions.append(s)
        with pytest.raises(ValueError):
            plan.complete_session(s.id)

    def test_cannot_complete_nonexistent_session(self):
        plan = _plan()
        plan.id = 1
        plan.status = PlanStatus.ACTIVE
        with pytest.raises(ValueError, match="not found"):
            plan.complete_session(9999)


class TestCancel:
    def test_cancel_draft(self):
        plan = _plan()
        plan.cancel()
        assert plan.status == PlanStatus.CANCELLED

    def test_cancel_active(self):
        plan = _plan()
        plan.id = 1
        plan.activate()
        plan.cancel()
        assert plan.status == PlanStatus.CANCELLED

    def test_cannot_cancel_completed(self):
        plan = _plan()
        plan.id = 1
        plan.status = PlanStatus.COMPLETED
        with pytest.raises(ValueError, match="COMPLETED"):
            plan.cancel()

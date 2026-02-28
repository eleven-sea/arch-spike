
from datetime import date
from typing import Self

from pydantic import BaseModel, PrivateAttr

from domain.plans.entities import WorkoutSession
from domain.plans.value_objects import PlanStatus, SessionStatus
from domain.shared.events import ApplicationEvent


class TrainingPlan(BaseModel):
    member_id: int
    coach_id: int
    name: str
    status: PlanStatus
    starts_at: date
    ends_at: date
    sessions: list[WorkoutSession] = []
    id: int | None = None

    _events: list[ApplicationEvent] = PrivateAttr(default_factory=list)  # pyright: ignore[reportUnknownVariableType]

    @classmethod
    def create(
        cls,
        member_id: int,
        coach_id: int,
        name: str,
        starts_at: date,
        ends_at: date,
    ) -> Self:
        from domain.plans.events import PlanCreated

        plan = cls(
            member_id=member_id,
            coach_id=coach_id,
            name=name,
            status=PlanStatus.DRAFT,
            starts_at=starts_at,
            ends_at=ends_at,
        )
        plan._events.append(
            PlanCreated(
                plan_id=plan.id,
                member_id=member_id,
                coach_id=coach_id,
            )
        )
        return plan

    def activate(self) -> None:
        from domain.plans.events import PlanActivated

        if self.status != PlanStatus.DRAFT:
            raise ValueError(
                f"Only DRAFT plans can be activated; current status: {self.status.value}"
            )
        self.status = PlanStatus.ACTIVE
        if self.id is not None:
            self._events.append(PlanActivated(plan_id=self.id))

    def add_session(self, session: WorkoutSession) -> None:
        if self.status != PlanStatus.DRAFT:
            raise ValueError("Sessions can only be added to DRAFT plans")
        self.sessions.append(session)

    def complete_session(self, session_id: int, notes: str | None = None) -> None:
        from domain.plans.events import PlanCompleted, SessionCompleted

        if self.status != PlanStatus.ACTIVE:
            raise ValueError(
                f"Cannot complete sessions on a {self.status.value} plan"
            )
        session = next((s for s in self.sessions if s.id == session_id), None)
        if session is None:
            raise ValueError(f"Session {session_id} not found")
        session.complete(notes)

        if self.id is not None:
            assert session.completed_at is not None
            self._events.append(
                SessionCompleted(
                    plan_id=self.id,
                    session_id=session_id,
                    completed_at=session.completed_at,
                )
            )

        all_done = all(
            s.status in (SessionStatus.COMPLETED, SessionStatus.SKIPPED)
            for s in self.sessions
        )
        if all_done and self.sessions:
            self.status = PlanStatus.COMPLETED
            if self.id is not None:
                self._events.append(
                    PlanCompleted(plan_id=self.id, member_id=self.member_id)
                )

    def cancel(self) -> None:
        if self.status in (PlanStatus.COMPLETED, PlanStatus.CANCELLED):
            raise ValueError(f"Cannot cancel a {self.status.value} plan")
        self.status = PlanStatus.CANCELLED

    def pull_events(self) -> list[ApplicationEvent]:
        events, self._events = self._events, []
        return events

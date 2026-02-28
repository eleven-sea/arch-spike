
from datetime import datetime

from domain.shared.events import ApplicationEvent


class PlanCreated(ApplicationEvent):
    plan_id: int | None
    member_id: int
    coach_id: int


class PlanActivated(ApplicationEvent):
    plan_id: int


class SessionCompleted(ApplicationEvent):
    plan_id: int
    session_id: int
    completed_at: datetime


class PlanCompleted(ApplicationEvent):
    plan_id: int
    member_id: int

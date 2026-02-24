from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from domain.shared.events import ApplicationEvent


@dataclass(frozen=True)
class PlanCreated(ApplicationEvent):
    plan_id: int | None
    member_id: int
    coach_id: int


@dataclass(frozen=True)
class PlanActivated(ApplicationEvent):
    plan_id: int


@dataclass(frozen=True)
class SessionCompleted(ApplicationEvent):
    plan_id: int
    session_id: int
    completed_at: datetime


@dataclass(frozen=True)
class PlanCompleted(ApplicationEvent):
    plan_id: int
    member_id: int

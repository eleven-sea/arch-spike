from __future__ import annotations

from dataclasses import dataclass

from domain.shared.events import ApplicationEvent


@dataclass(frozen=True)
class CoachRegistered(ApplicationEvent):
    coach_id: int | None
    email: str
    full_name: str

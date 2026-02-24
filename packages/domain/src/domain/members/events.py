from __future__ import annotations

from dataclasses import dataclass

from domain.shared.events import ApplicationEvent


@dataclass(frozen=True)
class MemberRegistered(ApplicationEvent):
    member_id: int | None
    email: str
    full_name: str


@dataclass(frozen=True)
class GoalAchieved(ApplicationEvent):
    member_id: int
    goal_id: int
    goal_type: str


@dataclass(frozen=True)
class MembershipUpgraded(ApplicationEvent):
    member_id: int
    old_tier: str
    new_tier: str

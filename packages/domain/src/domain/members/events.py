
from domain.shared.events import ApplicationEvent


class MemberRegistered(ApplicationEvent):
    member_id: int | None
    email: str
    full_name: str


class GoalAchieved(ApplicationEvent):
    member_id: int
    goal_id: int
    goal_type: str


class MembershipUpgraded(ApplicationEvent):
    member_id: int
    old_tier: str
    new_tier: str

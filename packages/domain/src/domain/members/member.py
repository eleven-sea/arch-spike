from __future__ import annotations

from dataclasses import dataclass, field

from domain.members.entities import FitnessGoal
from domain.members.value_objects import (
    FitnessLevel,
    GoalType,
    Membership,
    MembershipTier,
)
from domain.shared.value_objects import Email, FullName, PhoneNumber

FREE_MAX_GOALS = 2


@dataclass
class Member:
    name: FullName
    email: Email
    phone: PhoneNumber
    fitness_level: FitnessLevel
    membership: Membership
    goals: list[FitnessGoal] = field(default_factory=list)
    active_plan_id: int | None = None
    id: int | None = None

    _events: list = field(default_factory=list, repr=False, compare=False)

    # ------------------------------------------------------------------
    # Factory
    # ------------------------------------------------------------------
    @classmethod
    def create(
        cls,
        first_name: str,
        last_name: str,
        email: str,
        phone: str,
        fitness_level: FitnessLevel,
        membership: Membership,
    ) -> "Member":
        from domain.members.events import MemberRegistered

        member = cls(
            name=FullName(first_name, last_name),
            email=Email(email),
            phone=PhoneNumber(phone),
            fitness_level=fitness_level,
            membership=membership,
        )
        member._events.append(
            MemberRegistered(
                member_id=member.id,
                email=email,
                full_name=member.name.full,
            )
        )
        return member

    # ------------------------------------------------------------------
    # Invariants
    # ------------------------------------------------------------------
    def _assert_goal_limit(self) -> None:
        if (
            self.membership.tier == MembershipTier.FREE
            and len(self.goals) >= FREE_MAX_GOALS
        ):
            raise ValueError(
                f"FREE members may only have {FREE_MAX_GOALS} goals; "
                "upgrade your membership to add more."
            )

    # ------------------------------------------------------------------
    # Behaviour
    # ------------------------------------------------------------------
    def add_goal(self, goal: FitnessGoal) -> None:
        self._assert_goal_limit()
        self.goals.append(goal)

    def achieve_goal(self, goal_id: int) -> None:
        from domain.members.events import GoalAchieved

        goal = next((g for g in self.goals if g.id == goal_id), None)
        if goal is None:
            raise ValueError(f"Goal {goal_id} not found")
        goal.mark_achieved()
        if self.id is not None:
            self._events.append(
                GoalAchieved(
                    member_id=self.id,
                    goal_id=goal_id,
                    goal_type=goal.type.value,
                )
            )

    def upgrade_membership(self, new_membership: Membership) -> None:
        from domain.members.events import MembershipUpgraded

        old_tier = self.membership.tier
        self.membership = new_membership
        if self.id is not None:
            self._events.append(
                MembershipUpgraded(
                    member_id=self.id,
                    old_tier=old_tier.value,
                    new_tier=new_membership.tier.value,
                )
            )

    def assign_plan(self, plan_id: int) -> None:
        if self.active_plan_id is not None:
            raise ValueError(
                f"Member already has an active plan ({self.active_plan_id}). "
                "Complete or cancel it first."
            )
        self.active_plan_id = plan_id

    def clear_active_plan(self) -> None:
        self.active_plan_id = None

    def pull_events(self) -> list:
        events, self._events = self._events, []
        return events

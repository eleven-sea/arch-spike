"""Unit tests for the Member aggregate."""

from datetime import date, timedelta

import pytest

from domain.members.entities import FitnessGoal
from domain.members.events import MemberRegistered
from domain.members.member import Member
from domain.members.value_objects import (
    FitnessLevel,
    GoalType,
    Membership,
    MembershipTier,
)


def _membership(tier: MembershipTier = MembershipTier.FREE) -> Membership:
    return Membership(tier=tier, valid_until=date.today() + timedelta(days=30))


def _member(tier: MembershipTier = MembershipTier.FREE) -> Member:
    return Member.create(
        first_name="Jan",
        last_name="Kowalski",
        email="jan@test.com",
        phone="+48123456789",
        fitness_level=FitnessLevel.BEGINNER,
        membership=_membership(tier),
    )


def _goal(days_ahead: int = 30) -> FitnessGoal:
    return FitnessGoal(
        type=GoalType.LOSE_WEIGHT,
        description="Lose 5 kg",
        target_date=date.today() + timedelta(days=days_ahead),
    )


class TestMemberCreate:
    def test_emits_registered_event(self):
        member = _member()
        events = member.pull_events()
        assert len(events) == 1
        assert isinstance(events[0], MemberRegistered)
        assert events[0].email == "jan@test.com"

    def test_pull_events_clears_queue(self):
        member = _member()
        member.pull_events()
        assert member.pull_events() == []


class TestGoalLimit:
    def test_free_member_max_two_goals(self):
        member = _member(MembershipTier.FREE)
        member.add_goal(_goal(30))
        member.add_goal(_goal(60))
        with pytest.raises(ValueError, match="FREE members"):
            member.add_goal(_goal(90))

    def test_premium_member_can_add_more_goals(self):
        member = _member(MembershipTier.PREMIUM)
        for days in range(30, 180, 30):
            member.add_goal(_goal(days))
        assert len(member.goals) == 5



class TestActivePlan:
    def test_assign_plan(self):
        member = _member()
        member.id = 1
        member.assign_plan(42)
        assert member.active_plan_id == 42

    def test_cannot_assign_second_plan(self):
        member = _member()
        member.id = 1
        member.assign_plan(42)
        with pytest.raises(ValueError, match="already has an active plan"):
            member.assign_plan(99)

    def test_clear_active_plan(self):
        member = _member()
        member.assign_plan(42)
        member.clear_active_plan()
        assert member.active_plan_id is None

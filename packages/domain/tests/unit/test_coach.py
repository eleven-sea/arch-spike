"""Unit tests for the Coach aggregate."""

import pytest

from domain.coaches.coach import Coach
from domain.coaches.events import CoachRegistered
from domain.coaches.value_objects import CoachTier, Specialization
from domain.members.value_objects import MembershipTier


def _coach(tier: CoachTier = CoachTier.STANDARD, max_clients: int = 5) -> Coach:
    return Coach.create(
        first_name="Anna",
        last_name="Trainer",
        email="anna@gym.com",
        bio="Experienced trainer",
        tier=tier,
        specializations=frozenset({Specialization.STRENGTH, Specialization.CARDIO}),
        max_clients=max_clients,
    )


class TestCoachCreate:
    def test_emits_registered_event(self):
        coach = _coach()
        events = coach.pull_events()
        assert len(events) == 1
        assert isinstance(events[0], CoachRegistered)
        assert events[0].email == "anna@gym.com"


class TestCapacity:
    def test_can_accept_when_under_limit(self):
        coach = _coach(max_clients=3)
        assert coach.can_accept_client()

    def test_cannot_accept_when_full(self):
        coach = _coach(max_clients=1)
        coach.accept_client()
        assert not coach.can_accept_client()

    def test_accept_client_increments_count(self):
        coach = _coach(max_clients=5)
        coach.accept_client()
        assert coach.current_client_count == 1

    def test_accept_raises_when_full(self):
        coach = _coach(max_clients=1)
        coach.accept_client()
        with pytest.raises(ValueError, match="full capacity"):
            coach.accept_client()

    def test_release_decrements_count(self):
        coach = _coach(max_clients=5)
        coach.accept_client()
        coach.release_client()
        assert coach.current_client_count == 0

    def test_release_does_not_go_below_zero(self):
        coach = _coach()
        coach.release_client()
        assert coach.current_client_count == 0


class TestVIPTierRestriction:
    def test_vip_coach_rejects_non_vip_member(self):
        coach = _coach(tier=CoachTier.VIP, max_clients=10)
        assert not coach.can_accept_client(MembershipTier.FREE)
        assert not coach.can_accept_client(MembershipTier.PREMIUM)

    def test_vip_coach_accepts_vip_member(self):
        coach = _coach(tier=CoachTier.VIP, max_clients=10)
        assert coach.can_accept_client(MembershipTier.VIP)

    def test_standard_coach_accepts_any_tier(self):
        coach = _coach(tier=CoachTier.STANDARD, max_clients=10)
        assert coach.can_accept_client(MembershipTier.FREE)
        assert coach.can_accept_client(MembershipTier.PREMIUM)
        assert coach.can_accept_client(MembershipTier.VIP)

"""Unit tests for CoachService."""
from __future__ import annotations

from datetime import date, timedelta

import pytest

from application.coaches.coach_service import CoachService


@pytest.fixture()
def coach_service(coach_repo, member_repo, fake_cache, fake_dispatcher, fake_logger):
    return CoachService(
        coach_repo=coach_repo,
        member_repo=member_repo,
        cache=fake_cache,
        dispatcher=fake_dispatcher,
        app_logger=fake_logger,
    )


async def _register(svc: CoachService, email: str = "anna@gym.com"):
    return await svc.register(
        first_name="Anna",
        last_name="Trainer",
        email=email,
        bio="Experienced trainer",
        tier="STANDARD",
        specializations=["STRENGTH", "CARDIO"],
        max_clients=10,
    )


async def _register_member(member_repo, email: str = "jan@test.com"):
    from domain.members.member import Member
    from domain.members.value_objects import Membership, MembershipTier

    valid_until = date.today() + timedelta(days=30)
    member = Member.create(
        first_name="Jan",
        last_name="Kowalski",
        email=email,
        phone="+48123456789",
        fitness_level="BEGINNER",
        membership=Membership(tier=MembershipTier.FREE, valid_until=valid_until),
    )
    return await member_repo.save(member)


class TestRegister:
    async def test_creates_coach(self, coach_service, coach_repo):
        coach = await _register(coach_service)
        assert coach.id is not None
        stored = await coach_repo.get_by_id(coach.id)
        assert stored is not None

    async def test_duplicate_email_raises(self, coach_service):
        await _register(coach_service, "dup@gym.com")
        with pytest.raises(ValueError, match="already registered"):
            await _register(coach_service, "dup@gym.com")

    async def test_dispatches_registered_event(self, coach_service, fake_dispatcher):
        await _register(coach_service)
        fake_dispatcher.run_in_background.assert_called_once()


class TestFindAvailable:
    async def test_cache_miss_fetches_from_repo(self, coach_service, fake_cache):
        await _register(coach_service)
        coaches = await coach_service.find_available()
        assert len(coaches) >= 1

    async def test_cache_hit_returns_cached(self, coach_service, fake_cache):
        """If cache returns data, repo is not queried."""
        import json

        cached_data = json.dumps(
            [
                {
                    "id": 99,
                    "first_name": "Cached",
                    "last_name": "Coach",
                    "email": "cached@gym.com",
                    "bio": "",
                    "tier": "STANDARD",
                    "specializations": ["STRENGTH"],
                    "max_clients": 5,
                    "current_client_count": 0,
                }
            ]
        )
        fake_cache.get.return_value = cached_data
        coaches = await coach_service.find_available("STRENGTH")
        assert coaches[0].id == 99


class TestFindBestForMember:
    async def test_returns_best_matching_coach(
        self, coach_service, member_repo, fake_cache
    ):
        member = await _register_member(member_repo)
        # BEGINNER with no goals — any STANDARD coach with capacity is a candidate
        # but CoachMatchingService needs overlapping specs with member goals.
        # Add a goal so matching works.
        from domain.members.value_objects import GoalType
        from domain.members.entities import FitnessGoal

        member.goals.append(
            FitnessGoal(
                type=GoalType.BUILD_MUSCLE,
                description="Get stronger",
                target_date=date.today() + timedelta(days=90),
            )
        )
        await member_repo.save(member)

        await _register(coach_service)  # STRENGTH + CARDIO coach
        coach = await coach_service.find_best_for_member(member.id)
        assert coach is not None

    async def test_returns_none_when_no_match(self, coach_service, member_repo):
        member = await _register_member(member_repo)
        # No coaches registered → no match
        result = await coach_service.find_best_for_member(member.id)
        assert result is None

    async def test_raises_when_member_not_found(self, coach_service):
        with pytest.raises(ValueError, match="not found"):
            await coach_service.find_best_for_member(999)

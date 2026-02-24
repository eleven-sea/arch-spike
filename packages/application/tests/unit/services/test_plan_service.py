"""Unit tests for TrainingPlanService."""
from __future__ import annotations

from datetime import date, timedelta

import pytest

from application.plans.plan_service import TrainingPlanService
from domain.members.member import Member
from domain.members.value_objects import FitnessLevel, Membership, MembershipTier


@pytest.fixture()
def plan_service(plan_repo, member_repo, fake_cache, fake_exercise_client, fake_dispatcher, fake_logger):
    return TrainingPlanService(
        plan_repo=plan_repo,
        member_repo=member_repo,
        cache=fake_cache,
        exercise_client=fake_exercise_client,
        dispatcher=fake_dispatcher,
        app_logger=fake_logger,
    )


async def _make_member(member_repo) -> Member:
    from domain.shared.value_objects import Email, FullName, PhoneNumber

    member = Member(
        name=FullName("Jan", "Kowalski"),
        email=Email("jan@test.com"),
        phone=PhoneNumber("+48123456789"),
        fitness_level=FitnessLevel.BEGINNER,
        membership=Membership(
            tier=MembershipTier.FREE,
            valid_until=date.today() + timedelta(days=30),
        ),
    )
    return await member_repo.save(member)


class TestCreatePlan:
    async def test_creates_draft_plan(self, plan_service, member_repo):
        member = await _make_member(member_repo)
        plan = await plan_service.create_plan(
            member_id=member.id,
            coach_id=1,
            name="My Plan",
            starts_at=date.today().isoformat(),
            ends_at=(date.today() + timedelta(weeks=4)).isoformat(),
        )
        assert plan.id is not None
        assert plan.status.value == "DRAFT"

    async def test_raises_if_member_not_found(self, plan_service):
        with pytest.raises(ValueError, match="not found"):
            await plan_service.create_plan(
                member_id=9999,
                coach_id=1,
                name="x",
                starts_at=date.today().isoformat(),
                ends_at=(date.today() + timedelta(weeks=4)).isoformat(),
            )


class TestActivatePlan:
    async def test_activates_draft_plan(self, plan_service, member_repo):
        member = await _make_member(member_repo)
        plan = await plan_service.create_plan(
            member_id=member.id,
            coach_id=1,
            name="My Plan",
            starts_at=date.today().isoformat(),
            ends_at=(date.today() + timedelta(weeks=4)).isoformat(),
        )
        activated = await plan_service.activate_plan(plan.id)
        assert activated.status.value == "ACTIVE"


class TestAddSession:
    async def test_adds_session_with_exercise_lookup(
        self, plan_service, member_repo, fake_exercise_client
    ):
        member = await _make_member(member_repo)
        plan = await plan_service.create_plan(
            member_id=member.id,
            coach_id=1,
            name="My Plan",
            starts_at=date.today().isoformat(),
            ends_at=(date.today() + timedelta(weeks=4)).isoformat(),
        )
        updated = await plan_service.add_session(
            plan_id=plan.id,
            session_name="Leg Day",
            scheduled_date=(date.today() + timedelta(days=1)).isoformat(),
            exercises=[{"name": "Squat", "sets": 3, "reps": 10, "rest_seconds": 60}],
        )
        assert len(updated.sessions) == 1
        fake_exercise_client.search_exercises.assert_called_once_with("Squat")

    async def test_uses_cache_on_second_call(
        self, plan_service, member_repo, fake_cache, fake_exercise_client
    ):
        import json

        fake_cache.get.return_value = json.dumps({"exercise_id": "42", "name": "Squat"})
        member = await _make_member(member_repo)
        plan = await plan_service.create_plan(
            member_id=member.id,
            coach_id=1,
            name="My Plan",
            starts_at=date.today().isoformat(),
            ends_at=(date.today() + timedelta(weeks=4)).isoformat(),
        )
        await plan_service.add_session(
            plan_id=plan.id,
            session_name="Leg Day",
            scheduled_date=(date.today() + timedelta(days=1)).isoformat(),
            exercises=[{"name": "Squat", "sets": 3, "reps": 10, "rest_seconds": 60}],
        )
        # With cache hit, no exercise client call
        fake_exercise_client.search_exercises.assert_not_called()


class TestCompleteSession:
    async def _plan_with_active_session(self, plan_service, member_repo):
        member = await _make_member(member_repo)
        plan = await plan_service.create_plan(
            member_id=member.id,
            coach_id=1,
            name="My Plan",
            starts_at=date.today().isoformat(),
            ends_at=(date.today() + timedelta(weeks=4)).isoformat(),
        )
        plan = await plan_service.add_session(
            plan_id=plan.id,
            session_name="Day 1",
            scheduled_date=(date.today() + timedelta(days=1)).isoformat(),
            exercises=[{"name": "Squat", "sets": 3, "reps": 10, "rest_seconds": 60}],
        )
        plan = await plan_service.activate_plan(plan.id)
        return plan

    async def test_completes_session(self, plan_service, member_repo):
        plan = await self._plan_with_active_session(plan_service, member_repo)
        session_id = plan.sessions[0].id
        updated = await plan_service.complete_session(plan.id, session_id)
        assert updated.sessions[0].status.value == "COMPLETED"

    async def test_auto_completes_plan_when_last_session_done(
        self, plan_service, member_repo
    ):
        plan = await self._plan_with_active_session(plan_service, member_repo)
        session_id = plan.sessions[0].id
        updated = await plan_service.complete_session(plan.id, session_id)
        assert updated.status.value == "COMPLETED"


class TestGetProgress:
    async def test_empty_plan_is_zero(self, plan_service, member_repo):
        member = await _make_member(member_repo)
        plan = await plan_service.create_plan(
            member_id=member.id,
            coach_id=1,
            name="Empty",
            starts_at=date.today().isoformat(),
            ends_at=(date.today() + timedelta(weeks=4)).isoformat(),
        )
        pct = await plan_service.get_progress(plan.id)
        assert pct == 0.0

    async def test_one_of_two_sessions_completed(self, plan_service, member_repo):
        member = await _make_member(member_repo)
        plan = await plan_service.create_plan(
            member_id=member.id, coach_id=1, name="P",
            starts_at=date.today().isoformat(),
            ends_at=(date.today() + timedelta(weeks=4)).isoformat(),
        )
        for day in (1, 2):
            plan = await plan_service.add_session(
                plan_id=plan.id, session_name=f"Day {day}",
                scheduled_date=(date.today() + timedelta(days=day)).isoformat(),
                exercises=[],
            )
        plan = await plan_service.activate_plan(plan.id)
        await plan_service.complete_session(plan.id, plan.sessions[0].id)
        pct = await plan_service.get_progress(plan.id)
        assert pct == 50.0

    async def test_raises_for_missing_plan(self, plan_service):
        with pytest.raises(ValueError, match="not found"):
            await plan_service.get_progress(999)

"""Unit tests for MemberService."""

from datetime import date, timedelta

import pytest

from application.members.member_service import MemberService


@pytest.fixture()
def member_service(member_repo, fake_dispatcher, fake_logger, fake_task_dispatcher):
    return MemberService(
        member_repo=member_repo,
        dispatcher=fake_dispatcher,
        app_logger=fake_logger,
        task_dispatcher=fake_task_dispatcher,
    )


async def _register(svc: MemberService, email: str = "jan@test.com"):
    valid_until = (date.today() + timedelta(days=30)).isoformat()
    return await svc.register(
        first_name="Jan",
        last_name="Kowalski",
        email=email,
        phone="+48123456789",
        fitness_level="BEGINNER",
        membership_valid_until=valid_until,
    )


class TestRegister:
    async def test_creates_and_saves_member(self, member_service, member_repo):
        member = await _register(member_service)
        assert member.id is not None
        stored = await member_repo.get_by_id(member.id)
        assert stored is not None
        assert stored.email.value == "jan@test.com"

    async def test_dispatches_registered_event(self, member_service, fake_dispatcher):
        await _register(member_service)
        fake_dispatcher.run_in_background.assert_called_once()

    async def test_duplicate_email_raises(self, member_service):
        await _register(member_service, email="dup@test.com")
        with pytest.raises(ValueError, match="already registered"):
            await _register(member_service, email="dup@test.com")


class TestGetAll:
    async def test_returns_all_members(self, member_service):
        await _register(member_service, "a@test.com")
        await _register(member_service, "b@test.com")
        members = await member_service.get_all()
        assert len(members) == 2


class TestAddGoal:
    async def test_adds_goal_to_member(self, member_service):
        member = await _register(member_service)
        target = (date.today() + timedelta(days=60)).isoformat()
        updated = await member_service.add_goal(
            member_id=member.id,
            goal_type="LOSE_WEIGHT",
            description="Lose 5 kg",
            target_date=target,
        )
        assert len(updated.goals) == 1

    async def test_raises_if_member_not_found(self, member_service):
        with pytest.raises(ValueError):
            target = (date.today() + timedelta(days=60)).isoformat()
            await member_service.add_goal(9999, "LOSE_WEIGHT", "x", target)


class TestDelete:
    async def test_deletes_member(self, member_service, member_repo):
        member = await _register(member_service)
        await member_service.delete(member.id)
        with pytest.raises(ValueError):
            await member_repo.get_by_id(member.id)

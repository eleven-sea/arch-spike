"""Integration tests — Member aggregate against real PostgreSQL."""
from __future__ import annotations

from datetime import date, timedelta

import pytest


async def _register(svc, email: str = "jan@test.com"):
    valid_until = (date.today() + timedelta(days=30)).isoformat()
    return await svc.register(
        first_name="Jan",
        last_name="Kowalski",
        email=email,
        phone="+48123456789",
        fitness_level="BEGINNER",
        membership_valid_until=valid_until,
    )


class TestMemberIntegration:
    async def test_register_and_retrieve(self, member_service):
        member = await _register(member_service)
        assert member.id is not None
        fetched = await member_service.get(member.id)
        assert fetched is not None
        assert fetched.email.value == "jan@test.com"
        assert fetched.name.first_name == "Jan"

    async def test_add_goal_persisted(self, member_service):
        member = await _register(member_service)
        target = (date.today() + timedelta(days=60)).isoformat()
        updated = await member_service.add_goal(
            member_id=member.id,
            goal_type="LOSE_WEIGHT",
            description="Lose 5 kg",
            target_date=target,
        )
        assert len(updated.goals) == 1
        refetched = await member_service.get(member.id)
        assert len(refetched.goals) == 1
        assert refetched.goals[0].type.value == "LOSE_WEIGHT"

    async def test_duplicate_email_raises(self, member_service):
        await _register(member_service, email="dup@test.com")
        with pytest.raises(ValueError, match="already registered"):
            await _register(member_service, email="dup@test.com")

    async def test_delete_member(self, member_service):
        member = await _register(member_service)
        await member_service.delete(member.id)
        assert await member_service.get(member.id) is None

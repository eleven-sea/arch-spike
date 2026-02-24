"""Tests for BaseRepository using MemberORM as the concrete model."""
from __future__ import annotations

from datetime import date, timedelta

from infrastructure.database.models.member_models import MemberORM


def _make_member(email: str = "test@test.com") -> MemberORM:
    return MemberORM(
        first_name="Test",
        last_name="User",
        email=email,
        phone="+48123456789",
        fitness_level="BEGINNER",
        membership_tier="FREE",
        membership_valid_until=date.today() + timedelta(days=30),
    )


async def test_save_and_find_by_id(base_repo):
    member = await base_repo.save(_make_member("a@test.com"))
    assert member.id is not None

    found = await base_repo.find_by_id(member.id)
    assert found is not None
    assert found.email == "a@test.com"


async def test_find_by_id_not_found(base_repo):
    result = await base_repo.find_by_id(999999)
    assert result is None


async def test_save_all(base_repo):
    members = [_make_member("b@test.com"), _make_member("c@test.com")]
    saved = await base_repo.save_all(members)
    assert len(saved) == 2
    for m in saved:
        assert m.id is not None


async def test_find_all_empty(base_repo):
    result = await base_repo.find_all()
    assert result == []


async def test_find_all_with_data(base_repo):
    await base_repo.save(_make_member("d@test.com"))
    await base_repo.save(_make_member("e@test.com"))
    result = await base_repo.find_all()
    assert len(result) == 2


async def test_delete(base_repo):
    member = await base_repo.save(_make_member("f@test.com"))
    await base_repo.delete(member.id)
    assert await base_repo.find_by_id(member.id) is None


async def test_delete_all(base_repo):
    await base_repo.save(_make_member("g@test.com"))
    await base_repo.save(_make_member("h@test.com"))
    await base_repo.delete_all()
    assert await base_repo.find_all() == []


async def test_count_empty(base_repo):
    assert await base_repo.count() == 0


async def test_count_with_data(base_repo):
    await base_repo.save(_make_member("i@test.com"))
    await base_repo.save(_make_member("j@test.com"))
    assert await base_repo.count() == 2


async def test_exists_true(base_repo):
    member = await base_repo.save(_make_member("k@test.com"))
    assert await base_repo.exists(member.id) is True


async def test_exists_false(base_repo):
    assert await base_repo.exists(999999) is False

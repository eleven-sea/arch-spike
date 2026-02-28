"""Integration tests for transaction manager behaviour.

Scenarios:
- without any transaction wrapper each save is its own transaction
- transaction() wraps multiple saves in one atomic unit
- transaction() nested without new=True joins the outer transaction
- transaction(new=True) creates an independent inner transaction
"""

from datetime import date, timedelta

import pytest

from infrastructure.database.base_repository import BaseRepository
from infrastructure.database.models.member_models import MemberORM
from infrastructure.database.transaction_manager import TransactionManager


def _member(email: str) -> MemberORM:
    return MemberORM(
        first_name="Test",
        last_name="User",
        email=email,
        phone="+48100000000",
        fitness_level="BEGINNER",
        membership_tier="FREE",
        membership_valid_until=date.today() + timedelta(days=30),
    )


@pytest.fixture()
def repo(infra_database):
    return BaseRepository(MemberORM, infra_database.session)


@pytest.fixture()
def tm(infra_database):
    return TransactionManager(infra_database)


async def test_without_transaction_each_save_is_independent(repo):
    """First save must persist even when an exception is raised afterwards."""
    await repo.save(_member("first@test.com"))

    try:
        await repo.save(_member("second@test.com"))
        raise ValueError("simulated failure after second save")
    except ValueError:
        pass

    assert await repo.count() == 2


async def test_without_transaction_first_persists_if_second_never_called(repo):
    """Single save without transaction commits immediately."""
    await repo.save(_member("solo@test.com"))
    assert await repo.count() == 1


async def test_transaction_commits_all_on_success(repo, tm):
    async with tm.transaction():
        await repo.save(_member("tx-a@test.com"))
        await repo.save(_member("tx-b@test.com"))

    assert await repo.count() == 2


async def test_transaction_rollbacks_all_on_exception(repo, tm):
    with pytest.raises(ValueError):
        async with tm.transaction():
            await repo.save(_member("tx-c@test.com"))
            await repo.save(_member("tx-d@test.com"))
            raise ValueError("boom")

    assert await repo.count() == 0


async def test_nested_transaction_joins_outer_on_success(repo, tm):
    async with tm.transaction():
        await repo.save(_member("outer-a@test.com"))
        async with tm.transaction():
            await repo.save(_member("inner-a@test.com"))

    assert await repo.count() == 2


async def test_nested_transaction_joins_outer_rolls_back_together(repo, tm):
    """Inner 'commit' does nothing — outer rollback takes everything with it."""
    with pytest.raises(ValueError):
        async with tm.transaction():
            async with tm.transaction():
                await repo.save(_member("inner-b@test.com"))
            raise ValueError("outer boom")

    assert await repo.count() == 0


async def test_new_transaction_commits_independently_when_outer_succeeds(repo, tm):
    async with tm.transaction():
        await repo.save(_member("outer-b@test.com"))
        async with tm.transaction(new=True):
            await repo.save(_member("new-tx-a@test.com"))

    assert await repo.count() == 2


async def test_new_transaction_persists_when_outer_rolls_back(repo, tm):
    """Inner (new=True) commits before outer fails — inner data must survive."""
    with pytest.raises(ValueError):
        async with tm.transaction():
            async with tm.transaction(new=True):
                await repo.save(_member("new-tx-b@test.com"))
            raise ValueError("outer fails after inner committed")

    assert await repo.count() == 1


async def test_new_transaction_rolls_back_independently_when_inner_fails(repo, tm):
    """Inner failure rolls back only the inner transaction, outer continues."""
    async with tm.transaction():
        await repo.save(_member("outer-c@test.com"))
        with pytest.raises(ValueError):
            async with tm.transaction(new=True):
                await repo.save(_member("new-tx-c@test.com"))
                raise ValueError("inner fails")

    assert await repo.count() == 1
    members = await repo.find_all()
    assert members[0].email == "outer-c@test.com"

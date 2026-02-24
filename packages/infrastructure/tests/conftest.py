import pytest
import pytest_asyncio
from sqlalchemy import text

from infrastructure.database.session import Database
from infrastructure.database.migrations import run_migrations
from infrastructure.database.base_repository import BaseRepository
from infrastructure.database.models.member_models import MemberORM


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def infra_database(postgres_url):
    db = Database(postgres_url)
    await run_migrations(db.engine)
    yield db
    await db.engine.dispose()


@pytest.fixture()
def base_repo(infra_database):
    return BaseRepository(MemberORM, infra_database.session)


@pytest.fixture(autouse=True)
async def _clean_db(infra_database):
    yield
    async with infra_database.engine.begin() as conn:
        await conn.execute(text(
            "TRUNCATE planned_exercises, workout_sessions, training_plans, "
            "coach_spec_rows, availability_slots, certifications, coaches, "
            "fitness_goals, members RESTART IDENTITY CASCADE"
        ))

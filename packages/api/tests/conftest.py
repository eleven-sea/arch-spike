from __future__ import annotations

from unittest.mock import AsyncMock

import httpx
import pytest
import pytest_asyncio
from sqlalchemy import text

from bootstrap.context import ApplicationContext
from api.main import create_api


def _make_null_exercise_client():
    mock = AsyncMock()
    mock.search_exercises.return_value = [{"exercise_id": "0", "name": "Unknown"}]
    mock.get_exercise.return_value = None
    return mock


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def api_context(postgres_url, redis_url):
    ctx = ApplicationContext()
    ctx.container.config.database.url.override(postgres_url)
    ctx.container.config.redis.url.override(redis_url)
    # IExerciseClient (WgerAdapter) uses an external HTTP API — mock it in tests
    ctx.container.wger_client.override(AsyncMock())
    ctx.container.exercise_client.override(_make_null_exercise_client())
    await ctx.start()
    yield ctx
    await ctx.stop()


@pytest.fixture(scope="session")
def test_app(api_context):
    return create_api(api_context)


@pytest.fixture()
async def client(test_app):
    transport = httpx.ASGITransport(app=test_app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


@pytest.fixture(autouse=True)
async def _clean_db(api_context):
    yield
    db = api_context.container.database()
    async with db.engine.begin() as conn:
        await conn.execute(text(
            "TRUNCATE planned_exercises, workout_sessions, training_plans, "
            "coach_spec_rows, availability_slots, certifications, coaches, "
            "fitness_goals, members RESTART IDENTITY CASCADE"
        ))
    # Clear Redis cache between tests to prevent stale data
    redis_client = await api_context.container.redis_client.async_()
    await redis_client._redis.flushdb()

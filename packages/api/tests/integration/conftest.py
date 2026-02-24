"""Integration test fixtures — real PostgreSQL + Redis via testcontainers."""
from __future__ import annotations

from unittest.mock import AsyncMock

import pytest
import pytest_asyncio
from sqlalchemy import text

from bootstrap.context import ApplicationContext


def _make_null_exercise_client():
    mock = AsyncMock()
    mock.search_exercises.return_value = [{"exercise_id": "0", "name": "Unknown"}]
    mock.get_exercise.return_value = None
    return mock


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def app_context(postgres_url, redis_url):
    ctx = ApplicationContext()
    ctx.container.config.database.url.override(postgres_url)
    ctx.container.config.redis.url.override(redis_url)
    # IExerciseClient (WgerAdapter) uses an external HTTP API — mock it in tests
    ctx.container.wger_client.override(AsyncMock())
    ctx.container.exercise_client.override(_make_null_exercise_client())
    await ctx.start()
    yield ctx
    await ctx.stop()


@pytest.fixture()
def member_service(app_context):
    return app_context.container.member_service()


@pytest_asyncio.fixture()
async def coach_service(app_context):
    return await app_context.container.coach_service.async_()


@pytest_asyncio.fixture()
async def plan_service(app_context):
    return await app_context.container.plan_service.async_()


@pytest.fixture(autouse=True)
async def _clean_db(app_context):
    yield
    db = app_context.container.database()
    async with db.engine.begin() as conn:
        await conn.execute(text(
            "TRUNCATE planned_exercises, workout_sessions, training_plans, "
            "coach_spec_rows, availability_slots, certifications, coaches, "
            "fitness_goals, members RESTART IDENTITY CASCADE"
        ))
    # Clear Redis cache between tests
    redis_client = await app_context.container.redis_client.async_()
    await redis_client._redis.flushdb()

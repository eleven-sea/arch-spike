from __future__ import annotations

from collections.abc import AsyncIterator

from dependency_injector import containers, providers

from infrastructure.database.session import Database
from infrastructure.database.transaction_manager import TransactionManager
from infrastructure.redis.redis_client import RedisClient
from infrastructure.adapters.cache_adapter import RedisCacheAdapter
from infrastructure.adapters.broker_adapter import RedisBrokerAdapter
from infrastructure.adapters.exercise_adapter import WgerAdapter
from infrastructure.clients.exercise_client import WgerClient
from infrastructure.repositories.member_repository import PostgresMemberRepository
from infrastructure.repositories.coach_repository import PostgresCoachRepository
from infrastructure.repositories.plan_repository import PostgresTrainingPlanRepository
from application.members.member_service import MemberService
from application.members.event_handlers import MemberRegisteredHandler
from application.coaches.coach_service import CoachService
from application.coaches.event_handlers import CoachRegisteredHandler
from application.plans.plan_service import TrainingPlanService
from application.plans.event_handlers import SessionCompletedHandler, PlanCompletedHandler
from application.settings import Settings
from application.logger import ApplicationLogger
from application.event_dispatcher import EventDispatcher


async def init_redis_client(url: str) -> AsyncIterator[RedisClient]:
    client = RedisClient(url=url)
    yield client
    await client.close()


async def init_wger_client(base_url: str, timeout: float) -> AsyncIterator[WgerClient]:
    client = WgerClient(base_url=base_url, timeout=timeout)
    yield client
    await client.close()


class Container(containers.DeclarativeContainer):
    config = providers.Configuration(pydantic_settings=[Settings()])

    # ── Core ─────────────────────────────────────────────────────────────
    app_logger = providers.Singleton(ApplicationLogger)
    event_dispatcher = providers.Singleton(EventDispatcher, app_logger=app_logger)

    # ── Database ─────────────────────────────────────────────────────────
    database = providers.Singleton(
        Database,
        db_url=config.database.url,
        pool_size=config.database.pool_size,
        max_overflow=config.database.max_overflow,
        pool_timeout=config.database.pool_timeout,
        pool_recycle=config.database.pool_recycle,
    )

    # ── External resources ────────────────────────────────────────────────
    redis_client = providers.Resource(init_redis_client, url=config.redis.url)

    # Raw wger HTTP client — infrastructure detail, not exposed as a port
    wger_client = providers.Resource(
        init_wger_client,
        base_url=config.exercise_api.base_url,
        timeout=config.exercise_api.timeout,
    )

    # ── Adapters (port implementations) ──────────────────────────────────
    cache_adapter = providers.Singleton(RedisCacheAdapter, client=redis_client)
    broker_adapter = providers.Singleton(RedisBrokerAdapter, client=redis_client)
    # WgerAdapter implements IExerciseClient — named exercise_client to match the port
    exercise_client = providers.Singleton(WgerAdapter, client=wger_client, app_logger=app_logger)

    # ── Transaction manager ───────────────────────────────────────────────
    transaction_manager = providers.Factory(TransactionManager, database=database)

    # ── Repositories ─────────────────────────────────────────────────────
    member_repository = providers.Factory(
        PostgresMemberRepository,
        session_factory=database.provided.session,
    )
    coach_repository = providers.Factory(
        PostgresCoachRepository,
        session_factory=database.provided.session,
    )
    plan_repository = providers.Factory(
        PostgresTrainingPlanRepository,
        session_factory=database.provided.session,
    )

    # ── Event handlers ────────────────────────────────────────────────────
    member_registered_handler = providers.Singleton(
        MemberRegisteredHandler, broker=broker_adapter, app_logger=app_logger
    )
    coach_registered_handler = providers.Singleton(
        CoachRegisteredHandler, app_logger=app_logger
    )
    session_completed_handler = providers.Singleton(
        SessionCompletedHandler, app_logger=app_logger
    )
    plan_completed_handler = providers.Singleton(
        PlanCompletedHandler, broker=broker_adapter, app_logger=app_logger
    )

    # ── Application services ──────────────────────────────────────────────
    member_service = providers.Factory(
        MemberService,
        member_repo=member_repository,
        dispatcher=event_dispatcher,
        app_logger=app_logger,
    )
    coach_service = providers.Factory(
        CoachService,
        coach_repo=coach_repository,
        member_repo=member_repository,
        cache=cache_adapter,
        dispatcher=event_dispatcher,
        app_logger=app_logger,
    )
    plan_service = providers.Factory(
        TrainingPlanService,
        plan_repo=plan_repository,
        member_repo=member_repository,
        cache=cache_adapter,
        exercise_client=exercise_client,
        dispatcher=event_dispatcher,
        app_logger=app_logger,
    )

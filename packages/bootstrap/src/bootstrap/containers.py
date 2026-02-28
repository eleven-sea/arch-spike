
from collections.abc import AsyncIterator

from dependency_injector import containers, providers

from application.coaches.coach_service import CoachService
from application.coaches.event_handlers import CoachRegisteredHandler
from application.event_dispatcher import EventDispatcher
from application.logger import ApplicationLogger
from application.members.event_handlers import MemberRegisteredHandler
from application.members.member_service import MemberService
from application.plans.event_handlers import (
    PlanCompletedHandler,
    SessionCompletedHandler,
)
from application.plans.plan_service import TrainingPlanService
from application.settings import Settings
from infrastructure.adapters.broker_adapter import RedisBrokerAdapter
from infrastructure.adapters.cache_adapter import RedisCacheAdapter
from infrastructure.adapters.exercise_adapter import WgerAdapter
from infrastructure.adapters.task_dispatcher import TaskiqTaskDispatcher
from infrastructure.clients.exercise_client import WgerClient
from infrastructure.database.session import Database
from infrastructure.database.transaction_manager import TransactionManager
from infrastructure.redis.redis_client import RedisClient
from infrastructure.repositories.coach_repository import CoachRepository, PostgresCoachRepository
from infrastructure.repositories.member_repository import MemberRepository, PostgresMemberRepository
from infrastructure.repositories.plan_repository import PostgresTrainingPlanRepository, TrainingPlanRepository
from infrastructure.taskiq.broker import broker as _taskiq_broker


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

    app_logger = providers.Singleton(ApplicationLogger)
    event_dispatcher = providers.Singleton(EventDispatcher, app_logger=app_logger)

    database = providers.Singleton(
        Database,
        db_url=config.database.url,
        pool_size=config.database.pool_size,
        max_overflow=config.database.max_overflow,
        pool_timeout=config.database.pool_timeout,
        pool_recycle=config.database.pool_recycle,
    )

    redis_client = providers.Resource(init_redis_client, url=config.redis.url)

    wger_client = providers.Resource(
        init_wger_client,
        base_url=config.exercise_api.base_url,
        timeout=config.exercise_api.timeout,
    )

    cache_adapter = providers.Singleton(RedisCacheAdapter, client=redis_client)
    broker_adapter = providers.Singleton(RedisBrokerAdapter, client=redis_client)
    exercise_client = providers.Singleton(WgerAdapter, client=wger_client, app_logger=app_logger)
    taskiq_broker = providers.Object(_taskiq_broker)
    task_dispatcher = providers.Singleton(TaskiqTaskDispatcher, broker=taskiq_broker)

    transaction_manager = providers.Singleton(TransactionManager, database=database)

    postgres_member_repository = providers.Singleton(
        PostgresMemberRepository,
        session_factory=database.provided.session,
    )
    postgres_coach_repository = providers.Singleton(
        PostgresCoachRepository,
        session_factory=database.provided.session,
    )
    postgres_plan_repository = providers.Singleton(
        PostgresTrainingPlanRepository,
        session_factory=database.provided.session,
    )

    member_repository = providers.Singleton(MemberRepository, repo=postgres_member_repository)
    coach_repository = providers.Singleton(CoachRepository, repo=postgres_coach_repository)
    plan_repository = providers.Singleton(TrainingPlanRepository, repo=postgres_plan_repository)

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

    member_service = providers.Singleton(
        MemberService,
        member_repo=member_repository,
        dispatcher=event_dispatcher,
        app_logger=app_logger,
        task_dispatcher=task_dispatcher,
    )
    coach_service = providers.Singleton(
        CoachService,
        coach_repo=coach_repository,
        member_repo=member_repository,
        cache=cache_adapter,
        dispatcher=event_dispatcher,
        app_logger=app_logger,
    )
    plan_service = providers.Singleton(
        TrainingPlanService,
        plan_repo=plan_repository,
        member_repo=member_repository,
        cache=cache_adapter,
        exercise_client=exercise_client,
        dispatcher=event_dispatcher,
        app_logger=app_logger,
    )

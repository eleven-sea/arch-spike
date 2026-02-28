from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy.ext.asyncio import AsyncEngine

import infrastructure.database.models.coach_models  # noqa: F401
import infrastructure.database.models.member_models  # noqa: F401
import infrastructure.database.models.plan_models  # noqa: F401


async def run_migrations(engine: AsyncEngine) -> None:
    alembic_cfg = Config()
    alembic_cfg.set_main_option(
        "script_location", str(Path(__file__).resolve().parent)
    )

    def _run(connection: object) -> None:
        alembic_cfg.attributes["connection"] = connection
        command.upgrade(alembic_cfg, "head")

    async with engine.begin() as conn:
        await conn.run_sync(_run)


from typing import override

from application.core.events import IApplicationEventHandler
from application.core.logger import ILogger
from domain.coaches.events import CoachRegistered


class CoachRegisteredHandler(IApplicationEventHandler[CoachRegistered]):
    def __init__(self, app_logger: ILogger) -> None:
        self._log = app_logger.get_logger(__name__)

    @override
    async def handle(self, event: CoachRegistered) -> None:
        self._log.info(
            "Coach registered: id=%s name=%s email=%s",
            event.coach_id,
            event.full_name,
            event.email,
        )

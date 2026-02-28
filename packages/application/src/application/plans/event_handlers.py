
import json
from typing import override

from application.core.events import IApplicationEventHandler
from application.core.logger import ILogger
from application.core.ports import IMessageBroker
from domain.plans.events import PlanCompleted, SessionCompleted


class SessionCompletedHandler(IApplicationEventHandler[SessionCompleted]):
    def __init__(self, app_logger: ILogger) -> None:
        self._log = app_logger.get_logger(__name__)

    @override
    async def handle(self, event: SessionCompleted) -> None:
        self._log.info(
            "Session %s completed on plan %s at %s",
            event.session_id,
            event.plan_id,
            event.completed_at.isoformat(),
        )


class PlanCompletedHandler(IApplicationEventHandler[PlanCompleted]):
    def __init__(self, broker: IMessageBroker, app_logger: ILogger) -> None:
        self._broker = broker
        self._log = app_logger.get_logger(__name__)

    @override
    async def handle(self, event: PlanCompleted) -> None:
        payload = json.dumps(
            {
                "plan_id": event.plan_id,
                "member_id": event.member_id,
            }
        )
        await self._broker.publish("plan.completed", payload)
        self._log.info(
            "Published plan.completed for plan_id=%s member_id=%s",
            event.plan_id,
            event.member_id,
        )

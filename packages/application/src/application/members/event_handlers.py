from __future__ import annotations

import json

from domain.members.events import MemberRegistered
from application.core.events import IApplicationEventHandler
from application.core.logger import ILogger
from application.core.ports import IMessageBroker


class MemberRegisteredHandler(IApplicationEventHandler[MemberRegistered]):
    def __init__(self, broker: IMessageBroker, app_logger: ILogger) -> None:
        self._broker = broker
        self._log = app_logger.get_logger(__name__)

    async def handle(self, event: MemberRegistered) -> None:
        payload = json.dumps(
            {
                "member_id": event.member_id,
                "email": event.email,
                "full_name": event.full_name,
            }
        )
        await self._broker.publish("member.registered", payload)
        self._log.info("Published member.registered for member_id=%s", event.member_id)

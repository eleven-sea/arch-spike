from __future__ import annotations

from application.core.ports import IMessageBroker
from infrastructure.redis.redis_client import RedisClient


class RedisBrokerAdapter(IMessageBroker):
    def __init__(self, client: RedisClient) -> None:
        self._client = client

    async def publish(self, channel: str, message: str) -> None:
        await self._client.publish(channel, message)

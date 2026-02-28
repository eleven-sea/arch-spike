
from typing import override

from application.core.ports import ICache
from infrastructure.redis.redis_client import RedisClient


class RedisCacheAdapter(ICache):
    def __init__(self, client: RedisClient) -> None:
        self._client = client

    @override
    async def get(self, key: str) -> str | None:
        return await self._client.get(key)

    @override
    async def set(self, key: str, value: str, ttl_seconds: int) -> None:
        await self._client.set(key, value, ttl_seconds)

    @override
    async def delete(self, key: str) -> None:
        await self._client.delete(key)

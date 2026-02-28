import redis.asyncio as redis
from redis.asyncio.client import PubSub


class RedisClient:
    def __init__(self, url: str):
        self._redis = redis.from_url(url, decode_responses=True)

    async def publish(self, channel: str, message: str) -> None:
        await self._redis.publish(channel, message)  # pyright: ignore[reportUnknownMemberType]

    def pubsub(self) -> PubSub:
        return self._redis.pubsub()  # pyright: ignore[reportUnknownMemberType]

    async def subscribe(self, channel: str):
        pubsub = self._redis.pubsub()  # pyright: ignore[reportUnknownMemberType]
        await pubsub.subscribe(channel)  # pyright: ignore[reportUnknownMemberType]
        return pubsub

    async def get(self, key: str) -> str | None:
        return await self._redis.get(key)

    async def set(self, key: str, value: str, ttl_seconds: int) -> None:
        await self._redis.set(key, value, ex=ttl_seconds)

    async def delete(self, key: str) -> None:
        await self._redis.delete(key)

    async def close(self) -> None:
        await self._redis.aclose()

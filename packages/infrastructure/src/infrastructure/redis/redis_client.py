import redis.asyncio as redis


class RedisClient:
    def __init__(self, url: str):
        self._redis = redis.from_url(url, decode_responses=True)

    # ── Pub/Sub ──────────────────────────────────────────────────────────
    async def publish(self, channel: str, message: str) -> None:
        await self._redis.publish(channel, message)

    async def subscribe(self, channel: str):
        pubsub = self._redis.pubsub()
        await pubsub.subscribe(channel)
        return pubsub

    # ── Cache ─────────────────────────────────────────────────────────────
    async def get(self, key: str) -> str | None:
        return await self._redis.get(key)

    async def set(self, key: str, value: str, ttl_seconds: int) -> None:
        await self._redis.set(key, value, ex=ttl_seconds)

    async def delete(self, key: str) -> None:
        await self._redis.delete(key)

    async def close(self) -> None:
        await self._redis.aclose()

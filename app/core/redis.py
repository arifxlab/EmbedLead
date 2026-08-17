from redis.asyncio import Redis

from app.core.config import get_settings

settings = get_settings()

redis_client = Redis.from_url(
    settings.redis_url,
    decode_responses=True,
)


async def get_cached(key: str) -> str | None:
    return await redis_client.get(key)


async def set_cached(
    key: str,
    value: str,
    ttl_seconds: int,
) -> None:
    await redis_client.set(
        key,
        value,
        ex=ttl_seconds,
    )


async def delete_cached(key: str) -> None:
    await redis_client.delete(key)


async def close_redis() -> None:
    await redis_client.close()

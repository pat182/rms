from redis.asyncio import Redis
from app.core.config import settings


async def connect_redis(app):
    redis_client = Redis.from_url(
        settings.REDIS_URL,
        decode_responses=True,
    )

    await redis_client.ping()

    app.state.redis = redis_client

async def close_redis(app):
    redis_client = getattr(app.state, "redis", None)

    if redis_client:
        await redis_client.aclose()



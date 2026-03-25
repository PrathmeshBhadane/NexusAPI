import time
import redis.asyncio as aioredis
from fastapi import HTTPException
from app.core.config import settings

async def check_rate_limit(user_id: str):
    client = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
    try:
        key = f"rate_limit:{user_id}"
        now = time.time()
        window_start = now - settings.RATE_LIMIT_WINDOW

        pipe = client.pipeline()
        await pipe.zremrangebyscore(key, 0, window_start)
        await pipe.zcard(key)
        await pipe.zadd(key, {str(now): now})
        await pipe.expire(key, settings.RATE_LIMIT_WINDOW)
        
        # Track Lifetime Usage natively
        await pipe.incr(f"usage_total:{user_id}")
        
        results = await pipe.execute()

        request_count = results[1]

        if request_count >= settings.RATE_LIMIT_REQUESTS:
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded. Max {settings.RATE_LIMIT_REQUESTS} requests per hour."
            )
    finally:
        await client.aclose()
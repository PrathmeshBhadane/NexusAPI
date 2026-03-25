from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.core.config import settings
from app.routers import ai
import redis.asyncio as redis
from datetime import datetime
import asyncio

async def register_service(redis_client):
    while True:
        try:
            await redis_client.hset("registry:ai-service", mapping={
                "url": "http://ai-service:8003",
                "status": "healthy",
                "last_seen": datetime.utcnow().isoformat()
            })
            await redis_client.expire("registry:ai-service", 30)
        except:
            pass
        await asyncio.sleep(10)

@asynccontextmanager
async def lifespan(app: FastAPI):
    redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
    asyncio.create_task(register_service(redis_client))
    yield
    await redis_client.aclose()

app = FastAPI(title="AI Service", version="1.0.0", lifespan=lifespan)

app.include_router(ai.router)

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "ai-service"}
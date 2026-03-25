from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.core.database import engine, Base
from app.core.config import settings
from app.routers import data
import app.models
import redis.asyncio as redis
from datetime import datetime
import asyncio
import logging

logging.basicConfig(level=logging.INFO)

async def register_service(redis_client):
    while True:
        try:
            await redis_client.hset("registry:data-service", mapping={
                "url": "http://data-service:8004",
                "status": "healthy",
                "last_seen": datetime.utcnow().isoformat()
            })
            await redis_client.expire("registry:data-service", 30)
        except:
            pass
        await asyncio.sleep(10)

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
    asyncio.create_task(register_service(redis_client))

    yield

    await engine.dispose()
    await redis_client.aclose()

app = FastAPI(title="Data Service", version="1.0.0", lifespan=lifespan)

app.include_router(data.router)

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "data-service"}
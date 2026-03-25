from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.core.config import settings
from app.routers.proxy import router
import redis.asyncio as redis
from datetime import datetime
import asyncio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def register_service(redis_client):
    while True:
        try:
            await redis_client.hset("registry:gateway", mapping={
                "url": "http://gateway:8000",
                "status": "healthy",
                "last_seen": datetime.utcnow().isoformat()
            })
            await redis_client.expire("registry:gateway", 30)
        except:
            pass
        await asyncio.sleep(10)

@asynccontextmanager
async def lifespan(app: FastAPI):
    redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
    asyncio.create_task(register_service(redis_client))
    logger.info("Gateway started")
    yield
    await redis_client.aclose()

app = FastAPI(title="API Gateway", version="1.0.0", lifespan=lifespan)

app.include_router(router)

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "gateway"}
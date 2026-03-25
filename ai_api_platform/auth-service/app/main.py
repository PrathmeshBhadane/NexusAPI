from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.core.database import engine, Base
import app.models
from app.routers import auth, keys
import redis.asyncio as redis
from app.core.config import settings
from datetime import datetime
import asyncio

async def register_service(redis_client):
    while True:
        try:
            await redis_client.hset("registry:auth-service", mapping={
                "url": "http://auth-service:8001",
                "status": "healthy",
                "last_seen": datetime.utcnow().isoformat()
            })
            await redis_client.expire("registry:auth-service", 30)
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
    await redis_client.close()

app = FastAPI(title="Auth Service", version="1.0.0", lifespan=lifespan)

app.include_router(auth.router)
app.include_router(keys.router)

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "auth-service"}
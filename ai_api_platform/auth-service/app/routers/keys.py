import hashlib
import secrets
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.user import User
from app.models.api_key import ApiKey
from app.schemas.api_key import ApiKeyCreate, ApiKeyResponse, ApiKeyCreatedResponse, ValidateApiKeyRequest, ValidateApiKeyResponse

router = APIRouter(prefix="/keys", tags=["api-keys"])
bearer_scheme = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    payload = decode_access_token(credentials.credentials)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    result = await db.execute(select(User).where(User.id == payload.get("sub")))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

def generate_api_key():
    raw = secrets.token_urlsafe(32)
    prefix = raw[:8]
    hashed = hashlib.sha256(raw.encode()).hexdigest()
    return raw, prefix, hashed

@router.post("/create", response_model=ApiKeyCreatedResponse)
async def create_key(
    payload: ApiKeyCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    raw_key, prefix, hashed_key = generate_api_key()
    api_key = ApiKey(
        user_id=current_user.id,
        name=payload.name,
        service=payload.service,
        hashed_key=hashed_key,
        prefix=prefix
    )
    db.add(api_key)
    await db.commit()
    await db.refresh(api_key)
    return ApiKeyCreatedResponse(id=api_key.id, name=api_key.name, service=api_key.service, key=raw_key, prefix=prefix)

@router.get("/list", response_model=list[ApiKeyResponse])
async def list_keys(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(ApiKey).where(ApiKey.user_id == current_user.id, ApiKey.is_active == True)
    )
    keys = result.scalars().all()

    # Hydrate heavily with Redis Metrics
    import redis.asyncio as aioredis
    from app.core.config import settings
    import time
    
    client = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
    try:
        now = time.time()
        window_start = now - settings.RATE_LIMIT_WINDOW
        
        pipe = client.pipeline()
        for k in keys:
            pipe.get(f"usage_total:{k.id}")
            pipe.zcount(f"rate_limit:{k.id}", window_start, "+inf")
            
        results = await pipe.execute() if keys else []
        
        hydrated_keys = []
        for i, k in enumerate(keys):
            total = int(results[i*2]) if results[i*2] else 0
            hourly = int(results[i*2 + 1]) if results[i*2 + 1] else 0
            
            key_data = ApiKeyResponse.model_validate(k).model_dump()
            key_data["total_requests"] = total
            key_data["hourly_requests"] = hourly
            hydrated_keys.append(key_data)
            
        return hydrated_keys
    finally:
        await client.aclose()

@router.delete("/{key_id}")
async def delete_key(
    key_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(ApiKey).where(ApiKey.id == key_id, ApiKey.user_id == current_user.id)
    )
    api_key = result.scalar_one_or_none()
    if not api_key:
        raise HTTPException(status_code=404, detail="API key not found")

    api_key.is_active = False
    await db.commit()
    return {"message": "API key revoked"}

@router.post("/validate", response_model=ValidateApiKeyResponse)
async def validate_api_key(payload: ValidateApiKeyRequest, db: AsyncSession = Depends(get_db)):
    hashed = hashlib.sha256(payload.api_key.encode()).hexdigest()
    result = await db.execute(
        select(ApiKey).where(ApiKey.hashed_key == hashed, ApiKey.is_active == True)
    )
    key_obj = result.scalar_one_or_none()
    if not key_obj:
        return ValidateApiKeyResponse(valid=False)

    key_obj.last_used_at = datetime.utcnow()
    await db.commit()

    result = await db.execute(select(User).where(User.id == key_obj.user_id))
    user = result.scalar_one_or_none()
    if not user:
        return ValidateApiKeyResponse(valid=False)

    return ValidateApiKeyResponse(
        valid=True,
        key_id=str(key_obj.id),
        user_id=str(user.id),
        email=user.email,
        username=user.username,
        service=key_obj.service
    )
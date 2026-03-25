from pydantic import BaseModel
import uuid
from datetime import datetime

class ApiKeyCreate(BaseModel):
    name: str
    service: str = "all"

class ApiKeyResponse(BaseModel):
    id: uuid.UUID
    name: str
    service: str
    prefix: str
    is_active: bool
    created_at: datetime
    last_used_at: datetime | None
    total_requests: int = 0
    hourly_requests: int = 0

    class Config:
        from_attributes = True

class ApiKeyCreatedResponse(BaseModel):
    id: uuid.UUID
    name: str
    service: str
    key: str
    prefix: str
    message: str = "Store this key safely — it won't be shown again"

class ValidateApiKeyRequest(BaseModel):
    api_key: str

class ValidateApiKeyResponse(BaseModel):
    valid: bool
    key_id: str | None = None
    user_id: str | None = None
    email: str | None = None
    username: str | None = None
    service: str | None = None
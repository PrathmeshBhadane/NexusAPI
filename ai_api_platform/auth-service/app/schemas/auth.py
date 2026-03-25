from pydantic import BaseModel, EmailStr
import uuid

class RegisterRequest(BaseModel):
    email: EmailStr
    username: str
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    username: str
    is_active: bool

    class Config:
        from_attributes = True

class ValidateTokenRequest(BaseModel):
    token: str

class ValidateTokenResponse(BaseModel):
    valid: bool
    user_id: str | None = None
    email: str | None = None
    username: str | None = None
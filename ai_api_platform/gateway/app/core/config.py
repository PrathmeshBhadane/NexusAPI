from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    REDIS_URL: str
    AUTH_SERVICE_URL: str
    ML_SERVICE_URL: str
    AI_SERVICE_URL: str
    DATA_SERVICE_URL: str
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 3600

    class Config:
        env_file = ".env"

settings = Settings()
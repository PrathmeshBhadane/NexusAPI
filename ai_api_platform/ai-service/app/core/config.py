from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    REDIS_URL: str
    GROQ_API_KEY: str
    ANTHROPIC_API_KEY: str
    CACHE_TTL: int = 3600

    class Config:
        env_file = ".env"

settings = Settings()
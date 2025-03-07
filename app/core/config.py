from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
import os

class Settings(BaseSettings):
    testing: Optional[bool] = False
    SECRET_KEY: str = "your-super-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Set default values for testing environment
    DATABASE_URL: str = "sqlite:///./test.db" if os.getenv("TESTING") else "postgresql://postgres:postgres@localhost:5432/blogdb"
    REDIS_URL: str = "redis://localhost:6379/0"

    # Replace Config class with model_config
    model_config = SettingsConfigDict(
        env_file=".env.test" if os.getenv("TESTING") else ".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )

settings = Settings() 
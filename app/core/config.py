from pydantic_settings import BaseSettings
from typing import Optional, Dict, Any, List
import os


class Settings(BaseSettings):
    """
    Application settings.
    """
    # API settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Albedo API"
    DEBUG: bool = os.getenv("PYTHON_ENV", "development") == "development"
    
    # Security settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your_secret_key_here")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # Database settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/albedo")
    
    # Redis settings
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # CORS settings
    BACKEND_CORS_ORIGINS: List[str] = ["*"]
    
    class Config:
        case_sensitive = True


settings = Settings() 
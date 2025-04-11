from pydantic_settings import BaseSettings
from typing import Optional, Dict, Any, List
import os


class Config(BaseSettings):
    """
    Application config.
    """
    # API config
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Albedo API"
    DEBUG: bool = os.getenv("PYTHON_ENV", "development") == "development"
    
    # Security config
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your_secret_key_here")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # Database config
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@postgres:5432/albedo_db")
    
    # Redis config
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # CORS config
    BACKEND_CORS_ORIGINS: List[str] = ["*"]
    
    # Telegram notification config
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_CHAT_ID: str = os.getenv("TELEGRAM_CHAT_ID", "")
    TELEGRAM_NOTIFICATIONS_ENABLED: bool = os.getenv("TELEGRAM_NOTIFICATIONS_ENABLED", "false").lower() == "true"
    
    # Logging config
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE_PATH: str = os.getenv("LOG_FILE_PATH", "logs/app.log")
    
    # Google Cloud Logging config
    GOOGLE_CLOUD_LOGGING_ENABLED: bool = os.getenv("GOOGLE_CLOUD_LOGGING_ENABLED", "false").lower() == "true"
    GOOGLE_CLOUD_PROJECT_ID: Optional[str] = os.getenv("GOOGLE_CLOUD_PROJECT_ID")
    GOOGLE_CLOUD_LOG_NAME: str = os.getenv("GOOGLE_CLOUD_LOG_NAME", "albedo_api")
    
    # Azure Monitor config
    AZURE_MONITOR_ENABLED: bool = os.getenv("AZURE_MONITOR_ENABLED", "false").lower() == "true"
    AZURE_APPINSIGHTS_CONNECTION_STRING: Optional[str] = os.getenv("AZURE_APPINSIGHTS_CONNECTION_STRING")
    
    class Config:
        case_sensitive = True


config = Config() 
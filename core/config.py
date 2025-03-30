# core/config.py
import os
from pathlib import Path
from functools import lru_cache
from typing import Optional, List
from pydantic import BaseSettings, AnyUrl, PostgresDsn, validator

class Settings(BaseSettings):
    # Application Configuration
    ENV: str = "dev"  # dev|prod|test
    DEBUG: bool = False
    PROJECT_NAME: str = "Globalworth ESG API"
    API_VERSION: str = "1.0.0"
    API_PREFIX: str = "/api/v1"
    
    # Database Configuration
    DATABASE_URL: Optional[PostgresDsn] = None
    DB_USER: Optional[str] = None
    DB_PASSWORD: Optional[str] = None
    DB_HOST: Optional[str] = None
    DB_PORT: Optional[str] = "5432"
    DB_NAME: Optional[str] = "esg_db"
    
    # Security Configuration
    SECRET_KEY: str = "your-secret-key-here"  # Change in production!
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS Configuration
    CORS_ORIGINS: List[str] = ["*"]
    CORS_METHODS: List[str] = ["*"]
    CORS_HEADERS: List[str] = ["*"]
    
    # Testing Configuration
    TEST_DATABASE_URL: Optional[AnyUrl] = "sqlite+aiosqlite:///./test.db"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    @validator("DATABASE_URL", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: dict) -> AnyUrl:
        if isinstance(v, str):
            return v
            
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            user=values.get("DB_USER"),
            password=values.get("DB_PASSWORD"),
            host=values.get("DB_HOST"),
            port=values.get("DB_PORT"),
            path=f"/{values.get('DB_NAME') or ''}",
        )

@lru_cache()
def get_settings() -> Settings:
    return Settings()

# Export settings instance
settings = get_settings()

class Settings(BaseSettings):
    # BACnet Configuration
    BACNET_ADDRESS: str = "192.168.1.100/24"
    
    # MQTT Configuration
    MQTT_HOST: str = "localhost"
    MQTT_PORT: int = 1883
    MQTT_USER: Optional[str] = None
    MQTT_PASSWORD: Optional[str] = None
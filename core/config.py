from functools import lru_cache
from typing import Optional, Literal
from pydantic import PostgresDsn, field_validator, SecretStr
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # REORDERED FIELDS - database components first
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "esg_db"
    
    # DATABASE_URL now comes after its components
    DATABASE_URL: Optional[PostgresDsn] = None
    
    # Application config
    ENV: Literal["dev", "prod"] = "dev"
    DEBUG: bool = False
    SECRET_KEY: SecretStr = "your-strong-secret-key"

    @field_validator("DATABASE_URL", mode='before')
    @classmethod
    def assemble_db_connection(cls, v: Optional[str], info) -> Optional[PostgresDsn]:
        if isinstance(v, str):
            return v
            
        # Now values contains the processed DB_* fields
        values = info.data
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=values["DB_USER"],
            password=values["DB_PASSWORD"],
            host=values["DB_HOST"],
            port=values["DB_PORT"],
            path=f"/{values['DB_NAME']}",
        )

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
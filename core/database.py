from contextlib import asynccontextmanager
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from core.config import settings

# Database configuration using Pydantic settings
DATABASE_URL = settings.DATABASE_URL.unicode_string() if settings.DATABASE_URL else \
    f"postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASSWORD}@" \
    f"{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"

# Create async engine with optimized settings
engine = create_async_engine(
    DATABASE_URL,
    echo=settings.DEBUG,  # Only echo SQL in debug mode
    pool_size=20,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800
)

# Session factory with better defaults
async_session = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=True,
    future=True
)

Base = declarative_base()

@asynccontextmanager
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Async database session context manager"""
    session = async_session()
    try:
        yield session
        await session.commit()
    except Exception as exc:
        await session.rollback()
        raise exc
    finally:
        await session.close()
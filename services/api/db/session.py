"""Async session setup for Namesmith services."""
from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from ..settings import settings
from .base import Base


def create_engine() -> AsyncEngine:
    url = settings.database_url
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    
    # Configure for pgbouncer compatibility - disable all statement caching
    connect_args: dict[str, object] = {
        "statement_cache_size": 0,           # Disable asyncpg statement cache
        "prepared_statement_cache_size": 0,   # Disable SQLAlchemy prepared statement cache
        "server_settings": {
            "application_name": "namesmith_api",
        }
    }
    
    # Use NullPool to prevent SQLAlchemy pooling conflicts with pgbouncer
    return create_async_engine(
        url,
        echo=False,
        future=True,
        poolclass=NullPool,
        pool_pre_ping=True,
        connect_args=connect_args,
    )


engine: AsyncEngine = create_engine()
SessionFactory = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)


@asynccontextmanager
async def get_session() -> AsyncIterator[AsyncSession]:
    session = SessionFactory()
    try:
        yield session
    finally:
        await session.close()


async def init_models() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

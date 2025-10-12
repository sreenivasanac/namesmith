"""Async session setup for Namesmith services."""
from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from ..settings import settings
from .base import Base


def create_engine() -> AsyncEngine:
    url = settings.database_url
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    connect_args: dict[str, object] = {}
    if url.startswith("postgresql+asyncpg://"):
        connect_args["statement_cache_size"] = settings.asyncpg_statement_cache_size
    return create_async_engine(url, echo=False, future=True, connect_args=connect_args)


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

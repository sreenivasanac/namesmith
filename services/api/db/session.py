"""Async session setup for Namesmith services."""
from __future__ import annotations

from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from ..settings import settings
from .base import Base


def create_engine() -> AsyncEngine:
    url = settings.database_url
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return create_async_engine(url, echo=False, future=True)


engine: AsyncEngine = create_engine()
SessionFactory = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)


@asynccontextmanager
def get_session() -> AsyncSession:
    session = SessionFactory()
    try:
        yield session
    finally:
        await session.close()


async def init_models() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

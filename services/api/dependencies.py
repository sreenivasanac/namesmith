"""FastAPI dependency wiring."""
from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from .db.session import get_session


async def db_session() -> AsyncSession:
    async with get_session() as session:
        yield session

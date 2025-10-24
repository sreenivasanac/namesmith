"""User repository helpers."""
from __future__ import annotations

import uuid

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.models import User


async def get_user_by_id(session: AsyncSession, user_id: uuid.UUID) -> User | None:
    stmt: Select[tuple[User]] = select(User).where(User.id == user_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def upsert_user(session: AsyncSession, *, user_id: uuid.UUID, email: str, role: str) -> User:
    user = await get_user_by_id(session, user_id)
    if user is None:
        user = User(id=user_id, email=email.lower(), role=role)
        session.add(user)
        await session.flush()
        return user

    user.email = email.lower()
    user.role = role
    await session.flush()
    return user


async def get_user_by_email(session: AsyncSession, email: str) -> User | None:
    stmt: Select[tuple[User]] = select(User).where(func.lower(User.email) == email.lower())
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def ensure_user_by_email(session: AsyncSession, email: str, *, default_role: str = "viewer") -> User:
    user = await get_user_by_email(session, email)
    if user is None:
        user = User(email=email.lower(), role=default_role)
        session.add(user)
        await session.flush()
    return user

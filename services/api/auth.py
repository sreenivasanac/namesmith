"""Authentication helpers for cookie-based bearer tokens."""
from __future__ import annotations

import base64
import binascii
import json
import re
import uuid
from typing import Optional

from fastapi import Depends, Header
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from .dependencies import db_session
from .repositories import get_user_by_id, upsert_user

_BEARER_PATTERN = re.compile(r"Bearer\s+(?P<token>\S+)", re.IGNORECASE)


class UserContext(BaseModel):
    id: Optional[uuid.UUID] = None
    email: Optional[str] = None
    role: str = "viewer"


def _decode_token(token: str) -> tuple[uuid.UUID, str] | None:
    try:
        padded = token + "=" * (-len(token) % 4)
        raw = base64.urlsafe_b64decode(padded.encode("ascii"))
        data = json.loads(raw.decode("utf-8"))
        user_id = uuid.UUID(str(data["userId"]))
        email = str(data.get("email", "")).lower()
        return user_id, email
    except (KeyError, ValueError, TypeError, json.JSONDecodeError, binascii.Error):
        return None


async def get_current_user(
    authorization: Optional[str] = Header(default=None),
    session: AsyncSession = Depends(db_session),
) -> UserContext:
    if not authorization:
        return UserContext()

    match = _BEARER_PATTERN.match(authorization.strip())
    if not match:
        return UserContext()

    decoded = _decode_token(match.group("token"))
    if not decoded:
        return UserContext()

    user_id, email = decoded
    user = await get_user_by_id(session, user_id)
    if user is None:
        fallback_email = email or "unknown@example.com"
        user = await upsert_user(session, user_id=user_id, email=fallback_email, role="viewer")
    return UserContext(id=user.id, email=user.email, role=user.role)

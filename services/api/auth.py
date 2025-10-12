"""Authentication helpers (placeholder for Supabase JWT verification)."""
from __future__ import annotations

import re
import uuid
from typing import Optional

from fastapi import Header, HTTPException, status
from pydantic import BaseModel

_SUPABASE_JWT_BEARER_PATTERN = re.compile(r"Bearer\s+(?P<token>.+)", re.IGNORECASE)


class UserContext(BaseModel):
    id: Optional[uuid.UUID] = None
    email: Optional[str] = None
    role: str = "viewer"


async def get_current_user(authorization: Optional[str] = Header(default=None)) -> UserContext:
    """Parse the Authorization header.

    TODO: Replace with Supabase JWT verification using the public key.
    """
    if not authorization:
        # Allow anonymous access for development flows; tighten once Supabase JWT is wired.
        return UserContext(role="viewer")

    match = _SUPABASE_JWT_BEARER_PATTERN.match(authorization.strip())
    if not match:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authorization header")

    token = match.group("token")
    try:
        user_id = uuid.UUID(token.split(".")[0])
    except (ValueError, IndexError) as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc

    return UserContext(id=user_id, role="editor")

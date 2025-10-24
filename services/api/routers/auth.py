"""Authentication placeholder routes for cookie-based sessions."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from ..dependencies import db_session
from ..repositories import ensure_user_by_email


router = APIRouter(prefix="/v1/auth", tags=["auth"])


class LoginRequest(BaseModel):
    email: EmailStr


class LoginResponse(BaseModel):
    class UserModel(BaseModel):
        id: str
        email: EmailStr
        role: str

    user: UserModel


@router.post("/login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
    session: AsyncSession = Depends(db_session),
) -> LoginResponse:
    user = await ensure_user_by_email(session, request.email)
    await session.commit()
    return LoginResponse(user=LoginResponse.UserModel(id=str(user.id), email=user.email, role=user.role))

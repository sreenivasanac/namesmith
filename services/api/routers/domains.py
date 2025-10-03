"""Domains API router."""
from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from packages.shared_py.namesmith_schemas.domain import Domain, DomainListResponse

from ..dependencies import db_session
from ..repositories import get_domain_by_id, list_domains
from ..serializers import serialize_domain

router = APIRouter(prefix="/v1/domains", tags=["domains"])


def _parse_cursor(cursor: Optional[str]) -> Optional[datetime]:
    if not cursor:
        return None
    try:
        return datetime.fromisoformat(cursor)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid cursor format; expected ISO timestamp") from exc


@router.get("", response_model=DomainListResponse)
async def list_domain_names(
    limit: int = Query(default=20, ge=1, le=100),
    cursor: Optional[str] = Query(default=None),
    session: AsyncSession = Depends(db_session),
) -> DomainListResponse:
    dt_cursor = _parse_cursor(cursor)
    domains = await list_domains(session, limit=limit, cursor=dt_cursor)
    items = [serialize_domain(domain) for domain in domains]
    next_cursor = domains[-1].created_at.isoformat() if domains and len(domains) == limit else None
    return DomainListResponse(items=items, next_cursor=next_cursor)


@router.get("/{domain_id}", response_model=Domain)
async def get_domain(
    domain_id: UUID,
    session: AsyncSession = Depends(db_session),
) -> Domain:
    domain = await get_domain_by_id(session, domain_id)
    if domain is None:
        raise HTTPException(status_code=404, detail="Domain not found")
    return serialize_domain(domain)

"""Domains API router."""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from packages.shared_py.namesmith_schemas.domain import Domain, DomainFiltersMetadata, DomainListResponse

from ..dependencies import db_session
from ..repositories import get_domain_by_id, get_domain_filters_metadata, list_domains
from ..serializers import serialize_domain

logger = logging.getLogger(__name__)

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
    search: Optional[str] = Query(default=None),
    status: Optional[str] = Query(default=None),
    tld: Optional[str] = Query(default=None),
    agent_model: Optional[str] = Query(default=None),
    category: Optional[str] = Query(default=None),
    job_id: Optional[UUID] = Query(default=None),
    memorability_min: Optional[int] = Query(default=None),
    memorability_max: Optional[int] = Query(default=None),
    pronounceability_min: Optional[int] = Query(default=None),
    pronounceability_max: Optional[int] = Query(default=None),
    brandability_min: Optional[int] = Query(default=None),
    brandability_max: Optional[int] = Query(default=None),
    overall_min: Optional[int] = Query(default=None),
    overall_max: Optional[int] = Query(default=None),
    seo_keyword_relevance_min: Optional[int] = Query(default=None),
    seo_keyword_relevance_max: Optional[int] = Query(default=None),
    sort_by: str = Query(default="created_at"),
    sort_dir: str = Query(default="desc"),
    session: AsyncSession = Depends(db_session),
) -> DomainListResponse:
    dt_cursor = _parse_cursor(cursor)
    statuses = [value for value in (status.split(",") if status else []) if value]
    tlds = [value for value in (tld.split(",") if tld else []) if value]
    agent_models = [value for value in (agent_model.split(",") if agent_model else []) if value]
    categories = [value for value in (category.split(",") if category else []) if value]

    score_ranges: dict[str, tuple[int | None, int | None]] = {}
    if memorability_min is not None or memorability_max is not None:
        score_ranges["memorability"] = (memorability_min, memorability_max)
    if pronounceability_min is not None or pronounceability_max is not None:
        score_ranges["pronounceability"] = (pronounceability_min, pronounceability_max)
    if brandability_min is not None or brandability_max is not None:
        score_ranges["brandability"] = (brandability_min, brandability_max)
    if overall_min is not None or overall_max is not None:
        score_ranges["overall"] = (overall_min, overall_max)
    if seo_keyword_relevance_min is not None or seo_keyword_relevance_max is not None:
        score_ranges["seo_keyword_relevance"] = (seo_keyword_relevance_min, seo_keyword_relevance_max)

    try:
        domains = await list_domains(
            session,
            limit=limit,
            cursor=dt_cursor,
            search=search,
            statuses=statuses or None,
            tlds=tlds or None,
            agent_models=agent_models or None,
            categories=categories or None,
            job_id=job_id,
            score_ranges=score_ranges or None,
            sort_by=sort_by,
            sort_dir=sort_dir,
        )
        items = [serialize_domain(domain) for domain in domains]
        next_cursor = domains[-1].created_at.isoformat() if domains and len(domains) == limit else None
        metadata = await get_domain_filters_metadata(session)
        filters = DomainFiltersMetadata.model_validate(metadata)
        return DomainListResponse(items=items, next_cursor=next_cursor, filters=filters)
    except Exception as e:
        logger.exception("Error listing domains with job_id=%s: %s", job_id, str(e))
        raise HTTPException(status_code=500, detail=f"Error listing domains: {str(e)}") from e


@router.get("/{domain_id}", response_model=Domain)
async def get_domain(
    domain_id: UUID,
    session: AsyncSession = Depends(db_session),
) -> Domain:
    domain = await get_domain_by_id(session, domain_id)
    if domain is None:
        raise HTTPException(status_code=404, detail="Domain not found")
    return serialize_domain(domain)

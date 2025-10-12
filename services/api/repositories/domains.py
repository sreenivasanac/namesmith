"""Domain persistence helpers."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Iterable

from sqlalchemy import Select, func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..db.models import (
    AvailabilityCheck,
    DomainAvailabilityStatus,
    DomainEvaluation,
    DomainName,
    DomainSeoAnalysis,
    JobDomainLink,
)


def normalize_label(label: str) -> str:
    return label.strip().lower()


async def upsert_domain(
    session: AsyncSession,
    *,
    label: str,
    tld: str,
    display_name: str | None,
    processed_by_agent: str | None,
    agent_model: str | None,
) -> DomainName:
    normalized = normalize_label(label)
    stmt = insert(DomainName).values(
        label=normalized,
        tld=tld.lower(),
        display_name=display_name,
        length=len(normalized),
        processed_by_agent=processed_by_agent,
        agent_model=agent_model,
    )
    excluded = stmt.excluded
    stmt = stmt.on_conflict_do_update(
        index_elements=[DomainName.label, DomainName.tld],
        set_={
            "display_name": func.coalesce(excluded.display_name, DomainName.display_name),
            "processed_by_agent": func.coalesce(
                excluded.processed_by_agent, DomainName.processed_by_agent
            ),
            "agent_model": func.coalesce(excluded.agent_model, DomainName.agent_model),
            "length": func.coalesce(excluded.length, DomainName.length),
        },
    ).returning(DomainName)
    result = await session.execute(stmt)
    domain = result.scalar_one()
    await session.flush()
    return domain


async def upsert_availability(
    session: AsyncSession,
    *,
    domain_id: uuid.UUID,
    status: str,
    processed_by_agent: str | None,
    agent_model: str | None,
    registrar: str | None,
    method: str,
    raw_payload: dict | None,
    ttl_sec: int | None,
) -> DomainAvailabilityStatus:
    status_value = status.lower()
    stmt = (
        insert(DomainAvailabilityStatus)
        .values(
            domain_id=domain_id,
            status=status_value,
            processed_by_agent=processed_by_agent,
            agent_model=agent_model,
        )
        .on_conflict_do_update(
            index_elements=[DomainAvailabilityStatus.domain_id],
            set_={
                "status": status_value,
                "processed_by_agent": processed_by_agent,
                "agent_model": agent_model,
                "created_at": func.now(),
            },
        )
        .returning(DomainAvailabilityStatus)
    )
    result = await session.execute(stmt)
    availability = result.scalar_one()

    check = AvailabilityCheck(
        domain_id=domain_id,
        method=method,
        registrar=registrar,
        status=status_value,
        raw=raw_payload,
        ttl_sec=ttl_sec,
    )
    session.add(check)
    await session.flush()
    return availability


async def upsert_evaluation(
    session: AsyncSession,
    *,
    domain_id: uuid.UUID,
    possible_categories: Iterable[str],
    possible_keywords: Iterable[str],
    memorability_score: int,
    pronounceability_score: int,
    brandability_score: int,
    overall_score: int,
    description: str,
    processed_by_agent: str | None,
    agent_model: str | None,
) -> DomainEvaluation:
    categories = sorted({c.lower() for c in possible_categories if c})
    keywords = sorted({k.lower() for k in possible_keywords if k})
    stmt = insert(DomainEvaluation).values(
        domain_id=domain_id,
        possible_categories=categories,
        possible_keywords=keywords,
        memorability_score=memorability_score,
        pronounceability_score=pronounceability_score,
        brandability_score=brandability_score,
        overall_score=overall_score,
        description=description,
        processed_by_agent=processed_by_agent,
        agent_model=agent_model,
    )
    excluded = stmt.excluded
    stmt = stmt.on_conflict_do_update(
        index_elements=[DomainEvaluation.domain_id],
        set_={
            "possible_categories": categories,
            "possible_keywords": keywords,
            "memorability_score": memorability_score,
            "pronounceability_score": pronounceability_score,
            "brandability_score": brandability_score,
            "overall_score": overall_score,
            "description": description,
            "processed_by_agent": func.coalesce(excluded.processed_by_agent, DomainEvaluation.processed_by_agent),
            "agent_model": func.coalesce(excluded.agent_model, DomainEvaluation.agent_model),
            "created_at": func.now(),
        },
    ).returning(DomainEvaluation)
    result = await session.execute(stmt)
    evaluation = result.scalar_one()
    await session.flush()
    return evaluation


async def link_domain_to_job(
    session: AsyncSession,
    *,
    job_id: uuid.UUID,
    domain_id: uuid.UUID,
) -> None:
    stmt = insert(JobDomainLink).values(job_id=job_id, domain_id=domain_id).on_conflict_do_nothing()
    await session.execute(stmt)


async def get_domain_by_id(session: AsyncSession, domain_id: uuid.UUID) -> DomainName | None:
    stmt: Select[tuple[DomainName]] = (
        select(DomainName)
        .options(
            selectinload(DomainName.availability),
            selectinload(DomainName.evaluation),
            selectinload(DomainName.seo_analysis),
        )
        .where(DomainName.id == domain_id)
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def list_domains(
    session: AsyncSession,
    *,
    limit: int,
    cursor: datetime | None,
) -> list[DomainName]:
    stmt: Select[tuple[DomainName]] = (
        select(DomainName)
        .options(
            selectinload(DomainName.availability),
            selectinload(DomainName.evaluation),
            selectinload(DomainName.seo_analysis),
        )
        .order_by(DomainName.created_at.desc())
        .limit(limit)
    )
    if cursor is not None:
        stmt = stmt.where(DomainName.created_at < cursor)
    result = await session.execute(stmt)
    return list(result.scalars().all())

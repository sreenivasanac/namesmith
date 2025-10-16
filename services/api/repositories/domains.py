"""Domain persistence helpers."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Iterable, Sequence

from sqlalchemy import Select, and_, func, or_, select
from sqlalchemy.dialects.postgresql import array, insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased, selectinload

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
    search: str | None = None,
    statuses: Sequence[str] | None = None,
    tlds: Sequence[str] | None = None,
    agent_models: Sequence[str] | None = None,
    categories: Sequence[str] | None = None,
    job_id: uuid.UUID | None = None,
    score_ranges: dict[str, tuple[int | None, int | None]] | None = None,
    sort_by: str = "created_at",
    sort_dir: str = "desc",
) -> list[DomainName]:
    availability_alias = aliased(DomainAvailabilityStatus)
    evaluation_alias = aliased(DomainEvaluation)
    job_link_alias = aliased(JobDomainLink)
    seo_alias = aliased(DomainSeoAnalysis)

    stmt: Select[tuple[DomainName]] = (
        select(DomainName)
        .options(
            selectinload(DomainName.availability),
            selectinload(DomainName.evaluation),
            selectinload(DomainName.seo_analysis),
        )
        .outerjoin(availability_alias, DomainName.id == availability_alias.domain_id)
        .outerjoin(evaluation_alias, DomainName.id == evaluation_alias.domain_id)
        .outerjoin(job_link_alias, DomainName.id == job_link_alias.domain_id)
        .outerjoin(seo_alias, DomainName.id == seo_alias.domain_id)
    )

    filters: list = []

    if search:
        pattern = f"%{search.lower()}%"
        full_domain_expr = func.concat_ws(".", DomainName.label, DomainName.tld)
        filters.append(
            or_(
                func.lower(DomainName.label).like(pattern),
                func.lower(DomainName.display_name).like(pattern),
                func.lower(full_domain_expr).like(pattern),
            )
        )

    if statuses:
        status_values = [status.lower() for status in statuses if status]
        if status_values:
            filters.append(availability_alias.status.in_(status_values))

    if tlds:
        filters.append(func.lower(DomainName.tld).in_([t.lower() for t in tlds]))

    if agent_models:
        filters.append(DomainName.agent_model.in_(agent_models))

    if categories:
        filters.append(evaluation_alias.possible_categories.op("&&")(array(categories)))

    if job_id:
        filters.append(job_link_alias.job_id == job_id)

    score_mapping = {
        "memorability": evaluation_alias.memorability_score,
        "pronounceability": evaluation_alias.pronounceability_score,
        "brandability": evaluation_alias.brandability_score,
        "overall": evaluation_alias.overall_score,
        "seo_keyword_relevance": seo_alias.seo_keyword_relevance_score,
    }
    if score_ranges:
        for key, column in score_mapping.items():
            min_val, max_val = score_ranges.get(key, (None, None)) if score_ranges else (None, None)
            if min_val is not None:
                filters.append(column >= int(min_val))
            if max_val is not None:
                filters.append(column <= int(max_val))

    if filters:
        stmt = stmt.where(and_(*filters))

    order_column = DomainName.created_at
    if sort_by == "label":
        order_column = DomainName.label
    elif sort_by == "overall_score":
        order_column = evaluation_alias.overall_score

    order_direction = order_column.desc() if sort_dir.lower() == "desc" else order_column.asc()
    
    if cursor is not None:
        stmt = stmt.where(DomainName.created_at < cursor)

    stmt = stmt.distinct(DomainName.id).order_by(DomainName.id, order_direction, DomainName.created_at.desc()).limit(limit)

    result = await session.execute(stmt)
    return list(result.scalars().unique().all())


async def get_domain_filters_metadata(session: AsyncSession) -> dict[str, list[str]]:
    statuses_stmt = select(func.distinct(DomainAvailabilityStatus.status)).where(DomainAvailabilityStatus.status.isnot(None))
    tld_stmt = select(func.distinct(DomainName.tld)).where(DomainName.tld.isnot(None))
    agent_models_stmt = select(func.distinct(DomainName.agent_model)).where(DomainName.agent_model.isnot(None))
    industries_stmt = select(func.distinct(func.unnest(DomainEvaluation.possible_categories))).where(
        DomainEvaluation.possible_categories.isnot(None)
    )

    statuses = [row[0] for row in (await session.execute(statuses_stmt)).all() if row[0]]
    tlds = [row[0] for row in (await session.execute(tld_stmt)).all() if row[0]]
    agent_models = [row[0] for row in (await session.execute(agent_models_stmt)).all() if row[0]]
    industries = [row[0] for row in (await session.execute(industries_stmt)).all() if row[0]]

    return {
        "statuses": sorted(set(statuses)),
        "tlds": sorted(set(tlds)),
        "agent_models": sorted(set(agent_models)),
        "industries": sorted({value.lower(): value for value in industries}.values()),
    }

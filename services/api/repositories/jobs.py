"""Job persistence helpers."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Sequence

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..db.models import AgentRun, Job


async def create_job(
    session: AsyncSession,
    *,
    entry_path: str,
    job_type: str,
    created_by: uuid.UUID | None,
    params: dict[str, Any] | None,
) -> Job:
    job = Job(
        entry_path=entry_path,
        type=job_type,
        status="queued",
        created_by=created_by,
        params=params,
    )
    session.add(job)
    await session.flush()
    return job


async def get_job(session: AsyncSession, job_id: uuid.UUID) -> Job | None:
    stmt: Select[tuple[Job]] = (
        select(Job)
        .options(selectinload(Job.runs))
        .where(Job.id == job_id)
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def list_jobs(
    session: AsyncSession,
    *,
    created_by: uuid.UUID | None,
    limit: int,
    cursor: datetime | None,
) -> Sequence[Job]:
    stmt: Select[tuple[Job]] = select(Job).order_by(Job.created_at.desc()).limit(limit)
    stmt = stmt.options(selectinload(Job.runs))
    if cursor is not None:
        stmt = stmt.where(Job.created_at < cursor)
    if created_by is not None:
        stmt = stmt.where(Job.created_by == created_by)
    result = await session.execute(stmt)
    return result.scalars().all()


async def update_job_status(
    session: AsyncSession,
    job: Job,
    *,
    status: str,
    error: str | None = None,
    started_at: datetime | None = None,
    finished_at: datetime | None = None,
) -> Job:
    job.status = status
    if error is not None:
        job.error = error
    if started_at is not None:
        job.started_at = started_at
    if finished_at is not None:
        job.finished_at = finished_at
    await session.flush()
    return job


async def record_agent_run(
    session: AsyncSession,
    *,
    job_id: uuid.UUID,
    agent_name: str,
    status: str,
    input_payload: dict[str, Any] | None = None,
    output_payload: dict[str, Any] | None = None,
    started_at: datetime | None = None,
    finished_at: datetime | None = None,
    trace_id: str | None = None,
    eval_scores: dict[str, Any] | None = None,
) -> AgentRun:
    run = AgentRun(
        job_id=job_id,
        agent_name=agent_name,
        status=status,
        input=input_payload,
        output=output_payload,
        started_at=started_at,
        finished_at=finished_at,
        trace_id=trace_id,
        eval_scores=eval_scores,
    )
    session.add(run)
    await session.flush()
    return run

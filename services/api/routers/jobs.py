"""Jobs API router."""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from packages.shared_py.namesmith_schemas.jobs import JobCreateRequest, JobListResponse, JobResponse

from ..auth import UserContext, get_current_user
from ..dependencies import db_session
from ..repositories import create_job, get_job, list_jobs, upsert_user
from ..serializers import serialize_job
from ...agents.executor import run_generation_job
from ...agents.settings import settings as agent_settings
from ...agents.state import GenerationInputs

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/jobs", tags=["jobs"])


def _parse_cursor(cursor: Optional[str]) -> Optional[datetime]:
    if not cursor:
        return None
    try:
        return datetime.fromisoformat(cursor)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid cursor format; expected ISO timestamp") from exc


@router.post("/generate", response_model=JobResponse)
async def create_generation_job(
    request: JobCreateRequest,
    session: AsyncSession = Depends(db_session),
    user: UserContext = Depends(get_current_user),
) -> JobResponse:
    allowlist = agent_settings.model_allowlist
    if allowlist:
        if request.generation_model and request.generation_model not in allowlist:
            raise HTTPException(status_code=400, detail="Requested generation model is not supported")
        if request.scoring_model and request.scoring_model not in allowlist:
            raise HTTPException(status_code=400, detail="Requested scoring model is not supported")

    if user.id is not None:
        await upsert_user(session, user_id=user.id, email=user.email or "unknown@example.com", role=user.role)

    job = await create_job(
        session,
        entry_path=request.entry_path.value if hasattr(request.entry_path, "value") else str(request.entry_path),
        job_type="generate",
        created_by=user.id,
        params=request.model_dump(),
    )
    await session.commit()

    inputs = GenerationInputs(
        job_id=job.id,
        user_id=user.id,
        entry_path=request.entry_path,
        topic=request.topic,
        prompt=request.prompt,
        categories=request.categories,
        tlds=request.tlds,
        count=request.count,
        generation_model=request.generation_model,
        scoring_model=request.scoring_model,
    )

    async def _run_job() -> None:
        try:
            await run_generation_job(inputs)
        except Exception:  # noqa: BLE001
            logger.exception("Generation job %s failed", job.id)

    asyncio.create_task(_run_job())
    return serialize_job(job)


@router.get("", response_model=JobListResponse)
async def list_generation_jobs(
    limit: int = Query(default=20, ge=1, le=100),
    cursor: Optional[str] = Query(default=None),
    session: AsyncSession = Depends(db_session),
    user: UserContext = Depends(get_current_user),
) -> JobListResponse:
    dt_cursor = _parse_cursor(cursor)
    jobs = await list_jobs(session, created_by=user.id, limit=limit, cursor=dt_cursor)
    items = [serialize_job(job, progress=(job.params or {}).get("progress")) for job in jobs]
    next_cursor = jobs[-1].created_at.isoformat() if jobs and len(jobs) == limit else None
    return JobListResponse(items=items, next_cursor=next_cursor)


@router.get("/{job_id}", response_model=JobResponse)
async def get_generation_job(
    job_id: UUID,
    session: AsyncSession = Depends(db_session),
    user: UserContext = Depends(get_current_user),
) -> JobResponse:
    job = await get_job(session, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    if user.id is not None and job.created_by and job.created_by != user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this job")
    return serialize_job(job, progress=(job.params or {}).get("progress"))

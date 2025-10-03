"""Job-related schemas shared across services."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import Field

from .base import AvailabilityStatus, EntryPath, JobStatus, JobType, NamesmithModel


class JobCreateRequest(NamesmithModel):
    entry_path: EntryPath
    topic: Optional[str] = None
    prompt: Optional[str] = None
    categories: list[str] = Field(default_factory=list)
    tlds: list[str] = Field(default_factory=list)
    count: int = Field(default=20, ge=1, le=200)


class JobResponse(NamesmithModel):
    id: UUID
    type: JobType
    entry_path: EntryPath
    status: JobStatus
    created_at: datetime
    finished_at: Optional[datetime] = None
    error: Optional[str] = None
    progress: Optional[dict[str, Any]] = None


class JobListResponse(NamesmithModel):
    items: list[JobResponse]
    next_cursor: Optional[str] = None


class AvailabilityCheckRequest(NamesmithModel):
    domains: list[dict[str, str]]
    mode: Optional[str] = Field(default="auto")


class AvailabilityCheckResult(NamesmithModel):
    full_domain: str
    status: AvailabilityStatus


class AvailabilityCheckResponse(NamesmithModel):
    results: list[AvailabilityCheckResult]


class AvailabilityCheckBatchResponse(NamesmithModel):
    status: JobStatus
    results: Optional[list[AvailabilityCheckResult]] = None


__all__ = [
    "AvailabilityCheckBatchResponse",
    "AvailabilityCheckRequest",
    "AvailabilityCheckResponse",
    "AvailabilityCheckResult",
    "JobCreateRequest",
    "JobListResponse",
    "JobResponse",
]

"""Job-related schemas shared across services."""
from __future__ import annotations

from datetime import datetime
from typing import Any, ClassVar, Optional, Union
from uuid import UUID

from pydantic import Field, model_validator

from .base import AvailabilityStatus, EntryPath, JobStatus, JobType, NamesmithModel


class JobCreateRequest(NamesmithModel):
    entry_path: EntryPath
    topic: Optional[str] = None
    prompt: Optional[str] = None
    categories: list[str] = Field(default_factory=list)
    tlds: list[str] = Field(default_factory=list)
    count: int = Field(default=20, ge=1, le=200)
    generation_model: Optional[str] = None
    scoring_model: Optional[str] = None


class JobResponse(NamesmithModel):
    id: UUID
    type: JobType
    entry_path: EntryPath
    status: JobStatus
    created_at: datetime
    finished_at: Optional[datetime] = None
    error: Optional[str] = None
    progress: Optional[dict[str, Any]] = None
    generation_model: Optional[str] = None
    scoring_model: Optional[str] = None


class JobListResponse(NamesmithModel):
    items: list[JobResponse]
    next_cursor: Optional[str] = None


class DomainLookupBase(NamesmithModel):
    model_config = NamesmithModel.model_config | {"extra": "forbid"}
    _required_keys: ClassVar[set[str]] = set()
    _allowed_keys: ClassVar[set[str]] = set()

    @model_validator(mode="before")
    @classmethod
    def _validate_key_set(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
        keys = {key for key, value in data.items() if value is not None}
        missing = cls._required_keys - keys
        if missing:
            raise ValueError(f"Missing required fields: {', '.join(sorted(missing))}")
        extras = keys - cls._allowed_keys
        if extras:
            raise ValueError(f"Unexpected fields: {', '.join(sorted(extras))}")
        return data


class DomainLookupById(DomainLookupBase):
    _required_keys: ClassVar[set[str]] = {"id"}
    _allowed_keys: ClassVar[set[str]] = {"id"}

    id: UUID


class DomainLookupByFullDomain(DomainLookupBase):
    _required_keys: ClassVar[set[str]] = {"full_domain"}
    _allowed_keys: ClassVar[set[str]] = {"full_domain"}

    full_domain: str


class DomainLookupByLabelTld(DomainLookupBase):
    _required_keys: ClassVar[set[str]] = {"label", "tld"}
    _allowed_keys: ClassVar[set[str]] = {"label", "tld"}

    label: str
    tld: str


DomainLookup = Union[DomainLookupById, DomainLookupByFullDomain, DomainLookupByLabelTld]


class AvailabilityCheckRequest(NamesmithModel):
    domains: list[DomainLookup]


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

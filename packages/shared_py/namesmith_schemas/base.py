"""Shared Pydantic base classes and enums for Namesmith services."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Literal

from pydantic import BaseModel


class NamesmithModel(BaseModel):
    """Base model configured for ORM compatibility."""

    model_config = {
        "from_attributes": True,
        "populate_by_name": True,
        "extra": "ignore",
    }


AvailabilityStatus = Literal["available", "registered", "unknown", "error"]


class JobStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    PARTIAL = "partial"


class JobType(str, Enum):
    GENERATE = "generate"
    SCORE = "score"
    AVAILABILITY = "availability"
    RESEARCH = "research"


class EntryPath(str, Enum):
    INVESTOR = "investor"
    BUSINESS = "business"


class TimestampedModel(NamesmithModel):
    created_at: datetime


__all__ = [
    "AvailabilityStatus",
    "EntryPath",
    "JobStatus",
    "JobType",
    "NamesmithModel",
    "TimestampedModel",
]

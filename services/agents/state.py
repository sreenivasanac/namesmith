"""State definitions for Namesmith agent workflows."""
from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Field
from typing import TypedDict

from packages.shared_py.namesmith_schemas.base import EntryPath


class Trend(BaseModel):
    title: str
    summary: Optional[str] = None
    tags: list[str] = Field(default_factory=list)
    source: Optional[str] = None


class CompanyExample(BaseModel):
    name: str
    domain: Optional[str] = None
    description: Optional[str] = None
    categories: list[str] = Field(default_factory=list)
    source: Optional[str] = None
    score: Optional[float] = None


class Candidate(BaseModel):
    label: str
    tld: str
    display_name: Optional[str] = None
    reasoning: Optional[str] = None

    @property
    def full_domain(self) -> str:
        return f"{self.label.lower()}.{self.tld.lower()}"


class ScoredCandidate(Candidate):
    memorability: float
    pronounceability: float
    brandability: float
    overall: float
    rubric_version: str = "v1"
    rationale: Optional[str] = None


class AvailabilityResult(BaseModel):
    full_domain: str
    status: Literal["available", "registered", "unknown", "error"]
    registrar: Optional[str] = None
    checked_at: datetime = Field(default_factory=datetime.utcnow)


class GenerationInputs(BaseModel):
    job_id: UUID
    user_id: Optional[UUID] = None
    entry_path: EntryPath
    topic: Optional[str] = None
    prompt: Optional[str] = None
    categories: list[str] = Field(default_factory=list)
    tlds: list[str] = Field(default_factory=list)
    count: int = 20


class GenerationState(BaseModel):
    inputs: GenerationInputs
    trends: list[Trend] = Field(default_factory=list)
    company_examples: list[CompanyExample] = Field(default_factory=list)
    candidates: list[Candidate] = Field(default_factory=list)
    filtered: list[Candidate] = Field(default_factory=list)
    scored: list[ScoredCandidate] = Field(default_factory=list)
    availability: list[AvailabilityResult] = Field(default_factory=list)
    progress: dict[str, int] = Field(default_factory=dict)


class PersistResult(BaseModel):
    job_id: UUID
    domain_ids: list[UUID]


class GenerationStateDict(TypedDict, total=False):
    inputs: GenerationInputs
    trends: list[Trend]
    company_examples: list[CompanyExample]
    candidates: list[Candidate]
    filtered: list[Candidate]
    scored: list[ScoredCandidate]
    availability: list[AvailabilityResult]
    progress: dict[str, int]

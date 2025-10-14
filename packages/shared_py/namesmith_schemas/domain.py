"""Domain related schemas shared between API and agents."""
from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import Field

from .base import AvailabilityStatus, NamesmithModel


class DomainFiltersMetadata(NamesmithModel):
    statuses: list[str] = Field(default_factory=list)
    tlds: list[str] = Field(default_factory=list)
    agent_models: list[str] = Field(default_factory=list)
    industries: list[str] = Field(default_factory=list)


class DomainAvailability(NamesmithModel):
    status: AvailabilityStatus
    agent_model: Optional[str] = None
    checked_at: datetime = Field(alias="created_at")


class DomainEvaluation(NamesmithModel):
    possible_categories: list[str] = Field(default_factory=list)
    possible_keywords: list[str] = Field(default_factory=list)
    memorability_score: int
    pronounceability_score: int
    brandability_score: int
    overall_score: int
    description: str
    processed_by_agent: Optional[str] = None
    agent_model: Optional[str] = None
    created_at: datetime


class DomainSeoAnalysis(NamesmithModel):
    seo_keywords: list[str] = Field(default_factory=list)
    seo_keyword_relevance_score: int
    industry_relevance_score: int
    domain_age: int
    potential_resale_value: int
    language: str
    trademark_status: Optional[str] = None
    scored_by_agent: Optional[str] = None
    agent_model: Optional[str] = None
    description: str
    created_at: datetime


class Domain(NamesmithModel):
    id: UUID
    label: str
    tld: str
    full_domain: str
    display_name: Optional[str] = None
    length: int
    processed_by_agent: Optional[str] = None
    agent_model: Optional[str] = None
    created_at: datetime
    availability: Optional[DomainAvailability] = None
    evaluation: Optional[DomainEvaluation] = None
    seo_analysis: Optional[DomainSeoAnalysis] = None


class DomainListResponse(NamesmithModel):
    items: list[Domain]
    next_cursor: Optional[str] = None
    filters: Optional[DomainFiltersMetadata] = None


__all__ = [
    "Domain",
    "DomainAvailability",
    "DomainEvaluation",
    "DomainListResponse",
    "DomainSeoAnalysis",
    "DomainFiltersMetadata",
]

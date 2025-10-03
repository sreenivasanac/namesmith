"""Serialization helpers to map ORM models to shared schemas."""
from __future__ import annotations

from packages.shared_py.namesmith_schemas.domain import (
    Domain,
    DomainAvailability,
    DomainEvaluation,
    DomainSeoAnalysis,
)
from packages.shared_py.namesmith_schemas.jobs import JobResponse
from packages.shared_py.namesmith_schemas.base import JobStatus, JobType

from .db.models import DomainName, Job


def serialize_domain(domain: DomainName) -> Domain:
    full_domain = f"{domain.label}.{domain.tld}"
    availability = None
    if domain.availability:
        availability = DomainAvailability.model_validate(
            {
                "status": domain.availability.status,
                "agent_model": domain.availability.agent_model,
                "created_at": domain.availability.created_at,
            }
        )
    evaluation = None
    if domain.evaluation:
        evaluation = DomainEvaluation.model_validate(
            {
                "possible_categories": domain.evaluation.possible_categories or [],
                "possible_keywords": domain.evaluation.possible_keywords or [],
                "memorability_score": domain.evaluation.memorability_score,
                "pronounceability_score": domain.evaluation.pronounceability_score,
                "brandability_score": domain.evaluation.brandability_score,
                "overall_score": domain.evaluation.overall_score,
                "description": domain.evaluation.description,
                "processed_by_agent": domain.evaluation.processed_by_agent,
                "agent_model": domain.evaluation.agent_model,
                "created_at": domain.evaluation.created_at,
            }
        )
    seo_analysis = None
    if domain.seo_analysis:
        seo_analysis = DomainSeoAnalysis.model_validate(
            {
                "seo_keywords": domain.seo_analysis.seo_keywords or [],
                "seo_keyword_relevance_score": domain.seo_analysis.seo_keyword_relevance_score,
                "industry_relevance_score": domain.seo_analysis.industry_relevance_score,
                "domain_age": domain.seo_analysis.domain_age,
                "potential_resale_value": domain.seo_analysis.potential_resale_value,
                "language": domain.seo_analysis.language,
                "trademark_status": domain.seo_analysis.trademark_status,
                "scored_by_agent": domain.seo_analysis.scored_by_agent,
                "agent_model": domain.seo_analysis.agent_model,
                "description": domain.seo_analysis.description,
                "created_at": domain.seo_analysis.created_at,
            }
        )

    return Domain.model_validate(
        {
            "id": domain.id,
            "label": domain.label,
            "tld": domain.tld,
            "full_domain": full_domain,
            "display_name": domain.display_name,
            "length": domain.length,
            "processed_by_agent": domain.processed_by_agent,
            "agent_model": domain.agent_model,
            "created_at": domain.created_at,
            "availability": availability,
            "evaluation": evaluation,
            "seo_analysis": seo_analysis,
        }
    )


def serialize_job(job: Job, progress: dict[str, int] | None = None) -> JobResponse:
    return JobResponse.model_validate(
        {
            "id": job.id,
            "type": JobType(job.type),
            "entry_path": job.entry_path,
            "status": JobStatus(job.status),
            "created_at": job.created_at,
            "finished_at": job.finished_at,
            "error": job.error,
            "progress": progress or {},
        }
    )

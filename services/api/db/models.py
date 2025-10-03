"""SQLAlchemy ORM models for Namesmith backend."""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class DomainName(Base):
    __tablename__ = "domain_names"
    __table_args__ = (
        UniqueConstraint("label", "tld", name="uq_domain_names_label_tld"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    label: Mapped[str] = mapped_column(String(255), nullable=False)
    tld: Mapped[str] = mapped_column(String(20), nullable=False)
    display_name: Mapped[str | None] = mapped_column(String(255))
    length: Mapped[int] = mapped_column(Integer, nullable=False)
    processed_by_agent: Mapped[str | None] = mapped_column(String(255))
    agent_model: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    availability: Mapped["DomainAvailabilityStatus" | None] = relationship(
        "DomainAvailabilityStatus", back_populates="domain", uselist=False
    )
    evaluation: Mapped["DomainEvaluation" | None] = relationship(
        "DomainEvaluation", back_populates="domain", uselist=False
    )
    seo_analysis: Mapped["DomainSeoAnalysis" | None] = relationship(
        "DomainSeoAnalysis", back_populates="domain", uselist=False
    )
    availability_checks: Mapped[list["AvailabilityCheck"]] = relationship(
        "AvailabilityCheck", back_populates="domain"
    )
    jobs: Mapped[list["Job"]] = relationship(
        "Job",
        secondary="job_domain_links",
        back_populates="domains",
    )


class DomainAvailabilityStatus(Base):
    __tablename__ = "dn_availability_status"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    domain_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("domain_names.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    processed_by_agent: Mapped[str | None] = mapped_column(String(255))
    agent_model: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    domain: Mapped[DomainName] = relationship("DomainName", back_populates="availability")


class DomainEvaluation(Base):
    __tablename__ = "dn_evaluations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    domain_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("domain_names.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    possible_categories: Mapped[list[str]] = mapped_column(ARRAY(String(120)), default=list)
    possible_keywords: Mapped[list[str]] = mapped_column(ARRAY(String(120)), default=list)
    memorability_score: Mapped[int] = mapped_column(Integer, nullable=False)
    pronounceability_score: Mapped[int] = mapped_column(Integer, nullable=False)
    brandability_score: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str] = mapped_column(String)
    overall_score: Mapped[int] = mapped_column(Integer, nullable=False)
    processed_by_agent: Mapped[str | None] = mapped_column(String(255))
    agent_model: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    domain: Mapped[DomainName] = relationship("DomainName", back_populates="evaluation")

    __table_args__ = (
        CheckConstraint("memorability_score BETWEEN 0 AND 10", name="ck_memorability_bounds"),
        CheckConstraint("pronounceability_score BETWEEN 0 AND 10", name="ck_pronounceability_bounds"),
        CheckConstraint("brandability_score BETWEEN 0 AND 10", name="ck_brandability_bounds"),
        CheckConstraint("overall_score BETWEEN 0 AND 10", name="ck_overall_bounds"),
    )


class DomainSeoAnalysis(Base):
    __tablename__ = "dn_seo_analyses"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    domain_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("domain_names.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    seo_keywords: Mapped[list[str]] = mapped_column(ARRAY(String(120)), default=list)
    seo_keyword_relevance_score: Mapped[int] = mapped_column(Integer, nullable=False)
    industry_relevance_score: Mapped[int] = mapped_column(Integer, nullable=False)
    domain_age: Mapped[int] = mapped_column(Integer, nullable=False)
    potential_resale_value: Mapped[int] = mapped_column(Integer, nullable=False)
    language: Mapped[str] = mapped_column(String(32), nullable=False)
    trademark_status: Mapped[str | None] = mapped_column(String(120))
    scored_by_agent: Mapped[str | None] = mapped_column(String(255))
    agent_model: Mapped[str | None] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    domain: Mapped[DomainName] = relationship("DomainName", back_populates="seo_analysis")


class AvailabilityCheck(Base):
    __tablename__ = "availability_checks"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    domain_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("domain_names.id", ondelete="CASCADE"), nullable=False
    )
    method: Mapped[str] = mapped_column(String(32), nullable=False)
    registrar: Mapped[str | None] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    checked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    raw: Mapped[dict | None] = mapped_column(JSONB)
    ttl_sec: Mapped[int | None] = mapped_column(Integer)

    domain: Mapped[DomainName] = relationship("DomainName", back_populates="availability_checks")


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type: Mapped[str] = mapped_column(String(32), nullable=False)
    entry_path: Mapped[str] = mapped_column(String(32), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="queued")
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    params: Mapped[dict | None] = mapped_column(JSONB)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    error: Mapped[str | None] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    runs: Mapped[list["AgentRun"]] = relationship("AgentRun", back_populates="job")
    created_by_user: Mapped["User" | None] = relationship("User", back_populates="jobs")
    domains: Mapped[list[DomainName]] = relationship(
        DomainName,
        secondary="job_domain_links",
        back_populates="jobs",
    )


class AgentRun(Base):
    __tablename__ = "agent_runs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False
    )
    agent_name: Mapped[str] = mapped_column(String(64), nullable=False)
    input: Mapped[dict | None] = mapped_column(JSONB)
    output: Mapped[dict | None] = mapped_column(JSONB)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    trace_id: Mapped[str | None] = mapped_column(String(255))
    eval_scores: Mapped[dict | None] = mapped_column(JSONB)

    job: Mapped[Job] = relationship("Job", back_populates="runs")


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    role: Mapped[str] = mapped_column(String(32), nullable=False, default="viewer")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    jobs: Mapped[list[Job]] = relationship("Job", back_populates="created_by_user")


class JobDomainLink(Base):
    __tablename__ = "job_domain_links"

    job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("jobs.id", ondelete="CASCADE"), primary_key=True
    )
    domain_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("domain_names.id", ondelete="CASCADE"), primary_key=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    job: Mapped[Job] = relationship(Job, backref="job_domain_links")
    domain: Mapped[DomainName] = relationship(DomainName, backref="job_domain_links")


__all__ = [
    "AgentRun",
    "AvailabilityCheck",
    "DomainAvailabilityStatus",
    "DomainEvaluation",
    "DomainName",
    "DomainSeoAnalysis",
    "Job",
    "JobDomainLink",
    "User",
]

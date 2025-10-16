"""Initial schema for Namesmith backend."""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "domain_names",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("label", sa.String(length=255), nullable=False),
        sa.Column("tld", sa.String(length=20), nullable=False),
        sa.Column("display_name", sa.String(length=255), nullable=True),
        sa.Column("length", sa.Integer(), nullable=False),
        sa.Column("processed_by_agent", sa.String(length=255), nullable=True),
        sa.Column("agent_model", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("label", "tld", name="uq_domain_names_label_tld"),
    )
    op.create_table(
        "dn_availability_status",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("domain_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("processed_by_agent", sa.String(length=255), nullable=True),
        sa.Column("agent_model", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["domain_id"], ["domain_names.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("domain_id", name="uq_dn_availability_status_domain_id"),
    )
    op.create_table(
        "dn_evaluations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("domain_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("possible_categories", postgresql.ARRAY(sa.String(length=120)), nullable=False, server_default="{}"),
        sa.Column("possible_keywords", postgresql.ARRAY(sa.String(length=120)), nullable=False, server_default="{}"),
        sa.Column("memorability_score", sa.Integer(), nullable=False),
        sa.Column("pronounceability_score", sa.Integer(), nullable=False),
        sa.Column("brandability_score", sa.Integer(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("overall_score", sa.Integer(), nullable=False),
        sa.Column("processed_by_agent", sa.String(length=255), nullable=True),
        sa.Column("agent_model", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["domain_id"], ["domain_names.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("domain_id", name="uq_dn_evaluations_domain_id"),
        sa.CheckConstraint("memorability_score BETWEEN 0 AND 10", name="ck_memorability_bounds"),
        sa.CheckConstraint("pronounceability_score BETWEEN 0 AND 10", name="ck_pronounceability_bounds"),
        sa.CheckConstraint("brandability_score BETWEEN 0 AND 10", name="ck_brandability_bounds"),
        sa.CheckConstraint("overall_score BETWEEN 0 AND 10", name="ck_overall_bounds"),
    )
    op.create_table(
        "dn_seo_analyses",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("domain_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("seo_keywords", postgresql.ARRAY(sa.String(length=120)), nullable=False, server_default="{}"),
        sa.Column("seo_keyword_relevance_score", sa.Integer(), nullable=False),
        sa.Column("industry_relevance_score", sa.Integer(), nullable=False),
        sa.Column("domain_age", sa.Integer(), nullable=False),
        sa.Column("potential_resale_value", sa.Integer(), nullable=False),
        sa.Column("language", sa.String(length=32), nullable=False),
        sa.Column("trademark_status", sa.String(length=120), nullable=True),
        sa.Column("scored_by_agent", sa.String(length=255), nullable=True),
        sa.Column("agent_model", sa.String(length=255), nullable=True),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["domain_id"], ["domain_names.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("domain_id", name="uq_dn_seo_analyses_domain_id"),
    )
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("email", name="uq_users_email"),
    )
    op.create_table(
        "jobs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("type", sa.String(length=32), nullable=False),
        sa.Column("entry_path", sa.String(length=32), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("params", postgresql.JSONB(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="SET NULL"),
    )
    op.create_table(
        "availability_checks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("domain_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("method", sa.String(length=32), nullable=False),
        sa.Column("registrar", sa.String(length=64), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("checked_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("raw", postgresql.JSONB(), nullable=True),
        sa.Column("ttl_sec", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["domain_id"], ["domain_names.id"], ondelete="CASCADE"),
    )
    op.create_table(
        "agent_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("job_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("agent_name", sa.String(length=64), nullable=False),
        sa.Column("input", postgresql.JSONB(), nullable=True),
        sa.Column("output", postgresql.JSONB(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("trace_id", sa.String(length=255), nullable=True),
        sa.Column("eval_scores", postgresql.JSONB(), nullable=True),
        sa.ForeignKeyConstraint(["job_id"], ["jobs.id"], ondelete="CASCADE"),
    )

    op.create_table(
        "job_domain_links",
        sa.Column("job_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("domain_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["job_id"], ["jobs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["domain_id"], ["domain_names.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("job_id", "domain_id", name="pk_job_domain_links"),
    )

    op.create_index("ix_domain_names_tld", "domain_names", ["tld"])
    op.create_index("ix_jobs_status", "jobs", ["status"])
    op.create_index("ix_availability_checks_domain_id", "availability_checks", ["domain_id", "checked_at"], unique=False)


def downgrade() -> None:
    op.drop_table("job_domain_links")
    op.drop_index("ix_availability_checks_domain_id", table_name="availability_checks")
    op.drop_index("ix_jobs_status", table_name="jobs")
    op.drop_index("ix_domain_names_tld", table_name="domain_names")
    op.drop_table("agent_runs")
    op.drop_table("availability_checks")
    op.drop_table("jobs")
    op.drop_table("users")
    op.drop_table("dn_seo_analyses")
    op.drop_table("dn_evaluations")
    op.drop_table("dn_availability_status")
    op.drop_table("domain_names")

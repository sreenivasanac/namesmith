# Namesmith Data Model v1 (Minimal)

Scope: A simple relational model that mirrors the legacy Prisma schema in `old_code/` to keep the console/API straightforward. This focuses on domains and their per‑aspect details (availability, evaluation, SEO). More advanced entities (jobs, agent runs, trends) are intentionally omitted here to avoid complexity and can be layered later (see technical_specification-1.md).

## Core Entities

1) domain_names
- id (uuid, pk)
- label (text)  // lowercase label, e.g., "fathom"
- tld (text)    // e.g., "com", "ai"
- display_name (text)  // e.g., "Fathom" or "UniqueCars"
- length (int)  // label length only (no TLD)
- processed_by_agent (text)
- agent_model (text)
- created_at (timestamptz, default now)

Notes: Mirrors `DomainName` in legacy while clarifying semantics. We use a composite unique index on `(label, tld)` so the same label can exist across different TLDs (e.g., `corten.com` and `corten.ai`). Persist `label` in lowercase; `display_name` is used for TitleCase or branded display.

2) dn_availability_status
- id (uuid, pk)
- domain_id (uuid, fk → domain_names.id, unique)
- status (text)  // standardized: available | registered | unknown | error
- processed_by_agent (text)
- agent_model (text)
- created_at (timestamptz, default now)

Notes: One‑to‑one with `domain_names`. Matches legacy `DNAvailabilityStatus`.

3) dn_evaluations
- id (uuid, pk)
- domain_id (uuid, fk → domain_names.id, unique)
- possible_categories (text[])
- possible_keywords (text[])
- memorability_score (int)
- pronounceability_score (int)
- brandability_score (int)
- description (text)
- overall_score (int)  // may be computed in API
- processed_by_agent (text)
- agent_model (text)
- created_at (timestamptz, default now)

Notes: One‑to‑one with `domain_names`. Mirrors legacy `DNEvaluation` (overall_score is calculated in the old API as the mean of three scores).

4) dn_seo_analyses
- id (uuid, pk)
- domain_id (uuid, fk → domain_names.id, unique)
- seo_keywords (text[])
- seo_keyword_relevance_score (int)
- industry_relevance_score (int)
- domain_age (int)
- potential_resale_value (int)
- language (text)
- trademark_status (text, nullable)
- scored_by_agent (text)
- agent_model (text)
- description (text)
- created_at (timestamptz, default now)

Notes: One‑to‑one with `domain_names`. Mirrors legacy `DNSEOAnalysis`.

5) Users
- users
  - id (uuid, pk)
  - email (text, unique)
  - role (text)  // viewer | editor | admin
  - created_at (timestamptz, default now)

Indexes
- unique on (email)


## Relationships
- domain_names 1—1 dn_availability_status (optional)
- domain_names 1—1 dn_evaluations (optional)
- domain_names 1—1 dn_seo_analyses (optional)

## Indexes
- unique index on (label, tld)
- domain_names(tld)
- dn_availability_status(domain_id) unique
- dn_evaluations(domain_id) unique
- dn_seo_analyses(domain_id) unique
- GIN indexes on array columns used for filtering:
  - dn_evaluations(possible_categories)
  - dn_evaluations(possible_keywords)
  - dn_seo_analyses(seo_keywords)

## Field Conventions
- Timestamps are stored in UTC (`timestamptz`).
- Availability status values are standardized to `available`, `registered`, `unknown`, `error` (case‑insensitive handling in API).
- Agent attribution fields (`processed_by_agent`, `scored_by_agent`, `agent_model`) capture provenance and are optional.
- Persist `label` lowercase for uniqueness; `display_name` may use TitleCase for displaying in UI.

## Compatibility Notes
- This schema intentionally mirrors the legacy Prisma models for a smooth transition of the console and API routes already present in `old_code/`.
- If later we need richer workflow tracking (jobs, agent runs, availability checks history), see `2_db_model_extended.md` — it can be implemented without breaking this core.
 - Extended entities (users, jobs/agent_runs, trends, availability history, company_names reference table) are specified in `2_db_model_extended.md` and should be added when job tracking and business prompt flows (Entry B) are enabled.

## Implementation Notes
- ORM: SQLAlchemy 2.x (Python) is the single source of truth; no Prisma/TypeORM in the new stack.
- API: FastAPI (Python) exposes REST endpoints; Next.js interacts with the API over HTTP.
- Contracts: Pydantic models live in `packages/shared-py`; types in `packages/shared-ts` are generated/mirrored from OpenAPI/JSON Schema with CI parity checks.
- Migrations: Alembic maintains schema evolution; Postgres hosted in Supabase.
- Ownership: The Python API owns database access and migrations; the web app does not access the database directly.

The following are extended ones:

# Namesmith Data Model v1.5 (Extensions)

Scope: additive tables to support jobs, agent runs, research, availability history, and commercialization. These extend the minimal v1 schema in project_development_plan/technical_specification-2.md without breaking it.

Notes
- Keep v1 tables (domain_names, dn_availability_status, dn_evaluations, dn_seo_analyses) unchanged.
- All timestamps are UTC (`timestamptz`).
- Use lowercase storage for domains to avoid case duplication.

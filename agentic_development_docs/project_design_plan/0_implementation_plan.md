# Namesmith Implementation Plan (Mono‑Repo)

This plan sequences the work to deliver the new mono‑repo with an updated LangGraph‑based agents service, FastAPI backend, and a Next.js console. It avoids any changes to `old_code/` while re‑implementing required features in the new structure.

## Guiding Constraints

- Do not modify `old_code/` (reference only)
- Use code identifiers prefixed or scoped as `namesmith`; centralize display name in a single configurable variable/value “Namesmith”
- Pin library versions to ensure reproducibility; upgrade intentionally via PRs

## Toolchain & Versions

- Node.js 20.x, pnpm 9.x (web)
- Python 3.11.x (api/agents)
- FastAPI 0.115+, SQLAlchemy 2.x, Pydantic v2
 - LangGraph (latest stable, Python), Langfuse Python SDK
- Celery 5.x, Redis 7.x
- Postgres 15+ (Supabase) with pgvector
- Sentry SDKs (web + python)

## Repo Structure (Target)

```
apps/
  web/
services/
  api/
    migrations/
  agents/
packages/
  shared-ts/
  shared-py/
infra/
  docker/
  ops/
project_development_plan/
old_code/
```

## Phase 0 — Repo Bootstrap

Deliverables:
- Create `apps/web`, `services/api`, `services/agents`, `packages/shared-ts`, `packages/shared-py`, `infra/`
- Add root README with quickstart; CODEOWNERS
- Prettier/ESLint/tsconfig for web; ruff/black/isort for python
- Base Dockerfiles and a minimal `docker-compose.dev.yml` (db, redis, api, worker)

Acceptance:
- `pnpm dev` runs Next.js
- `make dev` (or `uv run uvicorn`) serves API health at `/healthz`
- `celery -A services.api.celery_app worker -Q default` starts worker

## Phase 1 — Database & Migrations

Deliverables:
- Define SQLAlchemy models for core entities: users, jobs, agent_runs, domain_names, dn_availability_status, dn_evaluations, dn_seo_analyses, availability_checks, trends, company_names
- Alembic migration setup and first migration applied locally
- pgvector extension migration and index creation

Acceptance:
- `alembic upgrade head` applies cleanly; tables and indexes exist
- Read/write smoke tests for each table

## Phase 2 — Shared Schemas & Contracts

Deliverables:
- Pydantic models for request/response in `packages/shared-py`
- Generated or hand‑mirrored TS types in `packages/shared-ts`
- CI check that TS and Py contracts align (JSON Schema diff)

Acceptance:
- Contract test job passes in CI

## Phase 3 — Agents Skeleton (LangGraph)

Deliverables:
- `services/agents` package with:
  - State models (GenerationState, Trend, Candidate, ScoredCandidate, AvailabilityResult)
  - Nodes: gather_trends, generate_names, dedupe_and_filter, score_names, availability_precheck, availability_verify, persist_results
  - Graph builder with subgraphs and checkpoint/persistence hooks
  - Provider abstraction for LLMs and registrar APIs
  - LiteLLM-backed generation + scoring providers with per-job model selection and allowlist validation
- Minimal in‑memory runner + Postgres persistence adapter

Acceptance:
- Local run produces candidates and persists job results into DB (with stubbed providers)

## Phase 4 — Availability Service

Deliverables:
- DNS heuristic tool (async resolver, timeouts, caching)
- Registrar provider interface and two providers (WhoAPI and WhoisJSONAPI or Domain‑checker7), feature‑flagged
- Negative cache & TTL logic in DB; audit trail in `availability_checks`

Acceptance:
- Batch availability job updates statuses deterministically (with recorded cassettes in tests)

## Phase 5 — Scoring Rubric & Evals

Deliverables:
- Hybrid scoring: heuristics + LLM judge; rubric versioning
- Langfuse integration for prompt versions and trace links back to agent_runs
- Unit tests for heuristics; golden set for LLM evals

Acceptance:
- Scores populate `dn_evaluations` (with `overall_score`); rubric version recorded; evaluation report generated in CI artifact

## Phase 6 — FastAPI Endpoints

Deliverables:
- Auth middleware (Supabase JWT verification)
- Endpoints:
  - POST `/v1/jobs/generate`
  - GET `/v1/jobs/{job_id}`
  - GET `/v1/domains`
  - GET `/v1/domains/{id}`
  - POST `/v1/availability/check`
  - POST `/v1/feedback`
- Pagination, filtering, error handling patterns

Acceptance:
- OpenAPI schema covers the above; Postman/HTTP tests pass; 95% handler coverage

## Phase 7 — Console (Next.js)

Deliverables:
- Dashboard: create job form; job status list/detail with live polling
- Domain table: virtualized table, filters, column chooser, export CSV
- Candidate detail: scores, availability history, feedback widget
- Theming and layout using shadcn/ui; Sentry integration

Acceptance:
- E2E (Playwright): create job → see candidates with scores and availability

## Phase 8 — Background Jobs & Scheduling

Deliverables:
- Celery queues: `default`, `availability`, `scoring`, `research`
- Celery beat schedules: trend refresh, re‑score drift, availability TTL rechecks
- Backpressure/rate‑limit strategies per provider

Acceptance:
- Beat triggers scheduled tasks; metrics show rates and success ratios

## Phase 9 — Observability & Ops

Deliverables:
- Langfuse project wired to agents, links visible from Console on candidate detail
- Sentry projects for web and api; release versions and source maps
- OTEL traces through API and critical Celery flows

Acceptance:
- Error reported in Sentry during test; trace viewable in Langfuse

## Phase 10 — Hardening & Beta

Deliverables:
- AuthZ: roles (viewer/editor/admin), endpoint guards
- Request quotas per user; cost budgets for LLM/registrars
- Seed data and demo script
- Production deploy configs (Fly/Render + Vercel), runbooks

Acceptance:
- Beta demo end‑to‑end run under production settings

## Data & Schema Details (Initial)

- domain_names: `id, label, tld, display_name, length, processed_by_agent, agent_model, created_at`
- dn_evaluations: `id, domain_id, possible_categories[], possible_keywords[], memorability_score, pronounceability_score, brandability_score, overall_score, processed_by_agent, agent_model, created_at`
- dn_availability_status: `id, domain_id, status, processed_by_agent, agent_model, created_at`
- availability_checks: `id, domain_id, method, registrar, status, checked_at, raw, ttl_sec`
- jobs: `id, type, entry_path, status, created_by, params, started_at, finished_at, error`

## API Contracts (Initial)

POST `/v1/jobs/generate`
- Body: `{ entry_path: 'investor'|'business', topic?: string, prompt?: string, categories?: string[], tlds?: string[], count?: number }`
- Response: `{ job_id: string }`

GET `/v1/jobs/{job_id}`
- Response: `{ id, type, entry_path, status, progress?, created_at, finished_at }`

GET `/v1/domains`
- Query: `search?, status?, tld?, agent_model?, category?, cursor?, limit?`
- Response: `{ items: Domain[], next_cursor? }`

## Environment & Secrets

- `WEB_` envs in `apps/web/.env.local`
- `API_` and `AGENTS_` envs in `services/api/.env` and `services/agents/.env`
- Supabase `DATABASE_URL`, JWT public key, Langfuse keys, Sentry DSNs, LLM keys

## CI/CD

- Lint/format (web + py), typecheck (tsc, mypy), tests
- Build docker images for api/agents; deploy via PR‑based environments
- Upload source maps for web; run DB migrations on deploy

## Migration From old_code

- Keep legacy as reference only; do not import runtime code
- Recreate UI flows (domains table, filters) using new API contracts
- If needed, write one‑off ETL scripts to import any seed data

## Risks & Mitigations

- Registrar API ambiguity → Provider abstraction + recorded tests + vendor fallback
- LLM variability → prompt versioning in Langfuse + golden datasets
- Cost control → quotas, caching, scheduled windows, batch sizes

## Definition of Done (Overall)

- Users can create a generation job, see candidates in Console with scores and availability, and provide feedback.
- Agents run via LangGraph with persistence and observability in Langfuse.
- API secured with Supabase JWT, rate‑limited and monitored.

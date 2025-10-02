# Namesmith API Specification (v1)

Base: `/v1` (FastAPI). Auth: Supabase JWT via `Authorization: Bearer <token>`.
Content-Type: `application/json`.

Stack & Integration
- API: Implemented in Python FastAPI. There is no separate TypeScript API service; the Next.js Console calls FastAPI directly over HTTP.
- Long‑running operations (generation jobs, large availability batches) run asynchronously via Celery workers; endpoints return job/batch ids for polling.
- Small availability payloads (≤ 50 domains) are processed synchronously in the API for low latency.
- Contracts: Pydantic models in `packages/shared-py` generate OpenAPI/JSON Schema; `packages/shared-ts` types are mirrored from these schemas and validated in CI.
- Frontend: React Query (or fetch in server components) calls FastAPI routes; Next.js API routes are not used for core resources.
 - User context: Supabase JWT identifies the requester; API resolves `user_id` from the token and records it in `jobs.created_by`. All job resources are scoped to the requesting user unless the role is `admin`.

Conventions
- Pagination: cursor-based with `cursor` and `limit` (default 25, max 100). Returns `next_cursor` when more.
- Errors: `{ code: string, message: string, details?: any }` with appropriate HTTP status.
- Domains: request may supply either `{ label, tld }` or `{ full_domain }`; the API normalizes to lowercase label and computes `full_domain` for responses as `label + '.' + tld`.
- Availability status values standardized: `available`, `registered`, `unknown`, `error` (case-insensitive input).
- Idempotency: POST endpoints MAY accept `Idempotency-Key` header; duplicate creates on domains return 200 with `created: false` (see below).

Resource: Domain
- Object shape
  - id: string (uuid)
  - label: string (lowercase)
  - tld: string
  - full_domain: string (computed)
  - display_name?: string
  - length: number (label length only)
  - processed_by_agent?: string
  - agent_model?: string
  - created_at: string (ISO)
  - availability?: { status: string, created_at: string }
  - evaluation?: { possible_categories: string[], possible_keywords: string[], memorability_score: number, pronounceability_score: number, brandability_score: number, overall_score: number, description: string, processed_by_agent?: string, agent_model?: string, created_at: string }
  - seo_analysis?: { seo_keywords: string[], seo_keyword_relevance_score: number, industry_relevance_score: number, domain_age: number, potential_resale_value: number, language: string, trademark_status?: string, scored_by_agent?: string, agent_model?: string, description: string, created_at: string }

Domains
- GET `/v1/domains`
  - Query: `search?` (matches label or full_domain), `status?` (comma list), `tld?` (comma list), `agent_model?` (comma list), `category?` (comma list), range filters: `memorability_min/max`, `pronounceability_min/max`, `brandability_min/max`, `overall_min/max`; `sort_by?` in { created_at, label, tld, overall_score }, `sort_dir?` in { asc, desc }, `cursor?`, `limit?`.
  - Response: `{ items: Domain[], next_cursor?: string }`.

- GET `/v1/domains/{id}`
  - Response: `Domain` (includes nested availability/evaluation/seo_analysis when present).

- POST `/v1/domains`
  - Body: `{ label: string, tld: string, display_name?: string }` OR `{ full_domain: string, display_name?: string }`.
  - Behavior: computes `label`, `tld`, `length`; enforces uniqueness on `(label,tld)` with idempotent semantics.
    - If newly created: 201 Created → `{ created: true, domain: Domain }`.
    - If already exists: 200 OK → `{ created: false, domain: Domain }` and header `X-Idempotent: true`.
    - Optional `Idempotency-Key` header de-duplicates retried requests within a server-defined window.
  - Response: as above.

- PATCH `/v1/domains/{id}`
  - Body: `{ display_name?: string, processed_by_agent?: string, agent_model?: string }`.
  - Behavior: label/tld immutable. `processed_by_agent` and `agent_model` are treated as write-once, rarely edited fields:
    - If currently null: allow set for any editor.
    - If non-null: require admin role to update and record an audit entry (v1.5: domain_audit).
  - Response: updated `Domain`.

Filters (for UI dashboard)
- GET `/v1/filters`
  - Response: `{ statuses: string[], tlds: string[], bots: string[], industries: string[] }`.

Availability
- POST `/v1/availability/check`
  - Body: `{ domains: ({ id: string } | { full_domain: string } | { label: string, tld: string })[], mode?: 'auto'|'dns'|'registrar' }`.
  - Behavior: small payloads (<= 50) may be processed synchronously; larger requests enqueue a job and return batch id.
  - Response (sync): `{ results: { full_domain: string, status: 'available'|'registered'|'unknown'|'error' }[] }`
  - Response (async): `{ batch_id: string }`
  - Order & audit: DNS heuristics before registrar provider checks; each check recorded in `availability_checks` with raw payload and optional TTL.

- GET `/v1/availability/batches/{batch_id}`
  - Response: `{ status: 'queued'|'running'|'succeeded'|'failed', results?: { full_domain: string, status: string }[] }`

Evaluation
- POST `/v1/evaluations`
  - Body: `{ domain_id: string, possible_categories: string[], possible_keywords: string[], memorability_score: number, pronounceability_score: number, brandability_score: number, description: string, processed_by_agent?: string, agent_model?: string }`
  - Behavior: computes `overall_score` if omitted; upserts by `domain_id`.
  - Response: `{ domain_id, overall_score, ... }`

- GET `/v1/evaluations/{domain_id}`
  - Response: evaluation object or 404

SEO Analysis
- POST `/v1/seo-analyses`
  - Body: `{ domain_id: string, seo_keywords: string[], seo_keyword_relevance_score: number, industry_relevance_score: number, domain_age: number, potential_resale_value: number, language: string, trademark_status?: string, scored_by_agent?: string, agent_model?: string, description: string }`
  - Behavior: upserts by `domain_id`.
  - Response: seo_analysis object

- GET `/v1/seo-analyses/{domain_id}`
  - Response: seo_analysis object or 404

Jobs (Agents)
- POST `/v1/jobs/generate`
  - Body: `{ entry_path: 'investor'|'business', topic?: string, prompt?: string, categories?: string[], tlds?: string[], count?: number }`
  - Behavior: extracts `user_id` from JWT and creates a job row with `created_by = user_id`, `type = 'generate'`, `entry_path`, and `params` containing input fields. Enqueues a Celery task to run the LangGraph pipeline.
  - Response: `{ job_id: string }`

- GET `/v1/jobs`
  - Query: `status?`, `cursor?`, `limit?`
  - Behavior: returns jobs created by the requesting user (admins can list all).
  - Response: `{ items: { id, type, entry_path, status, created_at, finished_at }[], next_cursor?: string }`

- GET `/v1/jobs/{job_id}`
  - Behavior: authorizes access (owner or admin). Aggregates progress counters from `agent_runs` where available.
  - Response: `{ id, type, entry_path, status: 'queued'|'running'|'succeeded'|'failed'|'partial', progress?: { generated?: number, scored?: number, checked?: number }, error?: string, created_at, finished_at }`

Security
- All endpoints require Supabase JWT; role checks apply to write endpoints (editor/admin).
- Rate limits: write endpoints limited per user; availability checks protected against abuse.
- Audit: updates to `processed_by_agent`/`agent_model` create audit log entries (v1.5 table) with `updated_by`, `old_value`, `new_value`, and timestamp.
 - Authorization scope: job resources are visible only to their `created_by` user; admins may access any job. `user_id` is taken from JWT.

Notes
- Response models will be authored in `packages/shared-py` and mirrored to `packages/shared-ts`.
 - Single DB/ORM ownership resides in Python (SQLAlchemy); the web app never queries the DB directly.
 - Jobs endpoints become available when v1.5 tables (jobs, agent_runs) are present.


## API & Integration Notes

- API stack choice: FastAPI (Python) is the backend API. There is no separate TypeScript API; the Next.js Console calls FastAPI over HTTP.
- Shared code: Pydantic models in `packages/shared-py` produce OpenAPI/JSON Schema; `packages/shared-ts` mirrors these for client types with CI parity checks.
- Data access: SQLAlchemy (Python) is the sole ORM. The web app does not access the database directly.
- Asynchrony: Long‑running tasks (generation, large availability batches) are executed via Celery workers; endpoints return job/batch ids for polling.
- Availability: Small batches (≤ 50) may run synchronously in API; otherwise, the API enqueues a Celery job. DNS heuristics precede registrar provider checks, and all checks are logged to `availability_checks`.

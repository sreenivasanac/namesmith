
## API & Integration Notes

- API stack choice: FastAPI (Python) is the sole backend API. The Next.js Console consumes it over HTTP; no separate TypeScript API is introduced.
- Contracts: Pydantic models in `packages/shared-py` define the canonical schemas; `packages/shared-ts` types are generated/mirrored from OpenAPI/JSON Schema with CI checks.
- ORM & ownership: SQLAlchemy (Python) owns database models and migrations (Alembic). The web app never directly connects to the database.
- Async processing: Use Celery workers for long‑running jobs (generation, batch availability); endpoints return job/batch ids and expose polling endpoints.
- Availability execution: For small batches (≤ 50), the API performs synchronous checks; otherwise, it enqueues a job.
For now we will call WhoAPI directly to check domain name availability. Later we will optimize to reduce paid API calls.
<!-- DNS heuristics precede registrar checks, and all checks are persisted to `availability_checks` with raw payloads. -->

## 7. Availability Strategy

Call WhoAPI to check domain name availability. In future versions, add a pluggable provider interface (e.g., WhoisJSONAPI, Domain‑checker7) and DNS heuristics to minimize paid calls.

<!-- Goals: minimize paid API calls, avoid false positives.

Steps:
1) Negative cache: if candidate seen registered within TTL, skip API recheck
2) DNS heuristics: if domain resolves with valid A/AAAA/CNAME or has SOA/NS, mark as “likely registered”; otherwise “unknown” (not “available”)
3) Registrar API confirmation (WhoAPI currently; but implemented such that  pluggable provider interface - possibly other providers like WhoisJSONAPI, Domain‑checker7 in the future) -->

All checks recorded in `availability_checks` with raw payload for auditability.

## 8. Prompting & Scoring

- Generation: structure prompts to prefer short, brandable, pronounceable names; avoid hyphens/numbers unless requested; TLD‑aware
- Scoring: LLM‑judge
- Langfuse: store prompt versions, attach evals

## 9. Console (Next.js)

- Views: Dashboard (job status), Domains table (virtualized, filterable), Candidate detail panel (scores, availability, history), Trends browser
- Actions: Create generation job; request re‑score; batch availability; mark feedback; export CSV
- Data: SWR/React Query with incremental fetching and optimistic updates for feedback
- Error handling: Sentry; retry policies with circuit‑breaker on 5xx

## 10. Security & Compliance

- Supabase Auth JWT verification on API; role‑based checks (viewer, editor, admin)
- Secret management via environment variables; no secrets in repo
- Request input validation (Pydantic & Zod), output strict models
- Rate limiting per user/IP for sensitive endpoints
- Audit trail via `agent_runs` and Langfuse traces

## 11. Testing Strategy

- Python: pytest unit tests for tools and graph nodes; integration tests against a test DB; replay cassettes for registrar calls (VCR.py)
- Web: vitest/unit for components; Playwright for critical flows (job create → results visible)
- Contract tests: shared schemas validated in CI both TS and Py

## 12. Deployment

- Web: Vercel (or similar) with environment injection; source maps uploaded to Sentry
- API/Agents/Workers: containerized; single image with multiple entrypoints (`api`, `worker`, `beat`); deploy to Fly.io/Render/Cloud Run
- DB: Supabase managed Postgres + pgvector
- Observability: Langfuse cloud/self‑hosted; Sentry projects for web and api

## 13. Migration From old_code

- Keep `old_code/` read‑only; do not import code paths into new services
- Recreate required UI features (domain table, filters) in `apps/web`
- Rebuild agents on LangGraph >= 0.2 with typed state and subgraphs
- Incrementally import historic data if needed via one‑off scripts (new `services/api/scripts/`)

## 14. Risks & Mitigations

- Registrar API drift/rate limits → provider abstraction + health checks + caching
- False availability signals from DNS → always confirm with registrar API before “available”
- Cost control for LLM/API → batching, caching, per‑user quotas, budget alerts
- Schema churn → migrations gated by contract tests and blue/green deploys

## 15. Acceptance Criteria (Spec)

- Mono‑repo structure defined and documented
- Tech choices pinned (LangGraph latest version in python, FastAPI, Celery, Supabase)
- Core schemas and endpoints enumerated
- Agent graph with state shape defined
- Availability strategy documented with vendor abstraction

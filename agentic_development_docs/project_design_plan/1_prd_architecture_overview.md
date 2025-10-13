# Namesmith Technical Specification v1

This document defines the target architecture, technologies, data model, API surface, and multi‑agent orchestration for the Namesmith mono‑repo. It supersedes the earlier split‑repo approach while retaining `old_code/` as a frozen reference.

## 1. Architecture Overview

High‑level components:

- Console (Web): Next.js App Router (TypeScript), Tailwind CSS, shadcn/ui
- Backend API: FastAPI (Python 3.11+), Pydantic v2, SQLAlchemy
- Agents Service: Python + LangGraph (>= langgraph 0.6), tool-driven multi‑agent workflows
- Workers: Celery + Redis for background jobs (bulk availability, alerts)
- Database: Postgres (Supabase)
<!-- Maybe with pgvector for semantic retrieval and analytics - not implemented now -->
- Observability: Langfuse (LLM traces, prompts, evals), Sentry (frontend + backend), OpenTelemetry
- Secrets/Config: `.env` files in dev, environment variables in prod

Flow (simplified):
1) User triggers a generation job from Console → 2) API authenticates via Supabase JWT, records `jobs.created_by` with the requester, creates Job row and (currently) schedules the LangGraph run in-process via `asyncio.create_task` → 3) Agents Service (LangGraph) runs the multi‑agent workflow → 4) Results persist to Postgres (Langfuse integration is deferred) → 5) Console streams job status and displays candidates, scores, and availability.
Small availability batches (≤ 50) run synchronously in the API; larger batches will migrate to Celery once long-running steps are introduced.

## 2. Tech Stack

- Frontend
  - Next.js 14+ (App Router, TypeScript)
  - Tailwind CSS + shadcn/ui
  - React Query (TanStack Query) for data fetching
  - Zod for client validation, simple schemas mirrored from API contracts
  - Sentry for error tracking, source map upload in CI
  - Package manager: `pnpm`

- Backend/API
  - FastAPI, Uvicorn/Gunicorn
  - Pydantic v2 for request/response models
  - SQLAlchemy 2.x + Alembic for migrations
  - Celery workers (separate process) + Redis broker
  - Auth: Supabase JWT verification middleware (Console issues JWT; API verifies)
  - Sentry SDK + OpenTelemetry
  - Decision: Use FastAPI (Python) for APIs (not a TypeScript API) to co‑locate with LangGraph and SQLAlchemy, avoid cross‑language duplication or proxy layers, and keep a single ORM and shared Pydantic models.
  - Contracts: Authoritative Pydantic models in `packages/shared-py`; OpenAPI/JSON Schema generate `packages/shared-ts` types; CI validates type parity.
  - DB ownership: Python API + SQLAlchemy own schema/migrations; the Next.js app never accesses the database directly and always calls the API.
  - Python tool: `uv` for environment/run tasks

- Agents/LLM
  - LangGraph >= 0.6 - latest version - python implementation
  - Tool calling pattern with httpx, DNS resolver, registrar SDK clients
  - Langfuse for prompt/version management, traces and evaluations *(TODO; tracked in implementation notes)*
  - LiteLLM unifies calls across OpenAI/Claude/Groq/etc.; models selectable per job with an allowlist gate in settings
  - Scored by an LLM judge returning integer scores between 1 and 10;

- Data
  - Postgres (Supabase hosted) with `pgvector`
  - SQLAlchemy models as the single source of truth (no dual ORMs)

- Background processing
  - Celery queues: `default`, `availability`, `scoring`, `research`
  - Scheduled tasks via Celery beat (e.g., trend refresh, re‑checks)

## 3. Mono‑Repo Layout

The new code lives outside `old_code/`. Keep `old_code/` untouched for reference.

```
namesmith/
├─ apps/
│  └─ web/                      # Next.js console (App Router)
├─ services/
│  ├─ api/                      # FastAPI app (REST) + Celery worker/beat entrypoints
│  │  ├─ migrations/            # Alembic migrations (owned by API)
│  │  └─ scripts/               # DB/ETL/seed scripts and one-offs
│  │     └─ scrapers/           # Company-name ingestion (YC, Crunchbase, etc.)
│  └─ agents/                   # LangGraph workflows, tools, runners
├─ packages/
│  ├─ shared-ts/                # Shared TS types (client contracts)
│  └─ shared-py/                # Shared Pydantic models, enums
├─ infra/
│  ├─ docker/                   # Dockerfiles, compose, dev stacks
│  └─ ops/                      # Deployment IaC, env templates
├─ agentic_development_docs/
│  └─ project_design_plan/      # Specs, plans (this doc)
└─ old_code/                    # Frozen legacy reference (do not modify)
```

Naming rule from rules1.md: use `namesmith` for code identifiers; keep display text configurable via a single global variable/value “Namesmith”.



Key design points:
- Persist checkpoints to Postgres (via a simple CheckpointStore) for resumability
- Tool nodes for DNS check, registrar clients, embeddings, and prompt calls
- Retries with exponential backoff and vendor‑specific rate limiting
- Single API surface: FastAPI serves all backend routes; the Next.js Console interacts with it over HTTP using shared contracts (no separate TS API service)
- Availability precheck/human notify stages are deferred; the graph currently uses a domain name availability check node.

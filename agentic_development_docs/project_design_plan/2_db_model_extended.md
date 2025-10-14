
## Users
- users
  - id (uuid, pk)
  - email (text, unique)
  - role (text)  // viewer | editor | admin
  - created_at (timestamptz, default now)

Indexes
- unique on (email)

## Jobs & Agent Runs
- jobs
  - id (uuid, pk)
  - type (text)  // generate | score | availability | research
  - entry_path (text)  // investor | business
  - status (text)  // queued | running | succeeded | failed | partial
  - created_by (uuid, fk → users.id, null ok)
  - params (jsonb)
  - started_at (timestamptz, null ok)
  - finished_at (timestamptz, null ok)
  - error (text, null ok)

- agent_runs
  - id (uuid, pk)
  - job_id (uuid, fk → jobs.id)
  - agent_name (text)
  - input (jsonb)
  - output (jsonb)
  - status (text)
  - started_at (timestamptz, null ok)
  - finished_at (timestamptz, null ok)
  - trace_id (text, null ok)  // Langfuse or APM trace
  - eval_scores (jsonb, null ok)

- job_domain_links
  - job_id (uuid, fk → jobs.id)
  - domain_id (uuid, fk → domain_names.id)
  - linked_at (timestamptz, default now)

Indexes
- jobs(status)
- agent_runs(job_id)
- job_domain_links(job_id, domain_id) unique

Notes
- `job_domain_links` maintains provenance for generated domains so ownership via `jobs.created_by` is queryable without denormalizing domain tables.

## Research Sources & Trends
- trend_sources
  - id (uuid, pk)
  - name (text)
  - kind (text)  // yc | crunchbase | reddit | web | manual
  - url (text, null ok)
  - last_sync_at (timestamptz, null ok)

- trends
  - id (uuid, pk)
  - source_id (uuid, fk → trend_sources.id)
  - title (text)
  - summary (text)
  - tags (text[])
  - embeddings (vector, null ok)
  - metadata (jsonb, null ok)
  - created_at (timestamptz, default now)

Indexes
- trends(source_id)
- GIN on trends(tags)
- vector index on trends(embeddings) when available

## Company Names (Reference)
- company_names
  - id (uuid, pk)
  - name (text)
  - domain (text, null ok)
  - description (text, null ok)
  - categories (text[])
  - tags (text[])
  - source (text)  // yc | crunchbase | web | manual | other
  - source_url (text, null ok)
  - embeddings (vector, null ok)
  - created_at (timestamptz, default now)

Indexes
- unique on (domain) where domain is not null
- GIN on company_names(categories)
- GIN on company_names(tags)
- vector index on company_names(embeddings) when available

## Availability History (Audit)
- availability_checks
  - id (uuid, pk)
  - domain_id (uuid, fk → domain_names.id)
  - method (text)  // dns | registrar
  - registrar (text, null ok)
  - status (text)  // available | registered | unknown | error
  - checked_at (timestamptz, default now)
  - raw (jsonb, null ok)
  - ttl_sec (int, null ok)

Indexes
- availability_checks(domain_id, checked_at desc)
- availability_checks(registrar)

## Commercialization
- purchases
  - id (uuid, pk)
  - domain_id (uuid, fk → domain_names.id)
  - registrar (text)
  - price_cents (int)
  - currency (text)  // e.g., USD
  - purchased_at (timestamptz)
  - order_ref (text, null ok)
  - notes (text, null ok)

- listings
  - id (uuid, pk)
  - domain_id (uuid, fk → domain_names.id)
  - marketplace (text)  // dan | sedo | afternic | custom
  - url (text)
  - status (text)
  - listed_at (timestamptz)
  - last_updated_at (timestamptz, null ok)

Indexes
- purchases(domain_id)
- listings(domain_id)

## Human Feedback
- human_feedback
  - id (uuid, pk)
  - domain_id (uuid, fk → domain_names.id)
  - user_id (uuid, fk → users.id, null ok)
  - verdict (text)  // keep | drop | buy
  - notes (text, null ok)
  - created_at (timestamptz, default now)

Indexes
- human_feedback(domain_id, created_at desc)

## Future Considerations (non‑blocking)
- Optional `source` on domain_names (generated | imported | human)
- Optional `rubric_version` on dn_evaluations for scoring provenance
- Optional `lang` and `country` tags on trends for filtering

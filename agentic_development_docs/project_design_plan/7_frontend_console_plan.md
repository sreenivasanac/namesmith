# Namesmith Console Frontend Design Plan

## Overview
- Build a modern console for business users to log in, launch domain-generation jobs, and review the resulting domains, evaluations, and availability data produced by the FastAPI + LangGraph backend.
- Replace the legacy Prisma-based `old_code/namesmith_console` UI while reusing battle-tested UX patterns (filter rail, sortable table, details drawer) and aligning with the new `/v1` API contracts.
- Scope targets the Business user workflow only; investor-focused trend dashboards remain future work.

## Goals & Non-Goals
| Goals | Non-Goals |
| --- | --- |
| Authenticated console using Supabase sessions with automatic token refresh. | Building registrar purchase or resale flows. |
| Job creation flow surfacing model choices, prompt context, and TLD preferences. | Implementing investor/trend research entry (will stub hooks). |
| Dashboard to inspect jobs and poll progress. | Implementing real-time WebSocket streaming. |
| Domain review workspace with filters, sorting, search, and detail drawer. | Mobile-native apps or offline sync. |
| Consistent styling with shadcn theme and accessible interactions. | |

## High-Level User Flows
1. **Authentication**
   - User hits `/login`, authenticates via Supabase Auth hosted UI (email/password or magic link).
   - Supabase client stores the session; a fetch wrapper injects `Authorization: Bearer <token>` for backend calls.
2. **Create Domain Generation Job**
   - From dashboard CTA or `/jobs/new`, user completes a single-page form (business prompt, categories, TLDs, quantity, model selections).
   - `POST /v1/jobs/generate` is invoked through a React Query mutation; successful response navigates to the new job detail page with toast confirmation.
3. **Track Job Progress**
   - Job detail view polls `GET /v1/jobs/{id}` (3s cadence) until status is `succeeded` or `failed`, showing progress metrics.
4. **Review Domain Results**
   - The job detail page and `/domains` route share a table UI with left filter rail (availability, TLDs, models, industries, score sliders).
   - Table supports server-side pagination parameters (`cursor`, `limit`), sorting, and search; selecting a row opens an info drawer.
5. **Follow-Up Actions**
   - Users can view detailed domain information in a side drawer with external WHOIS link.

## Application Architecture
- **Framework**: Next.js App Router (TypeScript) with a mix of server components (initial data fetch, auth gating) and client components (interactive tables, filters).
- **State/Data**: TanStack React Query handles API caching; Zustand manages lightweight UI state (filter selections, drawer state) similar to the legacy approach.
- **Auth**: Supabase JS client on both server (via `createServerComponentClient`) and client; sessions refreshed silently, edge middleware enforces protected routes.
- **Styling**: Tailwind CSS and shadcn/ui with the provided OKLCH theme tokens loaded in a central CSS file; global `ThemeProvider` toggles light/dark if enabled later.
- **Shared Types**: Import generated contracts from `packages/shared-ts` (e.g., `Domain`, `DomainListResponse`, `JobResponse`) to maintain parity with FastAPI schemas.
- **HTTP Client**: Central `lib/api-client.ts` wraps `fetch`, attaching Supabase JWT, handling retries, and normalizing errors.
- **Suggested Directory Layout (apps/web)**:
  ```
  app/
    (auth)/login/page.tsx
    (dashboard)/layout.tsx
    (dashboard)/page.tsx
    (dashboard)/jobs/page.tsx
    (dashboard)/jobs/[jobId]/page.tsx
    (dashboard)/jobs/new/page.tsx
    (dashboard)/domains/page.tsx
  components/
  features/
    auth/
    jobs/
    domains/
  lib/
    api-client.ts
    auth/
    queryKeys.ts
  providers/
    app-providers.tsx
  ```

## Routing & Layout
- **Protected Shell**: `(dashboard)/layout.tsx` renders sidebar navigation (Dashboard, Domains, Jobs, Settings placeholder), header with branding (`settings.branding_name`), and user menu.
- **Auth Boundary**: `/login` resides in `(auth)` route segment with minimal layout; middleware redirects logged-in users away from login and unauthorized users into it.
- **Nested Views**: Job detail pages share server-fetched job metadata to avoid duplicate requests.

## Data Fetching Strategy
- **Query Keys**
  - `['jobs', params]` → `GET /v1/jobs?cursor&limit&status`
  - `['job', jobId]` → `GET /v1/jobs/{id}`
  - `['domains', params]` → `GET /v1/domains` with search/filter query params
  - `['job-domains', jobId, params]` → same endpoint with an added `job_id` filter (extend API to accept it)
  - `['domain', domainId]` → `GET /v1/domains/{id}`
  - `['filters']` → new `GET /v1/domains/filters` (to implement) returning distinct values for sidebar options
- **Mutations**
  - `createJob` (`POST /v1/jobs/generate`) invalidates `['jobs']` and prefetches `['job', id]`.
- **Server Rendering**
  - Dashboard and job detail pages fetch initial data server-side using Supabase session to hydrate React Query caches via `dehydrate`.
  - All fetches respect API pagination; infinite scroll (Load more) handled via React Query `useInfiniteQuery` for domains.

In the backend API endpoint, - Should `/v1/domains` accept a `job_id` filter and return filter metadata in one response to cut extra queries? -> Yes, this will be very good. Or a new API endpoint can also be created.
Update the backend `/v1/domains` API endpoint - to return relavant domain related information based on job_id. If needed create a new API endpoint in the backend API as well.

## UI & Interaction Design
- **Dashboard Landing**
  - Top metrics cards (jobs run, available domains) with skeleton states; uses forthcoming summary endpoint or computes from cached data.
  - Recent jobs table with status badges (`queued`, `running`, `succeeded`, `failed`) and context menu actions.
- **Job Form**
  - **Implemented as**: Single-page form with all fields visible (simplified from original multi-step wizard plan).
  - Validated with `zod`; fields for entry path, prompt, categories, TLDs, count, and model selections.
  - Model selection input fields allow custom model names (backend validates against allowlist).
- **Job Detail**
  - Header cards showing job status, models used, and progress metrics.
  - Domain table scoped to job with infinite scroll pagination.
- **Domain Explorer**
  - Filter rail with availability checkboxes, TLD multi-select, model checkboxes, industry chips, and score sliders.
  - Table built on TanStack Table + shadcn `Table` with client-side column sorting.
- **Domain Detail Drawer**
  - shadcn `Sheet` component displaying domain information, evaluation scores, and SEO analysis.
  - Shows audit info (processed_by_agent, agent_model, timestamps) and external WHOIS link.
- **Notifications**
  - shadcn `useToast` for success/error.
  - Inline banners for persistent warnings (e.g., missing availability provider).

## Filter & Search Behaviour
- Filter state managed in Zustand store.
- Numeric sliders default to [1,10]; updates trigger API refetches automatically.
- Search input debounced (300ms) to avoid excessive fetches.
- Filter metadata fetched from backend `/v1/domains` response; includes statuses, TLDs, agent_models, and industries.

## Real-Time Updates & Background Activity
- Job detail polling (3s intervals) stops upon success/failure.
- React Query refetch intervals handle status updates automatically.

## Authentication & Authorization
- Supabase session stored in cookies; server components access via Supabase server client to fetch JWT for backend requests.
- Protected layout ensures unauthorized users redirect to `/login`.
- Logout button clears Supabase session and invalidates React Query caches.

## Accessibility & Responsiveness
- All interactive controls use shadcn components with built-in accessibility.
- Keyboard navigation supported across filters and tables.
- Drawer enforces focus trap and escape-to-close behaviour.

## Styling & Theming
- Apply provided OKLCH theme tokens in `globals.css`; map to Tailwind via CSS variables for colours, radii, shadows.
- Keep brand name in a single config file so text in navigation/header references `settings.branding_name`.
- Use shadcn typography scale for headings; limit custom CSS to layout helpers.
- Follow frontend design rules given in this markdown file agentic_development_docs/project_design_plan/6_frontend_design.md
- Follow the shadcn theme style given in agentic_development_docs/project_design_plan/6_frontend_design.md 

## Performance Considerations
- Paginate domains (default 50 rows) with "Load more" to avoid giant payloads.
- Memoize derived data and avoid redundant client-side filtering when server parameters suffice.
- React Query handles caching and stale-time optimization.

## Testing & Quality
- Unit tests with Vitest + Testing Library for filters, job form, and table components.
- Integration tests for data hooks using MSW to mock `/v1` endpoints.
- Playwright end-to-end tests covering login, job creation, job polling, filter application, and domain detail drawer.
- Linting (ESLint) and type-checking (tsc) in CI; `pnpm lint`, `pnpm test`, `pnpm typecheck` scripts run locally.

## Security & Compliance
- Never log JWTs or API keys; ensure production builds run with `console` stripped or gated.
- Use HTTPS-only, Secure cookies for Supabase session; enforce same-site `lax`.
- Sanitize user-provided strings before display; rely on backend validation but escape HTML in rationale fields.
- Handle 401/403 by signing out and redirecting to login to avoid infinite retry loops.

## Implementation Status
1. ✅ **Scaffold & Auth**: Next.js app, Supabase providers, protected layouts, base theme.
2. ✅ **Job Management**: Job list/detail pages with polling.
3. ✅ **Domain Explorer**: Table, filters, and detail drawer integrating `/v1/domains`.
4. ✅ **Job Creation Flow**: Single-page form, validation, success redirect, and toasts.



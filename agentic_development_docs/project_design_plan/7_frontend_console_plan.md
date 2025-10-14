# Namesmith Console Frontend Design Plan

## Overview
- Build a modern console for business users to log in, launch domain-generation jobs, and review the resulting domains, evaluations, and availability data produced by the FastAPI + LangGraph backend.
- Replace the legacy Prisma-based `old_code/namesmith_console` UI while reusing battle-tested UX patterns (filter rail, sortable table, details drawer) and aligning with the new `/v1` API contracts.
- Scope targets the Business user workflow only; investor-focused trend dashboards remain future work.

## Goals & Non-Goals
| Goals | Non-Goals |
| --- | --- |
| Authenticated console using Supabase sessions with automatic token refresh. | Building registrar purchase or resale flows. |
| Guided job creation flow surfacing model choices, prompt context, and TLD preferences. | Implementing investor/trend research entry (will stub hooks). |
| Robust dashboard to inspect jobs, poll progress, and inspect run logs. | Implementing real-time WebSocket streaming (leave interfaces ready). |
| Domain review workspace with filters, sorting, search, detail drawer, CSV export. | Take inspiration from the old Prisma API layer; all data must route through FastAPI. |
| Consistent styling with shadcn theme, responsive layouts, and accessible interactions. | Mobile-native apps or offline sync. |

## High-Level User Flows
1. **Authentication**
   - User hits `/login`, authenticates via Supabase Auth hosted UI (email/password or magic link).
   - Supabase client stores the session; a fetch wrapper injects `Authorization: Bearer <token>` for backend calls.
2. **Create Domain Generation Job**
   - From dashboard CTA or `/jobs/new`, user completes a multi-step form (business prompt, categories, TLDs, quantity, model selections).
   - `POST /v1/jobs/generate` is invoked through a React Query mutation; successful response navigates to the new job detail page with toast confirmation.
3. **Track Job Progress**
   - Job detail view polls `GET /v1/jobs/{id}` (3s cadence) until status is `succeeded` or `failed`, showing incremental counts (`generated`, `scored`, `availability_checked`).
   - Progress timeline and agent run log (from `job.runs`) communicate internal steps and any errors.
4. **Review Domain Results**
   - The job detail page and `/domains` route share a table UI with left filter rail (availability, TLDs, models, industries, score sliders) inspired by the legacy console.
   - Table supports server-side pagination parameters (`cursor`, `limit`), sorting, search, and virtualization for large result sets; selecting a row opens an info drawer.
5. **Follow-Up Actions**
   - Users can copy names, flag favorites (client-side bookmark list), trigger availability re-checks, and export current table view as CSV.
   - Future actions like feedback submission hit `/v1/feedback` when implemented.

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
- **Nested Views**: Job detail uses child routes (tabs via URL query) for "Overview", "Domains", and "Run Log" while sharing server-fetched job metadata to avoid duplicate requests.
- **Responsive Behaviour**: Sidebar collapses to top drawer on mobile; filters convert to modal with accordions for smaller screens.

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
  - `recheckAvailability` (`POST /v1/availability/check`) updates affected domain caches.
  - `submitFeedback` (`POST /v1/feedback`) appends feedback to domain detail (placeholder until backend ready).
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
  - Multi-step wizard using shadcn `Stepper` component.
  - Validated with `zod`; real-time preview of prompt context and computed request size estimate.
  - Model selection dropdown populated from backend allowlist (fallback to default).
- **Job Detail**
  - Header card summarizing job info (prompt excerpt, categories, TLDs, model names, timestamps, user).
  - Progress bar + timeline; run log table reading `job.runs` to surface agent stage insights.
  - Domain table scoped to job, with quick filters (availability toggles, minimum score slider).
- **Domain Explorer**
  - Filter rail replicates legacy UI with Tailwind grid: availability checkboxes with emoji badges, TLD multi-select, bot/model checkboxes, industry chips, score sliders.
  - Table built on TanStack Table + shadcn `Table`, with column sorting, resizable columns, and optional column visibility controls.
  - Bulk actions toolbar when rows selected; includes copy, export, re-check availability.
- **Domain Detail Drawer**
  - shadcn `Sheet` component with tabs for "Summary", "Evaluation", "Availability history", "Notes".
  - Displays audit info (processed_by_agent, agent_model, timestamps) and provides quick action buttons.
- **Notifications**
  - shadcn `useToast` for success/error.
  - Inline banners for persistent warnings (e.g., missing availability provider).

## Filter & Search Behaviour
- URL query parameters represent active filters (e.g., `?status=available&memorability_min=7&memorability_max=10`).
- Zustand store syncs with URL; initial load parses query to seed store, mirroring legacy behaviour with stronger typing.
- Numeric sliders default to [1,10]; updates change state immediately but API refetches occur when user clicks "Apply filters" (auto-apply later via debounce).
- Search input debounced (300ms) to avoid excessive fetches.
- Distinct filter metadata fetched once then memoized; fallback gracefully if endpoint unavailable (derive from current page results).

## Real-Time Updates & Background Activity
- Job detail polling stops upon success/failure; manual "Refresh" button available.
- React Query `onSuccess` handler compares previous status to trigger notifications.
- Availability re-check triggers progress indicator per domain and updates status cell optimistically.
- Future WebSocket integration kept possible by isolating polling logic inside a hook.

## Authentication & Authorization
- Supabase session stored in cookies; server components access via Supabase server client to fetch JWT for backend requests.
- Custom `withAuth` layout ensures unauthorized users redirect to `/login`.
- UI respects role (from Supabase JWT claims or `/v1/users/me`): viewers see disabled mutation buttons with tooltips; editors/admins access mutating actions.
- Logout button clears Supabase session and invalidates React Query caches.

## Accessibility & Responsiveness
- All interactive controls use shadcn components with built-in accessibility; additional `aria-label` props for icon-only buttons.
- Keyboard navigation supported across filters and tables (focus rings, skip links).
- Drawer enforces focus trap and escape-to-close behaviour.
- Responsive breakpoints ensure table scrolls horizontally while filters collapse into a modal on small screens.

## Styling & Theming
- Apply provided OKLCH theme tokens in `globals.css`; map to Tailwind via CSS variables for colours, radii, shadows.
- Keep brand name in a single config file so text in navigation/header references `settings.branding_name`.
- Use shadcn typography scale for headings; limit custom CSS to layout helpers.
- Follow frontend design rules given in this markdown file agentic_development_docs/project_design_plan/6_frontend_design.md
- Follow the shadcn theme style given in agentic_development_docs/project_design_plan/6_frontend_design.md 

## Performance Considerations
- Table virtualization (`@tanstack/react-virtual`) for large domain lists.
- Paginate domains (default 50 rows) with "Load more" to avoid giant payloads.
- Memoize derived data (e.g., computed filter summaries) and avoid redundant client-side filtering when server parameters suffice.
- Abort outstanding fetches when users adjust filters rapidly via `AbortController`.

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

## Implementation Phasing
1. **Scaffold & Auth**: Set up Next.js app, Supabase providers, protected layouts, base theme.
2. **Job Management**: Implement job list/detail pages with polling and run log display.
3. **Domain Explorer**: Build shared table, filters, and detail drawer integrating `/v1/domains`.
4. **Job Creation Flow**: Add multi-step form, validation, success redirect, and toasts.
5. **Enhancements**: CSV export, availability re-check, bookmarks, responsive polish.
6. **Testing & Hardening**: Expand automated tests, performance profiling, accessibility fixes.

## Open Questions & Future Enhancements
- Confirm how Langfuse trace links will surface; reserve slot in domain drawer once backend exposes `trace_id`.
- Determine whether Supabase role mapping is authoritative or if an API `/v1/users/me` endpoint is needed for additional metadata.
- Explore push notifications (email/Web) for job completion; UI already surfaces status but proactive alerts are deferred.

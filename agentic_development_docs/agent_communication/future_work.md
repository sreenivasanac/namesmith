## Backend Future Work

- Authentication is currently implemented as a lightweight placeholder that accepts a UUID bearer token. Replace `services/api/auth.py` with a Supabase JWT verifier when keys are available.
- LiteLLM credentials for any allowlisted models (OpenAI, Anthropic, etc.) will be provided via environment variables so runtime calls succeed without additional per-provider SDK wiring. Check if LiteLLM needs API Key / credentials.
- Job orchestration executes LangGraph workflows inside the API process via `asyncio.create_task`. The Celery stub (`services/api/celery_app.py`) remains future background worker adoption; see `agentic_development_docs/agent_communication/workflow_orchestration.md` for the current vs. planned flow.
- Context gathering is still a placeholder that currently returns empty trend and company lists; future work needs to replace it with real lookups.
- Unit tests now cover the LLM generation/scoring providers; database integration tests remain blocked pending a dedicated Postgres test fixture.
- Replace the placeholder context gatherer with investor-specific retrieval that leverages provider-backed trend, similar companies fetching logic and company lookups.
- Implement `POST /v1/availability/check` endpoint for domain availability re-checking (frontend has a disabled button awaiting this)
- Maybe consider any other auth provider for authentication.


## Frontend Future Work

### High Priority Features
1. **URL Query Parameter Sync for Filters** (bookmarkable/shareable filtered views)
   - Implementation approach:
     - Create a `useFilterSync` hook that bridges Zustand store and URL searchParams
     - Use Next.js `useSearchParams` and `useRouter` for URL manipulation
     - Parse URL params on initial load to hydrate Zustand store
     - Use shallow routing to prevent page reloads on filter changes
     - Handle complex types (arrays, ranges) with proper serialization
   - Benefits: Users can bookmark filtered views, share links with specific filters applied
   - Estimated effort: 4-6 hours

2. **Exponential Backoff for Job Polling**
   - Current: Simple 3-second polling while job is active
   - Needed: Exponential backoff (3s, 6s, 12s, 24s, max 60s) with max poll count (e.g., 100 attempts)
   - Benefit: Reduces unnecessary API requests for long-running jobs
   - Estimated effort: 2-3 hours

3. **Accessibility Improvements**
   - Add proper ARIA labels to interactive elements
   - Implement skip navigation links
   - Add aria-labels to sortable table headers
   - Add keyboard shortcuts documentation
   - Estimated effort: 3-4 hours

### Medium Priority Features
1. **Mobile Responsive Sidebar**
   - Convert sidebar to collapsible drawer on mobile devices
   - Implement hamburger menu toggle
   - Ensure filters work well in mobile modal
   - Estimated effort: 4-6 hours

2. **CSV Export Functionality**
   - Add export button to domain table
   - Support bulk selection and export of selected domains
   - Include all relevant fields (name, scores, availability, etc.)
   - Estimated effort: 3-4 hours

3. **Table Virtualization**
   - Implement @tanstack/react-virtual for large domain lists (>1000 items)
   - Improves performance for users with many domains
   - Estimated effort: 4-5 hours

4. **Role-Based Access Control UI**
   - Fetch user role from JWT or `/v1/users/me` endpoint
   - Show/hide UI elements based on role (viewer, editor, admin)
   - Disable mutation buttons for viewers with tooltips
   - Estimated effort: 3-4 hours

5. **AbortController for Filter Fetches**
   - Cancel outstanding API requests when users adjust filters rapidly
   - Prevents race conditions and stale data
   - Estimated effort: 2 hours

6. **Job Run Logs Display**
   - Display `job.runs` agent execution logs in job detail page
   - Show agent stage insights and any errors
   - Add timeline visualization
   - Estimated effort: 4-6 hours

7. **Domain Availability Re-check**
   - Implement UI for re-checking domain availability
   - Requires backend endpoint: `POST /v1/availability/check`
   - Show progress indicator and update status optimistically
   - Estimated effort: 3-4 hours (frontend only)

### Low Priority / Nice to Have
1. **Multi-Step Wizard for Job Creation**
   - Convert single-page form to multi-step wizard using shadcn Stepper
   - Improve UX for complex job configurations
   - Estimated effort: 6-8 hours

2. **Client-Side Domain Bookmarks/Favorites**
   - Allow users to flag favorite domains
   - Store in local storage or user preferences
   - Quick filter to show only bookmarked domains
   - Estimated effort: 3-4 hours

3. **Settings Page**
   - User preferences (theme, notifications, etc.)
   - Account settings
   - API key management
   - Estimated effort: 6-8 hours

4. **Bulk Actions Toolbar**
   - Select multiple domains in table
   - Bulk actions: export, copy, delete, tag
   - Show selection count and clear action
   - Estimated effort: 4-5 hours

5. **Comprehensive E2E Tests**
   - Playwright tests for critical flows
   - Cover login, job creation, polling, filtering, domain details
   - Set up CI pipeline for test execution
   - Estimated effort: 8-12 hours

6. **WebSocket Support**
   - Real-time job updates via WebSocket instead of polling
   - Show live progress updates
   - Requires backend WebSocket endpoint
   - Estimated effort: 6-8 hours

7. **Push Notifications**
   - Browser notifications for job completion
   - Optional email notifications
   - User preference controls
   - Estimated effort: 6-8 hours

8. **Advanced Filtering**
   - Saved filter presets
   - Filter by date ranges
   - Complex filter combinations (AND/OR logic)
   - Estimated effort: 6-8 hours

9. **Domain Detail Enhancements**
   - Tabbed interface for Summary/Evaluation/History/Notes
   - Availability history timeline
   - User notes/comments on domains
   - Langfuse trace links when backend exposes `trace_id`
   - Estimated effort: 6-8 hours

10. **Feedback Submission**
    - UI for submitting feedback on domains
    - Hit `/v1/feedback` endpoint when implemented
    - Show feedback history
    - Estimated effort: 3-4 hours

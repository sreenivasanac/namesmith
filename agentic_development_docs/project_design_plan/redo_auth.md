Goal
- Remove the current authentication implementations (Better Auth and Supabase JWT) and leave a minimal, temporary placeholder. Authentication will be re‑implemented later using Better Auth from scratch.

Scope
- Remove Better Auth code and Supabase JWT auth code across the project.
- Keep non‑auth cleanups/refactors that are generally useful (e.g., removing unused code, minor refactors).
- Remove SMTP/email sending logic.
- Remove auth‑related database tables and Alembic migration changes introduced for auth.
- Uninstall auth‑related libraries that are no longer needed.

Temporary behavior to keep
- Login page: one email input and a single button. On submit, create or insert the user record by email in the database (idempotent upsert).
- Set a basic cookie to represent a logged‑in state and keep it until the user clicks Sign out.
- Sign out button clears that cookie and effectively signs the user out.
- No emails are sent; no external auth providers; no tokens.

Required actions (in order)
1) Inventory staged changes: use the staged diff to locate all code added/modified for Better Auth and for Supabase JWT. List affected files and what changed.
2) Remove Better Auth implementation: delete new files, revert or strip changes in modified files (server/client helpers, routes/handlers, middleware, session utilities, UI/components tied to Better Auth). Preserve unrelated general cleanups.
3) Remove Supabase JWT auth implementation and any related utilities, routes, middleware, and UI logic.
4) Delete SMTP/email sending code and any configuration or environment usage related to email sending.
5) Database and migrations:
   - Remove auth‑related tables introduced for Better Auth and the corresponding Alembic migration(s).
   - Revert/adjust Alembic env or config changes that were only needed for auth.
   - Ensure migration history remains consistent after removal.
6) Minimal login/sign‑out placeholder:
   - On login submit, upsert by email into the existing user table/model.
   - Create a simple cookie (e.g., a boolean/flag value) to mark the session as logged‑in; no JWTs or access tokens.
   - Sign out clears this cookie.
7) Session/cookie helpers: remove or simplify existing session logic to match the basic cookie approach; keep any generally useful, non‑auth utilities.
8) Dependencies and configuration:
   - Uninstall auth libraries (Better Auth, Supabase auth) and SMTP/email libraries from the project where they are no longer needed.
   - Remove imports/references and related environment variables/config entries.
9) Codebase cleanup:
   - Remove dead code, imports, and feature flags left over from the removed auth paths.
   - Keep non‑auth refactors and general improvements from the staged changes.

Acceptance criteria
- App uses only the minimal email login UI and a basic cookie; Sign out clears the cookie.
- On login, the user record is created/updated by email in the database (no emails sent).
- No Better Auth or Supabase JWT code, tables, migrations, or dependencies remain.
- Non‑auth cleanups from staged changes are preserved.
## Namesmith Web Frontend

Next.js application for the Namesmith dashboard. The project lives inside a pnpm workspace; run commands from the repo root unless noted.

### Install dependencies

```bash
pnpm install
```

### Development server

```bash
pnpm --dir apps/web dev
```

### Type checking & linting

```bash
pnpm --dir apps/web typecheck
pnpm --dir apps/web lint
```

### Production build & start (mirrors Docker workflow)

```bash
pnpm --dir apps/web build
pnpm --dir apps/web start
```

Set `NEXT_PUBLIC_API_URL` in `.env.local` (or via the Docker build arg) to point at the deployed API.

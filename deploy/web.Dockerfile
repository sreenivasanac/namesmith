# syntax=docker/dockerfile:1

FROM node:22-bookworm-slim AS base

ENV PNPM_HOME=/root/.local/share/pnpm
ENV PATH=${PNPM_HOME}:${PATH}
ENV NEXT_TELEMETRY_DISABLED=1

# Pin pnpm so the build is deterministic and honors onlyBuiltDependencies
# (declared in pnpm-workspace.yaml) — older corepack-default pnpm ignores it.
RUN corepack enable && corepack prepare pnpm@10.27.0 --activate

WORKDIR /app

COPY pnpm-workspace.yaml pnpm-lock.yaml ./
COPY apps ./apps
COPY packages ./packages

RUN pnpm install --frozen-lockfile --filter web...

ARG NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}

RUN pnpm --dir apps/web build

FROM node:22-bookworm-slim AS runner

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

WORKDIR /app

# Copy build output owned by root (NOT the runtime user) so the app tree is
# read-only to the process -> blocks dropping/executing binaries in the app dir.
# (This is the kill-chain step the 2026-01 cryptominer used: writable app dir + root.)
COPY --from=base --chown=root:root /app/apps/web/.next/standalone ./standalone
COPY --from=base --chown=root:root /app/apps/web/.next/static ./standalone/apps/web/.next/static

# Run as the unprivileged 'node' user (uid 1000) shipped in the base image.
USER node

EXPOSE 3000

CMD ["node", "standalone/apps/web/server.js"]

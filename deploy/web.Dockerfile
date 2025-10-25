# syntax=docker/dockerfile:1

FROM node:22-bookworm-slim AS base

ENV PNPM_HOME=/root/.local/share/pnpm
ENV PATH=${PNPM_HOME}:${PATH}
ENV NEXT_TELEMETRY_DISABLED=1

RUN corepack enable

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

RUN corepack enable

WORKDIR /app

COPY --from=base /app/apps/web/.next/standalone ./standalone
COPY --from=base /app/apps/web/.next/static ./standalone/apps/web/.next/static

EXPOSE 3000

CMD ["node", "standalone/apps/web/server.js"]

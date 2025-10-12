Backend:
  - Runtime: Python 
  - Framework: Next.js 14+ (API routes + dashboard)
  - Agent Framework: LangGraph
  - Queue: BullMQ (Redis-based for async agent tasks)
  - Cache: Redis (for DNS checks, API responses)

Frontend:
  - Framework: Next.js with App Router
  - UI: shadcn/ui + Tailwind CSS
  - State: TanStack Query + Zustand

Database:
  - Primary: PostgreSQL (via Supabase)
  - Vector Store: pgvector extension
  - Cache: Redis

Observability:
  - Agent Monitoring: LangFuse open source alternative
  - Error Tracking: Sentry

Infrastructure:
  - Hosting: Vercel (frontend) + Railway/Render (backend workers)
  - Background Jobs: BullMQ + Redis
  - File Storage: Supabase Storage or S3

External Services:
  - LLM: Different model options like OpenAI API, Claude Sonnet, Grok
  - DNS Lookup: Node.js native dns module
  - Domain name availability checking API: whoapi
  - Domain name purchase API: Porkbun



namesmith/
├── apps/
│   ├── console/          # Next.js dashboard
│   ├── agents/           # LangGraph agents service
│   └── api/              # Optional: Dedicated API service
├── packages/
│   ├── database/         # Shared DB schemas, migrations, client
│   ├── types/            # Shared TypeScript types
│   ├── domain-utils/     # Domain name utilities
│   └── config/           # Shared configuration
├── docker-compose.yml
├── turbo.json           # Turborepo config
└── package.json



namesmith/
├── apps/
│   └── console/          # Dashboard (Next.js app)
│       ├── app/          # Next.js routes, pages, API routes
│       ├── components/   # UI components (e.g., domain review table)
│       ├── lib/          # Client-side utils (e.g., Supabase auth)
│       └── package.json  # Next.js dependencies
├── packages/
│   └── agents/           # LangGraph/LangChain agents (Node.js package)
│       ├── src/          # Agent code (e.g., bots for generation, scoring)
│       ├── lib/          # Shared utils (e.g., prompt templates)
│       └── package.json  # LangChain deps
├── shared/               # Optional: Shared types/utils (e.g., domain schemas)
│   └── types/            # TypeScript interfaces for DB models
├── .gitignore
├── turbo.json            # If using Turborepo for builds
├── package.json          # Root workspace config
└── tsconfig.json         # Shared TypeScript config


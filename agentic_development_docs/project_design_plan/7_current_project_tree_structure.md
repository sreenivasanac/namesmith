tree
.
├── packages
│   ├── __init__.py
│   └── shared_py
│       ├── __init__.py
│       └── namesmith_schemas
│           ├── __init__.py
│           ├── base.py
│           ├── domain.py
│           ├── jobs.py
│           └── py.typed
├── pyproject.toml
├── README.md
├── scripts
│   └── run_migrations.py
├── services
│   ├── __init__.py
│   ├── agents
│   │   ├── __init__.py
│   │   ├── executor.py
│   │   ├── graph.py
│   │   ├── nodes
│   │   │   ├── availability.py
│   │   │   ├── dedupe.py
│   │   │   ├── gather.py
│   │   │   ├── generate.py
│   │   │   ├── persist.py
│   │   │   └── score.py
│   │   ├── prompts.py
│   │   ├── providers
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── llm.py
│   │   │   ├── whoapi.py
│   │   │   └── whoisjson.py
│   │   ├── run_local.py
│   │   ├── settings.py
│   │   └── state.py
│   └── api
│       ├── __init__.py
│       ├── alembic.ini
│       ├── auth.py
│       ├── celery_app.py
│       ├── db
│       │   ├── __init__.py
│       │   ├── base.py
│       │   ├── models.py
│       │   └── session.py
│       ├── dependencies.py
│       ├── main.py
│       ├── migrations
│       │   ├── env.py
│       │   └── versions
│       ├── repositories
│       │   ├── __init__.py
│       │   ├── domains.py
│       │   ├── jobs.py
│       │   └── users.py
│       ├── routers
│       │   ├── __init__.py
│       │   ├── domains.py
│       │   ├── health.py
│       │   └── jobs.py
│       ├── serializers.py
│       └── settings.py
├── tests
│   ├── test_generation_provider.py
│   └── test_serializers.py
└── uv.lock
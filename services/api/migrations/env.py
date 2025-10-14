"""Alembic environment configuration for Namesmith."""
from __future__ import annotations

from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool
from sqlalchemy.ext.asyncio import async_engine_from_config

from services.api.db.base import Base
from services.api.db.models import *  # noqa: F401,F403
from services.api.settings import settings

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Ensure the runtime URL matches our settings
url = settings.database_url
if url.startswith("postgresql://"):
    url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
config.set_main_option("sqlalchemy.url", url)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        connect_args={"statement_cache_size": 0},
    )

    async def do_run() -> None:
        async with connectable.connect() as connection:
            await connection.run_sync(_run_migrations)

        await connectable.dispose()

    import asyncio

    asyncio.run(do_run())


def _run_migrations(connection) -> None:  # type: ignore[no-untyped-def]
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

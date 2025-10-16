#!/usr/bin/env python3
"""Utility script for running Alembic database migrations."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from alembic import command
from alembic.config import Config
from pydantic import ValidationError


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _ensure_project_on_path() -> None:
    project_path = str(PROJECT_ROOT)
    if project_path not in sys.path:
        sys.path.insert(0, project_path)


def _load_database_url() -> str:
    try:
        from services.api.settings import settings
    except ValidationError as exc:  # pragma: no cover - configuration error path
        raise RuntimeError("DATABASE_URL must be set before running migrations.") from exc

    url = settings.database_url

    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return url


def _make_alembic_config(database_url: str | None = None) -> Config:
    config_path = PROJECT_ROOT / "services" / "api" / "alembic.ini"
    migrations_path = PROJECT_ROOT / "services" / "api" / "migrations"

    alembic_cfg = Config(str(config_path))
    alembic_cfg.set_main_option("script_location", str(migrations_path))

    if database_url:
        alembic_cfg.set_main_option("sqlalchemy.url", database_url)

    return alembic_cfg


def _run_upgrade(config: Config, revision: str, sql: bool) -> None:
    command.upgrade(config, revision, sql=sql)


def _run_downgrade(config: Config, revision: str, sql: bool) -> None:
    command.downgrade(config, revision, sql=sql)


def _run_history(config: Config, verbose: bool) -> None:
    kwargs = {"verbose": verbose}
    command.history(config, **kwargs)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run Alembic database migrations.")
    parser.add_argument(
        "--database-url",
        dest="database_url",
        help="Override the database URL. Defaults to the value from settings.",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    upgrade_parser = subparsers.add_parser("upgrade", help="Upgrade the database to a target revision.")
    upgrade_parser.add_argument("revision", nargs="?", default="head", help="Revision identifier (default: head).")
    upgrade_parser.add_argument("--sql", action="store_true", help="Don't run migrations; dump SQL to stdout instead.")

    downgrade_parser = subparsers.add_parser("downgrade", help="Downgrade the database to a target revision.")
    downgrade_parser.add_argument(
        "revision",
        help="Revision identifier to downgrade to (e.g., -1 to step back one migration).",
    )
    downgrade_parser.add_argument("--sql", action="store_true", help="Don't run migrations; dump SQL to stdout instead.")

    history_parser = subparsers.add_parser("history", help="Show migration history.")
    history_parser.add_argument("--verbose", action="store_true", help="Show full revision details.")

    return parser


def main(argv: list[str] | None = None) -> int:
    _ensure_project_on_path()

    parser = build_parser()
    args = parser.parse_args(argv)

    database_url = args.database_url or _load_database_url()
    config = _make_alembic_config(database_url)

    try:
        if args.command == "upgrade":
            _run_upgrade(config, args.revision, args.sql)
        elif args.command == "downgrade":
            _run_downgrade(config, args.revision, args.sql)
        elif args.command == "history":
            _run_history(config, args.verbose)
        else:
            parser.error(f"Unknown command: {args.command}")
    except Exception as exc:  # pragma: no cover - CLI surfacing
        parser.exit(1, f"Error: {exc}\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

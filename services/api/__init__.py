"""Namesmith API package."""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # pragma: no cover - import only for type checkers
    from .main import app as _app

__all__ = ["app"]


def __getattr__(name: str) -> Any:
    if name == "app":
        from .main import app as _loaded_app

        return _loaded_app
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

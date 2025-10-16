"""Shared enums and helpers for domain availability providers."""
from __future__ import annotations

from enum import Enum


class DomainAvailabilityProvider(str, Enum):
    STUB = "stub"
    WHOAPI = "whoapi"
    WHOISJSONAPI = "whoisjsonapi"

    @classmethod
    def from_str(cls, value: str | "DomainAvailabilityProvider") -> "DomainAvailabilityProvider":
        if isinstance(value, cls):
            return value
        normalized = (value or "").strip().lower()
        if not normalized:
            raise ValueError("Registrar provider value cannot be empty")
        for member in cls:
            if member.value == normalized:
                return member
        raise ValueError(f"Unsupported registrar provider '{value}'")


__all__ = ["DomainAvailabilityProvider"]

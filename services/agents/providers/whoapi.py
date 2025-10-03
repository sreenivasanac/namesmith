"""Registrar provider implementation using WhoAPI."""
from __future__ import annotations

from typing import Iterable, Sequence

import httpx

from ..state import AvailabilityResult, Candidate, ScoredCandidate
from .base import AvailabilityProvider

_STATUS_MAP = {
    "available": "available",
    "registered": "registered",
    "taken": "registered",
    "unknown": "unknown",
    "error": "error",
}


class WhoapiAvailabilityProvider(AvailabilityProvider):
    """Call the WhoAPI `status` endpoint to verify domain availability."""

    def __init__(self, api_key: str, *, base_url: str = "https://whoisjsonapi.com/v1/status") -> None:
        self._api_key = api_key
        self._base_url = base_url
        self._client = httpx.AsyncClient(timeout=10.0)

    async def check(self, candidates: Iterable[Candidate | ScoredCandidate]) -> Sequence[AvailabilityResult]:
        results: list[AvailabilityResult] = []
        for candidate in candidates:
            domain = candidate.full_domain
            params = {"apiKey": self._api_key, "domain": domain}
            status = "unknown"
            try:
                response = await self._client.get(self._base_url, params=params)
                response.raise_for_status()
                payload = response.json()
                raw_status = str(payload.get("status", "unknown")).lower()
                status = _STATUS_MAP.get(raw_status, "unknown")
            except Exception:  # noqa: BLE001
                status = "error"
                payload = {"error": "request_failed"}
            results.append(
                AvailabilityResult(
                    full_domain=domain,
                    status=status,
                    registrar="whoapi",
                )
            )
        return results

    async def aclose(self) -> None:
        await self._client.aclose()

    async def __aenter__(self) -> "WhoapiAvailabilityProvider":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:  # type: ignore[override]
        await self.aclose()

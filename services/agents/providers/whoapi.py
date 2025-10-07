"""Registrar provider implementation using WhoAPI."""
from __future__ import annotations

from typing import Iterable, Sequence

import httpx

from ..state import AvailabilityResult, Candidate, ScoredCandidate
from .base import AvailabilityProvider


class WhoapiAvailabilityProvider(AvailabilityProvider):
    """Call the WhoAPI domain availability endpoint to verify domain status."""

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = "https://api.whoapi.com",
        request_type: str = "taken",
    ) -> None:
        self._api_key = api_key
        self._request_type = request_type
        # Ensure trailing slash so httpx base_url joins correctly
        sanitized_base = base_url.rstrip("/") + "/"
        self._client = httpx.AsyncClient(base_url=sanitized_base, timeout=10.0)

    async def check(self, candidates: Iterable[Candidate | ScoredCandidate]) -> Sequence[AvailabilityResult]:
        results: list[AvailabilityResult] = []
        for candidate in candidates:
            domain = candidate.full_domain
            params = {
                "domain": domain,
                "r": self._request_type,
                "apikey": self._api_key,
            }
            status = "unknown"
            try:
                response = await self._client.get("", params=params)
                response.raise_for_status()
                payload = response.json()
            except (httpx.HTTPError, ValueError):
                status = "error"
            else:
                status_code = str(payload.get("status", "")).strip()
                if status_code == "0":
                    taken_value = str(payload.get("taken", "")).lower()
                    if taken_value in {"1", 1, "true", "yes", "taken"}:
                        status = "registered"
                    elif taken_value in {"0", "false", "no", "available"}:
                        status = "available"
                    else:
                        status = "unknown"
                else:
                    status = "error"
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

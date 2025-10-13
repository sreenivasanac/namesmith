"""Registrar provider implementation using WhoisJSON API."""
from __future__ import annotations

from typing import Iterable, Sequence

import httpx

from ..settings import settings
from ..state import AvailabilityResult, Candidate, ScoredCandidate
from .base import AvailabilityProvider

# TODO think if this domain availability part is working within few seconds, or if this needs
# to be moved to a Celery job

class WhoisJsonAvailabilityProvider(AvailabilityProvider):
    """Call the WhoisJSON API status endpoint to verify domain availability."""

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = "https://whoisjsonapi.com/v1/",
        timeout: float | None = None,
    ) -> None:
        self._api_key = api_key
        self._base_url = base_url.rstrip("/") + "/"
        self._timeout = timeout or settings.dns_timeout_seconds

    async def check(self, candidates: Iterable[Candidate | ScoredCandidate]) -> Sequence[AvailabilityResult]:
        results: list[AvailabilityResult] = []
        if not candidates:
            return results

        async with httpx.AsyncClient(timeout=self._timeout) as client:
            for candidate in candidates:
                domain = candidate.full_domain
                url = f"{self._base_url}status/{domain}"
                status = "unknown"
                raw_payload: dict | None = None
                try:
                    response = await client.get(url, headers={"Authorization": f"Bearer {self._api_key}"})
                    response.raise_for_status()
                    raw_payload = response.json()
                except (httpx.HTTPError, ValueError):
                    status = "error"
                else:
                    normalized = str(raw_payload.get("status", "")).strip().lower() if raw_payload else ""
                    if normalized == "inactive":
                        status = "available"
                    elif normalized == "active":
                        status = "registered"
                    else:
                        status = "unknown"
                results.append(
                    AvailabilityResult(
                        full_domain=domain,
                        status=status,
                        registrar="whoisjson",
                        raw_payload=raw_payload,
                    )
                )
        return results


__all__ = ["WhoisJsonAvailabilityProvider"]

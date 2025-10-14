"""Registrar provider implementation using WhoAPI."""
from __future__ import annotations

from typing import Iterable, Sequence

import httpx

from ..settings import settings
from ..state import AvailabilityResult, Candidate, ScoredCandidate
from .base import AvailabilityProvider

# TODO think if this domain availability part is working within few seconds, or if this needs
# to be moved to a Celery job

class WhoapiAvailabilityProvider(AvailabilityProvider):
    """Call the WhoAPI domain availability endpoint to verify domain status."""

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = "https://api.whoapi.com",
        request_type: str = "taken",
        timeout: float | None = None,
    ) -> None:
        self._api_key = api_key
        self._request_type = request_type
        self._base_url = base_url.rstrip("/") + "/"
        self._timeout = timeout or settings.dns_timeout_seconds

    async def check(self, candidates: Iterable[Candidate | ScoredCandidate]) -> Sequence[AvailabilityResult]:
        results: list[AvailabilityResult] = []
        if not candidates:
            return results

        async with httpx.AsyncClient(base_url=self._base_url, timeout=self._timeout) as client:
            for candidate in candidates:
                domain = candidate.full_domain
                params = {
                    "domain": domain,
                    "r": self._request_type,
                    "apikey": self._api_key,
                }
                status = "unknown"
                raw_payload: dict | None = None
                try:
                    response = await client.get("", params=params)
                    response.raise_for_status()
                    raw_payload = response.json()
                except (httpx.HTTPError, ValueError):
                    status = "error"
                else:
                    status_code = str(raw_payload.get("status", "")).strip() if raw_payload else ""
                    if status_code == "0":
                        taken_value = str(raw_payload.get("taken", "")).lower()
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
                        raw_payload=raw_payload,
                    )
                )
        return results

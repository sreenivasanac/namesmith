import os
import pytest

from services.agents.providers.whoapi import WhoapiAvailabilityProvider
from services.agents.state import Candidate


@pytest.mark.asyncio
async def test_whoapi_availability_registered_real_api():
    api_key = os.getenv("WHOAPI_API_KEY")
    if not api_key:
        pytest.skip("WHOAPI_API_KEY not set; skipping live WhoAPI test")

    provider = WhoapiAvailabilityProvider(api_key=api_key)
    results = await provider.check([Candidate(label="google", tld="com")])

    assert len(results) == 1
    assert results[0].full_domain == "google.com"
    assert results[0].registrar == "whoapi"
    assert results[0].status == "registered"

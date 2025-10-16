import os
import pytest

from services.agents.providers.whoisjson import WhoisJsonAvailabilityProvider
from services.agents.state import Candidate


@pytest.mark.asyncio
async def test_whoisjson_availability_registered_real_api():
    token = os.getenv("WHOISJSON_API_KEY")
    if not token:
        pytest.skip("WHOISJSON_API_KEY not set; skipping live WhoisJSON test")

    provider = WhoisJsonAvailabilityProvider(api_key=token)
    results = await provider.check([Candidate(label="google", tld="com")])

    assert len(results) == 1
    assert results[0].full_domain == "google.com"
    assert results[0].registrar == "whoisjson"
    assert results[0].status == "registered"

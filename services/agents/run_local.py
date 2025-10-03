"""Utility script to exercise the generation agent locally."""
from __future__ import annotations

import argparse
import asyncio
import uuid

from .executor import run_generation_job
from .state import GenerationInputs


async def _main() -> None:
    parser = argparse.ArgumentParser(description="Run a Namesmith generation job locally")
    parser.add_argument("--topic", default="ai analytics", help="Topic or theme for generation")
    parser.add_argument("--tlds", nargs="*", default=["com", "ai"], help="Preferred TLDs")
    parser.add_argument("--count", type=int, default=10, help="Number of names to generate")
    args = parser.parse_args()

    job_id = uuid.uuid4()
    inputs = GenerationInputs(
        job_id=job_id,
        entry_path="investor",
        topic=args.topic,
        tlds=args.tlds,
        count=args.count,
    )
    result = await run_generation_job(inputs)

    availability_map = {item.full_domain: item for item in result.availability}
    print(f"Generated {len(result.scored)} candidates for job {job_id}")
    for candidate in result.scored:
        availability = availability_map.get(candidate.full_domain)
        availability_status = availability.status if availability else "unknown"
        print(f"- {candidate.full_domain} | score={candidate.overall} | availability={availability_status}")


if __name__ == "__main__":
    asyncio.run(_main())

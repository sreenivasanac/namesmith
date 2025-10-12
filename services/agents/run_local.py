"""Utility script to exercise the generation agent locally."""
from __future__ import annotations

import argparse
import asyncio
import uuid

from packages.shared_py.namesmith_schemas.base import EntryPath

from ..api.db.session import SessionFactory
from ..api.repositories import create_job
from .executor import run_generation_job
from .state import GenerationInputs


async def _create_job_record(args: argparse.Namespace) -> uuid.UUID:
    job_params = {
        "entry_path": args.entry_path,
        "topic": args.topic,
        "tlds": args.tlds,
        "count": args.count,
        "generation_model": args.generation_model,
        "scoring_model": args.scoring_model,
    }
    # Remove optional keys that were not provided
    filtered_params = {key: value for key, value in job_params.items() if value is not None}

    async with SessionFactory() as session:
        job = await create_job(
            session,
            entry_path=args.entry_path,
            job_type="generate",
            created_by=None,
            params=filtered_params,
        )
        await session.commit()
        return job.id


async def _main() -> None:
    parser = argparse.ArgumentParser(description="Run a Namesmith generation job locally")
    parser.add_argument("--topic", default="ai analytics", help="Topic or theme for generation")
    parser.add_argument("--tlds", nargs="*", default=["com", "ai"], help="Preferred TLDs")
    parser.add_argument("--count", type=int, default=10, help="Number of names to generate")
    parser.add_argument("--generation-model", dest="generation_model", default=None, help="Override generation model name")
    parser.add_argument("--scoring-model", dest="scoring_model", default=None, help="Override scoring model name")
    parser.add_argument(
        "--entry-path",
        dest="entry_path",
        choices=[choice.value for choice in EntryPath],
        default=EntryPath.BUSINESS.value,
        help="Entry path for the generation job",
    )
    args = parser.parse_args()

    job_id = await _create_job_record(args)
    entry_path = EntryPath(args.entry_path)
    inputs = GenerationInputs(
        job_id=job_id,
        entry_path=EntryPath.BUSINESS.value,
        topic=args.topic,
        tlds=args.tlds,
        count=args.count,
        generation_model=args.generation_model,
        scoring_model=args.scoring_model,
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

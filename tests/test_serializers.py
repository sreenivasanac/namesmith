from datetime import datetime, timezone
import uuid

from services.api.db.models import DomainAvailabilityStatus, DomainEvaluation, DomainName
from services.api.serializers import serialize_domain


def test_serialize_domain_handles_relationships():
    domain = DomainName(
        id=uuid.uuid4(),
        label="sparkwave",
        tld="com",
        display_name="Sparkwave",
        length=9,
        created_at=datetime.now(timezone.utc),
    )
    domain.availability = DomainAvailabilityStatus(
        id=uuid.uuid4(),
        domain_id=domain.id,
        status="available",
        created_at=datetime.now(timezone.utc),
    )
    domain.evaluation = DomainEvaluation(
        id=uuid.uuid4(),
        domain_id=domain.id,
        possible_categories=["ai"],
        possible_keywords=["analytics"],
        memorability_score=8,
        pronounceability_score=7,
        brandability_score=9,
        overall_score=8,
        description="Well-balanced brand name",
        created_at=datetime.now(timezone.utc),
    )

    schema = serialize_domain(domain)
    assert schema.full_domain == "sparkwave.com"
    assert schema.availability and schema.availability.status == "available"
    assert schema.evaluation and schema.evaluation.memorability_score == 8

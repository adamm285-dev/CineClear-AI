import pytest
from app.harness import ExtractorHarness, CriticHarness
from app.models import ClearanceFlag, ClearanceCategory, RiskLevel, ParallelVerification


def test_extractor_harness_deduplication():
    raw_candidates = [
        {"category": "TRADEMARK_LOGO", "detected_entity": "Starbucks Siren Cup", "timestamp_or_page": "00:00:02"},
        {"category": "TRADEMARK_LOGO", "detected_entity": "starbucks siren cup", "timestamp_or_page": "00:00:04"},
        {"category": "COPYRIGHTED_ART", "detected_entity": "Modern Abstract Oil Canvas", "timestamp_or_page": "00:00:02"}
    ]
    deduped = ExtractorHarness.deduplicate_entities(raw_candidates)
    assert len(deduped) == 2
    assert deduped[0]["detected_entity"] == "Starbucks Siren Cup"
    assert deduped[1]["detected_entity"] == "Modern Abstract Oil Canvas"


def test_extractor_harness_sanitization():
    raw = {"category": "TRADEMARK_LOGO"}
    sanitized = ExtractorHarness.sanitize_candidate(raw)
    assert sanitized["timestamp_or_page"] == "00:00:01"
    assert sanitized["detected_entity"] == "Unidentified Visual Entity"


def test_critic_harness_statutory_invariants():
    bad_flag = ClearanceFlag(
        timestamp_or_page="00:00:01",
        category=ClearanceCategory.TRADEMARK_LOGO,
        detected_entity="Apple MacBook Pro",
        visual_description="Laptop on desk",
        risk_level=RiskLevel.LOW,
        verification=ParallelVerification(
            search_objective="Check Apple",
            sources_checked=[],
            is_public_domain=True,  # Contradiction bug
            active_trademark_found=True,
            rights_holder_identified="Apple Inc.",
            statutory_context="Lanham Act"
        ),
        mitigation_action="Asset is in public domain."
    )
    
    clean_flags = CriticHarness.enforce_invariants([bad_flag])
    assert clean_flags[0].verification.is_public_domain is False
    assert clean_flags[0].risk_level != RiskLevel.LOW
    assert "public domain" not in clean_flags[0].mitigation_action.lower()


def test_critic_harness_phone_pii_clamp():
    phone_flag = ClearanceFlag(
        timestamp_or_page="Page 1",
        category=ClearanceCategory.PHONE_PII,
        detected_entity="Real Phone Number: (212) 555-8392",
        visual_description="Phone number on napkin",
        risk_level=RiskLevel.LOW,
        verification=ParallelVerification(
            search_objective="Check Phone",
            sources_checked=[],
            is_public_domain=False,
            active_trademark_found=False,
            statutory_context="NANPA rules"
        ),
        mitigation_action="Review number"
    )

    clean_flags = CriticHarness.enforce_invariants([phone_flag])
    assert clean_flags[0].risk_level == RiskLevel.CRITICAL
    assert "555" in clean_flags[0].mitigation_action

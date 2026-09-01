import pytest
from app.models import (
    RiskLevel,
    ClearanceCategory,
    ParallelVerification,
    ClearanceFlag,
    ClearanceAuditReport
)


def test_models_instantiation():
    verification = ParallelVerification(
        search_objective="Check Nike Swoosh trademark",
        sources_checked=["https://tsdr.uspto.gov"],
        is_public_domain=False,
        active_trademark_found=True,
        rights_holder_identified="Nike, Inc.",
        statutory_context="Lanham Act 15 U.S.C. § 1114"
    )

    flag = ClearanceFlag(
        timestamp_or_page="00:01:24",
        category=ClearanceCategory.TRADEMARK_LOGO,
        detected_entity="Nike Swoosh",
        visual_description="Logo on hoodie",
        risk_level=RiskLevel.HIGH,
        verification=verification,
        mitigation_action="Blur in VFX"
    )

    report = ClearanceAuditReport(
        project_title="Test Production",
        media_filename="scene1.mp4",
        total_flags=1,
        critical_count=0,
        high_count=1,
        flags=[flag],
        generated_at="2026-08-31 00:00:00 UTC"
    )

    assert report.total_flags == 1
    assert report.flags[0].detected_entity == "Nike Swoosh"
    assert report.flags[0].risk_level == RiskLevel.HIGH
    assert report.flags[0].verification.active_trademark_found is True


def test_fuzzy_category_and_risk_coercion():
    from app.models import normalize_clearance_category, normalize_risk_level

    assert normalize_clearance_category("TRADEMARK") == ClearanceCategory.TRADEMARK_LOGO
    assert normalize_clearance_category("artwork") == ClearanceCategory.COPYRIGHTED_ART
    assert normalize_clearance_category("phone-number") == ClearanceCategory.PHONE_PII
    assert normalize_clearance_category("song_cue") == ClearanceCategory.MUSIC_AUDIO
    assert normalize_clearance_category("building_facade") == ClearanceCategory.ARCHITECTURAL_RIGHTS
    assert normalize_clearance_category("defamation_risk") == ClearanceCategory.NAME_DEFAMATION

    assert normalize_risk_level("CRITICAL_RISK") == RiskLevel.CRITICAL
    assert normalize_risk_level("HI") == RiskLevel.HIGH
    assert normalize_risk_level("med") == RiskLevel.MEDIUM
    assert normalize_risk_level("public_domain") == RiskLevel.LOW


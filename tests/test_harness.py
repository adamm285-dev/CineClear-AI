import pytest
from app.harness import ExtractorHarness, CriticHarness
from app.models import (
    ClearanceFlag,
    ClearanceCategory,
    RiskLevel,
    ParallelVerification,
    ClearanceAuditReport,
    LegalReleaseAgreement,
    UPL_LEGAL_DISCLAIMER
)
from app.fair_use_analyzer import FairUseAnalyzer


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


def test_critic_harness_statutory_seal_red_cross_and_fbi_clamp():
    """Tests 18 U.S.C. § 706 (Red Cross) & § 701 (Federal Badges) criminal emblem bans."""
    red_cross_flag = ClearanceFlag(
        timestamp_or_page="00:02:15",
        category=ClearanceCategory.TRADEMARK_LOGO,
        detected_entity="Red Cross Emblem",
        visual_description="First aid medical tent with genuine red cross symbol",
        risk_level=RiskLevel.MEDIUM,
        verification=ParallelVerification(
            search_objective="Check Red Cross",
            sources_checked=[],
            is_public_domain=False,
            active_trademark_found=False,
            statutory_context="Geneva Convention / 18 U.S.C. § 706"
        ),
        mitigation_action="Review medical tent placement"
    )

    fbi_flag = ClearanceFlag(
        timestamp_or_page="00:03:00",
        category=ClearanceCategory.TRADEMARK_LOGO,
        detected_entity="FBI Badge Replica",
        visual_description="Actor wearing exact replica FBI law enforcement seal badge",
        risk_level=RiskLevel.LOW,
        verification=ParallelVerification(
            search_objective="Check FBI badge",
            sources_checked=[],
            is_public_domain=False,
            active_trademark_found=False,
            statutory_context="18 U.S.C. § 701"
        ),
        mitigation_action="Review badge"
    )

    sanitized = CriticHarness.enforce_invariants([red_cross_flag, fbi_flag])
    assert sanitized[0].risk_level == RiskLevel.CRITICAL
    assert "18 U.S.C. § 706" in sanitized[0].mitigation_action
    assert sanitized[1].risk_level == RiskLevel.CRITICAL
    assert "18 U.S.C." in sanitized[1].mitigation_action


def test_critic_harness_rfc2606_web_domain_safe_harbor():
    """Tests RFC 2606 domain safe harbor invariant."""
    real_domain_flag = ClearanceFlag(
        timestamp_or_page="00:01:10",
        category=ClearanceCategory.TRADEMARK_LOGO,
        detected_entity="Active Web Domain: techstartup-corp.io",
        visual_description="Actor types on laptop showing live URL http://techstartup-corp.io",
        risk_level=RiskLevel.LOW,
        verification=ParallelVerification(
            search_objective="Check domain",
            sources_checked=[],
            is_public_domain=False,
            active_trademark_found=False,
            statutory_context="Cyber-trespass / Lanham Act"
        ),
        mitigation_action="Review website"
    )

    sanitized = CriticHarness.enforce_invariants([real_domain_flag])
    assert sanitized[0].risk_level == RiskLevel.HIGH
    assert "RFC 2606" in sanitized[0].mitigation_action


def test_critic_harness_awcpa_architecture_safe_harbor():
    """Tests 17 U.S.C. § 120(a) public architectural work exemption."""
    skyline_flag = ClearanceFlag(
        timestamp_or_page="00:00:30",
        category=ClearanceCategory.ARCHITECTURAL_RIGHTS,
        detected_entity="Midtown Manhattan Commercial High-Rise Building",
        visual_description="Exterior building facade visible from public street in background",
        risk_level=RiskLevel.HIGH,
        verification=ParallelVerification(
            search_objective="Check architecture",
            sources_checked=[],
            is_public_domain=False,
            active_trademark_found=False,
            statutory_context="AWCPA 17 U.S.C. § 120(a)"
        ),
        mitigation_action="Obtain location release from building owner"
    )

    sanitized = CriticHarness.enforce_invariants([skyline_flag])
    assert sanitized[0].risk_level == RiskLevel.LOW
    assert "120(a)" in sanitized[0].mitigation_action


def test_critic_harness_prop_currency_compliance():
    """Tests 18 U.S.C. § 504 prop currency compliance invariant."""
    cash_flag = ClearanceFlag(
        timestamp_or_page="00:04:12",
        category=ClearanceCategory.TRADEMARK_LOGO,
        detected_entity="Stack of 100 Dollar Bills",
        visual_description="Briefcase opened revealing paper money currency props",
        risk_level=RiskLevel.LOW,
        verification=ParallelVerification(
            search_objective="Check prop money",
            sources_checked=[],
            is_public_domain=False,
            active_trademark_found=False,
            statutory_context="18 U.S.C. § 504"
        ),
        mitigation_action="Inspect cash"
    )

    sanitized = CriticHarness.enforce_invariants([cash_flag])
    assert "18 U.S.C. § 504" in sanitized[0].mitigation_action


def test_rogers_v_grimaldi_artistic_relevance_assessment():
    """Tests the 2-prong Rogers v. Grimaldi artistic relevance defense."""
    assessment = FairUseAnalyzer.evaluate_rogers_test(
        entity_name="Rolex Submariner",
        scene_context="Character glances at their vintage wristwatch in narrative dramatic scene.",
        category=ClearanceCategory.TRADEMARK_LOGO,
        risk_level=RiskLevel.MEDIUM
    )
    assert assessment.is_expressive_work is True
    assert assessment.artistic_relevance_passed is True
    assert assessment.explicitly_misleading is False
    assert assessment.rogers_protection_applies is True
    assert "Rogers v. Grimaldi" in assessment.statutory_rationale


def test_upl_disclaimer_invariant():
    """Tests the Unauthorized Practice of Law (UPL) statutory decision-support notice."""
    report = ClearanceAuditReport(
        project_title="Hollywood Feature",
        media_filename="scene_01.mp4"
    )
    assert report.legal_disclaimer == UPL_LEGAL_DISCLAIMER
    assert "State Bar regulations" in report.legal_disclaimer
    assert "Does not constitute formal legal counsel" in report.legal_disclaimer

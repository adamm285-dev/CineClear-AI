import pytest
from app.music_arch_analyzer import AWCPAValidator, MusicSyncAnalyzer
from app.models import ClearanceFlag, ClearanceCategory, RiskLevel, ParallelVerification


def test_awcpa_public_view_safe_harbor():
    # Generic public building in city panorama
    assessment = AWCPAValidator.evaluate_landmark(
        entity_name="Standard City Hall Facade",
        visual_context="Public street panoramic view of municipal building",
        risk_level=RiskLevel.MEDIUM
    )
    assert assessment.is_public_view_safe_harbor is True
    assert "17 U.S.C. § 120(a)" in assessment.governing_statute
    assert "CLEARANCE CONFIRMED" in assessment.clearance_recommendation


def test_restricted_landmark_detection():
    # Eiffel tower at night (copyrighted light show)
    assessment = AWCPAValidator.evaluate_landmark(
        entity_name="Eiffel Tower",
        visual_context="Night skyline establishing shot with active light illumination",
        risk_level=RiskLevel.HIGH
    )
    assert assessment.is_public_view_safe_harbor is False
    assert "RESTRICTED COMMERCIAL FACADE" in assessment.jurisdiction_status
    assert "SETE" in assessment.commercial_filing_restrictions


def test_music_cue_sheet_generation():
    music_flag = ClearanceFlag(
        timestamp_or_page="00:04:12",
        category=ClearanceCategory.MUSIC_AUDIO,
        detected_entity="Blinding Lights",
        visual_description="Source radio track playing inside hero vehicle",
        risk_level=RiskLevel.HIGH,
        verification=ParallelVerification(
            search_objective="Verify The Weeknd Blinding Lights",
            sources_checked=[],
            is_public_domain=False,
            active_trademark_found=False,
            rights_holder_identified="Republic Records / Universal Music Group",
            statutory_context="17 U.S.C. § 114 & § 106"
        ),
        mitigation_action="Obtain master and sync licenses."
    )

    cue_sheet = MusicSyncAnalyzer.build_cue_sheet([music_flag], project_title="Neon Odyssey")
    assert cue_sheet is not None
    assert len(cue_sheet.cue_entries) == 1
    assert cue_sheet.cue_entries[0].cue_number == "M-001"
    assert "Republic Records" in cue_sheet.cue_entries[0].master_rights_holder
    assert "ASCAP" in cue_sheet.cue_entries[0].publisher_pro

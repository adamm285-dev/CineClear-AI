import pytest
from app.edl_exporter import EDLExporter, timecode_to_frames, frames_to_timecode
from app.models import (
    ClearanceAuditReport,
    ClearanceCategory,
    ClearanceFlag,
    ParallelVerification,
    RiskLevel,
)


def test_timecode_and_frame_conversions():
    assert timecode_to_frames("00:00:01", fps=24) == 24
    assert timecode_to_frames("00:01:00", fps=24) == 1440
    assert timecode_to_frames("01:00:00", fps=24) == 86400
    assert frames_to_timecode(24, fps=24) == "00:00:01:00"
    assert frames_to_timecode(1440, fps=24) == "00:01:00:00"


def test_cmx3600_edl_generation():
    flag1 = ClearanceFlag(
        timestamp_or_page="00:00:05",
        category=ClearanceCategory.TRADEMARK_LOGO,
        detected_entity="Nike 'Swoosh' Logo",
        visual_description="Hero wardrobe hoodie with chest logo",
        risk_level=RiskLevel.HIGH,
        verification=ParallelVerification(
            search_objective="Verify Nike Swoosh",
            sources_checked=["https://www.nike.com"],
            is_public_domain=False,
            active_trademark_found=True,
            rights_holder_identified="Nike, Inc.",
            statutory_context="Lanham Act 15 U.S.C. § 1114"
        ),
        mitigation_action="Obtain signed wardrobe release or Greek logo in VFX.",
        box_2d=[310, 610, 780, 940]
    )

    flag2 = ClearanceFlag(
        timestamp_or_page="00:00:15",
        category=ClearanceCategory.PHONE_PII,
        detected_entity="Real Phone Number: (212) 555-8392",
        visual_description="On-screen napkin phone number",
        risk_level=RiskLevel.CRITICAL,
        verification=ParallelVerification(
            search_objective="Verify Phone PII",
            sources_checked=["https://www.nationalnanpa.com"],
            is_public_domain=False,
            active_trademark_found=False,
            rights_holder_identified="NANPA",
            statutory_context="FCC & NANPA Safe Harbor violation"
        ),
        mitigation_action="MANDATORY FIX: Replace with 555-01XX reserved number.",
        box_2d=None
    )

    report = ClearanceAuditReport(
        project_title="Neon Odyssey",
        media_filename="scene_01_dailies.mov",
        media_type="video",
        total_flags=2,
        critical_count=1,
        high_count=1,
        flags=[flag1, flag2]
    )

    edl = EDLExporter.generate_cmx3600_edl(report, fps=24)
    assert "TITLE: CINECLEAR_NEON_ODYSSEY" in edl
    assert "FCM: NON-DROP FRAME" in edl
    assert "* FROM CLIP NAME: scene_01_dailies.mov" in edl
    assert "* LOC: 00:00:05:00 Orange CINECLEAR: [HIGH] Nike 'Swoosh' Logo" in edl
    assert "* LOC: 00:00:15:00 Red CINECLEAR: [CRITICAL] Real Phone Number: (212) 555-8392" in edl
    assert "* COMMENT: Action: Obtain signed wardrobe release or Greek logo in VFX." in edl

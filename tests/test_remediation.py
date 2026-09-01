import pytest
from app.models import ClearanceFlag, ClearanceCategory, RiskLevel, ParallelVerification
from app.remediation_agent import RemediationAgent


def test_remediation_agent_generates_releases_and_vfx_orders():
    agent = RemediationAgent()
    
    flags = [
        ClearanceFlag(
            timestamp_or_page="00:01:15",
            category=ClearanceCategory.COPYRIGHTED_ART,
            detected_entity="Modern Abstract Oil Canvas",
            visual_description="Upper wall set painting",
            risk_level=RiskLevel.HIGH,
            verification=ParallelVerification(
                search_objective="Test Art",
                sources_checked=[],
                is_public_domain=False,
                active_trademark_found=False,
                rights_holder_identified="Elena Rostova",
                statutory_context="17 U.S.C. § 106"
            ),
            mitigation_action="Obtain Form-4A release."
        ),
        ClearanceFlag(
            timestamp_or_page="00:02:40",
            category=ClearanceCategory.TRADEMARK_LOGO,
            detected_entity="Apple MacBook Pro",
            visual_description="Hero laptop on desk",
            risk_level=RiskLevel.MEDIUM,
            verification=ParallelVerification(
                search_objective="Test Apple",
                sources_checked=[],
                is_public_domain=False,
                active_trademark_found=True,
                rights_holder_identified="Apple Inc.",
                statutory_context="Lanham Act"
            ),
            mitigation_action="Greek logo in VFX."
        ),
        ClearanceFlag(
            timestamp_or_page="Page 12",
            category=ClearanceCategory.PHONE_PII,
            detected_entity="305-555-9876",
            visual_description="Dialogue line",
            risk_level=RiskLevel.CRITICAL,
            verification=ParallelVerification(
                search_objective="Test Phone",
                sources_checked=[],
                is_public_domain=False,
                active_trademark_found=False,
                rights_holder_identified=None,
                statutory_context="PSTN Allocation"
            ),
            mitigation_action="Replace with 555-0149."
        )
    ]

    package = agent.generate_remediation_package(flags, project_title="Neon Odyssey")

    # Assertions
    assert len(package.legal_releases) == 2  # 1 Form-4A, 1 TM Release
    assert len(package.vfx_work_orders) == 2  # 1 Painting replacement, 1 Apple Greeking
    assert len(package.script_fixes) == 1     # 1 Phone PII fix

    assert package.legal_releases[0].form_type == "Form-4A Artwork Release"
    assert "Elena Rostova" in package.legal_releases[0].licensor_entity
    assert "212-555-0149" in package.script_fixes[0].recommended_replacement

import pytest
from pathlib import Path
from app.auditor import CineClearAuditor
from app.report_generator import generate_eo_clearance_binder
from app.models import ClearanceFlag, ClearanceCategory, RiskLevel, ParallelVerification


@pytest.mark.asyncio
async def test_cineclear_auditor_script():
    auditor = CineClearAuditor()
    sample_script = Path("sample_media/sample_screenplay.txt")
    assert sample_script.exists()

    report = await auditor.audit_media(
        file_path=str(sample_script),
        project_title="Midnight Drive",
        media_type="script"
    )

    assert report.total_flags > 0
    assert report.project_title == "Midnight Drive"
    assert report.critical_count > 0 or report.high_count > 0 or report.medium_count > 0
    assert report.pdf_report_path is not None
    assert Path(report.pdf_report_path).exists()


@pytest.mark.asyncio
async def test_cineclear_auditor_image():
    auditor = CineClearAuditor()
    sample_image = Path("sample_media/sample_set_photo.jpg")
    assert sample_image.exists()

    report = await auditor.audit_media(
        file_path=str(sample_image),
        project_title="Studio Interior",
        media_type="image"
    )

    assert report.total_flags >= 2
    assert any("Nike" in f.detected_entity or "Apple" in f.detected_entity or "Starbucks" in f.detected_entity or "Art" in f.detected_entity for f in report.flags)


@pytest.mark.asyncio
async def test_critic_agent_fixes_nike_hallucination():
    auditor = CineClearAuditor()
    
    # Simulate the hallucinated flag from single-pass extraction
    hallucinated_flag = ClearanceFlag(
        timestamp_or_page="00:00:01",
        category=ClearanceCategory.TRADEMARK_LOGO,
        detected_entity="NIKE 'SWOOSH' Logo",
        visual_description="Hero wardrobe hoodie with chest logo",
        risk_level=RiskLevel.LOW,
        verification=ParallelVerification(
            search_objective="Verify Nike Swoosh",
            sources_checked=["https://www.nike.com"],
            is_public_domain=True,  # Hallucinated bug
            active_trademark_found=True,
            rights_holder_identified="Nike, Inc.",
            statutory_context="Lanham Act 15 U.S.C. § 1114"
        ),
        mitigation_action="CLEARANCE CONFIRMED: Asset is in worldwide public domain (pre-1929)."
    )
    
    sanitized = await auditor.review_and_securitize_flags([hallucinated_flag])
    
    # Invariant assertions
    assert sanitized[0].verification.is_public_domain is False
    assert sanitized[0].risk_level != RiskLevel.LOW
    assert "public domain" not in sanitized[0].mitigation_action.lower()

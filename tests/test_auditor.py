import pytest
from pathlib import Path
from app.auditor import CineClearAuditor
from app.report_generator import generate_eo_clearance_binder
from app.models import RiskLevel


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
    assert report.critical_count > 0 or report.high_count > 0
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
    assert any(f.detected_entity == "Nike 'Swoosh' Logo" or "Nike" in f.detected_entity for f in report.flags)

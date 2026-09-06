import json
import pytest
from httpx import AsyncClient, ASGITransport
from app.config import settings
from server import app

JUDGE_HEADERS = {"X-Judge-Access": settings.JUDGE_ACCESS_KEY}


@pytest.mark.asyncio
async def test_terms_of_service_page():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/terms")
        assert response.status_code == 200
        body = response.text
        assert "AS-IS" in body
        assert "Limitation of liability" in body or "LIMITATION OF LIABILITY" in body
        assert "Indemnif" in body
        health = await client.get("/health")
        assert health.json().get("decision_support_only") is True


@pytest.mark.asyncio
async def test_favicon_is_served():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/favicon.ico")
        assert response.status_code == 200
        assert response.headers["content-type"] in (
            "image/x-icon",
            "image/vnd.microsoft.icon",
            "image/png",
            "image/svg+xml",
        )
        assert len(response.content) > 20


@pytest.mark.asyncio
async def test_health_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "CineClear AI"


@pytest.mark.asyncio
async def test_samples_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/samples")
        assert response.status_code == 200
        samples = response.json()
        assert len(samples) >= 3
        assert any(s["id"] == "sample-photo" for s in samples)


@pytest.mark.asyncio
async def test_audit_sample_screenplay_pdf_exists_or_is_created():
    """PDF SCRIPT sample must resolve even if sample_screenplay.pdf was gitignored/missing."""
    from app.config import settings
    from pathlib import Path

    pdf_path = settings.SAMPLE_MEDIA_DIR / "sample_screenplay.pdf"
    backup = None
    if pdf_path.exists():
        backup = pdf_path.read_bytes()
        pdf_path.unlink()

    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/audit",
                headers=JUDGE_HEADERS,
                data={
                    "project_title": "Feature Screenplay Excerpt",
                    "sample_id": "sample-screenplay",
                    "media_type": "auto",
                },
            )
        assert response.status_code == 200, response.text
        report = response.json()
        assert report["media_type"] == "script"
        assert report["total_flags"] >= 1
        assert pdf_path.exists()
    finally:
        if backup is not None:
            pdf_path.write_bytes(backup)


@pytest.mark.asyncio
async def test_audit_stream_emits_engine_stages_then_report():
    """Pipeline balls must follow real engine stages, not a fake timer."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        async with client.stream(
            "POST",
            "/api/audit/stream",
            headers=JUDGE_HEADERS,
            data={
                "project_title": "Streamed Studio Audit",
                "sample_id": "sample-photo",
                "media_type": "image",
            },
        ) as response:
            assert response.status_code == 200
            body = ""
            async for chunk in response.aiter_text():
                body += chunk

    events = []
    for frame in body.split("\n\n"):
        data_lines = [
            line[5:].strip()
            for line in frame.splitlines()
            if line.startswith("data:")
        ]
        payload = "\n".join(data_lines).strip()
        if not payload:
            continue
        events.append(json.loads(payload))
    types = [e.get("type") for e in events]
    assert "stage" in types
    assert types[-1] == "complete"
    steps = [e["step"] for e in events if e.get("type") == "stage"]
    assert steps[0] == 1
    assert 4 in steps
    report = events[-1]["report"]
    assert report["project_title"] == "Streamed Studio Audit"
    assert report["total_flags"] >= 1


@pytest.mark.asyncio
async def test_audit_sample_photo():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/audit",
            headers=JUDGE_HEADERS,
            data={
                "project_title": "Hollywood Test Studio",
                "sample_id": "sample-photo",
                "media_type": "image"
            }
        )
        assert response.status_code == 200
        report = response.json()
        assert "id" in report
        assert report["project_title"] == "Hollywood Test Studio"
        assert report["total_flags"] >= 2

        # Test retrieving JSON
        report_id = report["id"]
        get_res = await client.get(f"/api/reports/{report_id}")
        assert get_res.status_code == 200

        # Test downloading PDF binder
        pdf_res = await client.get(f"/api/reports/{report_id}/pdf")
        assert pdf_res.status_code == 200
        assert pdf_res.headers["content-type"] == "application/pdf"

        # Test downloading CMX 3600 EDL markers
        edl_res = await client.get(f"/api/reports/{report_id}/edl")
        assert edl_res.status_code == 200
        assert "text/plain" in edl_res.headers["content-type"]
        assert "TITLE: CINECLEAR_" in edl_res.text
        assert "FCM: NON-DROP FRAME" in edl_res.text


@pytest.mark.asyncio
async def test_export_pdf_and_edl_from_report_payload():
    """Bottom export buttons send the completed report body; must not depend on in-memory cache."""
    from app.models import ClearanceAuditReport, ClearanceFlag, ClearanceCategory, RiskLevel, ParallelVerification

    report = ClearanceAuditReport(
        id="export-test-id-1234",
        project_title="Export Studio",
        media_filename="scene.jpg",
        media_type="image",
        total_flags=1,
        high_count=1,
        flags=[
            ClearanceFlag(
                id="f1",
                timestamp_or_page="00:00:01",
                category=ClearanceCategory.TRADEMARK_LOGO,
                detected_entity="Nike Swoosh",
                visual_description="Hero hoodie logo",
                risk_level=RiskLevel.HIGH,
                verification=ParallelVerification(
                    search_objective="nike",
                    sources_checked=["https://www.uspto.gov"],
                    statutory_context="Lanham Act",
                ),
                mitigation_action="Greek the logo",
            )
        ],
    )
    payload = json.loads(report.model_dump_json())
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        pdf_res = await client.post("/api/export/pdf", json=payload)
        assert pdf_res.status_code == 200, pdf_res.text
        assert pdf_res.headers["content-type"] == "application/pdf"
        assert pdf_res.content[:4] == b"%PDF"

        edl_res = await client.post("/api/export/edl", json=payload)
        assert edl_res.status_code == 200, edl_res.text
        assert "TITLE: CINECLEAR_" in edl_res.text
        assert "FCM: NON-DROP FRAME" in edl_res.text


@pytest.mark.asyncio
async def test_judge_auth_verify_endpoint():
    from app.config import settings
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Without credentials
        res = await client.get("/api/auth/verify")
        assert res.status_code == 200
        data = res.json()
        assert "authenticated" in data

        # 2. With valid judge query parameter
        res_auth = await client.get(f"/api/auth/verify?access={settings.JUDGE_ACCESS_KEY}")
        assert res_auth.status_code == 200
        assert res_auth.json()["authenticated"] is True
        assert res_auth.json()["role"] == "VIP_JUDGE"

        # 3. With valid X-Judge-Access header
        res_hdr = await client.get("/api/auth/verify", headers={"X-Judge-Access": settings.JUDGE_ACCESS_KEY})
        assert res_hdr.status_code == 200
        assert res_hdr.json()["authenticated"] is True


@pytest.mark.asyncio
async def test_protected_upload_requires_judge_key_when_configured():
    from app.config import settings
    prev_state = settings.REQUIRE_JUDGE_AUTH_FOR_UPLOADS
    try:
        settings.REQUIRE_JUDGE_AUTH_FOR_UPLOADS = True
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # 1. Sample audit without VIP pass is blocked (protects Gemini/Parallel quota)
            res_sample_unauth = await client.post(
                "/api/audit",
                data={"project_title": "Public Sample", "sample_id": "sample-photo"}
            )
            assert res_sample_unauth.status_code == 401

            res_sample = await client.post(
                "/api/audit",
                headers={"X-Judge-Access": settings.JUDGE_ACCESS_KEY},
                data={"project_title": "Public Sample", "sample_id": "sample-photo"}
            )
            assert res_sample.status_code == 200

            # 2. Custom upload without auth fails with 401
            res_unauth = await client.post(
                "/api/audit",
                data={"project_title": "Unauthorized Upload"},
                files={"file": ("test.txt", b"INT. LIVING ROOM - DAY\nJohn checks his watch.", "text/plain")}
            )
            assert res_unauth.status_code == 401
            assert "Judge Access Required" in res_unauth.json()["detail"]

            # 3. Custom upload with Judge VIP Header succeeds
            res_auth = await client.post(
                "/api/audit",
                data={"project_title": "Authorized Upload"},
                headers={"X-Judge-Access": settings.JUDGE_ACCESS_KEY},
                files={"file": ("test.txt", b"INT. LIVING ROOM - DAY\nJohn checks his watch.", "text/plain")}
            )
            assert res_auth.status_code == 200
            assert "id" in res_auth.json()
    finally:
        settings.REQUIRE_JUDGE_AUTH_FOR_UPLOADS = prev_state

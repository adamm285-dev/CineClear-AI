import pytest
from httpx import AsyncClient, ASGITransport
from server import app


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
async def test_audit_sample_photo():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/audit",
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
            # 1. Public sample audit continues to work freely
            res_sample = await client.post(
                "/api/audit",
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

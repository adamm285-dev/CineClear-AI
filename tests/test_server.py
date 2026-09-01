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

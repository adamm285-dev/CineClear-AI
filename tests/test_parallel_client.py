import pytest
from app.parallel_client import ParallelSearchClient


@pytest.mark.asyncio
async def test_parallel_search_mock():
    client = ParallelSearchClient()
    result = await client.search(objective="Verify Nike Swoosh logo trademark")
    
    assert "results" in result
    assert len(result["results"]) > 0
    first_result = result["results"][0]
    assert "title" in first_result
    assert "url" in first_result
    assert "excerpt" in first_result or "excerpts" in first_result


@pytest.mark.asyncio
async def test_parallel_search_phone_pii():
    client = ParallelSearchClient()
    # Test phone PII query structure
    result = await client.search(objective="Verify NANPA 555 telephone number film clearance requirements")
    
    assert "results" in result
    assert len(result["results"]) > 0
    first_result = result["results"][0]
    assert "url" in first_result
    assert "title" in first_result

    # Also test mock fallback explicitly
    mock_res = client._mock_legal_search(objective="Verify phone number PII clearance requirements")
    assert "results" in mock_res
    assert any("555" in r.get("excerpt", "") or "nanpa" in r.get("title", "").lower() for r in mock_res["results"])

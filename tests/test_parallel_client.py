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
    assert "excerpt" in first_result
    assert "uspto" in first_result["url"].lower() or "nike" in first_result["title"].lower()


@pytest.mark.asyncio
async def test_parallel_search_phone_pii():
    client = ParallelSearchClient()
    result = await client.search(objective="Verify phone number PII clearance requirements")
    
    assert "results" in result
    assert len(result["results"]) > 0
    assert any("555" in r.get("excerpt", "") or "nanpa" in r.get("title", "").lower() for r in result["results"])

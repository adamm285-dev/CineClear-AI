import pytest
from app.gemini_cascade import GeminiCascadeClient, DEFAULT_MODEL_LADDER


def test_cascade_initialization():
    cascade = GeminiCascadeClient()
    assert len(cascade.ladder) == 4
    assert "gemini-3.6-flash" in cascade.ladder
    assert "gemini-2.5-flash" in cascade.ladder


def test_cascade_execution_order():
    cascade = GeminiCascadeClient()
    order = cascade._build_execution_order("gemini-2.5-pro")
    assert order[0] == "gemini-2.5-pro"
    assert "gemini-3.6-flash" in order
    assert len(order) == len(DEFAULT_MODEL_LADDER)


@pytest.mark.asyncio
async def test_cascade_offline_fallback():
    cascade = GeminiCascadeClient()
    # When no active client or keys fail, gracefully returns None to engage local harness
    result = await cascade.generate_content_with_cascade(contents="Test Prompt")
    assert result is None or isinstance(result, str)

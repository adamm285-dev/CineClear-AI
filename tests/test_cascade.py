import pytest
from app.gemini_cascade import GeminiCascadeClient, DEFAULT_MODEL_LADDER


def test_cascade_initialization():
    cascade = GeminiCascadeClient()
    assert len(cascade.ladder) == 5
    assert cascade.ladder[0] == "gemini-3.8-flash"
    assert "gemini-3.5-flash" in cascade.ladder
    assert "gemini-3.6-flash" in cascade.ladder


def test_cascade_execution_order():
    cascade = GeminiCascadeClient()
    order = cascade._build_execution_order("gemini-3.7-flash")
    assert order[0] == "gemini-3.7-flash"
    assert "gemini-3.5-flash" in order
    assert len(order) == len(DEFAULT_MODEL_LADDER) + 1


@pytest.mark.asyncio
async def test_cascade_offline_fallback():
    cascade = GeminiCascadeClient()
    # When no active client or keys fail, gracefully returns None to engage local harness
    result = await cascade.generate_content_with_cascade(contents="Test Prompt")
    assert result is None or isinstance(result, str)


def test_clean_json_text_and_parse_json_safe():
    from app.gemini_cascade import clean_json_text, parse_json_safe
    
    # 1. Standard markdown fenced json
    markdown_json = "```json\n[{\"detected_entity\": \"Nike Logo\"}]\n```"
    assert clean_json_text(markdown_json) == '[{"detected_entity": "Nike Logo"}]'
    parsed = parse_json_safe(markdown_json)
    assert isinstance(parsed, list)
    assert parsed[0]["detected_entity"] == "Nike Logo"

    # 2. General markdown backticks
    raw_backticks = "```\n{\"flags\": [1, 2, 3]}\n```"
    parsed_obj = parse_json_safe(raw_backticks)
    assert parsed_obj == {"flags": [1, 2, 3]}

    # 3. None and empty handling
    assert clean_json_text(None) == ""
    assert parse_json_safe(None) is None
    assert parse_json_safe("invalid text with no json") is None


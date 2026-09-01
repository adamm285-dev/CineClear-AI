"""
CineClear AI - Dynamic Model Cascade & Fallback Manager
Orchestrates hierarchical failover across Gemini model generations on 429 rate limits,
preserving pipeline continuity before triggering local deterministic harnesses.
"""

import json
import logging
from typing import Any, List, Optional
from google import genai
from google.genai import types
from google.genai.errors import APIError

from app.config import settings

import re

import asyncio

logger = logging.getLogger("cineclear.cascade")


def clean_json_text(text: Optional[str]) -> str:
    """Strips markdown code blocks, backticks, and whitespace from LLM output."""
    if not text:
        return ""
    cleaned = text.strip()
    # Strip ```json ... ``` or ``` ... ```
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        cleaned = "\n".join(lines).strip()
    return cleaned


def parse_json_safe(text: Optional[str]) -> Optional[Any]:
    """Parses JSON safely from LLM output, stripping markdown formatting."""
    if not text:
        return None
    cleaned = clean_json_text(text)
    try:
        return json.loads(cleaned)
    except Exception as e:
        # Attempt regex search for JSON array or object
        match = re.search(r'(\[.*\]|\{.*\})', cleaned, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except Exception:
                pass
        logger.warning(f"[Cascade] Failed to parse JSON from response: {e}")
        return None


# Hierarchical Fallback Ladder: High-Acuity -> High-Quota Production -> Standard Tier
DEFAULT_MODEL_LADDER = [
    "gemini-3.5-flash",
    "gemini-3.5-flash-lite",
    "gemini-3.6-flash",
    "gemini-flash-latest"
]


class GeminiCascadeClient:
    """Manages tiered API dispatching and graceful failover."""

    def __init__(self, model_ladder: Optional[List[str]] = None):
        self.ladder = model_ladder or DEFAULT_MODEL_LADDER
        self.api_key = settings.GEMINI_API_KEY
        self.client = self._init_client()

    def _init_client(self) -> Optional[genai.Client]:
        if self.api_key and self.api_key != "mock_gemini_key":
            try:
                return genai.Client(api_key=self.api_key)
            except Exception as e:
                logger.warning(f"[Cascade] Failed to initialize Google GenAI Client: {e}")
        return None

    def _build_execution_order(self, preferred_model: Optional[str]) -> List[str]:
        target = preferred_model or settings.GEMINI_MODEL
        order = [target] if target else []
        for m in self.ladder:
            if m not in order:
                order.append(m)
        return order

    async def generate_content_with_cascade(
        self,
        contents: Any,
        system_instruction: Optional[str] = None,
        response_mime_type: Optional[str] = None,
        preferred_model: Optional[str] = None
    ) -> Optional[str]:
        """Dispatches prompt to models down the ladder until success or complete exhaustion."""
        if not self.client:
            logger.info("[Cascade] No live Gemini API client initialized. Operating in local mode.")
            return None

        execution_order = self._build_execution_order(preferred_model)

        config_params = {}
        if system_instruction:
            config_params["system_instruction"] = system_instruction
        if response_mime_type:
            config_params["response_mime_type"] = response_mime_type

        gen_config = types.GenerateContentConfig(**config_params) if config_params else None

        for model_name in execution_order:
            try:
                logger.info(f"[Cascade] Dispatching payload to model tier: {model_name}")
                response = await asyncio.wait_for(
                    asyncio.to_thread(
                        self.client.models.generate_content,
                        model=model_name,
                        contents=contents,
                        config=gen_config
                    ),
                    timeout=8.0
                )
                if response and response.text:
                    logger.info(f"[Cascade] Execution successful on tier: {model_name}")
                    return response.text
            except asyncio.TimeoutError:
                logger.warning(f"[Cascade] Tier {model_name} timed out (>8s). Cascading down...")
                continue
            except APIError as e:
                if e.code == 429 or "RESOURCE_EXHAUSTED" in str(e):
                    logger.warning(f"[Cascade] Tier {model_name} exhausted (429 Rate Limit). Cascading down...")
                    continue
                elif e.code == 503 or "UNAVAILABLE" in str(e):
                    logger.warning(f"[Cascade] Tier {model_name} temporarily unavailable (503). Cascading down...")
                    continue
                elif e.code == 404 or "NOT_FOUND" in str(e):
                    logger.warning(f"[Cascade] Tier {model_name} not found / deprecated (404). Cascading down...")
                    continue
                logger.error(f"[Cascade] Non-quota API error on {model_name}: {e}")
                continue
            except Exception as e:
                logger.error(f"[Cascade] Unexpected exception on tier {model_name}: {e}")
                continue

        logger.warning("[Cascade] All Gemini cloud tiers exhausted. Triggering local deterministic harness.")
        return None

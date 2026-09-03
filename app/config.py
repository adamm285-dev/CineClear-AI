import os
from pathlib import Path
from typing import Optional, List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings and API credentials configuration."""

    # Gemini AI (High Quota Tier: 1,500 requests/day)
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-3.5-flash"
    GEMINI_FALLBACK_MODELS: list[str] = ["gemini-3.5-flash", "gemini-3.5-flash-lite", "gemini-3.6-flash", "gemini-flash-latest"]

    # Parallel Search API
    PARALLEL_API_KEY: str = ""
    PARALLEL_BASE_URL: str = "https://api.parallel.ai/v1"

    # Judge VIP Access Gate (Protects live uploads without login friction)
    JUDGE_ACCESS_KEY: str = "cineclear-judge-2026"
    REQUIRE_JUDGE_AUTH_FOR_UPLOADS: bool = False

    # Server Settings
    HOST: str = "0.0.0.0"
    PORT: int = 8085
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Storage paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    UPLOAD_DIR: Path = BASE_DIR / "uploads"
    REPORT_OUTPUT_DIR: Path = BASE_DIR / "reports"
    SAMPLE_MEDIA_DIR: Path = BASE_DIR / "sample_media"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    def is_gemini_configured(self) -> bool:
        return bool(self.GEMINI_API_KEY and self.GEMINI_API_KEY.strip() and self.GEMINI_API_KEY != "your_gemini_api_key_here")

    def is_parallel_configured(self) -> bool:
        return bool(self.PARALLEL_API_KEY and self.PARALLEL_API_KEY.strip() and self.PARALLEL_API_KEY != "your_parallel_api_key_here")

    def is_judge_authenticated(self, candidate: Optional[str]) -> bool:
        if not self.REQUIRE_JUDGE_AUTH_FOR_UPLOADS:
            return True
        if not candidate:
            return False
        clean = candidate.strip()
        if clean.lower().startswith("bearer "):
            clean = clean[7:].strip()
        return clean.lower() == self.JUDGE_ACCESS_KEY.strip().lower()


settings = Settings()

# Ensure required directories exist
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
settings.REPORT_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
settings.SAMPLE_MEDIA_DIR.mkdir(parents=True, exist_ok=True)

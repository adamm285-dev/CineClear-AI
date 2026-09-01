import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings and API credentials configuration."""

    # Gemini AI
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.5-pro"

    # Parallel Search API
    PARALLEL_API_KEY: str = ""
    PARALLEL_BASE_URL: str = "https://api.parallel.ai/v1"

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


settings = Settings()

# Ensure required directories exist
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
settings.REPORT_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
settings.SAMPLE_MEDIA_DIR.mkdir(parents=True, exist_ok=True)

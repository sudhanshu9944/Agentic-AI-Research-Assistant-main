"""
Application configuration loaded from environment variables.

Centralizes all settings using python-dotenv for .env file support.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# ──────────────────────────────────────────────
# Load .env from project root
# ──────────────────────────────────────────────
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(_PROJECT_ROOT / ".env")


class Settings:
    """Application settings loaded from environment variables."""

    # OpenRouter
    OPENROUTER_API_KEY: str = os.getenv("GROQ_API_KEY") or os.getenv("OPENROUTER_API_KEY", "")
    OPENROUTER_BASE_URL: str = os.getenv("OPENROUTER_BASE_URL", "https://api.groq.com/openai/v1")

    # Models
    DEFAULT_MODEL: str = os.getenv("DEFAULT_MODEL", "openai/gpt-oss-120b")
    RERANKER_MODEL: str = os.getenv("RERANKER_MODEL", "openai/gpt-oss-20b")
    GROQ_TOKEN_BUDGET: int = int(os.getenv("GROQ_TOKEN_BUDGET", "8000"))

    # Backend
    BACKEND_HOST: str = os.getenv("BACKEND_HOST", "0.0.0.0")
    BACKEND_PORT: int = int(os.getenv("PORT") or os.getenv("BACKEND_PORT") or "8000")

    # App
    APP_NAME: str = os.getenv("APP_NAME", "AI Research Assistant")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() in ("true", "1", "yes")

    # Paths
    PROJECT_ROOT: Path = _PROJECT_ROOT
    REPORTS_DIR: Path = Path(os.getenv("REPORTS_DIR", str(_PROJECT_ROOT / "reports")))
    MEMORY_DIR: Path = Path(os.getenv("MEMORY_DIR", str(_PROJECT_ROOT / "memory")))

    def __init__(self) -> None:
        """Ensure required directories exist."""
        self.REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        self.MEMORY_DIR.mkdir(parents=True, exist_ok=True)

    def validate(self) -> None:
        """Validate that critical settings are present."""
        if not self.OPENROUTER_API_KEY:
            raise ValueError(
                "OPENROUTER_API_KEY (or GROQ_API_KEY) is not set. "
                "Please set it in your .env file or environment."
            )


# Singleton instance
settings = Settings()

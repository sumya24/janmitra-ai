"""Application configuration loaded from environment variables.

All secrets, API keys, model names, and file-handling limits live here so
the rest of the codebase never hardcodes them or reads os.environ directly.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings:
    """Central place for all configuration values used across the app."""

    # Sarvam AI (speech-to-text + translation)
    SARVAM_API_KEY: str = os.getenv("SARVAM_API_KEY", "")
    SARVAM_BASE_URL: str = os.getenv("SARVAM_BASE_URL", "https://api.sarvam.ai")

    # LLM used for complaint summary generation (Sarvam's chat completion API by default,
    # so this can reuse SARVAM_API_KEY if LLM_API_KEY is left unset)
    LLM_API_KEY: str = os.getenv("LLM_API_KEY") or os.getenv("SARVAM_API_KEY", "")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "sarvam-105b")
    # sarvam-105b is a reasoning model: it spends tokens on internal reasoning_content
    # before emitting the final answer, so this needs much more headroom than a plain
    # 1-2 sentence summary would suggest, or the response gets cut off with empty content.
    # reasoning_effort="low" (set at each call site) reduces this on average but is not a
    # hard cap; 1024 was verified to still fail (finish_reason=length) on realistic,
    # slightly longer complaint text, while 4096 reliably completes.
    LLM_MAX_TOKENS: int = int(os.getenv("LLM_MAX_TOKENS", "4096"))
    # The SarvamAI SDK defaults to a 60s read timeout, which a reasoning model can
    # legitimately exceed on longer/harder inputs even at reasoning_effort="low". No
    # value here is guaranteed sufficient for every possible complaint (there's no fixed
    # cap that scales with an unbounded reasoning length) — this just gives slow-but-
    # otherwise-successful calls more room before the client gives up, on top of the
    # non-blocking fallback behavior in NormalizationService and ComplaintAgent.
    LLM_TIMEOUT_SECONDS: float = float(os.getenv("LLM_TIMEOUT_SECONDS", "120"))

    # File storage
    UPLOAD_FOLDER: str = os.getenv("UPLOAD_FOLDER", str(BASE_DIR / "uploads"))
    MAX_PHOTO_SIZE_BYTES: int = 5 * 1024 * 1024  # 5 MB
    ALLOWED_PHOTO_CONTENT_TYPES: tuple[str, ...] = ("image/jpeg", "image/png", "image/jpg")

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'janmitra.db'}")

    # Base URL the Streamlit frontends use to reach the FastAPI backend
    BACKEND_URL: str = os.getenv("BACKEND_URL", "http://localhost:8000")

    # Prompts directory
    PROMPTS_DIR: Path = BASE_DIR / "prompts"

    # Hardcoded identities (no auth in Milestone 1)
    HARDCODED_CITIZEN_ID: str = "citizen_001"
    HARDCODED_WORKER_ID: str = "worker_001"

    # Supported languages: short code -> (display name, Sarvam BCP-47 code)
    SUPPORTED_LANGUAGES: dict[str, dict[str, str]] = {
        "mr": {"name": "Marathi", "bcp47": "mr-IN"},
        "hi": {"name": "Hindi", "bcp47": "hi-IN"},
        "en": {"name": "English", "bcp47": "en-IN"},
    }


settings = Settings()


def get_prompt(filename: str) -> str:
    """Read and return the contents of a prompt file from the prompts directory.

    Args:
        filename: Name of the prompt file, e.g. "summary_prompt.txt".

    Returns:
        The prompt file contents as a string.
    """
    prompt_path = settings.PROMPTS_DIR / filename
    return prompt_path.read_text(encoding="utf-8")


def to_bcp47(language_code: str) -> str:
    """Map a short language code (e.g. "mr") to its Sarvam BCP-47 form (e.g. "mr-IN").

    Args:
        language_code: One of the short codes in SUPPORTED_LANGUAGES, e.g. "mr", "hi", "en".

    Returns:
        The corresponding BCP-47 language code used by the Sarvam AI APIs.

    Raises:
        ValueError: If the language code is not one of the supported languages.
    """
    language = settings.SUPPORTED_LANGUAGES.get(language_code)
    if language is None:
        raise ValueError(f"Unsupported language code: {language_code}")
    return language["bcp47"]

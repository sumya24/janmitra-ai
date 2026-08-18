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

    # Sarvam AI (speech-to-text + translation + text-to-speech)
    SARVAM_API_KEY: str = os.getenv("SARVAM_API_KEY", "")
    SARVAM_BASE_URL: str = os.getenv("SARVAM_BASE_URL", "https://api.sarvam.ai")
    # The `sarvamai` SDK defaults to a 60s httpx timeout when none is passed (see SarvamAI.__init__).
    # A real network hiccup during live testing surfaced as a citizen-facing complaint-creation
    # failure that took ~30s to honestly report itself (a lower-level OS connection-attempt
    # timeout firing before httpx's own 60s ceiling would have) -- every caller of this API
    # (sarvam_client.py, summary_service.py, answer_generation_service.py, normalization_service.py)
    # already falls back gracefully on ANY failure (see each module's own docstring), so shortening
    # this only changes how long a citizen waits before that honest fallback fires, not what
    # happens when it does.
    #
    # Two separate knobs, not one, because the failure observed was specifically a CONNECT timeout
    # (the TCP handshake itself never completed -- genuine network unreachability) -- a completely
    # different phase from "the model is still generating a slow-but-real answer" (a READ timeout,
    # which only starts once a connection already succeeded). sarvam-105b is a reasoning model
    # (see summary_service.py/answer_generation_service.py's own comments on reasoning_effort) that
    # legitimately needs real headroom to finish thinking -- capping THAT at the same short value
    # used for fast STT/translation/TTS calls would turn legitimate slow-but-working answers into
    # unnecessary fallback-to-raw-excerpt failures, trading one problem for a worse one. Verified
    # directly that the `sarvamai` SDK accepts an httpx.Timeout with separate connect/read here
    # (its own type hint only advertises a bare float, but the value is passed straight through to
    # httpx.Client(timeout=...), which httpx itself documents as accepting either).
    SARVAM_CONNECT_TIMEOUT_SECONDS: float = float(os.getenv("SARVAM_CONNECT_TIMEOUT_SECONDS", "10"))
    SARVAM_REQUEST_TIMEOUT_SECONDS: float = float(os.getenv("SARVAM_REQUEST_TIMEOUT_SECONDS", "15"))
    SARVAM_REASONING_READ_TIMEOUT_SECONDS: float = float(os.getenv("SARVAM_REASONING_READ_TIMEOUT_SECONDS", "45"))

    # Ask Sarthi voice assistant TTS (see backend/services/sarvam_client.py's
    # synthesize_speech()) -- one fixed default voice/model for v1, not user-configurable (a
    # cosmetic product decision, not an architectural one -- see the implementation plan).
    TTS_SPEAKER: str = os.getenv("TTS_SPEAKER", "anushka")
    TTS_MODEL: str = os.getenv("TTS_MODEL", "bulbul:v2")

    # LLM used for complaint summary generation (Sarvam's chat completion API by default,
    # so this can reuse SARVAM_API_KEY if LLM_API_KEY is left unset)
    LLM_API_KEY: str = os.getenv("LLM_API_KEY") or os.getenv("SARVAM_API_KEY", "")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "sarvam-105b")
    # sarvam-105b is a reasoning model: it spends tokens on internal reasoning_content
    # before emitting the final answer, so this needs much more headroom than a plain
    # 1-2 sentence summary would suggest, or the response gets cut off with empty content.
    LLM_MAX_TOKENS: int = int(os.getenv("LLM_MAX_TOKENS", "1024"))

    # File storage
    UPLOAD_FOLDER: str = os.getenv("UPLOAD_FOLDER", str(BASE_DIR / "uploads"))
    MAX_PHOTO_SIZE_BYTES: int = 5 * 1024 * 1024  # 5 MB
    ALLOWED_PHOTO_CONTENT_TYPES: tuple[str, ...] = ("image/jpeg", "image/png", "image/jpg")

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'janmitra.db'}")

    # Base URL the Streamlit frontends use to reach the FastAPI backend
    BACKEND_URL: str = os.getenv("BACKEND_URL", "http://localhost:8000")

    # Origins allowed to call the API from a browser (the React dev server, etc.)
    CORS_ORIGINS: list[str] = [
        origin.strip()
        for origin in os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")
        if origin.strip()
    ]

    # Prompts directory
    PROMPTS_DIR: Path = BASE_DIR / "prompts"

    # RAG civic-knowledge-base data (see backend/schemas/rag_knowledge.py) — reference content,
    # not app state, so it lives in flat files here rather than the SQLite DB (see that module's
    # docstring for why).
    RAG_DATA_DIR: Path = BASE_DIR / "data" / "rag_knowledge_base"

    # RAG retrieval config (see backend/services/rag_retriever.py, vector_store.py,
    # embedding_provider.py). RAG_TOP_K/RAG_RELEVANCE_THRESHOLD are tunable via env var without
    # a code change — see docs/ask_janmitra_rag_architecture.md for how these were chosen.
    RAG_EMBEDDINGS_INDEX_PATH: Path = BASE_DIR / "data" / "rag_knowledge_base" / "embeddings" / "index.json"
    RAG_TOP_K: int = int(os.getenv("RAG_TOP_K", "5"))
    # NOTE: this default applies to the LEGACY TF-IDF path only (scores 0.0-~0.4 typically).
    # The active default path (real embeddings) uses RAG_EMBEDDING_RELEVANCE_THRESHOLD below --
    # cosine similarity from a neural sentence embedding model has a very different, much
    # higher-and-narrower score distribution (empirically ~0.7-0.9 for both related and
    # unrelated text in this corpus -- see docs/ask_janmitra_rag_architecture.md's threshold
    # evaluation section for the actual measurements behind this default).
    RAG_RELEVANCE_THRESHOLD: float = float(os.getenv("RAG_RELEVANCE_THRESHOLD", "0.08"))

    # Real-embeddings + ChromaDB retrieval config (see backend/services/embedding_provider.py's
    # SentenceTransformerEmbeddingProvider and vector_store.py's ChromaVectorStore). This is the
    # active default retrieval path as of the RAG embeddings/ChromaDB migration -- see
    # docs/ask_janmitra_rag_architecture.md.
    EMBEDDING_MODEL_NAME: str = os.getenv("EMBEDDING_MODEL_NAME", "intfloat/multilingual-e5-small")

    # Ask Sarthi image understanding (see backend/services/vision_service.py). A small local
    # vision-language model, not a hosted vendor -- Sarvam has no vision capability, and the user
    # chose to avoid adding a new AI vendor/API key for this feature.
    VISION_MODEL_NAME: str = os.getenv("VISION_MODEL_NAME", "vikhyatk/moondream2")
    CHROMA_PERSIST_DIR: Path = Path(os.getenv("CHROMA_PERSIST_DIR", str(BASE_DIR / "data" / "rag_knowledge_base" / "chroma")))
    CHROMA_COLLECTION_NAME: str = os.getenv("CHROMA_COLLECTION_NAME", "janmitra_knowledge")
    # Chosen from two rounds of actual measurement, not a round-number guess -- see
    # docs/ask_janmitra_rag_architecture.md's threshold-calibration section for the full data.
    #
    # Round 1 (raw/unfiltered search, no category or location restriction): this model's cosine
    # similarity scores for this corpus cluster narrowly (~0.72-0.85) regardless of true
    # relevance -- "new electricity connection" (must be REJECTED) scored 0.82-0.83, HIGHER than
    # genuinely unrelated gibberish (~0.80). A flat threshold cannot separate relevant from
    # irrelevant text in this regime; a global cutoff alone is not a safe hallucination guard.
    #
    # Round 2 (realistic: category + location filter applied first, exactly as RagRetriever.
    # retrieve() always does in production), across TWO categories to avoid tuning on one:
    #   STREETLIGHTS+Mohali: genuine paraphrases ("The light outside my house has stopped
    #     working" / "There is no functioning street light near me" / "My road lamp is broken")
    #     scored >=0.803; off-topic/gibberish probes run through the SAME filter ("...chocolate
    #     cake" 0.746-0.750, "...capital of France?" 0.723-0.741, "xyzzy plugh..." 0.766-0.780)
    #     stayed <=0.780.
    #   ROADS_POTHOLES+Mohali: genuine paraphrases ("road has a large pothole" top=0.820,
    #     "there is a deep hole in the road" top=0.794) vs. the same three off-topic/gibberish
    #     probes (cake <=0.755, capital of France <=0.739, gibberish <=0.782).
    # An initial round-2 pass tried 0.80 -- it cleanly separated STREETLIGHTS, but rejected the
    # required ROADS_POTHOLES paraphrase "there is a deep hole in the road" (0.794 < 0.80), a
    # real measured false negative on one of the spec's mandatory paraphrase examples. 0.79 is
    # the threshold actually used: it still rejects every off-topic/gibberish probe measured in
    # both categories (max 0.782) while keeping every genuine paraphrase tested in both (min
    # 0.794) -- a clean, if narrow (0.782 vs 0.794), separation band.
    #
    # Conclusion, stated honestly: this threshold is a real, measured, effective filter WHEN
    # metadata filtering (category + location) has already restricted the candidate pool -- which
    # is the only way it is ever used in production. It is NOT, by itself, a reliable filter over
    # an unrestricted corpus (round 1). The primary hallucination-prevention mechanisms remain (1)
    # the intent classifier's explicit out-of-scope detection (electricity, new-connection, etc.,
    # which never reach the retriever at all) and (2) category+location metadata filtering applied
    # before similarity ranking -- this threshold is a secondary, but now-verified-effective,
    # safeguard on top of those, not a replacement for them. The separation margin (~0.01-0.03) is
    # narrow enough that a genuinely borderline real question could go either way -- documented as
    # a known limitation, not hidden (see docs/ask_janmitra_rag_architecture.md).
    RAG_EMBEDDING_RELEVANCE_THRESHOLD: float = float(os.getenv("RAG_EMBEDDING_RELEVANCE_THRESHOLD", "0.79"))

    # Hardcoded identities (kept only for the legacy Streamlit frontends, which
    # predate real auth and are superseded by the React app + JWT login below)
    HARDCODED_CITIZEN_ID: str = "citizen_001"
    HARDCODED_WORKER_ID: str = "worker_001"

    # Auth (JWT, HS256, implemented with the stdlib only — see services/auth_service.py)
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "")
    JWT_EXPIRE_MINUTES: int = int(os.getenv("JWT_EXPIRE_MINUTES", "1440"))  # 24h

    # Rate limiting (see backend/services/rate_limiter.py, backend/deps.py's
    # require_login_rate_limit/require_ai_rate_limit) -- a small, in-process, stdlib-only sliding
    # window, matching this codebase's existing preference for hand-rolled-over-new-dependency
    # (see auth_service.py's own docstring on why JWT is hand-rolled here). Protects POST
    # /auth/login (brute-force) and the three POST /ask-janmitra* endpoints (expensive Sarvam/LLM/
    # vision calls) -- see docs/RATE_LIMITING.md for the full design and its single-process
    # limitation.
    #
    # LOGIN: keyed per client IP, generous enough that no real login flow ever trips it (one
    # attempt, or a couple of role-switching demo logins in the same minute) while still capping a
    # brute-force script at a small, fixed number of guesses per minute.
    LOGIN_RATE_LIMIT: int = int(os.getenv("LOGIN_RATE_LIMIT", "5"))
    LOGIN_RATE_LIMIT_WINDOW_SECONDS: int = int(os.getenv("LOGIN_RATE_LIMIT_WINDOW_SECONDS", "60"))
    # AI: keyed per authenticated user id, sized against the real measured shape of a normal Ask
    # Sarthi turn (a location clarification round-trip alone is 2 calls; a complaint-confirmation
    # round-trip is another 2) -- 10/min gives a normal demo conversation (several exchanges) 3-4x
    # headroom while still catching a rapid-fire abuse script hammering the paid Sarvam API.
    AI_RATE_LIMIT: int = int(os.getenv("AI_RATE_LIMIT", "10"))
    AI_RATE_LIMIT_WINDOW_SECONDS: int = int(os.getenv("AI_RATE_LIMIT_WINDOW_SECONDS", "60"))
    # General baseline, applied to every route except /health by backend/middleware.py's
    # GeneralRateLimitMiddleware -- a safety net against scripted abuse/scraping across the whole
    # API, on top of (not instead of) LOGIN_RATE_LIMIT/AI_RATE_LIMIT's own stricter limits.
    # Generous: a real user clicking through the app (loading a dashboard, filing a complaint,
    # paging through workers) never comes close, verified live -- see docs/RATE_LIMITING.md.
    GENERAL_RATE_LIMIT: int = int(os.getenv("GENERAL_RATE_LIMIT", "60"))
    GENERAL_RATE_LIMIT_WINDOW_SECONDS: int = int(os.getenv("GENERAL_RATE_LIMIT_WINDOW_SECONDS", "60"))
    # Whether to trust the reverse proxy's X-Forwarded-For for the login rate limiter's per-IP
    # key, instead of the raw TCP peer address. Safe to enable ONLY when every request is
    # guaranteed to have passed through a reverse proxy that sets this header itself (this
    # project's production Caddy does, and the backend container publishes no port of its own --
    # see docker-compose.prod.yml) -- an attacker who can reach the backend directly could
    # otherwise spoof this header to bypass or misattribute the limit. Off by default (local dev
    # has no reverse proxy in front, so the raw TCP peer IS the real client); set true only in the
    # production environment that actually has Caddy in front (see docker-compose.prod.yml, which
    # sets this).
    TRUST_PROXY_HEADERS: bool = os.getenv("TRUST_PROXY_HEADERS", "false").strip().lower() == "true"

    # LangSmith observability (see backend/services/observability/tracing.py and
    # docs/ask_janmitra_langsmith_observability.md) -- a pure observability layer around the
    # existing LangGraph/RAG pipeline; OFF by default, and the app must behave identically
    # whether or not it's configured (see that doc's "failure behavior" section). Tracing is
    # only actually attempted when BOTH LANGSMITH_TRACING is true AND an API key is set --
    # matches SarvamClient's own "warn, don't require" pattern for optional external services.
    LANGSMITH_TRACING: bool = os.getenv("LANGSMITH_TRACING", "false").strip().lower() == "true"
    LANGSMITH_API_KEY: str = os.getenv("LANGSMITH_API_KEY", "")
    LANGSMITH_ENDPOINT: str = os.getenv("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com")
    LANGSMITH_PROJECT: str = os.getenv("LANGSMITH_PROJECT", "jansarthi-ai")
    # Optional deep-link template for the Admin dashboard's "View Trace" button, with a
    # "{trace_id}" placeholder, e.g.
    # "https://smith.langchain.com/o/<your-org-id>/projects/p/<project>/r/{trace_id}" -- copy the
    # prefix from your own LangSmith project's URL in the LangSmith UI. Left blank, trace IDs are
    # still stored and shown but without a clickable link (deliberately not auto-resolved via the
    # LangSmith API -- that would be a network call on the admin dashboard's read path).
    LANGSMITH_TRACE_URL_TEMPLATE: str = os.getenv("LANGSMITH_TRACE_URL_TEMPLATE", "")
    # LangSmith Annotation Queue every "insufficient_knowledge"/out-of-scope Ask Sarthi trace is
    # routed into for human review (see tracing.py's enqueue_for_review()) -- a knowledge-base-gap
    # backlog, not a moderation queue. Created automatically on first use if it doesn't exist yet.
    LANGSMITH_REVIEW_QUEUE_NAME: str = os.getenv("LANGSMITH_REVIEW_QUEUE_NAME", "jansarthi-ai-knowledge-gaps")

    # Supported languages: short code -> (display name, Sarvam BCP-47 code)
    SUPPORTED_LANGUAGES: dict[str, dict[str, str]] = {
        "mr": {"name": "Marathi", "bcp47": "mr-IN"},
        "hi": {"name": "Hindi", "bcp47": "hi-IN"},
        "en": {"name": "English", "bcp47": "en-IN"},
        "or": {"name": "Odia", "bcp47": "od-IN"},
        "gu": {"name": "Gujarati", "bcp47": "gu-IN"},
        "bn": {"name": "Bengali", "bcp47": "bn-IN"},
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

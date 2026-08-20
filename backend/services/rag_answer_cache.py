"""Caches previously-LLM-generated "Ask Sarthi" answers, keyed by (question text, language,
resolved retrieval context) -- see models.RagAnswerCache's own docstring for the full rationale
and why the retrieval context (service category/city/state) is part of the key, not just the
question text and language.

Mirrors complaint_translation_cache.py's own shape deliberately: same "look up, on a miss ask the
caller to compute it, then store" flow, same reasoning (the same question/context combination is
only ever sent to the LLM once, not on every ask).
"""

import hashlib
import logging

from sqlalchemy.orm import Session

from backend.models import RagAnswerCache

logger = logging.getLogger(__name__)


def _normalize_question(question_text: str) -> str:
    """Lowercased, whitespace-collapsed -- so "How long does a streetlight repair take?" and
    "how long does a streetlight repair take?" (or with stray double spaces) hit the same cache
    entry, without attempting any deeper paraphrase-matching (out of scope -- see this module's
    own docstring: exact-repeat questions are the target, not near-duplicates)."""
    return " ".join(question_text.strip().lower().split())


def _cache_key(
    question_text: str,
    language_code: str,
    service_category: str | None,
    city: str | None,
    state: str | None,
) -> str:
    normalized = _normalize_question(question_text)
    parts = [normalized, language_code, service_category or "", city or "", state or ""]
    return hashlib.sha256("\x1f".join(parts).encode("utf-8")).hexdigest()


def get_cached_answer(
    db: Session,
    question_text: str,
    language_code: str,
    service_category: str | None,
    city: str | None,
    state: str | None,
) -> str | None:
    """Returns the cached answer text for this exact (question, language, context) combination,
    or None on a cache miss -- never raises, a cache lookup must never be why a request fails."""
    key = _cache_key(question_text, language_code, service_category, city, state)
    row = db.query(RagAnswerCache).filter(RagAnswerCache.cache_key == key).first()
    return row.answer_text if row is not None else None


def store_answer(
    db: Session,
    question_text: str,
    language_code: str,
    service_category: str | None,
    city: str | None,
    state: str | None,
    answer_text: str,
) -> None:
    """Caches a genuinely LLM-generated answer -- caller (rag_flow_node) is responsible for only
    calling this when the answer actually came from the LLM, never the no-LLM-available fallback
    template (see this module's own docstring for why)."""
    key = _cache_key(question_text, language_code, service_category, city, state)
    existing = db.query(RagAnswerCache).filter(RagAnswerCache.cache_key == key).first()
    if existing is not None:
        # Already cached (a concurrent request beat this one to it) -- nothing to do, the
        # existing row already has a real, genuinely LLM-generated answer.
        return
    db.add(
        RagAnswerCache(
            cache_key=key,
            question_text=_normalize_question(question_text),
            language_code=language_code,
            service_category=service_category,
            location_city=city,
            location_state=state,
            answer_text=answer_text,
        )
    )
    db.commit()
    logger.info("Cached RAG answer (language=%s, category=%s, city=%s)", language_code, service_category, city)

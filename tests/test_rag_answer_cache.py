"""Unit tests for the RAG answer cache -- mirrors test_complaint_translation_cache.py's own shape
deliberately, since this module follows the exact same "look up, on a miss let the caller compute
it, then store" pattern for the same reason (the same question/language/context combination is
only ever sent to the LLM once, not on every ask)."""

from backend.models import RagAnswerCache
from backend.services.rag_answer_cache import get_cached_answer, store_answer


def test_cache_miss_returns_none(db_session):
    db = db_session()
    assert get_cached_answer(db, "How long does a streetlight repair take?", "en", "STREETLIGHTS", None, None) is None


def test_store_then_get_round_trips(db_session):
    db = db_session()
    store_answer(db, "How long does a streetlight repair take?", "en", "STREETLIGHTS", "Bengaluru", "Karnataka", "7-10 days.")

    result = get_cached_answer(db, "How long does a streetlight repair take?", "en", "STREETLIGHTS", "Bengaluru", "Karnataka")

    assert result == "7-10 days."
    assert db.query(RagAnswerCache).count() == 1


def test_lookup_is_case_and_whitespace_insensitive():
    """"How long...?" and "how   long...?" (extra spaces, different case) must hit the same
    cached entry -- citizens don't retype a starter question with perfectly identical casing/
    spacing every time."""
    from backend.services.rag_answer_cache import _cache_key

    key1 = _cache_key("How long does a streetlight repair take?", "en", "STREETLIGHTS", None, None)
    key2 = _cache_key("  how   LONG does a streetlight repair take?  ", "en", "STREETLIGHTS", None, None)
    assert key1 == key2


def test_same_question_different_city_does_not_collide(db_session):
    """The core safety property this cache exists to protect: the SAME question text, asked with
    a DIFFERENT resolved city, must never return the wrong city's cached answer."""
    db = db_session()
    store_answer(db, "How long does a streetlight repair take?", "en", "STREETLIGHTS", "Bengaluru", "Karnataka", "Bengaluru answer: 7-10 days.")
    store_answer(db, "How long does a streetlight repair take?", "en", "STREETLIGHTS", "Mohali", "Punjab", "Mohali answer: different SLA.")

    bengaluru_result = get_cached_answer(db, "How long does a streetlight repair take?", "en", "STREETLIGHTS", "Bengaluru", "Karnataka")
    mohali_result = get_cached_answer(db, "How long does a streetlight repair take?", "en", "STREETLIGHTS", "Mohali", "Punjab")
    no_city_result = get_cached_answer(db, "How long does a streetlight repair take?", "en", "STREETLIGHTS", None, None)

    assert bengaluru_result == "Bengaluru answer: 7-10 days."
    assert mohali_result == "Mohali answer: different SLA."
    assert no_city_result is None  # a third, distinct (no-city) context was never cached
    assert db.query(RagAnswerCache).count() == 2


def test_same_question_different_language_does_not_collide(db_session):
    db = db_session()
    store_answer(db, "How long does a streetlight repair take?", "en", "STREETLIGHTS", None, None, "English answer.")
    store_answer(db, "How long does a streetlight repair take?", "hi", "STREETLIGHTS", None, None, "हिंदी उत्तर.")

    assert get_cached_answer(db, "How long does a streetlight repair take?", "en", "STREETLIGHTS", None, None) == "English answer."
    assert get_cached_answer(db, "How long does a streetlight repair take?", "hi", "STREETLIGHTS", None, None) == "हिंदी उत्तर."


def test_storing_the_same_key_twice_does_not_duplicate_or_error(db_session):
    """A concurrent request beating this one to the cache write must never crash or create a
    second row for the same (question, language, context) combination."""
    db = db_session()
    store_answer(db, "Same question", "en", "WASTE_SANITATION", None, None, "First answer.")
    store_answer(db, "Same question", "en", "WASTE_SANITATION", None, None, "Second answer (should be ignored).")

    assert db.query(RagAnswerCache).count() == 1
    assert get_cached_answer(db, "Same question", "en", "WASTE_SANITATION", None, None) == "First answer."

"""Unit tests for the complaint translation cache."""

from datetime import datetime, timezone
from unittest.mock import Mock

from backend.models import Complaint, ComplaintTranslation
from backend.services.complaint_translation_cache import get_display_text_and_summary
from backend.services.sarvam_client import AIServiceError


def _make_complaint(db) -> Complaint:
    complaint = Complaint(
        citizen_id="1",
        original_text="कचरा उचलला नाही",
        original_language="mr",
        translated_text="Garbage has not been collected.",
        summary="Garbage complaint.",
        status="open",
        created_at=datetime.now(timezone.utc),
    )
    db.add(complaint)
    db.commit()
    db.refresh(complaint)
    return complaint


def test_english_never_touches_translation_service_or_cache(db_session):
    """Requesting English returns the stored text and summary directly — no translation, no cache row."""
    db = db_session()
    complaint = _make_complaint(db)
    fake_translation_service = Mock()

    text, summary = get_display_text_and_summary(db, complaint, "en", fake_translation_service)

    assert text == "Garbage has not been collected."
    assert summary == "Garbage complaint."
    fake_translation_service.to_language.assert_not_called()
    assert db.query(ComplaintTranslation).count() == 0


def test_cache_miss_translates_and_stores_both_text_and_summary(db_session):
    """A first view in a new language translates and caches both the text and the summary."""
    db = db_session()
    complaint = _make_complaint(db)
    fake_translation_service = Mock()
    fake_translation_service.to_language.side_effect = [
        "कचरा एकत्र नहीं किया गया।",
        "कचरे की शिकायत।",
    ]

    text, summary = get_display_text_and_summary(db, complaint, "hi", fake_translation_service)

    assert text == "कचरा एकत्र नहीं किया गया।"
    assert summary == "कचरे की शिकायत।"
    assert fake_translation_service.to_language.call_count == 2
    fake_translation_service.to_language.assert_any_call("Garbage has not been collected.", "hi")
    fake_translation_service.to_language.assert_any_call("Garbage complaint.", "hi")

    cached = db.query(ComplaintTranslation).filter_by(complaint_id=complaint.id, language_code="hi").first()
    assert cached is not None
    assert cached.translated_text == "कचरा एकत्र नहीं किया गया।"
    assert cached.translated_summary == "कचरे की शिकायत।"


def test_cache_hit_skips_translation_service(db_session):
    """A second view in the same language reuses the cached row instead of translating again."""
    db = db_session()
    complaint = _make_complaint(db)
    fake_translation_service = Mock()
    fake_translation_service.to_language.side_effect = ["কचরা সংগ্রহ করা হয়নি।", "কচরা অভিযোগ।"]

    first = get_display_text_and_summary(db, complaint, "bn", fake_translation_service)
    second = get_display_text_and_summary(db, complaint, "bn", fake_translation_service)

    assert first == second == ("কचরা সংগ্রহ করা হয়নি।", "কচরা অভিযোগ।")
    assert fake_translation_service.to_language.call_count == 2  # not called again on the second view


def test_cache_miss_failure_is_not_cached(db_session):
    """A failed translation isn't stored, so the next view retries instead of staying stuck."""
    db = db_session()
    complaint = _make_complaint(db)
    fake_translation_service = Mock()
    fake_translation_service.to_language.side_effect = AIServiceError("Sarvam is down.")

    try:
        get_display_text_and_summary(db, complaint, "gu", fake_translation_service)
        assert False, "expected AIServiceError to propagate"
    except AIServiceError:
        pass

    assert db.query(ComplaintTranslation).count() == 0


def test_row_missing_translated_summary_backfills_instead_of_reusing_stale_cache(db_session):
    """A cache row from before translated_summary existed (nullable, see models.py) is treated
    as incomplete and re-translated, rather than silently returning a null summary forever."""
    db = db_session()
    complaint = _make_complaint(db)
    db.add(
        ComplaintTranslation(
            complaint_id=complaint.id,
            language_code="mr",
            translated_text="जुना अनुवाद",
            translated_summary=None,
        )
    )
    db.commit()

    fake_translation_service = Mock()
    fake_translation_service.to_language.side_effect = ["कचरा गोळा केला नाही.", "कचऱ्याची तक्रार."]

    text, summary = get_display_text_and_summary(db, complaint, "mr", fake_translation_service)

    assert text == "कचरा गोळा केला नाही."
    assert summary == "कचऱ्याची तक्रार."
    assert fake_translation_service.to_language.call_count == 2

"""Unit tests for the complaint update translation cache -- mirrors
test_complaint_translation_cache.py's own shape deliberately, same reasoning applied to
worker-authored update text instead of complaint text."""

from datetime import datetime, timezone
from unittest.mock import Mock

from backend.models import ComplaintUpdate, ComplaintUpdateTranslation, User
from backend.services.auth_service import hash_password
from backend.services.complaint_update_translation_cache import get_display_text
from backend.services.sarvam_client import AIServiceError


def _make_worker(db, phone: str, preferred_language: str) -> User:
    worker = User(
        full_name="Test Worker", phone=phone, password_hash=hash_password("secret123"),
        role="worker", preferred_language=preferred_language, ward="Test Ward",
    )
    db.add(worker)
    db.commit()
    db.refresh(worker)
    return worker


def _make_update(db, worker_id: int, text: str) -> ComplaintUpdate:
    update = ComplaintUpdate(
        complaint_id=1, worker_id=worker_id, update_type="INITIAL_ASSESSMENT",
        text=text, created_at=datetime.now(timezone.utc),
    )
    db.add(update)
    db.commit()
    db.refresh(update)
    return update


def test_cache_miss_translates_with_auto_detected_source_and_stores_it(db_session):
    """No stored/approximated source language -- the translation service is asked to
    auto-detect the source, regardless of the authoring worker's own language preference."""
    db = db_session()
    worker = _make_worker(db, "9800000502", "mr")
    update = _make_update(db, worker.id, "Assessed the issue on site; proceeding with resolution.")
    fake_translation_service = Mock()
    fake_translation_service.translate_auto_detecting_source.return_value = "साइट का निरीक्षण किया; समाधान जारी है।"

    text = get_display_text(db, update, "hi", fake_translation_service)

    assert text == "साइट का निरीक्षण किया; समाधान जारी है।"
    fake_translation_service.translate_auto_detecting_source.assert_called_once_with(
        "Assessed the issue on site; proceeding with resolution.", "hi"
    )
    cached = db.query(ComplaintUpdateTranslation).filter_by(complaint_update_id=update.id, language_code="hi").first()
    assert cached is not None
    assert cached.translated_text == "साइट का निरीक्षण किया; समाधान जारी है।"


def test_cache_hit_skips_translation_service(db_session):
    db = db_session()
    worker = _make_worker(db, "9800000503", "mr")
    update = _make_update(db, worker.id, "साइटवर तपासणी केली.")
    fake_translation_service = Mock()
    fake_translation_service.translate_auto_detecting_source.return_value = "साइट का निरीक्षण किया।"

    first = get_display_text(db, update, "hi", fake_translation_service)
    second = get_display_text(db, update, "hi", fake_translation_service)

    assert first == second == "साइट का निरीक्षण किया।"
    fake_translation_service.translate_auto_detecting_source.assert_called_once()  # not called again on the second view


def test_cache_miss_failure_is_not_cached(db_session):
    db = db_session()
    worker = _make_worker(db, "9800000504", "mr")
    update = _make_update(db, worker.id, "साइटवर तपासणी केली.")
    fake_translation_service = Mock()
    fake_translation_service.translate_auto_detecting_source.side_effect = AIServiceError("Sarvam is down.")

    try:
        get_display_text(db, update, "hi", fake_translation_service)
        assert False, "expected AIServiceError to propagate"
    except AIServiceError:
        pass

    assert db.query(ComplaintUpdateTranslation).count() == 0


def test_missing_worker_still_translates(db_session):
    """A worker row that no longer exists (deleted account, orphaned FK) must not crash the
    lookup -- there's no worker lookup at all any more, so this is a non-event."""
    db = db_session()
    update = ComplaintUpdate(
        complaint_id=1, worker_id=999999, update_type="COMPLETION",
        text="Resolved.", created_at=datetime.now(timezone.utc),
    )
    db.add(update)
    db.commit()
    db.refresh(update)
    fake_translation_service = Mock()
    fake_translation_service.translate_auto_detecting_source.return_value = "समाधान झाले."

    text = get_display_text(db, update, "mr", fake_translation_service)

    assert text == "समाधान झाले."
    fake_translation_service.translate_auto_detecting_source.assert_called_once_with("Resolved.", "mr")

"""Integration tests for the /complaints API endpoints."""

from unittest.mock import Mock

import backend.routes.complaints as complaints_module
from backend.models import Complaint
from backend.services.sarvam_client import AIServiceError


def _fake_agent_create_complaint(db, citizen_id, language_code, text, audio_bytes, photo_path):
    """Stand in for ComplaintAgent.create_complaint without calling any external API."""
    complaint = Complaint(
        citizen_id=citizen_id,
        original_text=text or "(voice complaint)",
        original_language=language_code,
        translated_text=f"[en] {text or 'voice complaint'}",
        summary="A short summary.",
        photo_path=photo_path,
        status="open",
    )
    db.add(complaint)
    db.commit()
    db.refresh(complaint)
    return complaint


def test_create_complaint_with_text_succeeds(client, monkeypatch):
    """POST /complaints with typed text should store and return a new complaint."""
    monkeypatch.setattr(
        complaints_module, "_agent", Mock(create_complaint=_fake_agent_create_complaint)
    )

    response = client.post(
        "/complaints",
        data={"citizen_id": "citizen_001", "language": "mr", "text": "कचरा उचलला नाही"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["citizen_id"] == "citizen_001"
    assert body["original_language"] == "mr"
    assert body["status"] == "open"
    assert body["translated_text"] == "[en] कचरा उचलला नाही"


def test_create_complaint_without_text_or_audio_returns_400(client):
    """POST /complaints with neither text nor audio should be rejected."""
    response = client.post("/complaints", data={"citizen_id": "citizen_001", "language": "en"})
    assert response.status_code == 400


def test_create_complaint_unsupported_language_returns_400(client):
    """POST /complaints with an unsupported language code should be rejected."""
    response = client.post(
        "/complaints",
        data={"citizen_id": "citizen_001", "language": "fr", "text": "Bonjour"},
    )
    assert response.status_code == 400


def test_create_complaint_ai_failure_returns_502(client, monkeypatch):
    """If the AI pipeline fails, the API should return a clear 502, not crash."""

    def _raise(*args, **kwargs):
        raise AIServiceError("Sarvam AI is not configured.")

    monkeypatch.setattr(complaints_module, "_agent", Mock(create_complaint=_raise))

    response = client.post(
        "/complaints",
        data={"citizen_id": "citizen_001", "language": "mr", "text": "कचरा उचलला नाही"},
    )

    assert response.status_code == 502


def test_list_complaints_translates_on_read(client, monkeypatch, db_session):
    """GET /complaints?lang=hi should translate stored English text on read only."""
    db = db_session()
    complaint = Complaint(
        citizen_id="citizen_001",
        original_text="कचरा उचलला नाही",
        original_language="mr",
        translated_text="Garbage has not been collected.",
        summary="Garbage not collected.",
        photo_path=None,
        status="open",
    )
    db.add(complaint)
    db.commit()
    db.close()

    fake_translation_service = Mock()
    fake_translation_service.to_language.return_value = "कचरा एकत्र नहीं किया गया।"
    monkeypatch.setattr(complaints_module, "_translation_service", fake_translation_service)

    response = client.get("/complaints", params={"lang": "hi"})

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["display_text"] == "कचरा एकत्र नहीं किया गया।"
    # The stored English text is never mutated by on-read translation.
    assert body[0]["translated_text"] == "Garbage has not been collected."


def test_list_complaints_falls_back_to_english_on_translation_failure(client, monkeypatch, db_session):
    """If on-read translation fails, the API should still return the English text."""
    db = db_session()
    complaint = Complaint(
        citizen_id="citizen_001",
        original_text="Garbage issue",
        original_language="en",
        translated_text="Garbage has not been collected.",
        summary="Garbage not collected.",
        photo_path=None,
        status="open",
    )
    db.add(complaint)
    db.commit()
    db.close()

    fake_translation_service = Mock()
    fake_translation_service.to_language.side_effect = AIServiceError("translation down")
    monkeypatch.setattr(complaints_module, "_translation_service", fake_translation_service)

    response = client.get("/complaints", params={"lang": "hi"})

    assert response.status_code == 200
    assert response.json()[0]["display_text"] == "Garbage has not been collected."


def test_update_status_marks_complaint_resolved(client, db_session):
    """PATCH /complaints/{id} should update the status and persist it."""
    db = db_session()
    complaint = Complaint(
        citizen_id="citizen_001",
        original_text="Garbage issue",
        original_language="en",
        translated_text="Garbage has not been collected.",
        summary="Garbage not collected.",
        photo_path=None,
        status="open",
    )
    db.add(complaint)
    db.commit()
    db.refresh(complaint)
    complaint_id = complaint.id
    db.close()

    response = client.patch(f"/complaints/{complaint_id}", json={"status": "resolved"})

    assert response.status_code == 200
    assert response.json()["status"] == "resolved"


def test_update_status_invalid_value_returns_400(client, db_session):
    """PATCH with a status other than open/resolved should be rejected."""
    db = db_session()
    complaint = Complaint(
        citizen_id="citizen_001",
        original_text="Garbage issue",
        original_language="en",
        translated_text="Garbage has not been collected.",
        summary="Garbage not collected.",
        photo_path=None,
        status="open",
    )
    db.add(complaint)
    db.commit()
    db.refresh(complaint)
    complaint_id = complaint.id
    db.close()

    response = client.patch(f"/complaints/{complaint_id}", json={"status": "archived"})
    assert response.status_code == 400


def test_update_status_missing_complaint_returns_404(client):
    """PATCH on a nonexistent complaint id should return 404."""
    response = client.patch("/complaints/999999", json={"status": "resolved"})
    assert response.status_code == 404

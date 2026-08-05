"""Integration tests for the /complaints API endpoints.

All endpoints now require authentication and are scoped by role (see
backend/deps.py): citizens see only their own complaints, workers see only
their ward's complaints, and admins see everything.
"""

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


def test_create_complaint_with_text_succeeds(client, monkeypatch, make_citizen):
    """POST /complaints with typed text should store and return a new complaint."""
    monkeypatch.setattr(
        complaints_module, "_agent", Mock(create_complaint=_fake_agent_create_complaint)
    )
    token, user = make_citizen(phone="9000000001")

    response = client.post(
        "/complaints",
        headers={"Authorization": f"Bearer {token}"},
        data={"language": "mr", "text": "कचरा उचलला नाही"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["citizen_id"] == str(user["id"])
    assert body["original_language"] == "mr"
    assert body["status"] == "open"
    assert body["translated_text"] == "[en] कचरा उचलला नाही"


def test_create_complaint_requires_authentication(client):
    response = client.post("/complaints", data={"language": "en", "text": "hello"})
    assert response.status_code == 401


def test_worker_cannot_create_complaint(client, make_worker):
    """Only citizens may submit complaints — not workers, not admins."""
    token, _user = make_worker(phone="9000000002")
    response = client.post(
        "/complaints", headers={"Authorization": f"Bearer {token}"}, data={"language": "en", "text": "hello"}
    )
    assert response.status_code == 403


def test_create_complaint_without_text_or_audio_returns_400(client, make_citizen):
    token, _user = make_citizen(phone="9000000001")
    response = client.post(
        "/complaints", headers={"Authorization": f"Bearer {token}"}, data={"language": "en"}
    )
    assert response.status_code == 400


def test_create_complaint_unsupported_language_returns_400(client, make_citizen):
    token, _user = make_citizen(phone="9000000001")
    response = client.post(
        "/complaints",
        headers={"Authorization": f"Bearer {token}"},
        data={"language": "fr", "text": "Bonjour"},
    )
    assert response.status_code == 400


def test_create_complaint_ai_failure_returns_502(client, monkeypatch, make_citizen):
    """If the AI pipeline fails, the API should return a clear 502, not crash."""

    def _raise(*args, **kwargs):
        raise AIServiceError("Sarvam AI is not configured.")

    monkeypatch.setattr(complaints_module, "_agent", Mock(create_complaint=_raise))
    token, _user = make_citizen(phone="9000000001")

    response = client.post(
        "/complaints",
        headers={"Authorization": f"Bearer {token}"},
        data={"language": "mr", "text": "कचरा उचलला नाही"},
    )
    assert response.status_code == 502


def test_citizen_only_sees_own_complaints(client, make_citizen, db_session):
    token_a, user_a = make_citizen(phone="9000000001")
    token_b, user_b = make_citizen(phone="9000000002")

    db = db_session()
    db.add(Complaint(
        citizen_id=str(user_a["id"]), original_text="a", original_language="en",
        translated_text="Complaint from citizen A", summary="a", status="open",
    ))
    db.add(Complaint(
        citizen_id=str(user_b["id"]), original_text="b", original_language="en",
        translated_text="Complaint from citizen B", summary="b", status="open",
    ))
    db.commit()
    db.close()

    response = client.get("/complaints", headers={"Authorization": f"Bearer {token_a}"})
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["translated_text"] == "Complaint from citizen A"


def test_worker_only_sees_own_ward(client, make_worker, db_session):
    token, worker = make_worker(phone="9000000002", ward="Ward 14")

    db = db_session()
    db.add(Complaint(
        citizen_id="1", original_text="a", original_language="en",
        translated_text="In Ward 14", summary="a", ward="Ward 14", status="open",
    ))
    db.add(Complaint(
        citizen_id="1", original_text="b", original_language="en",
        translated_text="In Ward 9", summary="b", ward="Ward 9", status="open",
    ))
    db.commit()
    db.close()

    response = client.get("/complaints", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["translated_text"] == "In Ward 14"


def test_admin_sees_every_complaint(client, make_admin, db_session):
    make_admin(phone="9999999999", password="adminpass")
    login = client.post("/auth/login", json={"phone": "9999999999", "password": "adminpass"})
    admin_token = login.json()["access_token"]

    db = db_session()
    db.add(Complaint(
        citizen_id="1", original_text="a", original_language="en",
        translated_text="Ward 14 complaint", summary="a", ward="Ward 14", status="open",
    ))
    db.add(Complaint(
        citizen_id="2", original_text="b", original_language="en",
        translated_text="Ward 9 complaint", summary="b", ward="Ward 9", status="open",
    ))
    db.commit()
    db.close()

    response = client.get("/complaints", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_list_complaints_translates_on_read(client, monkeypatch, make_admin, db_session):
    """GET /complaints?lang=hi should translate stored English text on read only."""
    make_admin(phone="9999999999", password="adminpass")
    login = client.post("/auth/login", json={"phone": "9999999999", "password": "adminpass"})
    admin_token = login.json()["access_token"]

    db = db_session()
    db.add(Complaint(
        citizen_id="1", original_text="कचरा उचलला नाही", original_language="mr",
        translated_text="Garbage has not been collected.", summary="Garbage not collected.",
        status="open",
    ))
    db.commit()
    db.close()

    fake_translation_service = Mock()
    fake_translation_service.to_language.return_value = "कचरा एकत्र नहीं किया गया।"
    monkeypatch.setattr(complaints_module, "_translation_service", fake_translation_service)

    response = client.get("/complaints", params={"lang": "hi"}, headers={"Authorization": f"Bearer {admin_token}"})

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["display_text"] == "कचरा एकत्र नहीं किया गया।"
    assert body[0]["translated_text"] == "Garbage has not been collected."


def test_list_complaints_falls_back_to_english_on_translation_failure(client, monkeypatch, make_admin, db_session):
    """If on-read translation fails, the API should still return the English text."""
    make_admin(phone="9999999999", password="adminpass")
    login = client.post("/auth/login", json={"phone": "9999999999", "password": "adminpass"})
    admin_token = login.json()["access_token"]

    db = db_session()
    db.add(Complaint(
        citizen_id="1", original_text="Garbage issue", original_language="en",
        translated_text="Garbage has not been collected.", summary="Garbage not collected.",
        status="open",
    ))
    db.commit()
    db.close()

    fake_translation_service = Mock()
    fake_translation_service.to_language.side_effect = AIServiceError("translation down")
    monkeypatch.setattr(complaints_module, "_translation_service", fake_translation_service)

    response = client.get("/complaints", params={"lang": "hi"}, headers={"Authorization": f"Bearer {admin_token}"})

    assert response.status_code == 200
    assert response.json()[0]["display_text"] == "Garbage has not been collected."


def test_update_status_marks_complaint_resolved(client, make_worker, db_session):
    """PATCH /complaints/{id} should update the status and persist it."""
    token, worker = make_worker(phone="9000000002", ward="Ward 14")

    db = db_session()
    complaint = Complaint(
        citizen_id="1", original_text="Garbage issue", original_language="en",
        translated_text="Garbage has not been collected.", summary="Garbage not collected.",
        ward="Ward 14", status="open",
    )
    db.add(complaint)
    db.commit()
    db.refresh(complaint)
    complaint_id = complaint.id
    db.close()

    response = client.patch(
        f"/complaints/{complaint_id}", headers={"Authorization": f"Bearer {token}"}, json={"status": "resolved"}
    )

    assert response.status_code == 200
    assert response.json()["status"] == "resolved"


def test_citizen_cannot_update_status(client, make_citizen, db_session):
    token, user = make_citizen(phone="9000000001")

    db = db_session()
    complaint = Complaint(
        citizen_id=str(user["id"]), original_text="a", original_language="en",
        translated_text="a", summary="a", status="open",
    )
    db.add(complaint)
    db.commit()
    db.refresh(complaint)
    complaint_id = complaint.id
    db.close()

    response = client.patch(
        f"/complaints/{complaint_id}", headers={"Authorization": f"Bearer {token}"}, json={"status": "resolved"}
    )
    assert response.status_code == 403


def test_worker_cannot_resolve_complaint_outside_their_ward(client, make_worker, db_session):
    token, worker = make_worker(phone="9000000002", ward="Ward 14")

    db = db_session()
    complaint = Complaint(
        citizen_id="1", original_text="a", original_language="en",
        translated_text="a", summary="a", ward="Ward 9", status="open",
    )
    db.add(complaint)
    db.commit()
    db.refresh(complaint)
    complaint_id = complaint.id
    db.close()

    response = client.patch(
        f"/complaints/{complaint_id}", headers={"Authorization": f"Bearer {token}"}, json={"status": "resolved"}
    )
    assert response.status_code == 403


def test_update_status_invalid_value_returns_400(client, make_worker, db_session):
    token, worker = make_worker(phone="9000000002", ward="Ward 14")

    db = db_session()
    complaint = Complaint(
        citizen_id="1", original_text="a", original_language="en",
        translated_text="a", summary="a", ward="Ward 14", status="open",
    )
    db.add(complaint)
    db.commit()
    db.refresh(complaint)
    complaint_id = complaint.id
    db.close()

    response = client.patch(
        f"/complaints/{complaint_id}", headers={"Authorization": f"Bearer {token}"}, json={"status": "archived"}
    )
    assert response.status_code == 400


def test_update_status_missing_complaint_returns_404(client, make_worker):
    token, worker = make_worker(phone="9000000002", ward="Ward 14")
    response = client.patch(
        "/complaints/999999", headers={"Authorization": f"Bearer {token}"}, json={"status": "resolved"}
    )
    assert response.status_code == 404

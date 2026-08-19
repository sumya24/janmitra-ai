"""Integration tests for the /complaints API endpoints.

All endpoints require authentication and are scoped by role (see backend/deps.py): citizens see
only their own complaints, workers see only complaints currently assigned to them specifically
(not just anyone in their ward), and admins see everything.

Lifecycle covered here: pending -> assigned -> accepted -> resolved -> feedback, plus reject ->
reassign to the next worker in the same ward (or back to pending if none are left).
"""

from unittest.mock import Mock

import backend.routes.complaints as complaints_module
from backend.models import Complaint, User
from backend.services.auth_service import hash_password
from backend.services.sarvam_client import AIServiceError


def _fake_agent_create_complaint(db, citizen_id, language_code, text, audio_chunks, photo_path):
    """Stand in for ComplaintAgent.create_complaint without calling any external API."""
    complaint = Complaint(
        citizen_id=citizen_id,
        original_text=text or "(voice complaint)",
        original_language=language_code,
        translated_text=f"[en] {text or 'voice complaint'}",
        summary="A short summary.",
        photo_path=photo_path,
        status="pending",
    )
    db.add(complaint)
    db.commit()
    db.refresh(complaint)
    return complaint


def _make_worker_row(db_session, phone: str, ward: str, full_name: str = "Worker") -> int:
    """Insert a worker directly into the db (bypassing the /admin/workers API + its bootstrap-
    admin fixture, which can't be called twice with the same hardcoded admin phone) — needed for
    tests that want more than one worker in the same ward."""
    db = db_session()
    worker = User(
        full_name=full_name, phone=phone, password_hash=hash_password("secret123"),
        role="worker", preferred_language="en", ward=ward,
    )
    db.add(worker)
    db.commit()
    db.refresh(worker)
    worker_id = worker.id
    db.close()
    return worker_id


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
    assert body["status"] == "pending"  # no ward given, so no worker to assign to
    assert body["translated_text"] == "[en] कचरा उचलला नाही"
    assert body["assigned_worker_name"] is None


def test_create_complaint_assigns_to_worker_in_matching_ward(client, monkeypatch, make_citizen, make_worker):
    """A complaint filed into a ward with an eligible worker is immediately assigned, not pending."""
    monkeypatch.setattr(
        complaints_module, "_agent", Mock(create_complaint=_fake_agent_create_complaint)
    )
    _worker_token, worker = make_worker(phone="9000000002", ward="Ward 14")
    citizen_token, _user = make_citizen(phone="9000000001")

    response = client.post(
        "/complaints",
        headers={"Authorization": f"Bearer {citizen_token}"},
        data={"language": "en", "text": "Garbage issue", "ward": "Ward 14"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "assigned"
    assert body["assigned_worker_name"] == worker["full_name"]
    assert body["assigned_worker_phone"] is None  # not revealed until accepted


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
        translated_text="Complaint from citizen A", summary="a", status="pending",
    ))
    db.add(Complaint(
        citizen_id=str(user_b["id"]), original_text="b", original_language="en",
        translated_text="Complaint from citizen B", summary="b", status="pending",
    ))
    db.commit()
    db.close()

    response = client.get("/complaints", headers={"Authorization": f"Bearer {token_a}"})
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["translated_text"] == "Complaint from citizen A"


def test_worker_only_sees_complaints_assigned_to_them(client, make_worker, db_session):
    """A worker sees complaints assigned to *them*, not just anyone sharing their ward."""
    token, worker = make_worker(phone="9000000002", ward="Ward 14")
    other_worker_id = _make_worker_row(db_session, phone="9000000099", ward="Ward 14", full_name="Other Worker")

    db = db_session()
    db.add(Complaint(
        citizen_id="1", original_text="a", original_language="en",
        translated_text="Assigned to me", summary="a", ward="Ward 14",
        status="assigned", assigned_worker_id=worker["id"],
    ))
    db.add(Complaint(
        citizen_id="1", original_text="b", original_language="en",
        translated_text="Assigned to the other worker", summary="b", ward="Ward 14",
        status="assigned", assigned_worker_id=other_worker_id,
    ))
    db.commit()
    db.close()

    response = client.get("/complaints", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["translated_text"] == "Assigned to me"


def test_admin_sees_every_complaint(client, make_admin, db_session):
    make_admin(phone="9999999999", password="adminpass")
    login = client.post("/auth/login", json={"identifier": "9999999999", "password": "adminpass"})
    admin_token = login.json()["access_token"]

    db = db_session()
    db.add(Complaint(
        citizen_id="1", original_text="a", original_language="en",
        translated_text="Ward 14 complaint", summary="a", ward="Ward 14", status="pending",
    ))
    db.add(Complaint(
        citizen_id="2", original_text="b", original_language="en",
        translated_text="Ward 9 complaint", summary="b", ward="Ward 9", status="pending",
    ))
    db.commit()
    db.close()

    response = client.get("/complaints", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_admin_can_filter_by_worker_id(client, make_admin, make_worker, db_session):
    """The Admin Worker Detail page's data source -- see routes/complaints.py's list_complaints()
    docstring for why this is admin-only-effective, not a separate permission check."""
    make_admin(phone="9999999999", password="adminpass")
    login = client.post("/auth/login", json={"identifier": "9999999999", "password": "adminpass"})
    admin_token = login.json()["access_token"]
    _, worker = make_worker(phone="9000000002", ward="Ward 14")

    db = db_session()
    db.add(Complaint(
        citizen_id="1", original_text="a", original_language="en", translated_text="a",
        summary="a", ward="Ward 14", status="assigned", assigned_worker_id=worker["id"],
    ))
    db.add(Complaint(
        citizen_id="2", original_text="b", original_language="en", translated_text="b",
        summary="b", ward="Ward 9", status="pending",  # unassigned -- must not show up
    ))
    db.commit()
    db.close()

    response = client.get(
        "/complaints", params={"worker_id": worker["id"]}, headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["assigned_worker_name"] == worker["full_name"]


def test_worker_id_filter_is_ignored_for_non_admin_roles(client, make_worker, db_session):
    """A worker passing worker_id=<someone else> must still only ever see their OWN queue --
    the param is a no-op outside the admin role, never a way to see another worker's complaints."""
    token, worker = make_worker(phone="9000000002", ward="Ward 14")

    db = db_session()
    own = Complaint(
        citizen_id="1", original_text="a", original_language="en", translated_text="a",
        summary="a", ward="Ward 14", status="assigned", assigned_worker_id=worker["id"],
    )
    someone_elses = Complaint(
        citizen_id="2", original_text="b", original_language="en", translated_text="b",
        summary="b", ward="Ward 9", status="assigned", assigned_worker_id=999999,
    )
    db.add_all([own, someone_elses])
    db.commit()
    other_id = someone_elses.assigned_worker_id
    db.close()

    response = client.get(
        "/complaints", params={"worker_id": other_id}, headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["assigned_worker_name"] == worker["full_name"]


def test_list_complaints_translates_on_read(client, monkeypatch, make_admin, db_session):
    """GET /complaints?lang=hi should translate stored English text on read only."""
    make_admin(phone="9999999999", password="adminpass")
    login = client.post("/auth/login", json={"identifier": "9999999999", "password": "adminpass"})
    admin_token = login.json()["access_token"]

    db = db_session()
    db.add(Complaint(
        citizen_id="1", original_text="कचरा उचलला नाही", original_language="mr",
        translated_text="Garbage has not been collected.", summary="Garbage not collected.",
        status="pending",
    ))
    db.commit()
    db.close()

    fake_translation_service = Mock()
    fake_translation_service.to_language.side_effect = ["कचरा एकत्र नहीं किया गया।", "कचरा शिकायत।"]
    monkeypatch.setattr(complaints_module, "_translation_service", fake_translation_service)

    response = client.get("/complaints", params={"lang": "hi"}, headers={"Authorization": f"Bearer {admin_token}"})

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["display_text"] == "कचरा एकत्र नहीं किया गया।"
    assert body[0]["translated_text"] == "Garbage has not been collected."
    assert body[0]["display_summary"] == "कचरा शिकायत।"
    assert body[0]["summary"] == "Garbage not collected."  # summary field itself stays English


def test_list_complaints_falls_back_to_english_on_translation_failure(client, monkeypatch, make_admin, db_session):
    """If on-read translation fails, the API should still return the English text."""
    make_admin(phone="9999999999", password="adminpass")
    login = client.post("/auth/login", json={"identifier": "9999999999", "password": "adminpass"})
    admin_token = login.json()["access_token"]

    db = db_session()
    db.add(Complaint(
        citizen_id="1", original_text="Garbage issue", original_language="en",
        translated_text="Garbage has not been collected.", summary="Garbage not collected.",
        status="pending",
    ))
    db.commit()
    db.close()

    fake_translation_service = Mock()
    fake_translation_service.to_language.side_effect = AIServiceError("translation down")
    monkeypatch.setattr(complaints_module, "_translation_service", fake_translation_service)

    response = client.get("/complaints", params={"lang": "hi"}, headers={"Authorization": f"Bearer {admin_token}"})

    assert response.status_code == 200
    body = response.json()[0]
    assert body["display_text"] == "Garbage has not been collected."
    assert body["display_summary"] == "Garbage not collected."


def _make_assigned_complaint(db_session, worker_id: int, ward: str = "Ward 14", status: str = "assigned") -> int:
    db = db_session()
    complaint = Complaint(
        citizen_id="1", original_text="a", original_language="en",
        translated_text="Garbage issue", summary="Garbage not collected.",
        ward=ward, status=status, assigned_worker_id=worker_id,
    )
    db.add(complaint)
    db.commit()
    db.refresh(complaint)
    complaint_id = complaint.id
    db.close()
    return complaint_id


def test_accept_complaint_unlocks_phone_number(client, make_worker, db_session):
    token, worker = make_worker(phone="9000000002", ward="Ward 14")
    complaint_id = _make_assigned_complaint(db_session, worker["id"])

    response = client.post(f"/complaints/{complaint_id}/accept", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "accepted"
    assert body["assigned_worker_phone"] == worker["phone"]


def test_accept_complaint_not_assigned_to_you_returns_403(client, make_worker, db_session):
    token, worker = make_worker(phone="9000000002", ward="Ward 14")
    other_worker_id = _make_worker_row(db_session, phone="9000000099", ward="Ward 9")
    complaint_id = _make_assigned_complaint(db_session, other_worker_id, ward="Ward 9")

    response = client.post(f"/complaints/{complaint_id}/accept", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403


def test_accept_complaint_already_accepted_returns_400(client, make_worker, db_session):
    token, worker = make_worker(phone="9000000002", ward="Ward 14")
    complaint_id = _make_assigned_complaint(db_session, worker["id"], status="accepted")

    response = client.post(f"/complaints/{complaint_id}/accept", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 400


def test_citizen_cannot_accept_a_complaint(client, make_citizen, make_worker, db_session):
    _worker_token, worker = make_worker(phone="9000000002", ward="Ward 14")
    citizen_token, _user = make_citizen(phone="9000000001")
    complaint_id = _make_assigned_complaint(db_session, worker["id"])

    response = client.post(f"/complaints/{complaint_id}/accept", headers={"Authorization": f"Bearer {citizen_token}"})
    assert response.status_code == 403


def test_reject_complaint_reassigns_to_next_worker_in_ward(client, make_worker, db_session):
    """The first worker in a ward rejects — it should move to the second, not vanish."""
    token1, worker1 = make_worker(phone="9000000002", ward="Ward 14")
    worker2_id = _make_worker_row(db_session, phone="9000000098", ward="Ward 14", full_name="Second Worker")
    complaint_id = _make_assigned_complaint(db_session, worker1["id"])

    response = client.post(
        f"/complaints/{complaint_id}/reject", headers={"Authorization": f"Bearer {token1}"},
        json={"reason": "Outside my assigned area."},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "assigned"
    assert body["assigned_worker_name"] == "Second Worker"
    assert body["rejection_count"] == 1
    # worker1 no longer sees it — it moved to worker2.
    response = client.get("/complaints", headers={"Authorization": f"Bearer {token1}"})
    assert len(response.json()) == 0


def test_reject_complaint_with_no_other_worker_becomes_pending(client, make_worker, db_session):
    token, worker = make_worker(phone="9000000002", ward="Ward 14")
    complaint_id = _make_assigned_complaint(db_session, worker["id"])

    response = client.post(
        f"/complaints/{complaint_id}/reject", headers={"Authorization": f"Bearer {token}"},
        json={"reason": "Not my specialty."},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "pending"
    assert body["assigned_worker_name"] is None


def test_reject_complaint_wrong_status_returns_400(client, make_worker, db_session):
    token, worker = make_worker(phone="9000000002", ward="Ward 14")
    complaint_id = _make_assigned_complaint(db_session, worker["id"], status="accepted")

    response = client.post(
        f"/complaints/{complaint_id}/reject", headers={"Authorization": f"Bearer {token}"},
        json={"reason": "Doesn't matter, wrong status."},
    )
    assert response.status_code == 400


def test_reject_complaint_requires_a_reason(client, make_worker, db_session):
    """Mandatory rejection reason -- worker-workflow phase. Empty and whitespace-only reasons
    must both be rejected (Pydantic's min_length catches the former, an explicit .strip() check
    catches the latter)."""
    token, worker = make_worker(phone="9000000002", ward="Ward 14")
    complaint_id = _make_assigned_complaint(db_session, worker["id"])

    empty = client.post(f"/complaints/{complaint_id}/reject", headers={"Authorization": f"Bearer {token}"}, json={"reason": ""})
    assert empty.status_code == 422  # Pydantic min_length=1

    whitespace = client.post(f"/complaints/{complaint_id}/reject", headers={"Authorization": f"Bearer {token}"}, json={"reason": "   "})
    assert whitespace.status_code == 400
    assert "reason" in whitespace.json()["detail"].lower()


def test_reject_complaint_reason_is_stored(client, make_worker, db_session):
    token, worker = make_worker(phone="9000000002", ward="Ward 14")
    complaint_id = _make_assigned_complaint(db_session, worker["id"])

    response = client.post(
        f"/complaints/{complaint_id}/reject", headers={"Authorization": f"Bearer {token}"},
        json={"reason": "Wrong ward, this belongs elsewhere."},
    )
    assert response.status_code == 200

    db = db_session()
    from backend.models import ComplaintRejection
    rejection = db.query(ComplaintRejection).filter(ComplaintRejection.complaint_id == complaint_id).first()
    assert rejection is not None
    assert rejection.reason == "Wrong ward, this belongs elsewhere."
    assert rejection.worker_id == worker["id"]
    db.close()


def test_resolve_complaint_requires_accepted_first(client, make_worker, db_session):
    token, worker = make_worker(phone="9000000002", ward="Ward 14")
    complaint_id = _make_assigned_complaint(db_session, worker["id"], status="assigned")

    response = client.post(
        f"/complaints/{complaint_id}/resolve", headers={"Authorization": f"Bearer {token}"},
        data={"completion_status": "Done."},
    )
    assert response.status_code == 400


def test_resolve_complaint_requires_in_progress_not_just_accepted(client, make_worker, db_session):
    """Worker-workflow phase: "accepted" is no longer sufficient to resolve -- the complaint must
    have gone through start_work() into "in_progress" first (accepted -> in_progress ->
    resolved, not accepted -> resolved directly)."""
    token, worker = make_worker(phone="9000000002", ward="Ward 14")
    complaint_id = _make_assigned_complaint(db_session, worker["id"], status="accepted")

    response = client.post(
        f"/complaints/{complaint_id}/resolve", headers={"Authorization": f"Bearer {token}"},
        data={"completion_status": "Done."},
    )
    assert response.status_code == 400


def test_resolve_complaint_succeeds_after_in_progress(client, make_worker, db_session):
    token, worker = make_worker(phone="9000000002", ward="Ward 14")
    complaint_id = _make_assigned_complaint(db_session, worker["id"], status="in_progress")

    response = client.post(
        f"/complaints/{complaint_id}/resolve", headers={"Authorization": f"Bearer {token}"},
        data={"completion_status": "Fixture replaced and tested successfully."},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "resolved"


def test_resolve_complaint_requires_completion_status(client, make_worker, db_session):
    token, worker = make_worker(phone="9000000002", ward="Ward 14")
    complaint_id = _make_assigned_complaint(db_session, worker["id"], status="in_progress")

    empty = client.post(f"/complaints/{complaint_id}/resolve", headers={"Authorization": f"Bearer {token}"}, data={"completion_status": "   "})
    assert empty.status_code == 400

    db = db_session()
    from backend.models import Complaint as ComplaintModel
    complaint = db.query(ComplaintModel).filter(ComplaintModel.id == complaint_id).first()
    assert complaint.status == "in_progress"  # unchanged -- never silently resolved
    db.close()


def test_resolve_complaint_missing_returns_404(client, make_worker):
    token, worker = make_worker(phone="9000000002", ward="Ward 14")
    response = client.post(
        "/complaints/999999/resolve", headers={"Authorization": f"Bearer {token}"},
        data={"completion_status": "Done."},
    )
    assert response.status_code == 404


def test_submit_feedback_on_resolved_complaint(client, make_citizen, make_worker, db_session):
    citizen_token, user = make_citizen(phone="9000000001")
    _worker_token, worker = make_worker(phone="9000000002", ward="Ward 14")

    db = db_session()
    complaint = Complaint(
        citizen_id=str(user["id"]), original_text="a", original_language="en",
        translated_text="a", summary="a", ward="Ward 14",
        status="resolved", assigned_worker_id=worker["id"],
    )
    db.add(complaint)
    db.commit()
    db.refresh(complaint)
    complaint_id = complaint.id
    db.close()

    response = client.post(
        f"/complaints/{complaint_id}/feedback",
        headers={"Authorization": f"Bearer {citizen_token}"},
        json={"rating": 5, "comment": "Fixed quickly, thank you!"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["feedback_rating"] == 5
    assert body["feedback_comment"] == "Fixed quickly, thank you!"


def test_submit_feedback_before_resolved_returns_400(client, make_citizen, db_session):
    citizen_token, user = make_citizen(phone="9000000001")

    db = db_session()
    complaint = Complaint(
        citizen_id=str(user["id"]), original_text="a", original_language="en",
        translated_text="a", summary="a", status="assigned",
    )
    db.add(complaint)
    db.commit()
    db.refresh(complaint)
    complaint_id = complaint.id
    db.close()

    response = client.post(
        f"/complaints/{complaint_id}/feedback",
        headers={"Authorization": f"Bearer {citizen_token}"},
        json={"rating": 3},
    )
    assert response.status_code == 400


def test_submit_feedback_on_someone_elses_complaint_returns_403(client, make_citizen, db_session):
    token_a, _user_a = make_citizen(phone="9000000001")
    _token_b, user_b = make_citizen(phone="9000000002")

    db = db_session()
    complaint = Complaint(
        citizen_id=str(user_b["id"]), original_text="a", original_language="en",
        translated_text="a", summary="a", status="resolved",
    )
    db.add(complaint)
    db.commit()
    db.refresh(complaint)
    complaint_id = complaint.id
    db.close()

    response = client.post(
        f"/complaints/{complaint_id}/feedback",
        headers={"Authorization": f"Bearer {token_a}"},
        json={"rating": 1},
    )
    assert response.status_code == 403


def test_submit_feedback_rating_out_of_range_returns_422(client, make_citizen, db_session):
    citizen_token, user = make_citizen(phone="9000000001")

    db = db_session()
    complaint = Complaint(
        citizen_id=str(user["id"]), original_text="a", original_language="en",
        translated_text="a", summary="a", status="resolved",
    )
    db.add(complaint)
    db.commit()
    db.refresh(complaint)
    complaint_id = complaint.id
    db.close()

    response = client.post(
        f"/complaints/{complaint_id}/feedback",
        headers={"Authorization": f"Bearer {citizen_token}"},
        json={"rating": 7},
    )
    assert response.status_code == 422

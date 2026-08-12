"""Integration tests for /admin/workers — the only place a worker account can be created."""


def _login(client, phone, password):
    response = client.post("/auth/login", json={"phone": phone, "password": password})
    assert response.status_code == 200
    return response.json()["access_token"]


def test_admin_can_create_worker(client, make_admin):
    make_admin(phone="9999999999", password="adminpass")
    admin_token = _login(client, "9999999999", "adminpass")

    response = client.post(
        "/admin/workers",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "full_name": "Ramesh Kadam",
            "phone": "9000000002",
            "password": "secret123",
            "ward": "Ward 14",
            "preferred_language": "hi",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["role"] == "worker"
    assert body["ward"] == "Ward 14"

    # and the new worker can actually log in
    worker_login = client.post("/auth/login", json={"phone": "9000000002", "password": "secret123"})
    assert worker_login.status_code == 200
    assert worker_login.json()["user"]["role"] == "worker"


def test_citizen_cannot_create_worker(client, make_citizen):
    token, _user = make_citizen(phone="9000000001")
    response = client.post(
        "/admin/workers",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "full_name": "Ramesh Kadam",
            "phone": "9000000002",
            "password": "secret123",
            "ward": "Ward 14",
            "preferred_language": "hi",
        },
    )
    assert response.status_code == 403


def test_worker_cannot_create_another_worker(client, make_worker):
    token, _user = make_worker(phone="9000000002")
    response = client.post(
        "/admin/workers",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "full_name": "Another Worker",
            "phone": "9000000003",
            "password": "secret123",
            "ward": "Ward 9",
            "preferred_language": "en",
        },
    )
    assert response.status_code == 403


def test_unauthenticated_request_is_rejected(client):
    response = client.post(
        "/admin/workers",
        json={
            "full_name": "Ramesh",
            "phone": "9000000002",
            "password": "secret123",
            "ward": "Ward 14",
            "preferred_language": "hi",
        },
    )
    assert response.status_code == 401


def test_create_worker_rejects_duplicate_phone(client, make_admin, make_citizen):
    make_admin(phone="9999999999", password="adminpass")
    admin_token = _login(client, "9999999999", "adminpass")
    make_citizen(phone="9000000001")  # phone already taken by a citizen

    response = client.post(
        "/admin/workers",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "full_name": "Ramesh",
            "phone": "9000000001",
            "password": "secret123",
            "ward": "Ward 14",
            "preferred_language": "hi",
        },
    )
    assert response.status_code == 409


def test_list_workers_reports_open_and_resolved_counts(client, make_admin, make_worker, db_session):
    from backend.models import Complaint

    token, worker = make_worker(phone="9000000002", ward="Ward 14")
    admin_token = _login(client, "9999900000", "bootstrap-pass")

    db = db_session()
    db.add(Complaint(
        citizen_id="1", original_text="a", original_language="en", translated_text="a",
        summary="a", ward="Ward 14", status="assigned", assigned_worker_id=worker["id"],
    ))
    db.add(Complaint(
        citizen_id="1", original_text="b", original_language="en", translated_text="b",
        summary="b", ward="Ward 14", status="resolved", assigned_worker_id=worker["id"],
    ))
    db.commit()
    db.close()

    response = client.get("/admin/workers", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    workers = response.json()
    ramesh = next(w for w in workers if w["phone"] == "9000000002")
    assert ramesh["open_complaints"] == 1
    assert ramesh["resolved_complaints"] == 1


# --- PATCH /admin/workers/{id} ---


def test_admin_can_edit_worker_profile(client, make_admin, make_worker):
    make_admin(phone="9999999999", password="adminpass")
    admin_token = _login(client, "9999999999", "adminpass")
    _, worker = make_worker(phone="9000000002", ward="Ward 14", preferred_language="hi")

    response = client.patch(
        f"/admin/workers/{worker['id']}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"full_name": "Renamed Worker", "ward": "Ward 22", "preferred_language": "mr"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["full_name"] == "Renamed Worker"
    assert body["ward"] == "Ward 22"
    assert body["preferred_language"] == "mr"
    assert body["phone"] == "9000000002"  # unchanged -- not editable via this endpoint


def test_edit_worker_partial_update_only_changes_given_fields(client, make_admin, make_worker):
    make_admin(phone="9999999999", password="adminpass")
    admin_token = _login(client, "9999999999", "adminpass")
    _, worker = make_worker(phone="9000000002", ward="Ward 14", preferred_language="hi", full_name="Original Name")

    response = client.patch(
        f"/admin/workers/{worker['id']}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"ward": "Ward 99"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["full_name"] == "Original Name"  # untouched
    assert body["ward"] == "Ward 99"
    assert body["preferred_language"] == "hi"  # untouched


def test_edit_worker_rejects_empty_full_name(client, make_admin, make_worker):
    make_admin(phone="9999999999", password="adminpass")
    admin_token = _login(client, "9999999999", "adminpass")
    _, worker = make_worker(phone="9000000002")

    response = client.patch(
        f"/admin/workers/{worker['id']}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"full_name": "   "},
    )
    assert response.status_code == 400


def test_edit_worker_rejects_unsupported_language(client, make_admin, make_worker):
    make_admin(phone="9999999999", password="adminpass")
    admin_token = _login(client, "9999999999", "adminpass")
    _, worker = make_worker(phone="9000000002")

    response = client.patch(
        f"/admin/workers/{worker['id']}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"preferred_language": "xx"},
    )
    assert response.status_code == 400


def test_edit_worker_not_found(client, make_admin):
    make_admin(phone="9999999999", password="adminpass")
    admin_token = _login(client, "9999999999", "adminpass")
    response = client.patch(
        "/admin/workers/999999",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"full_name": "Someone"},
    )
    assert response.status_code == 404


def test_citizen_cannot_edit_worker(client, make_citizen, make_worker):
    token, _ = make_citizen(phone="9000000001")
    _, worker = make_worker(phone="9000000002")
    response = client.patch(
        f"/admin/workers/{worker['id']}",
        headers={"Authorization": f"Bearer {token}"},
        json={"full_name": "Hacked"},
    )
    assert response.status_code == 403


# --- POST /admin/workers/{id}/reset-password ---


def test_admin_can_reset_worker_password(client, make_admin, make_worker):
    make_admin(phone="9999999999", password="adminpass")
    admin_token = _login(client, "9999999999", "adminpass")
    _, worker = make_worker(phone="9000000002", password="oldpassword")

    response = client.post(
        f"/admin/workers/{worker['id']}/reset-password",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"new_password": "brandnewpass123"},
    )
    assert response.status_code == 200

    # old password no longer works, new one does
    old_login = client.post("/auth/login", json={"phone": "9000000002", "password": "oldpassword"})
    assert old_login.status_code == 401
    new_login = client.post("/auth/login", json={"phone": "9000000002", "password": "brandnewpass123"})
    assert new_login.status_code == 200


def test_reset_worker_password_rejects_too_short(client, make_admin, make_worker):
    make_admin(phone="9999999999", password="adminpass")
    admin_token = _login(client, "9999999999", "adminpass")
    _, worker = make_worker(phone="9000000002")

    response = client.post(
        f"/admin/workers/{worker['id']}/reset-password",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"new_password": "abc"},
    )
    assert response.status_code == 400


def test_reset_worker_password_not_found(client, make_admin):
    make_admin(phone="9999999999", password="adminpass")
    admin_token = _login(client, "9999999999", "adminpass")
    response = client.post(
        "/admin/workers/999999/reset-password",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"new_password": "brandnewpass123"},
    )
    assert response.status_code == 404


def test_worker_cannot_reset_own_or_others_password(client, make_worker, db_session):
    from backend.models import User
    from backend.services.auth_service import hash_password

    token, _ = make_worker(phone="9000000002")
    db = db_session()
    other = User(
        full_name="Other Worker", phone="9000000003", password_hash=hash_password("secret123"),
        role="worker", preferred_language="en", ward="Ward 9",
    )
    db.add(other)
    db.commit()
    other_id = other.id
    db.close()

    response = client.post(
        f"/admin/workers/{other_id}/reset-password",
        headers={"Authorization": f"Bearer {token}"},
        json={"new_password": "brandnewpass123"},
    )
    assert response.status_code == 403


# --- DELETE /admin/workers/{id} ---


def test_admin_can_delete_worker(client, make_admin, make_worker):
    make_admin(phone="9999999999", password="adminpass")
    admin_token = _login(client, "9999999999", "adminpass")
    _, worker = make_worker(phone="9000000002")

    response = client.delete(f"/admin/workers/{worker['id']}", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    assert response.json() == {"deleted_worker_id": worker["id"], "reset_to_pending": 0}

    # deleted -- no longer able to log in
    login = client.post("/auth/login", json={"phone": "9000000002", "password": "secret123"})
    assert login.status_code == 401

    # and gone from the worker list
    listing = client.get("/admin/workers", headers={"Authorization": f"Bearer {admin_token}"})
    assert all(w["id"] != worker["id"] for w in listing.json())


def test_delete_worker_resets_their_assigned_complaints_to_pending(client, make_admin, make_worker, db_session):
    from backend.models import Complaint

    make_admin(phone="9999999999", password="adminpass")
    admin_token = _login(client, "9999999999", "adminpass")
    _, worker = make_worker(phone="9000000002", ward="Ward 14")

    db = db_session()
    c1 = Complaint(
        citizen_id="1", original_text="a", original_language="en", translated_text="a",
        summary="a", ward="Ward 14", status="assigned", assigned_worker_id=worker["id"],
    )
    c2 = Complaint(
        citizen_id="1", original_text="b", original_language="en", translated_text="b",
        summary="b", ward="Ward 14", status="accepted", assigned_worker_id=worker["id"],
    )
    c3 = Complaint(  # already resolved -- must NOT be reset, deleting a worker doesn't undo finished work
        citizen_id="1", original_text="c", original_language="en", translated_text="c",
        summary="c", ward="Ward 14", status="resolved", assigned_worker_id=worker["id"],
    )
    db.add_all([c1, c2, c3])
    db.commit()
    ids = [c1.id, c2.id, c3.id]
    db.close()

    response = client.delete(f"/admin/workers/{worker['id']}", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    assert response.json()["reset_to_pending"] == 2

    db = db_session()
    reloaded = db.query(Complaint).filter(Complaint.id.in_(ids)).order_by(Complaint.id).all()
    assert [c.status for c in reloaded] == ["pending", "pending", "resolved"]
    assert reloaded[0].assigned_worker_id is None
    assert reloaded[1].assigned_worker_id is None
    assert reloaded[2].assigned_worker_id == worker["id"]  # resolved one keeps its history
    db.close()


def test_delete_worker_resets_in_progress_complaints_too(client, make_admin, make_worker, db_session):
    """Regression test: `in_progress` (set once a worker submits their mandatory initial
    assessment -- see routes/complaints.py) was added to the complaint lifecycle after
    delete_worker() was first written, and its reset-to-pending filter didn't originally include
    it -- meaning a deleted worker's in-progress complaint kept `assigned_worker_id` pointing at
    an account that no longer existed. See `_OPEN_COMPLAINT_STATUSES` in routes/admin.py."""
    from backend.models import Complaint

    make_admin(phone="9999999999", password="adminpass")
    admin_token = _login(client, "9999999999", "adminpass")
    _, worker = make_worker(phone="9000000002", ward="Ward 14")

    db = db_session()
    complaint = Complaint(
        citizen_id="1", original_text="a", original_language="en", translated_text="a",
        summary="a", ward="Ward 14", status="in_progress", assigned_worker_id=worker["id"],
    )
    db.add(complaint)
    db.commit()
    complaint_id = complaint.id
    db.close()

    response = client.delete(f"/admin/workers/{worker['id']}", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    assert response.json()["reset_to_pending"] == 1

    db = db_session()
    reloaded = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    assert reloaded.status == "pending"
    assert reloaded.assigned_worker_id is None  # not left dangling
    db.close()


def test_delete_worker_logs_status_history(client, make_admin, make_worker, db_session):
    from backend.models import Complaint, ComplaintStatusHistory

    make_admin(phone="9999999999", password="adminpass")
    admin_token = _login(client, "9999999999", "adminpass")
    _, worker = make_worker(phone="9000000002", ward="Ward 14")

    db = db_session()
    complaint = Complaint(
        citizen_id="1", original_text="a", original_language="en", translated_text="a",
        summary="a", ward="Ward 14", status="accepted", assigned_worker_id=worker["id"],
    )
    db.add(complaint)
    db.commit()
    complaint_id = complaint.id
    db.close()

    response = client.delete(f"/admin/workers/{worker['id']}", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200

    db = db_session()
    history = db.query(ComplaintStatusHistory).filter(ComplaintStatusHistory.complaint_id == complaint_id).all()
    assert len(history) == 1
    assert history[0].from_status == "accepted"
    assert history[0].to_status == "pending"
    assert history[0].actor_role == "admin"
    db.close()


def test_delete_worker_not_found(client, make_admin):
    make_admin(phone="9999999999", password="adminpass")
    admin_token = _login(client, "9999999999", "adminpass")
    response = client.delete("/admin/workers/999999", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 404


def test_citizen_cannot_delete_worker(client, make_citizen, make_worker):
    token, _ = make_citizen(phone="9000000001")
    _, worker = make_worker(phone="9000000002")
    response = client.delete(f"/admin/workers/{worker['id']}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403


def test_worker_cannot_delete_worker(client, make_worker, db_session):
    """Builds the "other" worker directly in the DB (like this file's other tests build
    Complaint rows) rather than via a second make_worker() call -- that fixture always bootstraps
    its own admin account on a fixed phone number, so calling it twice in one test collides."""
    from backend.models import User
    from backend.services.auth_service import hash_password

    token, _ = make_worker(phone="9000000002")

    db = db_session()
    other = User(
        full_name="Other Worker", phone="9000000003", password_hash=hash_password("secret123"),
        role="worker", preferred_language="en", ward="Ward 9",
    )
    db.add(other)
    db.commit()
    other_id = other.id
    db.close()

    response = client.delete(f"/admin/workers/{other_id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403


# --- DELETE /admin/complaints/{id} ---


def test_admin_can_delete_complaint(client, make_admin, make_citizen, db_session):
    from backend.models import Complaint

    make_admin(phone="9999999999", password="adminpass")
    admin_token = _login(client, "9999999999", "adminpass")
    citizen_token, citizen = make_citizen(phone="9000000001")

    db = db_session()
    complaint = Complaint(
        citizen_id=str(citizen["id"]), original_text="a", original_language="en", translated_text="a",
        summary="a", ward="Ward 14", status="pending",
    )
    db.add(complaint)
    db.commit()
    complaint_id = complaint.id
    db.close()

    response = client.delete(f"/admin/complaints/{complaint_id}", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    assert response.json() == {"deleted_complaint_id": complaint_id}

    listing = client.get("/complaints", headers={"Authorization": f"Bearer {citizen_token}"})
    assert all(c["id"] != complaint_id for c in listing.json())


def test_delete_complaint_removes_status_history_and_updates(client, make_admin, make_citizen, db_session):
    """Regression coverage for the cascade cleanup added alongside ComplaintStatusHistory/
    ComplaintUpdate (both new tables, added after delete_complaint() was first written) -- a
    deleted complaint must not leave orphaned rows in either."""
    from backend.models import Complaint, ComplaintStatusHistory, ComplaintUpdate

    make_admin(phone="9999999999", password="adminpass")
    admin_token = _login(client, "9999999999", "adminpass")
    _, citizen = make_citizen(phone="9000000001")

    db = db_session()
    complaint = Complaint(
        citizen_id=str(citizen["id"]), original_text="a", original_language="en", translated_text="a",
        summary="a", ward="Ward 14", status="pending",
    )
    db.add(complaint)
    db.commit()
    complaint_id = complaint.id
    db.add(ComplaintStatusHistory(complaint_id=complaint_id, from_status=None, to_status="pending", actor_role="system"))
    db.add(ComplaintUpdate(complaint_id=complaint_id, worker_id=1, update_type="PROGRESS_UPDATE", text="update"))
    db.commit()
    db.close()

    response = client.delete(f"/admin/complaints/{complaint_id}", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200

    db = db_session()
    assert db.query(ComplaintStatusHistory).filter(ComplaintStatusHistory.complaint_id == complaint_id).count() == 0
    assert db.query(ComplaintUpdate).filter(ComplaintUpdate.complaint_id == complaint_id).count() == 0
    db.close()


def test_delete_complaint_not_found(client, make_admin):
    make_admin(phone="9999999999", password="adminpass")
    admin_token = _login(client, "9999999999", "adminpass")
    response = client.delete("/admin/complaints/999999", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 404


def test_citizen_cannot_delete_complaint(client, make_citizen, db_session):
    from backend.models import Complaint

    token, citizen = make_citizen(phone="9000000001")
    db = db_session()
    complaint = Complaint(
        citizen_id=str(citizen["id"]), original_text="a", original_language="en", translated_text="a",
        summary="a", ward="Ward 14", status="pending",
    )
    db.add(complaint)
    db.commit()
    complaint_id = complaint.id
    db.close()

    response = client.delete(f"/admin/complaints/{complaint_id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403


# --- POST /admin/complaints/{id}/assign ---


def test_admin_can_manually_assign_a_pending_complaint(client, make_admin, make_worker, db_session):
    from backend.models import Complaint

    make_admin(phone="9999999999", password="adminpass")
    admin_token = _login(client, "9999999999", "adminpass")
    _, worker = make_worker(phone="9000000002", ward="Ward 99")  # different ward than the complaint

    db = db_session()
    complaint = Complaint(
        citizen_id="1", original_text="a", original_language="en", translated_text="a",
        summary="a", ward="Some Other Ward", status="pending",
    )
    db.add(complaint)
    db.commit()
    complaint_id = complaint.id
    db.close()

    response = client.post(
        f"/admin/complaints/{complaint_id}/assign",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"worker_id": worker["id"]},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "assigned"
    assert body["assigned_worker_id"] == worker["id"]
    assert body["assigned_worker_name"] == worker["full_name"]

    db = db_session()
    reloaded = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    assert reloaded.status == "assigned"
    assert reloaded.assigned_worker_id == worker["id"]
    db.close()


def test_assign_complaint_logs_status_history(client, make_admin, make_worker, db_session):
    from backend.models import Complaint, ComplaintStatusHistory

    make_admin(phone="9999999999", password="adminpass")
    admin_token = _login(client, "9999999999", "adminpass")
    _, worker = make_worker(phone="9000000002", ward="Ward 99")

    db = db_session()
    complaint = Complaint(
        citizen_id="1", original_text="a", original_language="en", translated_text="a",
        summary="a", ward="Some Other Ward", status="pending",
    )
    db.add(complaint)
    db.commit()
    complaint_id = complaint.id
    db.close()

    response = client.post(
        f"/admin/complaints/{complaint_id}/assign",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"worker_id": worker["id"]},
    )
    assert response.status_code == 200

    db = db_session()
    history = db.query(ComplaintStatusHistory).filter(ComplaintStatusHistory.complaint_id == complaint_id).all()
    assert len(history) == 1
    assert history[0].from_status == "pending"
    assert history[0].to_status == "assigned"
    assert history[0].actor_role == "admin"
    assert worker["full_name"] in (history[0].note or "")
    db.close()


def test_assign_complaint_not_found(client, make_admin, make_worker):
    make_admin(phone="9999999999", password="adminpass")
    admin_token = _login(client, "9999999999", "adminpass")
    _, worker = make_worker(phone="9000000002")

    response = client.post(
        "/admin/complaints/999999/assign",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"worker_id": worker["id"]},
    )
    assert response.status_code == 404


def test_assign_complaint_worker_not_found(client, make_admin, db_session):
    from backend.models import Complaint

    make_admin(phone="9999999999", password="adminpass")
    admin_token = _login(client, "9999999999", "adminpass")

    db = db_session()
    complaint = Complaint(
        citizen_id="1", original_text="a", original_language="en", translated_text="a",
        summary="a", ward="Ward 14", status="pending",
    )
    db.add(complaint)
    db.commit()
    complaint_id = complaint.id
    db.close()

    response = client.post(
        f"/admin/complaints/{complaint_id}/assign",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"worker_id": 999999},
    )
    assert response.status_code == 404


def test_citizen_cannot_assign_complaint(client, make_citizen, make_worker, db_session):
    from backend.models import Complaint

    token, citizen = make_citizen(phone="9000000001")
    _, worker = make_worker(phone="9000000002")

    db = db_session()
    complaint = Complaint(
        citizen_id=str(citizen["id"]), original_text="a", original_language="en", translated_text="a",
        summary="a", ward="Ward 14", status="pending",
    )
    db.add(complaint)
    db.commit()
    complaint_id = complaint.id
    db.close()

    response = client.post(
        f"/admin/complaints/{complaint_id}/assign",
        headers={"Authorization": f"Bearer {token}"},
        json={"worker_id": worker["id"]},
    )
    assert response.status_code == 403

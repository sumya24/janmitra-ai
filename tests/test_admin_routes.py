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
        summary="a", ward="Ward 14", status="open",
    ))
    db.add(Complaint(
        citizen_id="1", original_text="b", original_language="en", translated_text="b",
        summary="b", ward="Ward 14", status="resolved",
    ))
    db.commit()
    db.close()

    response = client.get("/admin/workers", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    workers = response.json()
    ramesh = next(w for w in workers if w["phone"] == "9000000002")
    assert ramesh["open_complaints"] == 1
    assert ramesh["resolved_complaints"] == 1

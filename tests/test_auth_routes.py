"""Integration tests for /auth/signup, /auth/login, and /auth/me.

Note the absence of any test that tries to sign up as "worker" or "admin" —
there is no such option in the API to test against; sign-up always produces
a citizen account (see routes/auth.py).
"""


def test_signup_creates_citizen_and_returns_token(client):
    response = client.post(
        "/auth/signup",
        json={
            "full_name": "Priya Deshmukh",
            "phone": "9000000001",
            "password": "secret123",
            "preferred_language": "mr",
            "ward": "Ward 14",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["user"]["role"] == "citizen"
    assert body["user"]["preferred_language"] == "mr"
    assert body["user"]["ward"] == "Ward 14"
    assert body["access_token"]


def test_signup_rejects_missing_ward(client):
    response = client.post(
        "/auth/signup",
        json={"full_name": "Priya", "phone": "9000000001", "password": "secret123", "preferred_language": "en"},
    )
    assert response.status_code == 422


def test_signup_rejects_blank_ward(client):
    response = client.post(
        "/auth/signup",
        json={"full_name": "Priya", "phone": "9000000001", "password": "secret123", "preferred_language": "en", "ward": "   "},
    )
    assert response.status_code == 400


def test_signup_rejects_duplicate_phone(client, make_citizen):
    make_citizen(phone="9000000001")
    response = client.post(
        "/auth/signup",
        json={
            "full_name": "Someone Else",
            "phone": "9000000001",
            "password": "secret123",
            "preferred_language": "en",
            "ward": "Ward 14",
        },
    )
    assert response.status_code == 409


def test_signup_rejects_short_password(client):
    response = client.post(
        "/auth/signup",
        json={"full_name": "Priya", "phone": "9000000001", "password": "abc", "preferred_language": "en", "ward": "Ward 14"},
    )
    assert response.status_code == 400


def test_signup_rejects_unsupported_language(client):
    response = client.post(
        "/auth/signup",
        json={"full_name": "Priya", "phone": "9000000001", "password": "secret123", "preferred_language": "fr", "ward": "Ward 14"},
    )
    assert response.status_code == 400


def test_login_with_correct_credentials_succeeds(client, make_citizen):
    make_citizen(phone="9000000001", password="secret123")
    response = client.post("/auth/login", json={"phone": "9000000001", "password": "secret123"})
    assert response.status_code == 200
    assert response.json()["access_token"]


def test_login_with_wrong_password_returns_401(client, make_citizen):
    make_citizen(phone="9000000001", password="secret123")
    response = client.post("/auth/login", json={"phone": "9000000001", "password": "wrong"})
    assert response.status_code == 401


def test_login_with_unknown_phone_returns_401_not_404(client):
    """Unknown phone and wrong password must look identical — never reveal which."""
    response = client.post("/auth/login", json={"phone": "0000000000", "password": "whatever"})
    assert response.status_code == 401


def test_me_requires_authentication(client):
    response = client.get("/auth/me")
    assert response.status_code == 401


def test_me_returns_current_user(client, make_citizen):
    token, user = make_citizen(phone="9000000001", full_name="Priya Deshmukh")
    response = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["full_name"] == "Priya Deshmukh"


def test_me_rejects_garbage_token(client):
    response = client.get("/auth/me", headers={"Authorization": "Bearer garbage.token.here"})
    assert response.status_code == 401


def test_patch_me_updates_preferred_language(client, make_citizen):
    token, _user = make_citizen(phone="9000000001", preferred_language="en")
    response = client.patch(
        "/auth/me", headers={"Authorization": f"Bearer {token}"}, json={"preferred_language": "hi"}
    )
    assert response.status_code == 200
    assert response.json()["preferred_language"] == "hi"


def test_patch_me_rejects_unsupported_language(client, make_citizen):
    token, _user = make_citizen(phone="9000000001")
    response = client.patch(
        "/auth/me", headers={"Authorization": f"Bearer {token}"}, json={"preferred_language": "fr"}
    )
    assert response.status_code == 400

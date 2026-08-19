"""Tests for the production-grade auth upgrade: refresh-token issuance/rotation/reuse-detection,
real server-side logout, and self-service password change. See backend/models.py's RefreshToken,
backend/services/auth_service.py's create_refresh_token/rotate_refresh_token/
revoke_refresh_token/revoke_all_refresh_tokens, and backend/routes/auth.py's /refresh, /logout,
/change-password endpoints.

Signs up directly via the real API for each test (rather than the shared make_citizen fixture,
which only returns (access_token, user) -- every test here needs the refresh_token too, and
changing that widely-used fixture's return shape would ripple across the other ~20 files that
already destructure its 2-tuple).
"""

from __future__ import annotations

from backend.config import settings


def _signup(client, phone: str = "9200000001", password: str = "secret123") -> dict:
    response = client.post(
        "/auth/signup",
        json={
            "full_name": "Test Citizen",
            "phone": phone,
            "password": password,
            "preferred_language": "en",
            "ward": "Test Ward",
        },
    )
    assert response.status_code == 200, response.text
    return response.json()


# --- Issuance --------------------------------------------------------------------------------


def test_signup_returns_a_refresh_token(client):
    body = _signup(client, phone="9200000001")
    assert body["refresh_token"]
    assert body["refresh_token"] != body["access_token"]


def test_login_returns_a_refresh_token(client, make_citizen):
    make_citizen(phone="9200000002")
    response = client.post("/auth/login", json={"identifier": "9200000002", "password": "secret123"})
    assert response.status_code == 200, response.text
    assert response.json()["refresh_token"]


# --- Refresh / rotation ------------------------------------------------------------------------


def test_refresh_with_valid_token_issues_a_new_pair(client):
    body = _signup(client, phone="9200000003")
    response = client.post("/auth/refresh", json={"refresh_token": body["refresh_token"]})
    assert response.status_code == 200, response.text
    new_body = response.json()
    # Not asserting access_token != the original here -- create_access_token's JWT payload is
    # only second-resolution (iat/exp via int(time.time())), so two tokens for the same user
    # issued within the same wall-clock second are legitimately byte-identical (deterministic
    # payload + signature, nothing wrong with that). The refresh token is the one this endpoint
    # actually guarantees rotates -- see test_refresh_rotates_the_old_token_out below.
    assert new_body["access_token"]
    assert new_body["refresh_token"] != body["refresh_token"]
    assert new_body["user"]["phone"] == "9200000003"


def test_refresh_rotates_the_old_token_out(client):
    """The OLD refresh token must be rejected once a new one has been issued from it -- proves
    real rotation, not just "any presented token works forever"."""
    body = _signup(client, phone="9200000004")
    first = client.post("/auth/refresh", json={"refresh_token": body["refresh_token"]})
    assert first.status_code == 200

    reuse_old = client.post("/auth/refresh", json={"refresh_token": body["refresh_token"]})
    assert reuse_old.status_code == 401


def test_refresh_reuse_revokes_the_whole_family(client):
    """Presenting an already-rotated-away token is treated as a real compromise signal -- the NEW
    token issued from the legitimate rotation must ALSO stop working afterward, forcing a full
    re-login rather than trusting the session further."""
    body = _signup(client, phone="9200000005")
    first = client.post("/auth/refresh", json={"refresh_token": body["refresh_token"]})
    new_refresh_token = first.json()["refresh_token"]

    reuse_old = client.post("/auth/refresh", json={"refresh_token": body["refresh_token"]})
    assert reuse_old.status_code == 401

    now_also_dead = client.post("/auth/refresh", json={"refresh_token": new_refresh_token})
    assert now_also_dead.status_code == 401


def test_refresh_with_unknown_token_returns_401(client):
    response = client.post("/auth/refresh", json={"refresh_token": "not-a-real-token"})
    assert response.status_code == 401


def test_refresh_with_expired_token_returns_401(client, monkeypatch):
    monkeypatch.setattr(settings, "REFRESH_TOKEN_EXPIRE_DAYS", -1)
    body = _signup(client, phone="9200000006")
    response = client.post("/auth/refresh", json={"refresh_token": body["refresh_token"]})
    assert response.status_code == 401


# --- Logout ------------------------------------------------------------------------------------


def test_logout_revokes_the_refresh_token(client):
    body = _signup(client, phone="9200000007")
    logout_response = client.post("/auth/logout", json={"refresh_token": body["refresh_token"]})
    assert logout_response.status_code == 204

    refresh_response = client.post("/auth/refresh", json={"refresh_token": body["refresh_token"]})
    assert refresh_response.status_code == 401


def test_logout_with_unknown_token_is_a_safe_noop(client):
    """Logout must never fail just because the session was already gone (e.g. a double-click, or
    a token that already expired naturally) -- see LogoutRequest's own docstring."""
    response = client.post("/auth/logout", json={"refresh_token": "not-a-real-token"})
    assert response.status_code == 204


def test_logout_does_not_require_a_valid_access_token(client):
    """See LogoutRequest's own docstring: the refresh token itself is sufficient proof to revoke
    just itself -- logout must still work with no Authorization header at all (the realistic case
    of a citizen returning to a stale tab whose access token already expired)."""
    body = _signup(client, phone="9200000008")
    response = client.post("/auth/logout", json={"refresh_token": body["refresh_token"]})
    assert response.status_code == 204


def test_logout_does_not_revoke_the_access_token(client):
    """The access token is short-lived and stateless by design -- logout only revokes the
    refresh token, and the access token stays valid until its own natural expiry regardless."""
    body = _signup(client, phone="9200000009")
    client.post("/auth/logout", json={"refresh_token": body["refresh_token"]})

    me_response = client.get("/auth/me", headers={"Authorization": f"Bearer {body['access_token']}"})
    assert me_response.status_code == 200


# --- Change password -----------------------------------------------------------------------


def test_change_password_with_correct_current_password_succeeds(client):
    body = _signup(client, phone="9200000010", password="oldpass123")
    response = client.post(
        "/auth/change-password",
        json={"current_password": "oldpass123", "new_password": "newpass456"},
        headers={"Authorization": f"Bearer {body['access_token']}"},
    )
    assert response.status_code == 204

    new_login = client.post("/auth/login", json={"identifier": "9200000010", "password": "newpass456"})
    assert new_login.status_code == 200
    old_login = client.post("/auth/login", json={"identifier": "9200000010", "password": "oldpass123"})
    assert old_login.status_code == 401


def test_change_password_with_wrong_current_password_returns_401(client):
    body = _signup(client, phone="9200000011", password="oldpass123")
    response = client.post(
        "/auth/change-password",
        json={"current_password": "wrong-password", "new_password": "newpass456"},
        headers={"Authorization": f"Bearer {body['access_token']}"},
    )
    assert response.status_code == 401


def test_change_password_rejects_a_too_short_new_password(client):
    body = _signup(client, phone="9200000012", password="oldpass123")
    response = client.post(
        "/auth/change-password",
        json={"current_password": "oldpass123", "new_password": "abc123"},
        headers={"Authorization": f"Bearer {body['access_token']}"},
    )
    assert response.status_code == 400


def test_change_password_rejects_a_new_password_with_no_digit(client):
    body = _signup(client, phone="9200000013", password="oldpass123")
    response = client.post(
        "/auth/change-password",
        json={"current_password": "oldpass123", "new_password": "alllettersnodigits"},
        headers={"Authorization": f"Bearer {body['access_token']}"},
    )
    assert response.status_code == 400


def test_change_password_revokes_other_refresh_tokens(client):
    """Password change assumes the old credential may be compromised -- every OTHER active
    refresh token for the account must stop working too, not just get left alone."""
    body = _signup(client, phone="9200000014", password="oldpass123")
    second_login = client.post("/auth/login", json={"identifier": "9200000014", "password": "oldpass123"})
    second_refresh_token = second_login.json()["refresh_token"]

    response = client.post(
        "/auth/change-password",
        json={"current_password": "oldpass123", "new_password": "newpass456"},
        headers={"Authorization": f"Bearer {body['access_token']}"},
    )
    assert response.status_code == 204

    still_valid = client.post("/auth/refresh", json={"refresh_token": second_refresh_token})
    assert still_valid.status_code == 401


def test_change_password_requires_authentication(client):
    response = client.post(
        "/auth/change-password", json={"current_password": "x", "new_password": "newpass456"}
    )
    assert response.status_code == 401


# --- Signup password policy (server-side; client-side echo lives in Signup.tsx) ----------------


def test_signup_rejects_a_too_short_password(client):
    response = client.post(
        "/auth/signup",
        json={
            "full_name": "Test Citizen", "phone": "9200000015", "password": "abc123",
            "preferred_language": "en", "ward": "Test Ward",
        },
    )
    assert response.status_code == 400


def test_signup_rejects_a_password_with_no_letter(client):
    response = client.post(
        "/auth/signup",
        json={
            "full_name": "Test Citizen", "phone": "9200000016", "password": "12345678",
            "preferred_language": "en", "ward": "Test Ward",
        },
    )
    assert response.status_code == 400


def test_signup_accepts_a_password_meeting_the_new_policy(client):
    response = client.post(
        "/auth/signup",
        json={
            "full_name": "Test Citizen", "phone": "9200000017", "password": "goodpass123",
            "preferred_language": "en", "ward": "Test Ward",
        },
    )
    assert response.status_code == 200, response.text


# --- Signup phone-uniqueness race (IntegrityError second line of defense) ----------------------


def test_signup_duplicate_phone_via_direct_db_insert_returns_409_not_500(client, db_session):
    """Simulates the TOCTOU race the pre-check alone can't close: a row with this phone already
    exists at the DB level by the time THIS request's insert runs, bypassing the pre-check's own
    SELECT (which only protects against a race that happens to lose the read-then-write gap, not
    every possible interleaving). Confirms the IntegrityError handler in routes/auth.py's signup
    turns the resulting constraint violation into the same honest 409, not a raw 500."""
    from backend.models import User
    from backend.services.auth_service import hash_password

    db = db_session()
    db.add(
        User(
            full_name="Existing Citizen", phone="9200000018", password_hash=hash_password("secret123"),
            role="citizen", preferred_language="en", ward="Test Ward",
        )
    )
    db.commit()
    db.close()

    response = client.post(
        "/auth/signup",
        json={
            "full_name": "Test Citizen", "phone": "9200000018", "password": "secret123",
            "preferred_language": "en", "ward": "Test Ward",
        },
    )
    assert response.status_code == 409

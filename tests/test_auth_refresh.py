"""Tests for the production-grade auth upgrade: refresh-token issuance/rotation/reuse-detection,
real server-side logout, and self-service password change. See backend/models.py's RefreshToken,
backend/services/auth_service.py's create_refresh_token/rotate_refresh_token/
revoke_refresh_token/revoke_all_refresh_tokens, and backend/routes/auth.py's /refresh, /logout,
/change-password endpoints.

Signs up directly via the real API for each test (rather than the shared make_citizen fixture,
which only returns (access_token, user) -- every test here needs the refresh_token too, and
changing that widely-used fixture's return shape would ripple across the other ~20 files that
already destructure its 2-tuple).

Email verification is mandatory at signup, decoupled from the rest of the form (see
backend/routes/auth.py's module docstring) -- _signup() below drives the full three-call round
trip itself (send-code, verify-code, then signup with the returned proof token), intercepting
backend.routes.auth.send_otp_email the same way tests/test_email_otp.py and conftest.py's
make_citizen do, so every test in this file keeps the same "one call, get back the full
AuthResponse dict" shape it always had.
"""

from __future__ import annotations

from backend.config import settings


def _signup(client, monkeypatch, phone: str = "9200000001", password: str = "secret123!") -> dict:
    email = f"citizen{phone}@example.com"
    sent_codes: list[str] = []
    monkeypatch.setattr(
        "backend.routes.auth.send_otp_email",
        lambda to_email, code, purpose: sent_codes.append(code),
    )

    send_response = client.post("/auth/signup/email/send-code", json={"email": email})
    assert send_response.status_code == 204, send_response.text
    assert sent_codes, "signup should have emailed a verification code"

    verify_response = client.post(
        "/auth/signup/email/verify-code", json={"email": email, "code": sent_codes[-1]}
    )
    assert verify_response.status_code == 200, verify_response.text
    token = verify_response.json()["email_verification_token"]

    response = client.post(
        "/auth/signup",
        json={
            "full_name": "Test Citizen",
            "phone": phone,
            "email": email,
            "email_verification_token": token,
            "password": password,
            "preferred_language": "en",
            "ward": "Test Ward",
        },
    )
    assert response.status_code == 200, response.text
    return response.json()


# --- Issuance --------------------------------------------------------------------------------


def test_signup_returns_a_refresh_token(client, monkeypatch):
    body = _signup(client, monkeypatch, phone="9200000001")
    assert body["refresh_token"]
    assert body["refresh_token"] != body["access_token"]


def test_login_returns_a_refresh_token(client, make_citizen):
    make_citizen(phone="9200000002")
    response = client.post("/auth/login", json={"identifier": "9200000002", "password": "secret123!"})
    assert response.status_code == 200, response.text
    assert response.json()["refresh_token"]


# --- Refresh / rotation ------------------------------------------------------------------------


def test_refresh_with_valid_token_issues_a_new_pair(client, monkeypatch):
    body = _signup(client, monkeypatch, phone="9200000003")
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


def test_refresh_rotates_the_old_token_out(client, monkeypatch):
    """The OLD refresh token must be rejected once a new one has been issued from it -- proves
    real rotation, not just "any presented token works forever"."""
    body = _signup(client, monkeypatch, phone="9200000004")
    first = client.post("/auth/refresh", json={"refresh_token": body["refresh_token"]})
    assert first.status_code == 200

    reuse_old = client.post("/auth/refresh", json={"refresh_token": body["refresh_token"]})
    assert reuse_old.status_code == 401


def test_refresh_reuse_revokes_the_whole_family(client, monkeypatch):
    """Presenting an already-rotated-away token is treated as a real compromise signal -- the NEW
    token issued from the legitimate rotation must ALSO stop working afterward, forcing a full
    re-login rather than trusting the session further."""
    body = _signup(client, monkeypatch, phone="9200000005")
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
    body = _signup(client, monkeypatch, phone="9200000006")
    response = client.post("/auth/refresh", json={"refresh_token": body["refresh_token"]})
    assert response.status_code == 401


# --- Logout ------------------------------------------------------------------------------------


def test_logout_revokes_the_refresh_token(client, monkeypatch):
    body = _signup(client, monkeypatch, phone="9200000007")
    logout_response = client.post("/auth/logout", json={"refresh_token": body["refresh_token"]})
    assert logout_response.status_code == 204

    refresh_response = client.post("/auth/refresh", json={"refresh_token": body["refresh_token"]})
    assert refresh_response.status_code == 401


def test_logout_with_unknown_token_is_a_safe_noop(client):
    """Logout must never fail just because the session was already gone (e.g. a double-click, or
    a token that already expired naturally) -- see LogoutRequest's own docstring."""
    response = client.post("/auth/logout", json={"refresh_token": "not-a-real-token"})
    assert response.status_code == 204


def test_logout_does_not_require_a_valid_access_token(client, monkeypatch):
    """See LogoutRequest's own docstring: the refresh token itself is sufficient proof to revoke
    just itself -- logout must still work with no Authorization header at all (the realistic case
    of a citizen returning to a stale tab whose access token already expired)."""
    body = _signup(client, monkeypatch, phone="9200000008")
    response = client.post("/auth/logout", json={"refresh_token": body["refresh_token"]})
    assert response.status_code == 204


def test_logout_does_not_revoke_the_access_token(client, monkeypatch):
    """The access token is short-lived and stateless by design -- logout only revokes the
    refresh token, and the access token stays valid until its own natural expiry regardless."""
    body = _signup(client, monkeypatch, phone="9200000009")
    client.post("/auth/logout", json={"refresh_token": body["refresh_token"]})

    me_response = client.get("/auth/me", headers={"Authorization": f"Bearer {body['access_token']}"})
    assert me_response.status_code == 200


# --- Change password -----------------------------------------------------------------------


def test_change_password_with_correct_current_password_succeeds(client, monkeypatch):
    body = _signup(client, monkeypatch, phone="9200000010", password="oldpass123!")
    response = client.post(
        "/auth/change-password",
        json={"current_password": "oldpass123!", "new_password": "newpass456!"},
        headers={"Authorization": f"Bearer {body['access_token']}"},
    )
    assert response.status_code == 204

    new_login = client.post("/auth/login", json={"identifier": "9200000010", "password": "newpass456!"})
    assert new_login.status_code == 200
    old_login = client.post("/auth/login", json={"identifier": "9200000010", "password": "oldpass123!"})
    assert old_login.status_code == 401


def test_change_password_with_wrong_current_password_returns_401(client, monkeypatch):
    body = _signup(client, monkeypatch, phone="9200000011", password="oldpass123!")
    response = client.post(
        "/auth/change-password",
        json={"current_password": "wrong-password", "new_password": "newpass456!"},
        headers={"Authorization": f"Bearer {body['access_token']}"},
    )
    assert response.status_code == 401


def test_change_password_rejects_a_too_short_new_password(client, monkeypatch):
    body = _signup(client, monkeypatch, phone="9200000012", password="oldpass123!")
    response = client.post(
        "/auth/change-password",
        json={"current_password": "oldpass123!", "new_password": "abc123"},
        headers={"Authorization": f"Bearer {body['access_token']}"},
    )
    assert response.status_code == 400


def test_change_password_rejects_a_new_password_with_no_digit(client, monkeypatch):
    body = _signup(client, monkeypatch, phone="9200000013", password="oldpass123!")
    response = client.post(
        "/auth/change-password",
        json={"current_password": "oldpass123!", "new_password": "alllettersnodigits"},
        headers={"Authorization": f"Bearer {body['access_token']}"},
    )
    assert response.status_code == 400


def test_change_password_revokes_other_refresh_tokens(client, monkeypatch):
    """Password change assumes the old credential may be compromised -- every OTHER active
    refresh token for the account must stop working too, not just get left alone."""
    body = _signup(client, monkeypatch, phone="9200000014", password="oldpass123!")
    second_login = client.post("/auth/login", json={"identifier": "9200000014", "password": "oldpass123!"})
    second_refresh_token = second_login.json()["refresh_token"]

    response = client.post(
        "/auth/change-password",
        json={"current_password": "oldpass123!", "new_password": "newpass456!"},
        headers={"Authorization": f"Bearer {body['access_token']}"},
    )
    assert response.status_code == 204

    still_valid = client.post("/auth/refresh", json={"refresh_token": second_refresh_token})
    assert still_valid.status_code == 401


def test_change_password_requires_authentication(client):
    response = client.post(
        "/auth/change-password", json={"current_password": "x", "new_password": "newpass456!"}
    )
    assert response.status_code == 401


# --- Signup password policy (server-side; client-side echo lives in Signup.tsx) ----------------
# Password strength is validated before email_verification_token is checked (see routes/auth.py's
# signup()), so these can use an obviously-fake token and still exercise the intended 400 path --
# an empty string is enough to satisfy SignupRequest's Pydantic schema without a real email
# verification round trip.


def test_signup_rejects_a_too_short_password(client):
    response = client.post(
        "/auth/signup",
        json={
            "full_name": "Test Citizen", "phone": "9200000015", "email": "c9200000015@example.com",
            "email_verification_token": "", "password": "abc123", "preferred_language": "en", "ward": "Test Ward",
        },
    )
    assert response.status_code == 400


def test_signup_rejects_a_password_with_no_letter(client):
    response = client.post(
        "/auth/signup",
        json={
            "full_name": "Test Citizen", "phone": "9200000016", "email": "c9200000016@example.com",
            "email_verification_token": "", "password": "12345678", "preferred_language": "en", "ward": "Test Ward",
        },
    )
    assert response.status_code == 400


def test_signup_accepts_a_password_meeting_the_new_policy(client, monkeypatch):
    """A password meeting the policy, combined with a real verified-email proof token, creates
    the account directly -- 200 with a full AuthResponse, not a 204 (see this file's module
    docstring: signup is a single call now, not two-phase)."""
    body = _signup(client, monkeypatch, phone="9200000017", password="goodpass123!")
    assert body["access_token"]
    assert body["user"]["phone"] == "9200000017"


# --- Signup phone-uniqueness race (IntegrityError second line of defense) ----------------------


def test_signup_duplicate_phone_via_direct_db_insert_returns_409(client, db_session):
    """A row with this phone already existing at request time is caught by POST /auth/signup's
    own pre-check SELECT -- see test_signup_duplicate_phone_race_returns_409_not_500 below for
    the real IntegrityError fallback, which only comes into play for a race that happens *after*
    this pre-check. Uses an obviously-fake email_verification_token since the pre-check runs
    before that token is ever consumed."""
    from backend.models import User
    from backend.services.auth_service import hash_password

    db = db_session()
    db.add(
        User(
            full_name="Existing Citizen", phone="9200000018", password_hash=hash_password("secret123!"),
            role="citizen", preferred_language="en", ward="Test Ward",
        )
    )
    db.commit()
    db.close()

    response = client.post(
        "/auth/signup",
        json={
            "full_name": "Test Citizen", "phone": "9200000018", "email": "c9200000018@example.com",
            "email_verification_token": "", "password": "secret123!", "preferred_language": "en", "ward": "Test Ward",
        },
    )
    assert response.status_code == 409


def test_signup_duplicate_phone_race_returns_409_not_500(client, db_session, monkeypatch):
    """Simulates the TOCTOU race the pre-check alone can't close: a row with this phone gets
    inserted at the DB level *between* the email-verification round trip and POST /auth/signup's
    actual INSERT into `users` -- bypassing the pre-check, which only protects against a race
    that happens to lose the read-then-write gap, not every possible interleaving. Confirms the
    IntegrityError handler in routes/auth.py's signup() turns the resulting constraint violation
    into the same honest 409, not a raw 500."""
    from backend.models import User
    from backend.services.auth_service import hash_password

    phone = "9200000019"
    email = "c9200000019@example.com"
    sent_codes: list[str] = []
    monkeypatch.setattr(
        "backend.routes.auth.send_otp_email",
        lambda to_email, code, purpose: sent_codes.append(code),
    )
    send_response = client.post("/auth/signup/email/send-code", json={"email": email})
    assert send_response.status_code == 204, send_response.text

    verify_response = client.post(
        "/auth/signup/email/verify-code", json={"email": email, "code": sent_codes[-1]}
    )
    assert verify_response.status_code == 200, verify_response.text
    token = verify_response.json()["email_verification_token"]

    # The race: a real account with this same phone appears only now, after the email was
    # verified but before the final POST /auth/signup call.
    db = db_session()
    db.add(
        User(
            full_name="Existing Citizen", phone=phone, password_hash=hash_password("secret123!"),
            role="citizen", preferred_language="en", ward="Test Ward",
        )
    )
    db.commit()
    db.close()

    response = client.post(
        "/auth/signup",
        json={
            "full_name": "Test Citizen", "phone": phone, "email": email,
            "email_verification_token": token, "password": "secret123!", "preferred_language": "en", "ward": "Test Ward",
        },
    )
    assert response.status_code == 409, response.text

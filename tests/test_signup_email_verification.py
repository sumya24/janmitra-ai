"""Tests for the mandatory, inline email-verification flow behind Signup.tsx's "Verify" button:
POST /auth/signup/email/send-code, POST /auth/signup/email/verify-code, and the final
POST /auth/signup call that actually creates the account using the proof token verify-code
returns. See backend/routes/auth.py's module docstring and backend/models.py's
SignupEmailVerification for the design.

backend.routes.auth.send_otp_email is monkeypatched in every test below to record calls instead
of hitting real SMTP, same pattern as tests/test_email_otp.py.
"""

from __future__ import annotations

from backend.config import settings
from backend.models import SignupEmailVerification, User


def _fake_send_otp_email(monkeypatch):
    sent = []

    def _fake(to_email, code, purpose):
        sent.append((to_email, code, purpose))

    monkeypatch.setattr("backend.routes.auth.send_otp_email", _fake)
    return sent


def _signup_body(phone: str, email: str, token: str) -> dict:
    return {
        "full_name": "Test Citizen", "phone": phone, "email": email,
        "email_verification_token": token, "password": "secret123!",
        "preferred_language": "en", "ward": "Test Ward",
    }


def _get_verification_token(client, monkeypatch, email: str) -> str:
    """Drives the send-code -> verify-code round trip and returns the proof token, for tests that
    only care about the final POST /auth/signup call."""
    sent = _fake_send_otp_email(monkeypatch)
    send_response = client.post("/auth/signup/email/send-code", json={"email": email})
    assert send_response.status_code == 204, send_response.text
    code = sent[-1][1]

    verify_response = client.post("/auth/signup/email/verify-code", json={"email": email, "code": code})
    assert verify_response.status_code == 200, verify_response.text
    return verify_response.json()["email_verification_token"]


# --- Send code ---------------------------------------------------------------------------------


def test_send_code_emails_a_verification_code_and_creates_no_user_yet(client, db_session, monkeypatch):
    sent = _fake_send_otp_email(monkeypatch)
    response = client.post("/auth/signup/email/send-code", json={"email": "citizen1@example.com"})
    assert response.status_code == 204
    assert len(sent) == 1
    assert sent[0][0] == "citizen1@example.com"
    assert sent[0][2] == "verify_email"

    db = db_session()
    assert db.query(User).count() == 0
    row = db.query(SignupEmailVerification).one()
    assert row.email == "citizen1@example.com"
    assert row.verified_at is None
    db.close()


def test_send_code_returns_503_when_smtp_not_configured(client, monkeypatch):
    """No monkeypatch of send_otp_email here -- the real SMTP path runs, and with blank
    SMTP_USERNAME/SMTP_PASSWORD (the default test environment) it must fail as a clear 503."""
    monkeypatch.setattr(settings, "SMTP_USERNAME", "")
    monkeypatch.setattr(settings, "SMTP_PASSWORD", "")
    response = client.post("/auth/signup/email/send-code", json={"email": "citizen1@example.com"})
    assert response.status_code == 503


def test_send_code_rejects_email_already_used_by_a_verified_account(client, make_citizen, monkeypatch):
    make_citizen(phone="9300000002", email="taken@example.com")
    _fake_send_otp_email(monkeypatch)
    response = client.post("/auth/signup/email/send-code", json={"email": "taken@example.com"})
    assert response.status_code == 409


def test_send_code_rejects_malformed_email(client):
    response = client.post("/auth/signup/email/send-code", json={"email": "not-an-email"})
    assert response.status_code == 400


# --- Verify code (issues the proof token POST /auth/signup redeems) ----------------------------


def test_verify_code_with_correct_code_issues_a_proof_token(client, monkeypatch):
    sent = _fake_send_otp_email(monkeypatch)
    client.post("/auth/signup/email/send-code", json={"email": "citizen10@example.com"})
    code = sent[-1][1]

    response = client.post("/auth/signup/email/verify-code", json={"email": "citizen10@example.com", "code": code})
    assert response.status_code == 200, response.text
    assert response.json()["email_verification_token"]


def test_verify_code_with_wrong_code_does_not_issue_a_token(client, monkeypatch):
    sent = _fake_send_otp_email(monkeypatch)
    client.post("/auth/signup/email/send-code", json={"email": "citizen12@example.com"})
    real_code = sent[-1][1]
    wrong_code = "000000" if real_code != "000000" else "111111"

    response = client.post("/auth/signup/email/verify-code", json={"email": "citizen12@example.com", "code": wrong_code})
    assert response.status_code == 400

    # The real code must still work afterward -- one wrong guess doesn't burn the row outright.
    ok = client.post("/auth/signup/email/verify-code", json={"email": "citizen12@example.com", "code": real_code})
    assert ok.status_code == 200, ok.text


def test_verify_code_exhausted_after_max_attempts(client, monkeypatch):
    monkeypatch.setattr(settings, "OTP_MAX_ATTEMPTS", 2)
    sent = _fake_send_otp_email(monkeypatch)
    client.post("/auth/signup/email/send-code", json={"email": "citizen13@example.com"})
    real_code = sent[-1][1]
    wrong_code = "000000" if real_code != "000000" else "111111"

    for _ in range(2):
        response = client.post("/auth/signup/email/verify-code", json={"email": "citizen13@example.com", "code": wrong_code})
        assert response.status_code == 400

    exhausted = client.post("/auth/signup/email/verify-code", json={"email": "citizen13@example.com", "code": real_code})
    assert exhausted.status_code == 400


def test_verify_code_with_expired_code_fails(client, monkeypatch):
    monkeypatch.setattr(settings, "OTP_EXPIRE_MINUTES", -1)
    sent = _fake_send_otp_email(monkeypatch)
    client.post("/auth/signup/email/send-code", json={"email": "citizen14@example.com"})
    code = sent[-1][1]

    response = client.post("/auth/signup/email/verify-code", json={"email": "citizen14@example.com", "code": code})
    assert response.status_code == 400


def test_verify_code_with_unknown_email_fails(client):
    response = client.post("/auth/signup/email/verify-code", json={"email": "nobody-sent-a-code@example.com", "code": "123456"})
    assert response.status_code == 400


def test_resend_uses_the_latest_code(client, monkeypatch):
    """A citizen who requests a second code (e.g. didn't receive the first) should be able to use
    the newer one -- the older row is simply superseded, not treated as an error."""
    sent = _fake_send_otp_email(monkeypatch)
    client.post("/auth/signup/email/send-code", json={"email": "citizen16@example.com"})
    client.post("/auth/signup/email/send-code", json={"email": "citizen16@example.com"})
    assert len(sent) == 2
    latest_code = sent[-1][1]

    response = client.post("/auth/signup/email/verify-code", json={"email": "citizen16@example.com", "code": latest_code})
    assert response.status_code == 200, response.text


# --- Signup (redeems the proof token, actually creates the account) ----------------------------


def test_signup_with_valid_proof_token_creates_the_account(client, monkeypatch):
    email = "citizen20@example.com"
    token = _get_verification_token(client, monkeypatch, email)

    response = client.post("/auth/signup", json=_signup_body("9300000020", email, token))
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["access_token"]
    assert body["refresh_token"]
    assert body["user"]["phone"] == "9300000020"
    assert body["user"]["email"] == email
    assert body["user"]["email_verified"] is True
    assert body["user"]["role"] == "citizen"


def test_signup_can_log_in_afterward_by_phone_or_email(client, monkeypatch):
    email = "citizen21@example.com"
    token = _get_verification_token(client, monkeypatch, email)
    client.post("/auth/signup", json=_signup_body("9300000021", email, token))

    login = client.post("/auth/login", json={"identifier": "9300000021", "password": "secret123!"})
    assert login.status_code == 200
    login_by_email = client.post("/auth/login", json={"identifier": email, "password": "secret123!"})
    assert login_by_email.status_code == 200


def test_signup_rejects_a_reused_proof_token(client, db_session, monkeypatch):
    """A proof token can only ever create one account -- see
    consume_signup_email_verification's own docstring."""
    email = "citizen22@example.com"
    token = _get_verification_token(client, monkeypatch, email)

    first = client.post("/auth/signup", json=_signup_body("9300000022", email, token))
    assert first.status_code == 200, first.text

    replay = client.post("/auth/signup", json=_signup_body("9300000023", "citizen22b@example.com", token))
    assert replay.status_code == 400

    db = db_session()
    assert db.query(User).filter(User.phone == "9300000023").first() is None
    db.close()


def test_signup_rejects_an_expired_proof_token(client, monkeypatch):
    monkeypatch.setattr(settings, "EMAIL_VERIFICATION_TOKEN_EXPIRE_MINUTES", -1)
    email = "citizen24@example.com"
    token = _get_verification_token(client, monkeypatch, email)

    response = client.post("/auth/signup", json=_signup_body("9300000024", email, token))
    assert response.status_code == 400


def test_signup_rejects_a_token_issued_for_a_different_email(client, monkeypatch):
    """A proof token is only valid for the exact email address it was issued for -- swapping in a
    different (even if separately verified) email must not let it through."""
    token_for_a = _get_verification_token(client, monkeypatch, "citizen25a@example.com")

    response = client.post("/auth/signup", json=_signup_body("9300000025", "citizen25b@example.com", token_for_a))
    assert response.status_code == 400


def test_signup_rejects_an_unverified_token(client):
    response = client.post(
        "/auth/signup",
        json=_signup_body("9300000026", "citizen26@example.com", "not-a-real-token"),
    )
    assert response.status_code == 400

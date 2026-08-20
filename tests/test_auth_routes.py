"""Integration tests for /auth/signup(+/email/send-code,/email/verify-code), /auth/login, and
/auth/me.

Note the absence of any test that tries to sign up as "worker" or "admin" —
there is no such option in the API to test against; sign-up always produces
a citizen account (see routes/auth.py).

Email verification is mandatory at signup but decoupled from the rest of the form behind its own
"Verify" button on the frontend (see routes/auth.py's module docstring):
POST /auth/signup/email/send-code + POST /auth/signup/email/verify-code handle that round trip
using only the email address and return a one-time proof token; POST /auth/signup then creates
the account directly, but only if it can present that token. _signup_and_verify() below drives
the full three-call round trip (intercepting backend.routes.auth.send_otp_email the same way
conftest.py's make_citizen does) for the tests that need a real created account. The
validation-rejection tests below that only need a 400/409/422 from POST /auth/signup itself pass
an obviously-fake email_verification_token -- SignupRequest requires the field to be present at
all (a Pydantic-level 422 otherwise), but most of those tests are checking a validation that runs
before the token is ever consumed (see routes/auth.py's signup() for the exact order), so a fake
value is enough to reach the intended app-level check.
"""

from backend.models import User
from tests.test_location_system import _seed_full_hierarchy


def _signup_and_verify(client, monkeypatch, **signup_fields) -> dict:
    email = signup_fields.setdefault("email", f"c{signup_fields['phone']}@example.com")
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
    signup_fields["email_verification_token"] = verify_response.json()["email_verification_token"]

    response = client.post("/auth/signup", json=signup_fields)
    assert response.status_code == 200, response.text
    return response.json()


def test_signup_creates_citizen_and_returns_token(client, monkeypatch):
    body = _signup_and_verify(
        client, monkeypatch,
        full_name="Priya Deshmukh", phone="9000000001", password="secret123!",
        preferred_language="mr", ward="Ward 14",
    )
    assert body["user"]["role"] == "citizen"
    assert body["user"]["preferred_language"] == "mr"
    assert body["user"]["ward"] == "Ward 14"
    assert body["user"]["email_verified"] is True
    assert body["access_token"]


def test_signup_rejects_missing_ward(client):
    response = client.post(
        "/auth/signup",
        json={
            "full_name": "Priya", "phone": "9000000001", "email": "priya@example.com",
            "password": "secret123!", "preferred_language": "en",
        },
    )
    assert response.status_code == 422


def test_signup_rejects_missing_email(client):
    response = client.post(
        "/auth/signup",
        json={
            "full_name": "Priya", "phone": "9000000001", "password": "secret123!",
            "preferred_language": "en", "ward": "Ward 14",
        },
    )
    assert response.status_code == 422


def test_signup_rejects_malformed_email(client):
    response = client.post(
        "/auth/signup",
        json={
            "full_name": "Priya", "phone": "9000000001", "email": "not-an-email",
            "email_verification_token": "", "password": "secret123!", "preferred_language": "en", "ward": "Ward 14",
        },
    )
    assert response.status_code == 400


def test_signup_rejects_blank_ward(client):
    response = client.post(
        "/auth/signup",
        json={
            "full_name": "Priya", "phone": "9000000001", "email": "priya@example.com",
            "email_verification_token": "", "password": "secret123!", "preferred_language": "en", "ward": "   ",
        },
    )
    assert response.status_code == 400


def test_signup_rejects_duplicate_phone(client, make_citizen):
    make_citizen(phone="9000000001")
    response = client.post(
        "/auth/signup",
        json={
            "full_name": "Someone Else",
            "phone": "9000000001",
            "email": "someone-else@example.com",
            "email_verification_token": "",
            "password": "secret123!",
            "preferred_language": "en",
            "ward": "Ward 14",
        },
    )
    assert response.status_code == 409


def test_signup_email_send_code_rejects_duplicate_verified_email(client, make_citizen):
    """Email uniqueness is checked at POST /auth/signup/email/send-code now, not at the final
    POST /auth/signup call -- see that endpoint's own docstring: it fails fast, before even
    sending an OTP, rather than making a citizen complete the whole verification round trip only
    to be rejected at the last step."""
    make_citizen(phone="9000000001", email="taken@example.com")
    response = client.post("/auth/signup/email/send-code", json={"email": "taken@example.com"})
    assert response.status_code == 409


def test_signup_rejects_non_numeric_phone(client):
    """Real gap this closes: previously any non-empty string was accepted as a phone number."""
    response = client.post(
        "/auth/signup",
        json={
            "full_name": "Priya", "phone": "not-a-phone", "email": "priya@example.com",
            "email_verification_token": "", "password": "secret123!", "preferred_language": "en", "ward": "Ward 14",
        },
    )
    assert response.status_code == 400


def test_signup_rejects_phone_with_wrong_digit_count(client):
    response = client.post(
        "/auth/signup",
        json={
            "full_name": "Priya", "phone": "12345", "email": "priya@example.com",
            "email_verification_token": "", "password": "secret123!", "preferred_language": "en", "ward": "Ward 14",
        },
    )
    assert response.status_code == 400


def test_signup_rejects_phone_starting_with_invalid_digit(client):
    """Indian mobile numbers start 6-9 -- a landline-shaped "0..." or "1..." number is rejected."""
    response = client.post(
        "/auth/signup",
        json={
            "full_name": "Priya", "phone": "0123456789", "email": "priya@example.com",
            "email_verification_token": "", "password": "secret123!", "preferred_language": "en", "ward": "Ward 14",
        },
    )
    assert response.status_code == 400


def test_signup_rejects_short_password(client):
    response = client.post(
        "/auth/signup",
        json={
            "full_name": "Priya", "phone": "9000000001", "email": "priya@example.com",
            "email_verification_token": "", "password": "abc", "preferred_language": "en", "ward": "Ward 14",
        },
    )
    assert response.status_code == 400


def test_signup_rejects_unsupported_language(client):
    response = client.post(
        "/auth/signup",
        json={
            "full_name": "Priya", "phone": "9000000001", "email": "priya@example.com",
            "email_verification_token": "", "password": "secret123!", "preferred_language": "fr", "ward": "Ward 14",
        },
    )
    assert response.status_code == 400


def test_signup_rejects_unverified_email(client):
    """The core guarantee this whole feature exists for: POST /auth/signup with a well-formed but
    never-verified email_verification_token must never create an account."""
    response = client.post(
        "/auth/signup",
        json={
            "full_name": "Priya", "phone": "9000000001", "email": "priya@example.com",
            "email_verification_token": "not-a-real-token", "password": "secret123!",
            "preferred_language": "en", "ward": "Ward 14",
        },
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Email is not verified. Please verify your email address first."


def test_login_with_correct_credentials_succeeds(client, make_citizen):
    make_citizen(phone="9000000001", password="secret123!")
    response = client.post("/auth/login", json={"identifier": "9000000001", "password": "secret123!"})
    assert response.status_code == 200
    assert response.json()["access_token"]


def test_login_with_wrong_password_returns_401(client, make_citizen):
    make_citizen(phone="9000000001", password="secret123!")
    response = client.post("/auth/login", json={"identifier": "9000000001", "password": "wrong"})
    assert response.status_code == 401


def test_login_with_unknown_phone_returns_401_not_404(client):
    """Unknown phone and wrong password must look identical — never reveal which."""
    response = client.post("/auth/login", json={"identifier": "0000000000", "password": "whatever"})
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


# --- optional structured home_*_id fields (the new State/City/Ward/Area picker) -- see
# routes/auth.py's SignupRequest and _resolve_home_location, and routes/locations.py.
# Deliberately additive: none of the tests above (which never send these fields) needed any
# change for this feature to land -- the existing `ward` free-text behavior is untouched. ---


def test_signup_without_home_location_fields_still_works_unchanged(client, db_session, monkeypatch):
    """The common case today (only 6 of 36 states have real seeded data): a citizen signs up
    with no home_*_id fields at all, exactly like before this feature existed."""
    body = _signup_and_verify(
        client, monkeypatch,
        full_name="Priya", phone="9000000001", password="secret123!",
        preferred_language="en", ward="Ward 14",
    )
    assert body["user"]["ward"] == "Ward 14"

    db = db_session()
    user = db.query(User).filter(User.phone == "9000000001").first()
    assert user.home_state_id is None
    assert user.home_ward_id is None
    db.close()


def test_signup_with_home_ward_id_derives_full_parent_chain(client, db_session, monkeypatch):
    """Sending only the deepest selection (home_ward_id) is enough -- state/district/ulb are
    derived server-side from it, not required from the client."""
    db = db_session()
    chain = _seed_full_hierarchy(db)
    state_id, district_id, ulb_id, ward_id = chain["state"].id, chain["district"].id, chain["ulb"].id, chain["ward"].id
    db.close()

    _signup_and_verify(
        client, monkeypatch,
        full_name="Priya", phone="9000000002", password="secret123!",
        preferred_language="en", ward="Ward 14", home_ward_id=ward_id,
    )

    db = db_session()
    user = db.query(User).filter(User.phone == "9000000002").first()
    assert user.home_state_id == state_id
    assert user.home_district_id == district_id
    assert user.home_ulb_id == ulb_id
    assert user.home_ward_id == ward_id
    # The existing free-text ward field is completely unaffected by the structured picker.
    assert user.ward == "Ward 14"
    db.close()


def test_signup_with_home_locality_id_derives_ward_and_above(client, db_session, monkeypatch):
    db = db_session()
    chain = _seed_full_hierarchy(db)
    ward_id, locality_id = chain["ward"].id, chain["locality"].id
    db.close()

    _signup_and_verify(
        client, monkeypatch,
        full_name="Priya", phone="9000000003", password="secret123!",
        preferred_language="en", ward="Ward 14", home_locality_id=locality_id,
    )

    db = db_session()
    user = db.query(User).filter(User.phone == "9000000003").first()
    assert user.home_ward_id == ward_id
    assert user.home_locality_id == locality_id
    db.close()


def test_signup_with_nonexistent_home_ward_id_is_rejected(client, monkeypatch):
    """Uses a real, verified email_verification_token (via the full send-code/verify-code round
    trip) so this actually reaches _resolve_home_location's own validation -- a fake token would
    also 400, but for the wrong reason ("email not verified" instead of "ward not found"), since
    the phone/token checks in signup() both run before home-location resolution."""
    email = "priya4@example.com"
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

    response = client.post(
        "/auth/signup",
        json={
            "full_name": "Priya", "phone": "9000000004", "email": email,
            "email_verification_token": token, "password": "secret123!", "preferred_language": "en",
            "ward": "Ward 14", "home_ward_id": 999999,
        },
    )
    assert response.status_code == 400

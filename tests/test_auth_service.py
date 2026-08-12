"""Unit tests for password hashing and the stdlib-only JWT implementation."""

import time
from types import SimpleNamespace

import pytest

from backend.services.auth_service import (
    InvalidTokenError,
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


def test_hash_password_does_not_store_plaintext():
    """The stored hash should never equal the original password."""
    password_hash = hash_password("correct-horse-battery-staple")
    assert password_hash != "correct-horse-battery-staple"


def test_verify_password_accepts_correct_password():
    password_hash = hash_password("correct-horse-battery-staple")
    assert verify_password("correct-horse-battery-staple", password_hash) is True


def test_verify_password_rejects_wrong_password():
    password_hash = hash_password("correct-horse-battery-staple")
    assert verify_password("wrong-password", password_hash) is False


def test_verify_password_rejects_malformed_hash_without_raising():
    assert verify_password("anything", "not-a-real-bcrypt-hash") is False


def test_access_token_round_trips_user_identity():
    user = SimpleNamespace(id=42, role="citizen")
    token = create_access_token(user)
    payload = decode_access_token(token)
    assert payload["sub"] == "42"
    assert payload["role"] == "citizen"


def test_decode_rejects_tampered_signature():
    user = SimpleNamespace(id=1, role="citizen")
    token = create_access_token(user)
    header_b64, payload_b64, _signature_b64 = token.split(".")
    tampered = f"{header_b64}.{payload_b64}.not-the-real-signature"
    with pytest.raises(InvalidTokenError):
        decode_access_token(tampered)


def test_decode_rejects_malformed_token():
    with pytest.raises(InvalidTokenError):
        decode_access_token("this-is-not-a-jwt")


def test_decode_rejects_expired_token(monkeypatch):
    user = SimpleNamespace(id=1, role="citizen")
    monkeypatch.setattr("backend.services.auth_service.settings.JWT_EXPIRE_MINUTES", 0)
    token = create_access_token(user)
    time.sleep(1.1)
    with pytest.raises(InvalidTokenError):
        decode_access_token(token)

"""Property-based tests (Hypothesis) for the pure/deterministic logic in the backend.

These complement the example-based tests elsewhere in tests/: instead of a handful of
hand-picked inputs, Hypothesis generates a wide range of inputs to check invariants that
should hold for *any* value, not just the ones a developer thought to try.
"""

from dataclasses import dataclass

import pytest
from hypothesis import given, settings as hypothesis_settings, strategies as st

from backend.config import to_bcp47, settings
from backend.services.auth_service import (
    InvalidTokenError,
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


# bcrypt only uses the first 72 *bytes* of a password; staying well under that (and
# sticking to single-byte codepoints) keeps every generated case a true round trip
# instead of accidentally exercising bcrypt's truncation behavior.
password_strategy = st.text(min_size=1, max_size=30, alphabet=st.characters(min_codepoint=0x20, max_codepoint=0x7E))


# bcrypt's cost factor makes each hash take ~100-400ms by design (that's the point of
# it), which blows Hypothesis's default 200ms per-example deadline and its default 100
# examples. Disable the deadline and cap examples so these still run in reasonable time.
@hypothesis_settings(deadline=None, max_examples=20)
@given(password=password_strategy)
def test_hash_password_round_trips_for_any_password(password: str) -> None:
    """Any password verifies successfully against its own hash."""
    hashed = hash_password(password)
    assert verify_password(password, hashed) is True


@hypothesis_settings(deadline=None, max_examples=20)
@given(password=password_strategy, other=password_strategy)
def test_verify_password_rejects_any_different_password(password: str, other: str) -> None:
    """A password only ever verifies against its own hash, never another's."""
    if password == other:
        return
    hashed = hash_password(password)
    assert verify_password(other, hashed) is False


@dataclass
class _FakeUser:
    id: int
    role: str


user_id_strategy = st.integers(min_value=1, max_value=2_147_483_647)
role_strategy = st.sampled_from(["citizen", "worker", "admin"])


@given(user_id=user_id_strategy, role=role_strategy)
def test_access_token_round_trips_for_any_user(user_id: int, role: str) -> None:
    """Any (id, role) pair encodes into a token that decodes back to the same values."""
    token = create_access_token(_FakeUser(id=user_id, role=role))
    payload = decode_access_token(token)
    assert payload["sub"] == str(user_id)
    assert payload["role"] == role


@given(garbage=st.text(min_size=0, max_size=100))
def test_decode_access_token_never_raises_uncaught_exception_on_garbage(garbage: str) -> None:
    """Arbitrary, non-token input is always rejected as InvalidTokenError, never crashes."""
    try:
        decode_access_token(garbage)
    except InvalidTokenError:
        pass
    else:
        # Vanishingly unlikely for random text to be a validly-signed token, but if it
        # ever happens the payload must still be well-formed.
        pass


@given(code=st.sampled_from(list(settings.SUPPORTED_LANGUAGES.keys())))
def test_to_bcp47_is_defined_for_every_supported_language(code: str) -> None:
    """Every language code declared as supported actually maps to a BCP-47 code."""
    result = to_bcp47(code)
    assert result == settings.SUPPORTED_LANGUAGES[code]["bcp47"]
    assert "-" in result  # BCP-47 region form, e.g. "mr-IN"


@given(code=st.text(min_size=1, max_size=10).filter(lambda c: c not in settings.SUPPORTED_LANGUAGES))
def test_to_bcp47_rejects_any_unsupported_code(code: str) -> None:
    """Any code that isn't in SUPPORTED_LANGUAGES is rejected, never silently accepted."""
    with pytest.raises(ValueError):
        to_bcp47(code)

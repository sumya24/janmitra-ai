"""Password hashing and JWT session tokens for account login.

JWTs are implemented directly against the standard library (HS256 only) rather
than a third-party JWT package, since this project only ever needs to verify
tokens it issued itself with one shared secret — no external issuers, no key
rotation, no asymmetric signing. This keeps the dependency surface small.
"""

import base64
import hashlib
import hmac
import json
import logging
import secrets
import time

import bcrypt

from backend.config import settings
from backend.models import User

logger = logging.getLogger(__name__)

# If no JWT_SECRET_KEY is configured, generate a random one for this process so
# the app still runs (e.g. local demos) — sessions just won't survive a restart.
# Any real deployment should set JWT_SECRET_KEY explicitly in .env.
_RUNTIME_SECRET = settings.JWT_SECRET_KEY or secrets.token_hex(32)
if not settings.JWT_SECRET_KEY:
    logger.warning(
        "JWT_SECRET_KEY is not set; using a random per-process secret. "
        "All existing sessions will be invalidated on restart."
    )


class InvalidTokenError(Exception):
    """Raised when a token is missing, malformed, expired, or has a bad signature."""


def hash_password(password: str) -> str:
    """Hash a plaintext password for storage.

    Args:
        password: The plaintext password.

    Returns:
        A bcrypt hash safe to store in the database.
    """
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("ascii")


def verify_password(password: str, password_hash: str) -> bool:
    """Check a plaintext password against a stored bcrypt hash.

    Args:
        password: The plaintext password to check.
        password_hash: The bcrypt hash previously produced by hash_password().

    Returns:
        True if the password matches, False otherwise (never raises on mismatch).
    """
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("ascii"))
    except ValueError:
        logger.error("Stored password hash is malformed; treating as no match.")
        return False


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64url_decode(data: str) -> bytes:
    padded = data + "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(padded)


def create_access_token(user: User) -> str:
    """Create a signed session token for a logged-in user.

    Args:
        user: The authenticated user to encode a token for.

    Returns:
        A compact JWT string: base64url(header).base64url(payload).base64url(signature).
    """
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {
        "sub": str(user.id),
        "role": user.role,
        "iat": int(time.time()),
        "exp": int(time.time()) + settings.JWT_EXPIRE_MINUTES * 60,
    }
    header_b64 = _b64url_encode(json.dumps(header, separators=(",", ":")).encode())
    payload_b64 = _b64url_encode(json.dumps(payload, separators=(",", ":")).encode())
    signing_input = f"{header_b64}.{payload_b64}".encode()
    signature = hmac.new(_RUNTIME_SECRET.encode(), signing_input, hashlib.sha256).digest()
    return f"{header_b64}.{payload_b64}.{_b64url_encode(signature)}"


def decode_access_token(token: str) -> dict:
    """Verify and decode a session token.

    Args:
        token: The JWT string from the Authorization header.

    Returns:
        The decoded payload, e.g. {"sub": "12", "role": "citizen", "exp": ...}.

    Raises:
        InvalidTokenError: If the token is malformed, has a bad signature, or expired.
    """
    try:
        header_b64, payload_b64, signature_b64 = token.split(".")
    except ValueError as exc:
        raise InvalidTokenError("Malformed token.") from exc

    signing_input = f"{header_b64}.{payload_b64}".encode()
    expected_signature = hmac.new(_RUNTIME_SECRET.encode(), signing_input, hashlib.sha256).digest()
    try:
        actual_signature = _b64url_decode(signature_b64)
    except Exception as exc:
        raise InvalidTokenError("Malformed token signature.") from exc

    if not hmac.compare_digest(expected_signature, actual_signature):
        raise InvalidTokenError("Invalid token signature.")

    try:
        payload = json.loads(_b64url_decode(payload_b64))
    except Exception as exc:
        raise InvalidTokenError("Malformed token payload.") from exc

    if "exp" in payload and time.time() > payload["exp"]:
        raise InvalidTokenError("Token has expired.")

    return payload

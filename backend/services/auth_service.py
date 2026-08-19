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
from datetime import datetime, timedelta, timezone

import bcrypt
from sqlalchemy.orm import Session

from backend.config import settings
from backend.models import RefreshToken, User

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


# --- Refresh tokens ------------------------------------------------------------------------
# Opaque random strings, not JWTs -- see models.RefreshToken's own docstring for why. Naive-UTC
# throughout (never `datetime.now(timezone.utc)` directly) rather than timezone-aware: this
# project's SQLite DateTime columns have no real timezone-aware storage, and this codebase has no
# prior art anywhere for comparing a stored datetime back against "now" (every existing
# created_at/updated_at column is only ever written, never read back and compared) -- so rather
# than depend on how SQLAlchemy/SQLite happen to round-trip an aware value, every refresh-token
# timestamp here is naive-UTC consistently on both write and comparison, which sidesteps the
# aware-vs-naive TypeError risk entirely regardless of that round-trip behavior.


def _now_utc_naive() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _hash_refresh_token(plaintext: str) -> str:
    return hashlib.sha256(plaintext.encode("utf-8")).hexdigest()


def create_refresh_token(user: User, db: Session) -> str:
    """Issue a brand-new refresh token for a just-logged-in/signed-up user.

    Args:
        user: The user to issue a refresh token for.
        db: Active database session (the new row is committed here).

    Returns:
        The plaintext refresh token -- returned to the client exactly once; only its SHA-256
        hash is ever persisted.
    """
    plaintext = secrets.token_urlsafe(32)
    db.add(
        RefreshToken(
            user_id=user.id,
            token_hash=_hash_refresh_token(plaintext),
            expires_at=_now_utc_naive() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        )
    )
    db.commit()
    return plaintext


def rotate_refresh_token(db: Session, plaintext_token: str) -> tuple[User, str, str] | None:
    """Redeem a refresh token for a new access+refresh token pair, rotating it in the process.

    Args:
        db: Active database session.
        plaintext_token: The refresh token presented by the client.

    Returns:
        (user, new_access_token, new_refresh_token) on success, or None if the token is unknown,
        expired, or was already used (in which case every other active refresh token for that
        user is also revoked -- see this module's docstring section and
        models.RefreshToken.revoked_at's own docstring for why reuse is treated as compromise).
    """
    row = db.query(RefreshToken).filter(RefreshToken.token_hash == _hash_refresh_token(plaintext_token)).first()
    if row is None:
        return None

    now = _now_utc_naive()

    if row.revoked_at is not None:
        revoke_all_refresh_tokens(db, row.user_id)
        logger.warning("Refresh token reuse detected (user_id=%s) -- all active sessions revoked.", row.user_id)
        return None

    if row.expires_at <= now:
        return None

    user = db.query(User).filter(User.id == row.user_id).first()
    if user is None:
        return None

    new_plaintext = secrets.token_urlsafe(32)
    new_row = RefreshToken(
        user_id=user.id,
        token_hash=_hash_refresh_token(new_plaintext),
        expires_at=now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )
    db.add(new_row)
    db.flush()  # populate new_row.id before linking replaced_by_id below

    row.revoked_at = now
    row.replaced_by_id = new_row.id
    db.commit()

    return user, create_access_token(user), new_plaintext


def revoke_refresh_token(db: Session, plaintext_token: str) -> None:
    """Real, server-side logout: marks one refresh token revoked so it can never be redeemed
    again, regardless of its natural expiry. A no-op (not an error) if the token is already
    unknown/revoked -- logout should never fail just because the session was already gone."""
    row = db.query(RefreshToken).filter(RefreshToken.token_hash == _hash_refresh_token(plaintext_token)).first()
    if row is not None and row.revoked_at is None:
        row.revoked_at = _now_utc_naive()
        db.commit()


def revoke_all_refresh_tokens(db: Session, user_id: int) -> None:
    """Revokes every currently-active refresh token for one user in a single statement -- shared
    by rotate_refresh_token's reuse-detection path (a suspected-compromise response) and
    routes/auth.py's change-password endpoint (a "the credential may be stale, sign out
    everywhere else" response to a deliberate password change). Commits itself."""
    db.query(RefreshToken).filter(RefreshToken.user_id == user_id, RefreshToken.revoked_at.is_(None)).update(
        {"revoked_at": _now_utc_naive()}
    )
    db.commit()

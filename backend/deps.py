"""FastAPI dependencies for authenticating requests, enforcing roles, and rate limiting."""

import logging

from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session

from backend.config import settings
from backend.database import get_db
from backend.models import User
from backend.services.auth_service import InvalidTokenError, decode_access_token
from backend.services.rate_limiter import RateLimiter

logger = logging.getLogger(__name__)


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    """Resolve the authenticated user from the request's Authorization header.

    Args:
        request: The incoming request, expected to carry "Authorization: Bearer <token>".
        db: Active database session.

    Returns:
        The authenticated User.

    Raises:
        HTTPException: 401 if the header is missing, the token is invalid/expired,
            or the user it refers to no longer exists.
    """
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or malformed Authorization header.")

    token = auth_header.removeprefix("Bearer ").strip()
    try:
        payload = decode_access_token(token)
    except InvalidTokenError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc

    user = db.query(User).filter(User.id == int(payload["sub"])).first()
    if user is None:
        raise HTTPException(status_code=401, detail="Account no longer exists.")
    return user


def require_role(*allowed_roles: str):
    """Build a dependency that only allows users whose role is in allowed_roles.

    Args:
        *allowed_roles: Role names that may access the route, e.g. "admin".

    Returns:
        A FastAPI dependency raising 403 for any other authenticated role.
    """

    def _check(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(status_code=403, detail="You do not have access to this action.")
        return current_user

    return _check


# --- Rate limiting -----------------------------------------------------------------------------
# See backend/services/rate_limiter.py's module docstring for the design (in-process sliding
# window, single-process deployment only) and docs/RATE_LIMITING.md for the full picture. Three
# separate limiter instances -- login, AI, and the general baseline (see backend/middleware.py)
# never share a counting namespace, so exhausting one never affects another. A request to POST
# /auth/login or POST /ask-janmitra* is checked against BOTH its own strict, purpose-specific
# limit here AND the general middleware's coarser one -- the general limiter is a safety net for
# every OTHER route, not a replacement for these two.

_login_limiter = RateLimiter()
_ai_limiter = RateLimiter()


def client_ip(request: Request) -> str:
    """The safest available pre-authentication identifier -- used for login rate limiting, and
    reused by backend/middleware.py's general limiter as its fallback for requests with no valid
    token.

    Only trusts `X-Forwarded-For` when `settings.TRUST_PROXY_HEADERS` is explicitly on (see that
    setting's own docstring in config.py) -- an arbitrary client can set this header to anything,
    so honoring it by default would let an attacker either bypass the limit entirely (claim a
    fresh IP on every request) or frame another real client (claim their IP). Off by default;
    this project's production Caddy sets it truthfully and the backend container publishes no
    port of its own for anyone to bypass Caddy and spoof it directly -- see docker-compose.prod.yml.
    Falls back to a fixed placeholder (never crashes) on the rare test/ASGI-transport case where
    `request.client` is None.
    """
    if settings.TRUST_PROXY_HEADERS:
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            # The client's own original IP is the FIRST hop Caddy appends -- anything after that
            # was added by intermediate proxies Caddy itself saw, not attacker-controlled once
            # TRUST_PROXY_HEADERS is only enabled behind a topology where Caddy is the sole entry
            # point (see this setting's docstring).
            return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def require_login_rate_limit(request: Request) -> None:
    """Dependency for POST /auth/login -- throttles login attempts per client IP, independent of
    whether the credentials turn out to be valid (a brute-force script's failed attempts must
    count too, not just successful logins)."""
    allowed, retry_after = _login_limiter.check(
        client_ip(request), settings.LOGIN_RATE_LIMIT, settings.LOGIN_RATE_LIMIT_WINDOW_SECONDS
    )
    if not allowed:
        raise HTTPException(
            status_code=429,
            detail="Too many login attempts. Please try again later.",
            headers={"Retry-After": str(retry_after)},
        )


def require_ai_rate_limit(current_user: User = Depends(get_current_user)) -> None:
    """Dependency for the POST /ask-janmitra* endpoints -- throttles expensive Sarvam/LLM/vision
    calls per authenticated user, shared across all three routes (text/image/voice) so a citizen
    can't dodge the limit by switching endpoints. Depends on `get_current_user` itself (rather
    than reading a raw token) so an invalid/expired token is rejected with its own real 401 before
    any rate-limit bookkeeping happens -- an unauthenticated request never consumes any specific
    user's quota. FastAPI resolves/caches `get_current_user` once per request, so routes that also
    declare it directly don't pay for a second DB lookup."""
    allowed, retry_after = _ai_limiter.check(
        f"user:{current_user.id}", settings.AI_RATE_LIMIT, settings.AI_RATE_LIMIT_WINDOW_SECONDS
    )
    if not allowed:
        raise HTTPException(
            status_code=429,
            detail="Too many requests to Ask Sarthi. Please wait a moment and try again.",
            headers={"Retry-After": str(retry_after)},
        )

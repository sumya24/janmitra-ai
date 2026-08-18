"""ASGI middleware -- currently just the general rate-limit safety net.

See backend/services/rate_limiter.py (the limiter itself) and backend/deps.py's
require_login_rate_limit/require_ai_rate_limit (the two stricter, purpose-specific limits already
on POST /auth/login and POST /ask-janmitra*). This module is what gives every OTHER route
(complaint creation, uploads, worker/admin actions, etc.) baseline coverage too, without hand-
wiring a dependency into each one individually -- registered once in main.py, applies
automatically to every request.
"""

from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from backend.config import settings
from backend.deps import client_ip
from backend.services.auth_service import InvalidTokenError, decode_access_token
from backend.services.rate_limiter import RateLimiter

_general_limiter = RateLimiter()

# GET /health must stay reachable for monitoring/deploy healthchecks regardless of load elsewhere
# -- the only exemption; every other route (including /auth/signup and every GET) is covered.
_EXEMPT_PATHS = {"/health"}


def _general_identifier(request: Request) -> str:
    """Authenticated user id when a valid token is present, client IP otherwise -- matches
    require_ai_rate_limit's "prefer real user identity" preference, but decodes the token directly
    here (verifies signature + expiry, no DB lookup) rather than depending on get_current_user, to
    keep this middleware cheap on every single request. An invalid/missing/expired token is NOT
    rejected here -- that 401 is each route's own auth dependency's job; this middleware only
    needs *an* identifier to count against, never authenticates anything itself."""
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header.removeprefix("Bearer ").strip()
        try:
            payload = decode_access_token(token)
            return f"user:{payload['sub']}"
        except InvalidTokenError:
            pass
    return f"ip:{client_ip(request)}"


class GeneralRateLimitMiddleware(BaseHTTPMiddleware):
    """A generous baseline limit (settings.GENERAL_RATE_LIMIT per
    settings.GENERAL_RATE_LIMIT_WINDOW_SECONDS) applied to every request except /health -- see
    module docstring. Registered BEFORE CORSMiddleware in main.py (so CORS ends up outermost,
    handling preflight and attaching CORS headers to every response including a 429 from here --
    getting this registration order backwards would make a cross-origin browser request unable to
    even read this middleware's 429 body). Also skips OPTIONS defensively regardless of ordering,
    since a preflight is the browser's own automatic traffic, never a real user action to count."""

    async def dispatch(self, request: Request, call_next):
        if request.method == "OPTIONS" or request.url.path in _EXEMPT_PATHS:
            return await call_next(request)

        identifier = _general_identifier(request)
        allowed, retry_after = _general_limiter.check(
            identifier, settings.GENERAL_RATE_LIMIT, settings.GENERAL_RATE_LIMIT_WINDOW_SECONDS
        )
        if not allowed:
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests. Please try again later."},
                headers={"Retry-After": str(retry_after)},
            )
        return await call_next(request)

"""FastAPI dependencies for authenticating requests and enforcing roles."""

import logging

from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import User
from backend.services.auth_service import InvalidTokenError, decode_access_token

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

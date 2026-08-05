"""Authentication endpoints: citizen sign-up, login, and account settings.

There is deliberately no role field anywhere in this file. Sign-up always
creates a "citizen" account — it is the only self-service entry point in the
system. Worker accounts are only ever created by a super admin (see
routes/admin.py); the first super admin account is seeded directly into the
database when the system is set up, not created through any API here.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from backend.config import settings
from backend.database import get_db
from backend.deps import get_current_user
from backend.models import User
from backend.services.auth_service import create_access_token, hash_password, verify_password

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["auth"])

MIN_PASSWORD_LENGTH = 6


class SignupRequest(BaseModel):
    """Request body for citizen self-registration."""

    full_name: str
    phone: str
    password: str
    preferred_language: str


class LoginRequest(BaseModel):
    """Request body for logging in."""

    phone: str
    password: str


class MeUpdateRequest(BaseModel):
    """Request body for updating the current user's own profile."""

    full_name: str | None = None
    preferred_language: str | None = None


class UserResponse(BaseModel):
    """Public-facing representation of a user account (never includes the password hash)."""

    id: int
    full_name: str
    phone: str
    role: str
    preferred_language: str
    ward: str | None

    model_config = ConfigDict(from_attributes=True)


class AuthResponse(BaseModel):
    """Response returned by both sign-up and login."""

    access_token: str
    user: UserResponse


def _validate_language(language: str) -> None:
    if language not in settings.SUPPORTED_LANGUAGES:
        raise HTTPException(status_code=400, detail=f"Unsupported language: {language}")


@router.post("/signup", response_model=AuthResponse)
def signup(body: SignupRequest, db: Session = Depends(get_db)) -> AuthResponse:
    """Register a new citizen account and log them in immediately."""
    full_name = body.full_name.strip()
    phone = body.phone.strip()

    if not full_name:
        raise HTTPException(status_code=400, detail="Full name is required.")
    if not phone:
        raise HTTPException(status_code=400, detail="Phone number is required.")
    if len(body.password) < MIN_PASSWORD_LENGTH:
        raise HTTPException(
            status_code=400, detail=f"Password must be at least {MIN_PASSWORD_LENGTH} characters."
        )
    _validate_language(body.preferred_language)

    if db.query(User).filter(User.phone == phone).first() is not None:
        raise HTTPException(status_code=409, detail="An account with this phone number already exists.")

    user = User(
        full_name=full_name,
        phone=phone,
        password_hash=hash_password(body.password),
        role="citizen",
        preferred_language=body.preferred_language,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    logger.info("New citizen account created (user_id=%s)", user.id)

    token = create_access_token(user)
    return AuthResponse(access_token=token, user=UserResponse.model_validate(user))


@router.post("/login", response_model=AuthResponse)
def login(body: LoginRequest, db: Session = Depends(get_db)) -> AuthResponse:
    """Log in with a phone number and password, for any role."""
    user = db.query(User).filter(User.phone == body.phone.strip()).first()
    if user is None or not verify_password(body.password, user.password_hash):
        # Deliberately identical error for "no such phone" and "wrong password" —
        # never reveal which one it was.
        raise HTTPException(status_code=401, detail="Incorrect phone number or password.")

    logger.info("User logged in (user_id=%s, role=%s)", user.id, user.role)
    token = create_access_token(user)
    return AuthResponse(access_token=token, user=UserResponse.model_validate(user))


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)) -> UserResponse:
    """Return the current logged-in user's profile."""
    return UserResponse.model_validate(current_user)


@router.patch("/me", response_model=UserResponse)
def update_me(
    body: MeUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserResponse:
    """Update the current user's own display name and/or preferred language."""
    if body.preferred_language is not None:
        _validate_language(body.preferred_language)
        current_user.preferred_language = body.preferred_language
    if body.full_name is not None:
        full_name = body.full_name.strip()
        if not full_name:
            raise HTTPException(status_code=400, detail="Full name cannot be empty.")
        current_user.full_name = full_name

    db.commit()
    db.refresh(current_user)
    logger.info("Profile updated (user_id=%s)", current_user.id)
    return UserResponse.model_validate(current_user)

"""Authentication endpoints: citizen sign-up, login, and account settings.

There is deliberately no role field anywhere in this file. Sign-up always
creates a "citizen" account — it is the only self-service entry point in the
system. Worker accounts are only ever created by a super admin (see
routes/admin.py); the first super admin account is seeded directly into the
database when the system is set up, not created through any API here.
"""

import logging
import re

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.config import settings
from backend.database import get_db
from backend.deps import get_current_user, require_login_rate_limit, require_signup_rate_limit
from backend.models import District, Locality, State, ULB, User, Ward
from backend.services.auth_service import (
    create_access_token,
    create_refresh_token,
    hash_password,
    revoke_all_refresh_tokens,
    revoke_refresh_token,
    rotate_refresh_token,
    verify_password,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["auth"])

# 8+ chars with at least one letter and one digit -- NIST-style "length over complexity-theater"
# (no forced symbol/uppercase rules, which frustrate users without proportionate benefit), but a
# real step up from the previous bare 6-char-minimum. Only enforced at signup and change-password
# (see _validate_password_strength below) -- never at login, so no pre-existing account created
# under the old, looser rule is ever locked out of its own login.
MIN_PASSWORD_LENGTH = 8
_PASSWORD_HAS_LETTER = re.compile(r"[A-Za-z]")
_PASSWORD_HAS_DIGIT = re.compile(r"\d")

# Standard Indian mobile number: 10 digits, first digit 6-9 -- matches every phone number already
# used across this codebase's tests/seed data (all 10 digits, all start with 9), and this is the
# real, deployed audience (see memory: Oracle Cloud India deployment). Previously `signup`/`login`
# only checked "non-empty" -- any string ("abc", "1") was accepted as a phone number, a real
# validation gap: it let a citizen register with something that could never receive an SMS/call,
# and let `phone` silently double as a free-text username instead of what it's actually used for
# (login identifier, `User.phone`, unique+indexed). Checked at signup only, matching how phone is
# otherwise immutable (no phone field in MeUpdateRequest) -- login itself must stay a plain
# "wrong credentials" check, not a format gate, so a citizen who signed up before this validation
# existed is never locked out of their own account.
_PHONE_PATTERN = re.compile(r"^[6-9]\d{9}$")


class SignupRequest(BaseModel):
    """Request body for citizen self-registration."""

    full_name: str
    phone: str
    password: str
    preferred_language: str
    # Mandatory, one-time-at-signup -- not editable later (no ward field in MeUpdateRequest
    # below), so every citizen account is guaranteed to have one. Free text matching User.ward,
    # same field workers already have; picked from the same GET /complaints/wards list the
    # complaint-report wizard already uses, so "My Area" (routes/complaints.py's
    # /area-summary) always has something real to key off.
    ward: str
    # Optional, additive: the new cascading State/City/Ward/Area picker (see routes/locations.py)
    # feeds these into User.home_*_id -- the structured columns models.py already reserved for
    # exactly this (see User.home_state_id's own docstring), previously always null. Deliberately
    # NOT required and NOT used to derive/override `ward` above -- the existing free-text field
    # keeps working exactly as it does today (worker matching, "My Area", the AI's location
    # fallback) for every citizen, whether or not they complete this optional picker. Only the
    # deepest one the citizen actually reached needs to be sent; the signup handler derives the
    # rest of the parent chain from it server-side (see _resolve_home_location below), so the
    # frontend never has to track/send the whole chain itself.
    home_state_id: int | None = None
    home_district_id: int | None = None
    home_ward_id: int | None = None
    home_locality_id: int | None = None


class LoginRequest(BaseModel):
    """Request body for logging in."""

    phone: str
    password: str


class RefreshRequest(BaseModel):
    """Request body for POST /auth/refresh."""

    refresh_token: str


class LogoutRequest(BaseModel):
    """Request body for POST /auth/logout. No auth dependency on that route -- the refresh
    token itself is already sufficient proof of ownership to revoke just itself, and requiring a
    still-valid access token too would make logout needlessly fail for the realistic case of a
    citizen returning to a stale tab whose access token already expired."""

    refresh_token: str


class ChangePasswordRequest(BaseModel):
    """Request body for POST /auth/change-password."""

    current_password: str
    new_password: str


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
    """Response returned by sign-up, login, and refresh."""

    access_token: str
    refresh_token: str
    user: UserResponse


def _validate_language(language: str) -> None:
    if language not in settings.SUPPORTED_LANGUAGES:
        raise HTTPException(status_code=400, detail=f"Unsupported language: {language}")


def _validate_password_strength(password: str) -> None:
    if len(password) < MIN_PASSWORD_LENGTH:
        raise HTTPException(
            status_code=400, detail=f"Password must be at least {MIN_PASSWORD_LENGTH} characters."
        )
    if not _PASSWORD_HAS_LETTER.search(password) or not _PASSWORD_HAS_DIGIT.search(password):
        raise HTTPException(status_code=400, detail="Password must include at least one letter and one number.")


def _resolve_home_location(db: Session, body: SignupRequest) -> dict[str, int | None]:
    """Derives the full home_state_id -> home_locality_id chain from whichever ID the citizen's
    optional cascading picker actually reached (see routes/locations.py and SignupRequest's own
    docstring) -- only the deepest selection needs to be sent; every ancestor is looked up from
    it here, authoritatively, rather than trusted from separate client-supplied IDs that could in
    principle disagree with each other. Returns an all-None dict when nothing was provided (the
    common case today, since only 6 of 36 states have real city/ward/locality data). Raises 400
    if a given ID doesn't exist -- the same honest-validation standard as the rest of this
    handler, never silently ignored."""
    ward: Ward | None = None
    locality: Locality | None = None
    if body.home_locality_id is not None:
        locality = db.query(Locality).filter(Locality.id == body.home_locality_id).first()
        if locality is None:
            raise HTTPException(status_code=400, detail="Selected area not found.")
        ward = db.query(Ward).filter(Ward.id == locality.ward_id).first()
    elif body.home_ward_id is not None:
        ward = db.query(Ward).filter(Ward.id == body.home_ward_id).first()
        if ward is None:
            raise HTTPException(status_code=400, detail="Selected ward not found.")

    ulb: ULB | None = None
    district: District | None = None
    if ward is not None:
        ulb = db.query(ULB).filter(ULB.id == ward.ulb_id).first()
        district = db.query(District).filter(District.id == ulb.district_id).first() if ulb else None
    elif body.home_district_id is not None:
        district = db.query(District).filter(District.id == body.home_district_id).first()
        if district is None:
            raise HTTPException(status_code=400, detail="Selected city not found.")

    state_id: int | None = None
    if district is not None:
        state_id = district.state_id
    elif body.home_state_id is not None:
        if db.query(State).filter(State.id == body.home_state_id).first() is None:
            raise HTTPException(status_code=400, detail="Selected state not found.")
        state_id = body.home_state_id

    return {
        "home_state_id": state_id,
        "home_district_id": district.id if district else None,
        "home_ulb_id": ulb.id if ulb else None,
        "home_ward_id": ward.id if ward else None,
        "home_locality_id": locality.id if locality else None,
    }


@router.post("/signup", response_model=AuthResponse, dependencies=[Depends(require_signup_rate_limit)])
def signup(body: SignupRequest, db: Session = Depends(get_db)) -> AuthResponse:
    """Register a new citizen account and log them in immediately.

    Rate-limited per client IP (see backend/deps.py's require_signup_rate_limit) -- its own
    dedicated, stricter-than-general limit against mass fake-account creation.
    """
    full_name = body.full_name.strip()
    phone = body.phone.strip()
    ward = body.ward.strip()

    if not full_name:
        raise HTTPException(status_code=400, detail="Full name is required.")
    if not phone:
        raise HTTPException(status_code=400, detail="Phone number is required.")
    if not _PHONE_PATTERN.match(phone):
        raise HTTPException(status_code=400, detail="Enter a valid 10-digit mobile number.")
    if not ward:
        raise HTTPException(status_code=400, detail="Area / ward is required.")
    _validate_password_strength(body.password)
    _validate_language(body.preferred_language)

    if db.query(User).filter(User.phone == phone).first() is not None:
        raise HTTPException(status_code=409, detail="An account with this phone number already exists.")

    home_location = _resolve_home_location(db, body)

    user = User(
        full_name=full_name,
        phone=phone,
        password_hash=hash_password(body.password),
        role="citizen",
        preferred_language=body.preferred_language,
        ward=ward,
        **home_location,
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        # Second line of defense against the phone-uniqueness pre-check above racing a
        # concurrent signup for the same number -- the pre-check alone has a real TOCTOU gap
        # between the query and this insert; the database's own unique constraint on
        # User.phone is the actual source of truth, this just turns its violation into the
        # same honest 409 instead of a raw 500.
        db.rollback()
        raise HTTPException(status_code=409, detail="An account with this phone number already exists.")
    db.refresh(user)
    logger.info("New citizen account created (user_id=%s)", user.id)

    access_token = create_access_token(user)
    refresh_token = create_refresh_token(user, db)
    return AuthResponse(access_token=access_token, refresh_token=refresh_token, user=UserResponse.model_validate(user))


@router.post("/login", response_model=AuthResponse, dependencies=[Depends(require_login_rate_limit)])
def login(body: LoginRequest, db: Session = Depends(get_db)) -> AuthResponse:
    """Log in with a phone number and password, for any role.

    Rate-limited per client IP (see backend/deps.py's require_login_rate_limit) -- counts every
    attempt, successful or not, before any credential check runs.
    """
    user = db.query(User).filter(User.phone == body.phone.strip()).first()
    if user is None or not verify_password(body.password, user.password_hash):
        # Deliberately identical error for "no such phone" and "wrong password" —
        # never reveal which one it was.
        raise HTTPException(status_code=401, detail="Incorrect phone number or password.")

    logger.info("User logged in (user_id=%s, role=%s)", user.id, user.role)
    access_token = create_access_token(user)
    refresh_token = create_refresh_token(user, db)
    return AuthResponse(access_token=access_token, refresh_token=refresh_token, user=UserResponse.model_validate(user))


@router.post("/refresh", response_model=AuthResponse)
def refresh(body: RefreshRequest, db: Session = Depends(get_db)) -> AuthResponse:
    """Redeem a refresh token for a new short-lived access token, rotating the refresh token in
    the process (see services/auth_service.py's rotate_refresh_token for the rotation/reuse-
    detection design). Deliberately not rate-limited the way /login is -- a legitimate client
    calls this automatically, silently, potentially several times per session (see the frontend's
    401-triggered silent-refresh), which is a fundamentally different traffic shape from a
    human/script guessing credentials.
    """
    result = rotate_refresh_token(db, body.refresh_token)
    if result is None:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token. Please log in again.")
    user, access_token, refresh_token = result
    return AuthResponse(access_token=access_token, refresh_token=refresh_token, user=UserResponse.model_validate(user))


@router.post("/logout", status_code=204)
def logout(body: LogoutRequest, db: Session = Depends(get_db)) -> None:
    """Real, server-side logout -- revokes the refresh token so it can never be redeemed again,
    unlike the old client-side-only "clear localStorage" logout (under which a captured token
    stayed valid until its natural expiry regardless). See LogoutRequest's own docstring for why
    this route has no auth dependency of its own."""
    revoke_refresh_token(db, body.refresh_token)


@router.post("/change-password", status_code=204)
def change_password(
    body: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    """Self-service password change -- previously there was no way for a citizen to change their
    own password at all (only an admin-mediated reset existed, for worker accounts). Revokes
    every one of the account's other active refresh tokens on success, the same "assume the old
    credential may be compromised" posture a password change implies -- every other
    logged-in device/tab gets signed out and must log in again with the new password.
    """
    if not verify_password(body.current_password, current_user.password_hash):
        raise HTTPException(status_code=401, detail="Current password is incorrect.")
    _validate_password_strength(body.new_password)

    current_user.password_hash = hash_password(body.new_password)
    db.commit()
    revoke_all_refresh_tokens(db, current_user.id)
    logger.info("Password changed (user_id=%s) -- all other sessions revoked.", current_user.id)


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

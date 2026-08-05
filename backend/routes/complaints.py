"""API endpoints for creating, listing, and updating complaints.

Access is scoped by the authenticated user's role (see backend/deps.py):
citizens only ever see their own complaints, workers only see their own
ward's complaints, and super admins see everything.
"""

import logging
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from backend.config import settings
from backend.database import get_db
from backend.deps import get_current_user, require_role
from backend.models import Complaint, User
from backend.services.complaint_agent import ComplaintAgent
from backend.services.sarvam_client import AIServiceError
from backend.services.translation_service import TranslationService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/complaints", tags=["complaints"])

_agent = ComplaintAgent()
_translation_service = TranslationService()


class ComplaintResponse(BaseModel):
    """Response body representing a single complaint."""

    id: int
    citizen_id: str
    original_text: str
    original_language: str
    translated_text: str
    display_text: str
    summary: str
    photo_path: str | None
    status: str
    ward: str | None
    created_at: str

    model_config = ConfigDict(from_attributes=True)


class StatusUpdateRequest(BaseModel):
    """Request body for updating a complaint's status."""

    status: str


def _save_photo(photo: UploadFile) -> str:
    """Validate and save an uploaded photo to the upload folder.

    Args:
        photo: The uploaded photo file.

    Returns:
        The saved photo's filename (not a full path), so it can be served from the
        /uploads static mount and stored as a small, portable value in the database.

    Raises:
        HTTPException: If the photo type or size is not allowed.
    """
    if photo.content_type not in settings.ALLOWED_PHOTO_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported photo type: {photo.content_type}. Use JPEG or PNG.",
        )

    contents = photo.file.read()
    if len(contents) > settings.MAX_PHOTO_SIZE_BYTES:
        raise HTTPException(status_code=400, detail="Photo exceeds the 5MB size limit.")

    upload_dir = Path(settings.UPLOAD_FOLDER)
    upload_dir.mkdir(parents=True, exist_ok=True)

    extension = Path(photo.filename or "").suffix or ".jpg"
    filename = f"{uuid.uuid4().hex}{extension}"
    (upload_dir / filename).write_bytes(contents)

    return filename


def _to_response(complaint: Complaint, display_language: str | None) -> ComplaintResponse:
    """Build a ComplaintResponse, translating the display text on read if requested.

    Args:
        complaint: The complaint ORM record.
        display_language: Short language code to translate the English text into,
            or None to display the stored English text as-is.
    """
    display_text = complaint.translated_text
    if display_language and display_language != "en":
        try:
            display_text = _translation_service.to_language(
                complaint.translated_text, display_language
            )
        except AIServiceError as exc:
            logger.error("On-read translation failed for complaint %s: %s", complaint.id, exc)
            display_text = complaint.translated_text

    return ComplaintResponse(
        id=complaint.id,
        citizen_id=complaint.citizen_id,
        original_text=complaint.original_text,
        original_language=complaint.original_language,
        translated_text=complaint.translated_text,
        display_text=display_text,
        summary=complaint.summary,
        photo_path=complaint.photo_path,
        status=complaint.status,
        ward=complaint.ward,
        created_at=complaint.created_at.isoformat(),
    )


@router.post("", response_model=ComplaintResponse)
def create_complaint(
    language: str = Form(...),
    text: str | None = Form(None),
    ward: str | None = Form(None),
    photo: UploadFile | None = File(None),
    audio: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    citizen: User = Depends(require_role("citizen")),
) -> ComplaintResponse:
    """Create a new complaint from typed text or a voice recording, with an optional photo.

    The citizen is taken from the authenticated session — there is no way to
    submit a complaint on someone else's behalf.
    """
    if language not in settings.SUPPORTED_LANGUAGES:
        raise HTTPException(status_code=400, detail=f"Unsupported language: {language}")
    if not text and not audio:
        raise HTTPException(status_code=400, detail="Either text or audio must be provided.")

    photo_path = _save_photo(photo) if photo is not None and photo.filename else None
    audio_bytes = audio.file.read() if audio is not None and audio.filename else None

    try:
        complaint = _agent.create_complaint(
            db=db,
            citizen_id=str(citizen.id),
            language_code=language,
            text=text,
            audio_bytes=audio_bytes,
            photo_path=photo_path,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except AIServiceError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    if ward is not None and ward.strip():
        complaint.ward = ward.strip()
        db.commit()
        db.refresh(complaint)

    return _to_response(complaint, display_language=None)


@router.get("", response_model=list[ComplaintResponse])
def list_complaints(
    lang: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ComplaintResponse]:
    """List complaints visible to the current user, translated into `lang` on read.

    Citizens see only their own complaints; workers see only their ward's
    complaints; super admins see every complaint. Defaults to the user's own
    preferred language if `lang` is not given.
    """
    if lang is not None and lang not in settings.SUPPORTED_LANGUAGES:
        raise HTTPException(status_code=400, detail=f"Unsupported language: {lang}")
    display_language = lang or current_user.preferred_language

    query = db.query(Complaint)
    if current_user.role == "citizen":
        query = query.filter(Complaint.citizen_id == str(current_user.id))
    elif current_user.role == "worker":
        query = query.filter(Complaint.ward == current_user.ward)
    # admins see everything: no filter

    complaints = query.order_by(Complaint.created_at.desc()).all()
    return [_to_response(c, display_language=display_language) for c in complaints]


@router.patch("/{complaint_id}", response_model=ComplaintResponse)
def update_status(
    complaint_id: int,
    body: StatusUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("worker", "admin")),
) -> ComplaintResponse:
    """Update a complaint's status (e.g. mark it "resolved"). Workers and admins only."""
    if body.status not in ("open", "resolved"):
        raise HTTPException(status_code=400, detail="Status must be 'open' or 'resolved'.")

    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if complaint is None:
        raise HTTPException(status_code=404, detail="Complaint not found.")

    if current_user.role == "worker" and complaint.ward != current_user.ward:
        raise HTTPException(status_code=403, detail="This complaint is outside your ward.")

    complaint.status = body.status
    db.commit()
    db.refresh(complaint)
    logger.info("Complaint %s status updated to %s by user %s", complaint_id, body.status, current_user.id)
    return _to_response(complaint, display_language=None)

"""API endpoints for creating, listing, and tracking complaints through their lifecycle.

Lifecycle: pending -> assigned -> accepted -> resolved, with citizen feedback afterward.
A complaint starts "pending" (or "assigned" immediately, if its ward already has an eligible
worker). The assigned worker can accept (moves to "accepted", unlocking their phone number for
the citizen) or reject (assignment_service.py hands it to the next worker in that ward, or back
to "pending" if none are left). Only an accepted complaint's assigned worker can resolve it.

Access is scoped by the authenticated user's role (see backend/deps.py): citizens only ever see
their own complaints, workers only see complaints currently assigned to them, and super admins
see everything.
"""

import logging
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from backend.config import settings
from backend.database import get_db
from backend.deps import get_current_user, require_role
from backend.models import Complaint, ComplaintRejection, User
from backend.services.assignment_service import assign_next_worker
from backend.services.complaint_agent import ComplaintAgent
from backend.services.complaint_translation_cache import get_display_text_and_summary
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
    display_summary: str
    photo_path: str | None
    status: str
    ward: str | None
    assigned_worker_name: str | None
    # Deliberately withheld until the assigned worker accepts — see _to_response.
    assigned_worker_phone: str | None
    rejection_count: int
    feedback_rating: int | None
    feedback_comment: str | None
    created_at: str

    model_config = ConfigDict(from_attributes=True)


class FeedbackRequest(BaseModel):
    """Request body for a citizen leaving feedback on a resolved complaint."""

    rating: int = Field(ge=1, le=5)
    comment: str | None = None


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


def _to_response(db: Session, complaint: Complaint, display_language: str | None) -> ComplaintResponse:
    """Build a ComplaintResponse, translating the display text and summary on read if requested.

    Args:
        db: Active database session, used to read/write the translation cache.
        complaint: The complaint ORM record.
        display_language: Short language code to translate the English text into,
            or None to display the stored English text as-is.
    """
    display_text = complaint.translated_text
    display_summary = complaint.summary
    if display_language and display_language != "en":
        try:
            display_text, display_summary = get_display_text_and_summary(
                db, complaint, display_language, _translation_service
            )
        except AIServiceError as exc:
            logger.error("On-read translation failed for complaint %s: %s", complaint.id, exc)
            display_text = complaint.translated_text
            display_summary = complaint.summary

    assigned_worker_name = None
    assigned_worker_phone = None
    if complaint.assigned_worker_id is not None:
        worker = db.query(User).filter(User.id == complaint.assigned_worker_id).first()
        if worker is not None:
            assigned_worker_name = worker.full_name
            # The citizen can see who it's assigned to as soon as it's assigned, but the phone
            # number only unlocks once that worker has actually accepted it — showing it earlier
            # would let a citizen contact someone who hasn't agreed to take the complaint yet.
            if complaint.status in ("accepted", "resolved"):
                assigned_worker_phone = worker.phone

    rejection_count = db.query(ComplaintRejection).filter(ComplaintRejection.complaint_id == complaint.id).count()

    return ComplaintResponse(
        id=complaint.id,
        citizen_id=complaint.citizen_id,
        original_text=complaint.original_text,
        original_language=complaint.original_language,
        translated_text=complaint.translated_text,
        display_text=display_text,
        summary=complaint.summary,
        display_summary=display_summary,
        photo_path=complaint.photo_path,
        status=complaint.status,
        ward=complaint.ward,
        assigned_worker_name=assigned_worker_name,
        assigned_worker_phone=assigned_worker_phone,
        rejection_count=rejection_count,
        feedback_rating=complaint.feedback_rating,
        feedback_comment=complaint.feedback_comment,
        created_at=complaint.created_at.isoformat(),
    )


def _get_owned_complaint(db: Session, complaint_id: int, worker: User) -> Complaint:
    """Fetch a complaint and verify it's currently assigned to `worker`, or raise."""
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if complaint is None:
        raise HTTPException(status_code=404, detail="Complaint not found.")
    if complaint.assigned_worker_id != worker.id:
        raise HTTPException(status_code=403, detail="This complaint isn't assigned to you.")
    return complaint


@router.get("/wards", response_model=list[str])
def list_wards(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[str]:
    """List every ward that has a worker assigned to it.

    Backs the ward picker on the citizen's complaint form: a complaint can only
    ever reach a worker if its ward exactly matches a worker's ward, so the
    dropdown only ever offers wards that actually have someone staffing them —
    it's impossible to pick a name that doesn't route anywhere.
    """
    rows = db.query(User.ward).filter(User.role == "worker", User.ward.isnot(None)).distinct().all()
    return sorted({row[0] for row in rows if row[0]})


@router.post("", response_model=ComplaintResponse)
def create_complaint(
    language: str = Form(...),
    text: str | None = Form(None),
    ward: str | None = Form(None),
    photo: UploadFile | None = File(None),
    audio: list[UploadFile] | None = File(None),
    db: Session = Depends(get_db),
    citizen: User = Depends(require_role("citizen")),
) -> ComplaintResponse:
    """Create a new complaint from typed text or a voice recording, with an optional photo.

    `audio` may contain more than one file: Sarvam's speech-to-text endpoint hard-caps a
    single request at 30 seconds of audio (see docs/ai_pipeline_limits.md), so a longer
    recording arrives as several short chunks — the citizen-facing recorder splits into
    ~28s segments client-side (frontend-react/src/lib/useAudioRecorder.ts) rather than
    sending one file that would just get rejected. Each chunk is transcribed independently
    and stitched back into one transcript (see ComplaintAgent._transcribe_chunks).

    The citizen is taken from the authenticated session — there is no way to
    submit a complaint on someone else's behalf. Immediately assigned to the first
    eligible worker in its ward, if any (see assignment_service.py).
    """
    if language not in settings.SUPPORTED_LANGUAGES:
        raise HTTPException(status_code=400, detail=f"Unsupported language: {language}")

    audio_chunks = [a.file.read() for a in audio if a.filename] if audio else None
    if not text and not audio_chunks:
        raise HTTPException(status_code=400, detail="Either text or audio must be provided.")

    photo_path = _save_photo(photo) if photo is not None and photo.filename else None

    try:
        complaint = _agent.create_complaint(
            db=db,
            citizen_id=str(citizen.id),
            language_code=language,
            text=text,
            audio_chunks=audio_chunks,
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

    assign_next_worker(db, complaint)
    db.refresh(complaint)

    return _to_response(db, complaint, display_language=None)


@router.get("", response_model=list[ComplaintResponse])
def list_complaints(
    lang: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ComplaintResponse]:
    """List complaints visible to the current user, translated into `lang` on read.

    Citizens see only their own complaints; workers see only complaints currently
    assigned to them specifically (not just anyone in their ward — see
    assignment_service.py); super admins see every complaint. Defaults to the
    user's own preferred language if `lang` is not given.
    """
    if lang is not None and lang not in settings.SUPPORTED_LANGUAGES:
        raise HTTPException(status_code=400, detail=f"Unsupported language: {lang}")
    display_language = lang or current_user.preferred_language

    query = db.query(Complaint)
    if current_user.role == "citizen":
        query = query.filter(Complaint.citizen_id == str(current_user.id))
    elif current_user.role == "worker":
        query = query.filter(Complaint.assigned_worker_id == current_user.id)
    # admins see everything: no filter

    complaints = query.order_by(Complaint.created_at.desc()).all()
    return [_to_response(db, c, display_language=display_language) for c in complaints]


@router.post("/{complaint_id}/accept", response_model=ComplaintResponse)
def accept_complaint(
    complaint_id: int,
    db: Session = Depends(get_db),
    worker: User = Depends(require_role("worker")),
) -> ComplaintResponse:
    """Accept a complaint currently assigned to you. Unlocks your phone number for the citizen."""
    complaint = _get_owned_complaint(db, complaint_id, worker)
    if complaint.status != "assigned":
        raise HTTPException(status_code=400, detail=f"Cannot accept a complaint that is '{complaint.status}'.")

    complaint.status = "accepted"
    db.commit()
    db.refresh(complaint)
    logger.info("Complaint %s accepted by worker %s", complaint_id, worker.id)
    return _to_response(db, complaint, display_language=None)


@router.post("/{complaint_id}/reject", response_model=ComplaintResponse)
def reject_complaint(
    complaint_id: int,
    db: Session = Depends(get_db),
    worker: User = Depends(require_role("worker")),
) -> ComplaintResponse:
    """Reject a complaint currently assigned to you — hands it to the next worker in your ward."""
    complaint = _get_owned_complaint(db, complaint_id, worker)
    if complaint.status != "assigned":
        raise HTTPException(status_code=400, detail=f"Cannot reject a complaint that is '{complaint.status}'.")

    db.add(ComplaintRejection(complaint_id=complaint.id, worker_id=worker.id))
    db.commit()
    logger.info("Complaint %s rejected by worker %s", complaint_id, worker.id)

    assign_next_worker(db, complaint)
    db.refresh(complaint)
    return _to_response(db, complaint, display_language=None)


@router.post("/{complaint_id}/resolve", response_model=ComplaintResponse)
def resolve_complaint(
    complaint_id: int,
    db: Session = Depends(get_db),
    worker: User = Depends(require_role("worker")),
) -> ComplaintResponse:
    """Mark a complaint you've accepted as resolved."""
    complaint = _get_owned_complaint(db, complaint_id, worker)
    if complaint.status != "accepted":
        raise HTTPException(status_code=400, detail="Only an accepted complaint can be marked resolved.")

    complaint.status = "resolved"
    db.commit()
    db.refresh(complaint)
    logger.info("Complaint %s resolved by worker %s", complaint_id, worker.id)
    return _to_response(db, complaint, display_language=None)


@router.post("/{complaint_id}/feedback", response_model=ComplaintResponse)
def submit_feedback(
    complaint_id: int,
    body: FeedbackRequest,
    db: Session = Depends(get_db),
    citizen: User = Depends(require_role("citizen")),
) -> ComplaintResponse:
    """Leave a rating (and optional comment) on your own resolved complaint."""
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if complaint is None:
        raise HTTPException(status_code=404, detail="Complaint not found.")
    if complaint.citizen_id != str(citizen.id):
        raise HTTPException(status_code=403, detail="This isn't your complaint.")
    if complaint.status != "resolved":
        raise HTTPException(status_code=400, detail="You can only leave feedback once a complaint is resolved.")

    complaint.feedback_rating = body.rating
    complaint.feedback_comment = body.comment.strip() if body.comment else None
    db.commit()
    db.refresh(complaint)
    logger.info("Feedback submitted for complaint %s by citizen %s", complaint_id, citizen.id)
    return _to_response(db, complaint, display_language=None)

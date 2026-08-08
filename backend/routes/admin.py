"""Super-admin-only endpoints: creating and listing worker accounts.

Every route here requires the "admin" role via require_role("admin"). There is
no route anywhere in the app that lets a citizen or worker create another
worker or admin account — provisioning staff is exclusively a super admin action.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.config import settings
from backend.database import get_db
from backend.deps import require_role
from backend.models import Complaint, User
from backend.routes.auth import MIN_PASSWORD_LENGTH, UserResponse
from backend.services.auth_service import hash_password

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/admin", tags=["admin"])


class CreateWorkerRequest(BaseModel):
    """Request body for a super admin creating a new worker account."""

    full_name: str
    phone: str
    password: str
    ward: str
    preferred_language: str


class WorkerSummary(UserResponse):
    """A worker's profile plus a quick view of their current workload."""

    open_complaints: int
    resolved_complaints: int


@router.post("/workers", response_model=UserResponse)
def create_worker(
    body: CreateWorkerRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(require_role("admin")),
) -> UserResponse:
    """Create a new worker account for a given ward. Super admin only."""
    full_name = body.full_name.strip()
    phone = body.phone.strip()
    ward = body.ward.strip()

    if not full_name:
        raise HTTPException(status_code=400, detail="Full name is required.")
    if not phone:
        raise HTTPException(status_code=400, detail="Phone number is required.")
    if not ward:
        raise HTTPException(status_code=400, detail="Ward is required.")
    if len(body.password) < MIN_PASSWORD_LENGTH:
        raise HTTPException(
            status_code=400, detail=f"Password must be at least {MIN_PASSWORD_LENGTH} characters."
        )
    if body.preferred_language not in settings.SUPPORTED_LANGUAGES:
        raise HTTPException(status_code=400, detail=f"Unsupported language: {body.preferred_language}")

    if db.query(User).filter(User.phone == phone).first() is not None:
        raise HTTPException(status_code=409, detail="An account with this phone number already exists.")

    worker = User(
        full_name=full_name,
        phone=phone,
        password_hash=hash_password(body.password),
        role="worker",
        preferred_language=body.preferred_language,
        ward=ward,
    )
    db.add(worker)
    db.commit()
    db.refresh(worker)
    logger.info("Worker account created by admin (admin_id=%s, worker_id=%s, ward=%s)", admin.id, worker.id, ward)
    return UserResponse.model_validate(worker)


@router.get("/workers", response_model=list[WorkerSummary])
def list_workers(
    db: Session = Depends(get_db),
    admin: User = Depends(require_role("admin")),
) -> list[WorkerSummary]:
    """List every worker account with their current open/resolved complaint counts."""
    workers = db.query(User).filter(User.role == "worker").order_by(User.created_at.desc()).all()

    summaries = []
    for worker in workers:
        # Counted by actual assignment now, not ward text match — accurate even when a ward has
        # more than one worker (see assignment_service.py), unlike the old ward-only count.
        open_count = (
            db.query(Complaint)
            .filter(Complaint.assigned_worker_id == worker.id, Complaint.status.in_(["assigned", "accepted"]))
            .count()
        )
        resolved_count = (
            db.query(Complaint)
            .filter(Complaint.assigned_worker_id == worker.id, Complaint.status == "resolved")
            .count()
        )
        summaries.append(
            WorkerSummary(
                **UserResponse.model_validate(worker).model_dump(),
                open_complaints=open_count,
                resolved_complaints=resolved_count,
            )
        )
    return summaries

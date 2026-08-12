"""Super-admin-only endpoints: creating and listing worker accounts.

Every route here requires the "admin" role via require_role("admin"). There is
no route anywhere in the app that lets a citizen or worker create another
worker or admin account — provisioning staff is exclusively a super admin action.
"""

import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.config import settings
from backend.database import get_db
from backend.deps import require_role
from backend.models import Complaint, ComplaintRejection, ComplaintStatusHistory, ComplaintTranslation, ComplaintUpdate, User
from backend.repositories import ai_request_log_repository, complaint_workflow_repository
from backend.routes.auth import MIN_PASSWORD_LENGTH, UserResponse
from backend.services.auth_service import hash_password
from backend.services.observability import tracing

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/admin", tags=["admin"])

# "Open" = assigned to a worker but not yet resolved, at any stage of the worker's own workflow
# (see routes/complaints.py's `_STATUS_ACCEPTED`/`_STATUS_IN_PROGRESS`). Named once here so
# list_workers()'s open-count query and delete_worker()'s reset-to-pending query can't drift out
# of sync with each other the way they already did once (in_progress was added to that workflow
# without this file being updated to match -- see the ComplaintStatusHistory-related fixes below).
_OPEN_COMPLAINT_STATUSES = ("assigned", "accepted", "in_progress")


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


class UpdateWorkerRequest(BaseModel):
    """Request body for a super admin editing a worker's profile. Every field optional -- only
    the fields actually sent are changed (a PATCH, not a full replace). Deliberately excludes
    `phone` -- it's the login identifier and changing it has uniqueness/re-login implications
    this endpoint doesn't take on; nothing in this app currently needs that."""

    full_name: str | None = None
    ward: str | None = None
    preferred_language: str | None = None


class ResetWorkerPasswordRequest(BaseModel):
    """Request body for a super admin setting a new password for a worker who's lost access --
    there's no self-service "forgot password" flow anywhere in this app, so this is the only
    recovery path."""

    new_password: str


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
            .filter(Complaint.assigned_worker_id == worker.id, Complaint.status.in_(_OPEN_COMPLAINT_STATUSES))
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


@router.patch("/workers/{worker_id}", response_model=UserResponse)
def update_worker(
    worker_id: int,
    body: UpdateWorkerRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(require_role("admin")),
) -> UserResponse:
    """Edit a worker's profile (name/ward/preferred language). Super admin only. Only fields
    actually present in the request body are changed."""
    worker = db.query(User).filter(User.id == worker_id, User.role == "worker").first()
    if worker is None:
        raise HTTPException(status_code=404, detail="Worker not found.")

    if body.full_name is not None:
        full_name = body.full_name.strip()
        if not full_name:
            raise HTTPException(status_code=400, detail="Full name cannot be empty.")
        worker.full_name = full_name
    if body.ward is not None:
        ward = body.ward.strip()
        if not ward:
            raise HTTPException(status_code=400, detail="Ward cannot be empty.")
        worker.ward = ward
    if body.preferred_language is not None:
        if body.preferred_language not in settings.SUPPORTED_LANGUAGES:
            raise HTTPException(status_code=400, detail=f"Unsupported language: {body.preferred_language}")
        worker.preferred_language = body.preferred_language

    db.commit()
    db.refresh(worker)
    logger.info("Worker profile updated by admin (admin_id=%s, worker_id=%s)", admin.id, worker_id)
    return UserResponse.model_validate(worker)


@router.post("/workers/{worker_id}/reset-password", response_model=UserResponse)
def reset_worker_password(
    worker_id: int,
    body: ResetWorkerPasswordRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(require_role("admin")),
) -> UserResponse:
    """Set a new password for a worker who's lost access to their account. Super admin only."""
    worker = db.query(User).filter(User.id == worker_id, User.role == "worker").first()
    if worker is None:
        raise HTTPException(status_code=404, detail="Worker not found.")

    if len(body.new_password) < MIN_PASSWORD_LENGTH:
        raise HTTPException(status_code=400, detail=f"Password must be at least {MIN_PASSWORD_LENGTH} characters.")

    worker.password_hash = hash_password(body.new_password)
    db.commit()
    db.refresh(worker)
    logger.info("Worker password reset by admin (admin_id=%s, worker_id=%s)", admin.id, worker_id)
    return UserResponse.model_validate(worker)


# ------------------------------------------------------------------
# Worker/complaint management -- delete a worker, delete a complaint, or manually assign a
# complaint to a specific worker (an override for when assignment_service.py's automatic
# ward-matching left a complaint "pending" with nobody eligible, or an admin simply wants to
# reassign one). Every route here is super-admin-only, matching this file's own module
# docstring: provisioning/removing staff, and overriding assignment, is never available to a
# citizen or worker.
# ------------------------------------------------------------------


class AssignComplaintRequest(BaseModel):
    """Request body for a super admin manually assigning a complaint to a specific worker."""

    worker_id: int


class ComplaintAdminSummary(BaseModel):
    """Minimal confirmation of a complaint's state after an admin action -- not the full
    ComplaintResponse shape from routes/complaints.py (translation/display-text concerns that
    route owns), just enough for the Admin dashboard to update its own table row in place."""

    id: int
    status: str
    assigned_worker_id: int | None
    assigned_worker_name: str | None


class DeleteWorkerResponse(BaseModel):
    deleted_worker_id: int
    # Any complaint that was "assigned"/"accepted" to this worker is reset to "pending" (not
    # deleted) rather than left pointing at a worker id that no longer exists -- see
    # delete_worker()'s docstring. This count lets the admin dashboard tell the admin how many
    # complaints now need a new assignment.
    reset_to_pending: int


class DeleteComplaintResponse(BaseModel):
    deleted_complaint_id: int


@router.delete("/workers/{worker_id}", response_model=DeleteWorkerResponse)
def delete_worker(
    worker_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_role("admin")),
) -> DeleteWorkerResponse:
    """Delete a worker account. Super admin only.

    Any complaint currently assigned to this worker (status "assigned", "accepted", or
    "in_progress" -- see `_OPEN_COMPLAINT_STATUSES`) is reset to "pending" with no assigned
    worker -- never silently deleted along with the worker, and never left with a dangling
    `assigned_worker_id`. The admin can reassign it via POST /admin/complaints/{id}/assign, or
    leave it for a new/existing worker in that ward. Each reset is also logged to the complaint's
    status-history timeline (see complaint_workflow_repository.record_status_change()), the same
    way every other status change in this app already is.
    """
    worker = db.query(User).filter(User.id == worker_id, User.role == "worker").first()
    if worker is None:
        raise HTTPException(status_code=404, detail="Worker not found.")

    affected = (
        db.query(Complaint)
        .filter(Complaint.assigned_worker_id == worker_id, Complaint.status.in_(_OPEN_COMPLAINT_STATUSES))
        .all()
    )
    previous_statuses = {complaint.id: complaint.status for complaint in affected}
    for complaint in affected:
        complaint.status = "pending"
        complaint.assigned_worker_id = None

    db.query(ComplaintRejection).filter(ComplaintRejection.worker_id == worker_id).delete(synchronize_session=False)

    db.delete(worker)
    db.commit()

    for complaint in affected:
        complaint_workflow_repository.record_status_change(
            db, complaint, from_status=previous_statuses[complaint.id], to_status="pending",
            actor_role="admin", actor_user_id=admin.id, note="Worker account deleted.",
        )
    logger.info(
        "Worker deleted by admin (admin_id=%s, worker_id=%s, complaints_reset_to_pending=%s)",
        admin.id, worker_id, len(affected),
    )
    return DeleteWorkerResponse(deleted_worker_id=worker_id, reset_to_pending=len(affected))


@router.delete("/complaints/{complaint_id}", response_model=DeleteComplaintResponse)
def delete_complaint(
    complaint_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_role("admin")),
) -> DeleteComplaintResponse:
    """Permanently delete a complaint and every record that references it (rejections,
    translations, status history, worker-authored updates). Super admin only -- irreversible,
    unlike a status change."""
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if complaint is None:
        raise HTTPException(status_code=404, detail="Complaint not found.")

    db.query(ComplaintRejection).filter(ComplaintRejection.complaint_id == complaint_id).delete(synchronize_session=False)
    db.query(ComplaintTranslation).filter(ComplaintTranslation.complaint_id == complaint_id).delete(synchronize_session=False)
    db.query(ComplaintStatusHistory).filter(ComplaintStatusHistory.complaint_id == complaint_id).delete(synchronize_session=False)
    db.query(ComplaintUpdate).filter(ComplaintUpdate.complaint_id == complaint_id).delete(synchronize_session=False)
    db.delete(complaint)
    db.commit()
    logger.info("Complaint deleted by admin (admin_id=%s, complaint_id=%s)", admin.id, complaint_id)
    return DeleteComplaintResponse(deleted_complaint_id=complaint_id)


@router.post("/complaints/{complaint_id}/assign", response_model=ComplaintAdminSummary)
def assign_complaint(
    complaint_id: int,
    body: AssignComplaintRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(require_role("admin")),
) -> ComplaintAdminSummary:
    """Manually assign a complaint to a specific worker, overriding the automatic ward-matching
    assignment (see assignment_service.py) -- for a complaint stuck "pending" because no worker
    matched its ward automatically, or to move it to a different worker. Super admin only.
    Logged to the complaint's status-history timeline like every other status change.
    """
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if complaint is None:
        raise HTTPException(status_code=404, detail="Complaint not found.")

    worker = db.query(User).filter(User.id == body.worker_id, User.role == "worker").first()
    if worker is None:
        raise HTTPException(status_code=404, detail="Worker not found.")

    previous_status = complaint.status
    complaint.assigned_worker_id = worker.id
    complaint.status = "assigned"
    db.commit()
    complaint_workflow_repository.record_status_change(
        db, complaint, from_status=previous_status, to_status="assigned",
        actor_role="admin", actor_user_id=admin.id, note=f"Manually assigned to {worker.full_name} by admin.",
    )
    logger.info(
        "Complaint manually assigned by admin (admin_id=%s, complaint_id=%s, worker_id=%s)",
        admin.id, complaint_id, worker.id,
    )
    return ComplaintAdminSummary(
        id=complaint.id, status=complaint.status, assigned_worker_id=complaint.assigned_worker_id, assigned_worker_name=worker.full_name
    )


# ------------------------------------------------------------------
# AI Monitoring -- application-level observability for the Ask JanMitra LangGraph pipeline (see
# backend/services/observability/tracing.py and docs/ask_janmitra_langsmith_observability.md).
#
# Deliberately NOT a LangSmith dashboard reimplementation: these two endpoints read only
# `AiRequestLog` (see backend/repositories/ai_request_log_repository.py), a local table populated
# by every `/ask-janmitra` call regardless of whether LangSmith tracing is configured -- so this
# section of the Admin dashboard keeps working identically whether LangSmith is fully wired up,
# misconfigured, or not set up at all. `trace_url` on each request is the only place LangSmith
# enters the picture, and even that is a locally-built string (see `tracing.get_trace_url()`) --
# no LangSmith API call happens on this read path.
# ------------------------------------------------------------------


class AiMonitoringSummary(BaseModel):
    """High-level AI Monitoring tiles for the Admin dashboard. See
    ai_request_log_repository.get_ai_monitoring_summary() for how each field is computed."""

    total_requests: int
    successful_requests: int
    failed_requests: int
    error_rate: float
    average_latency_ms: float
    rag_requests: int
    complaint_requests: int
    status_requests: int
    out_of_scope_requests: int
    clarification_requests: int


class AiRequestLogEntry(BaseModel):
    """One row of the Admin dashboard's recent-AI-requests table."""

    id: int
    request_id: str
    intent: str | None
    service_category: str | None
    routed_to: str
    success: bool
    error_type: str | None
    latency_ms: float
    created_at: datetime
    # None when LANGSMITH_TRACE_URL_TEMPLATE isn't configured, tracing was disabled for this
    # request, or the request predates this feature -- the frontend shows the raw request id
    # without a link in that case (see tracing.get_trace_url()'s docstring).
    trace_url: str | None


@router.get("/ai-monitoring", response_model=AiMonitoringSummary)
def ai_monitoring_summary(
    db: Session = Depends(get_db),
    admin: User = Depends(require_role("admin")),
) -> AiMonitoringSummary:
    """Aggregate Ask JanMitra request counts/rates for the Admin dashboard's AI Monitoring tiles."""
    return AiMonitoringSummary(**ai_request_log_repository.get_ai_monitoring_summary(db))


@router.get("/ai-monitoring/requests", response_model=list[AiRequestLogEntry])
def ai_monitoring_requests(
    limit: int = 50,
    db: Session = Depends(get_db),
    admin: User = Depends(require_role("admin")),
) -> list[AiRequestLogEntry]:
    """Most recent Ask JanMitra requests, each with a "View Trace" link where configured."""
    rows = ai_request_log_repository.get_recent_ai_requests(db, limit=min(max(limit, 1), 200))
    return [
        AiRequestLogEntry(
            id=row.id,
            request_id=row.request_id,
            intent=row.intent,
            service_category=row.service_category,
            routed_to=row.routed_to,
            success=row.success,
            error_type=row.error_type,
            latency_ms=row.latency_ms,
            created_at=row.created_at,
            trace_url=tracing.get_trace_url(row.langsmith_trace_id),
        )
        for row in rows
    ]

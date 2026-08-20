"""Repository layer for the worker complaint-lifecycle workflow: status history, worker updates
(initial assessment / progress update / completion), and rejection-with-reason.

Mirrors complaint_repository.py's plain-function style and layering (LangGraph/route -> business
logic in the route itself for this simple a workflow -> repository -> database). Every function
here is a fixed, reviewable statement -- no LLM ever constructs or influences any of these
queries, matching this codebase's established boundary (see complaint_repository.py's docstring).
"""

from __future__ import annotations

from sqlalchemy.orm import Session

from backend.models import Complaint, ComplaintRejection, ComplaintStatusHistory, ComplaintUpdate


def record_status_change(
    db: Session,
    complaint: Complaint,
    *,
    from_status: str | None,
    to_status: str,
    actor_role: str,
    actor_user_id: int | None,
    note: str | None = None,
) -> ComplaintStatusHistory:
    """Appends one row to the complaint's status timeline. Does NOT itself change
    `complaint.status` -- callers set that separately (see routes/complaints.py), so this
    function's only job is the append-only log, never the source of truth for current status.

    `from_status` is a required, explicit argument (not read off `complaint.status`) on purpose:
    every call site sets `complaint.status = to_status` and commits before it can call this (so
    the response it returns reflects the new state) -- reading `complaint.status` in here would
    silently read the ALREADY-mutated value and record a no-op from_status == to_status transition
    every time. Pass `None` only for the complaint's very first row (no prior status).
    """
    entry = ComplaintStatusHistory(
        complaint_id=complaint.id,
        from_status=from_status,
        to_status=to_status,
        actor_role=actor_role,
        actor_user_id=actor_user_id,
        note=note,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


def get_status_history(db: Session, complaint_id: int) -> list[ComplaintStatusHistory]:
    return (
        db.query(ComplaintStatusHistory)
        .filter(ComplaintStatusHistory.complaint_id == complaint_id)
        .order_by(ComplaintStatusHistory.created_at.asc())
        .all()
    )


def add_complaint_update(
    db: Session,
    *,
    complaint_id: int,
    worker_id: int,
    update_type: str,
    text: str,
    photo_path: str | None = None,
) -> ComplaintUpdate:
    """Records one worker-authored update (INITIAL_ASSESSMENT / PROGRESS_UPDATE / COMPLETION).
    Callers are responsible for validating `text` is non-empty before calling this (see
    routes/complaints.py's mandatory-field checks) -- this function persists whatever it's given.
    """
    update = ComplaintUpdate(
        complaint_id=complaint_id,
        worker_id=worker_id,
        update_type=update_type,
        text=text,
        photo_path=photo_path,
    )
    db.add(update)
    db.commit()
    db.refresh(update)
    return update


def get_complaint_updates(db: Session, complaint_id: int) -> list[ComplaintUpdate]:
    return (
        db.query(ComplaintUpdate)
        .filter(ComplaintUpdate.complaint_id == complaint_id)
        .order_by(ComplaintUpdate.created_at.asc())
        .all()
    )


def record_rejection(db: Session, *, complaint_id: int, worker_id: int, reason: str) -> ComplaintRejection:
    """Records a worker's rejection with its mandatory reason. Replaces the previous no-reason
    insert in routes/complaints.py's reject_complaint() -- same table, same uniqueness
    constraint (complaint_id, worker_id), just with `reason` populated going forward.
    """
    rejection = ComplaintRejection(complaint_id=complaint_id, worker_id=worker_id, reason=reason)
    db.add(rejection)
    db.commit()
    db.refresh(rejection)
    return rejection


def get_rejections_for_complaint(db: Session, complaint_id: int) -> list[ComplaintRejection]:
    """Admin-only read path (see routes/complaints.py's _to_detail_response) -- citizens and
    workers never see this; only an admin viewing a complaint's detail gets these rows."""
    return (
        db.query(ComplaintRejection)
        .filter(ComplaintRejection.complaint_id == complaint_id)
        .order_by(ComplaintRejection.created_at.asc())
        .all()
    )

"""Repository layer for complaint evidence (multi-file uploads) -- see backend/models.py's
ComplaintEvidence docstring for the storage model. Mirrors complaint_workflow_repository.py's
plain-function style and layering.
"""

from __future__ import annotations

from sqlalchemy.orm import Session

from backend.models import ComplaintEvidence


def add_evidence(
    db: Session,
    *,
    complaint_id: int,
    update_id: int | None,
    uploaded_by: int,
    uploader_role: str,
    file_name: str,
    file_path: str,
    file_type: str,
    file_size: int,
    stage: str,
) -> ComplaintEvidence:
    """Records one uploaded evidence file. Callers are responsible for having already validated
    and saved the file to disk (see routes/complaints.py's _save_photo) -- this function only
    persists the metadata/reference row."""
    evidence = ComplaintEvidence(
        complaint_id=complaint_id,
        update_id=update_id,
        uploaded_by=uploaded_by,
        uploader_role=uploader_role,
        file_name=file_name,
        file_path=file_path,
        file_type=file_type,
        file_size=file_size,
        stage=stage,
    )
    db.add(evidence)
    db.commit()
    db.refresh(evidence)
    return evidence


def get_evidence_for_complaint(db: Session, complaint_id: int) -> list[ComplaintEvidence]:
    """Every evidence file on a complaint, across every stage -- callers group by `.stage`
    themselves (see routes/complaints.py's _to_detail_response / complaint_report_service.py)."""
    return (
        db.query(ComplaintEvidence)
        .filter(ComplaintEvidence.complaint_id == complaint_id)
        .order_by(ComplaintEvidence.created_at.asc())
        .all()
    )


def get_evidence_for_update(db: Session, update_id: int) -> list[ComplaintEvidence]:
    """Evidence attached to one specific worker update -- used to build the response for a
    single just-created update (see routes/complaints.py's add_progress_update/start_work),
    where fetching the whole complaint's evidence would be needless extra work."""
    return (
        db.query(ComplaintEvidence)
        .filter(ComplaintEvidence.update_id == update_id)
        .order_by(ComplaintEvidence.created_at.asc())
        .all()
    )

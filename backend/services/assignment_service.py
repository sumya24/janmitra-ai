"""Assigns a complaint to a worker, and reassigns it when the current worker rejects it.

A ward can have more than one worker. Assignment always tries workers in the same ward, in a
stable order (lowest id first — i.e. whoever was added to that ward first), skipping anyone who
has already rejected this specific complaint. If every worker in the ward has rejected it (or
there are no workers in that ward at all), the complaint goes to "pending" with no assigned
worker until an admin adds one or an existing one's ward changes.
"""

import logging

from sqlalchemy.orm import Session

from backend.models import Complaint, ComplaintRejection, User

logger = logging.getLogger(__name__)


def assign_next_worker(db: Session, complaint: Complaint) -> None:
    """Assign `complaint` to the next eligible worker in its ward, or mark it pending.

    Args:
        db: Active database session.
        complaint: The complaint to (re)assign. Mutated in place and committed.
    """
    if not complaint.ward:
        complaint.status = "pending"
        complaint.assigned_worker_id = None
        db.commit()
        return

    already_rejected_ids = {
        row.worker_id
        for row in db.query(ComplaintRejection).filter(ComplaintRejection.complaint_id == complaint.id).all()
    }

    candidates = (
        db.query(User)
        .filter(User.role == "worker", User.ward == complaint.ward)
        .order_by(User.id.asc())
        .all()
    )
    next_worker = next((w for w in candidates if w.id not in already_rejected_ids), None)

    if next_worker is None:
        complaint.status = "pending"
        complaint.assigned_worker_id = None
        logger.info("Complaint %s has no eligible worker left in ward %r; now pending", complaint.id, complaint.ward)
    else:
        complaint.status = "assigned"
        complaint.assigned_worker_id = next_worker.id
        logger.info("Complaint %s assigned to worker %s (ward=%r)", complaint.id, next_worker.id, complaint.ward)

    db.commit()

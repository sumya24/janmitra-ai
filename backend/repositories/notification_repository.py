"""Repository layer for `Notification` -- see models.py's `Notification` docstring for scope
(worker-only, NEW_ASSIGNMENT/REASSIGNED, created solely from assignment_service.py).
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from backend.models import Notification


def create_notification(
    db: Session,
    *,
    recipient_id: int,
    type: str,
    title: str,
    message: str,
    complaint_id: int | None,
) -> Notification:
    notification = Notification(
        recipient_id=recipient_id, type=type, title=title, message=message, complaint_id=complaint_id,
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification


def list_notifications(db: Session, recipient_id: int, limit: int = 50) -> list[Notification]:
    return (
        db.query(Notification)
        .filter(Notification.recipient_id == recipient_id)
        .order_by(Notification.created_at.desc())
        .limit(limit)
        .all()
    )


def count_unread(db: Session, recipient_id: int) -> int:
    return (
        db.query(Notification)
        .filter(Notification.recipient_id == recipient_id, Notification.read_at.is_(None))
        .count()
    )


def mark_read(db: Session, notification: Notification) -> Notification:
    """Marks one notification read -- idempotent (re-marking an already-read notification just
    leaves its original read_at untouched, never bumped forward)."""
    if notification.read_at is None:
        notification.read_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(notification)
    return notification

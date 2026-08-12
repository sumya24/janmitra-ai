"""API endpoints for a user's own in-app notifications -- see models.py's `Notification`
docstring for scope (worker-only today, created solely by assignment_service.py).
"""

import logging

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.deps import get_current_user
from backend.models import Notification, User
from backend.repositories import notification_repository

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/notifications", tags=["notifications"])


class NotificationResponse(BaseModel):
    id: int
    type: str
    title: str
    message: str
    complaint_id: int | None
    created_at: str
    read_at: str | None

    model_config = ConfigDict(from_attributes=True)


class NotificationListResponse(BaseModel):
    notifications: list[NotificationResponse]
    unread_count: int


def _to_response(n) -> NotificationResponse:
    return NotificationResponse(
        id=n.id, type=n.type, title=n.title, message=n.message, complaint_id=n.complaint_id,
        created_at=n.created_at.isoformat(),
        read_at=n.read_at.isoformat() if n.read_at else None,
    )


@router.get("", response_model=NotificationListResponse)
def list_notifications(
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> NotificationListResponse:
    """The current user's own notifications, most recent first, plus their unread count. Every
    role can call this (not worker-only) even though only workers are ever sent one today --
    scoped to `recipient_id == current_user.id` regardless of role, so it's naturally correct if
    a future phase starts notifying citizens/admins too, with zero route changes needed.
    """
    rows = notification_repository.list_notifications(db, current_user.id, limit=min(max(limit, 1), 200))
    unread = notification_repository.count_unread(db, current_user.id)
    return NotificationListResponse(notifications=[_to_response(n) for n in rows], unread_count=unread)


@router.post("/{notification_id}/read", response_model=NotificationResponse)
def mark_notification_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> NotificationResponse:
    """Marks one of the current user's own notifications read. Idempotent -- marking an
    already-read notification again just returns it unchanged (see notification_repository.
    mark_read). A user can never mark someone else's notification read (404, not 403 -- doesn't
    reveal whether the id belongs to another user at all).
    """
    notification = (
        db.query(Notification)
        .filter(Notification.id == notification_id, Notification.recipient_id == current_user.id)
        .first()
    )
    if notification is None:
        raise HTTPException(status_code=404, detail="Notification not found.")
    updated = notification_repository.mark_read(db, notification)
    return _to_response(updated)

"""ORM models for the JanMitra AI database."""

from datetime import datetime, timezone

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.database import Base


class Complaint(Base):
    """A single citizen complaint about garbage collection.

    Attributes:
        id: Primary key.
        citizen_id: Hardcoded citizen identifier (no auth in Milestone 1).
        original_text: The complaint text as spoken/typed by the citizen.
        original_language: Short language code of the original text (e.g. "mr").
        translated_text: The complaint translated into English (canonical storage).
        summary: A short LLM-generated summary of the complaint.
        photo_path: Relative path to an optionally attached photo, or None.
        status: Either "open" or "resolved".
        created_at: UTC timestamp of when the complaint was created.
    """

    __tablename__ = "complaints"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    citizen_id: Mapped[str] = mapped_column(String(64), nullable=False)
    original_text: Mapped[str] = mapped_column(Text, nullable=False)
    original_language: Mapped[str] = mapped_column(String(8), nullable=False)
    translated_text: Mapped[str] = mapped_column(Text, nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    photo_path: Mapped[str | None] = mapped_column(String(512), nullable=True)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="open")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )

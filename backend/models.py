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
    ward: Mapped[str | None] = mapped_column(String(120), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )


class User(Base):
    """A JanMitra AI account: a citizen, a worker, or a super admin.

    Citizens self-register (see routes/auth.py). Workers are only ever created by
    a super admin (see routes/admin.py) — there is deliberately no way for anyone
    to sign up as a worker or as a super admin; the first super admin account is
    seeded directly into the database when the system is set up.

    Attributes:
        id: Primary key.
        phone: Login identifier, unique.
        password_hash: Bcrypt hash of the password — the plaintext is never stored.
        full_name: Display name.
        role: One of "citizen", "worker", "admin".
        preferred_language: Short language code, e.g. "mr", used across the app
            and changeable anytime from account settings.
        ward: The area a worker is responsible for. Unused for citizens/admins.
        created_at: UTC timestamp of account creation.
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    phone: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    role: Mapped[str] = mapped_column(String(16), nullable=False)
    preferred_language: Mapped[str] = mapped_column(String(8), nullable=False, default="en")
    ward: Mapped[str | None] = mapped_column(String(120), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )

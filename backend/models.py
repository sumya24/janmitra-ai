"""ORM models for the JanMitra AI database."""

from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from backend.database import Base


class Complaint(Base):
    """A single citizen complaint, tracked through an assignment/accept/reject/resolve lifecycle.

    Attributes:
        id: Primary key.
        citizen_id: The citizen who filed this complaint.
        original_text: The complaint text as spoken/typed by the citizen.
        original_language: Short language code of the original text (e.g. "mr").
        translated_text: The complaint translated into English (canonical storage).
        summary: A short LLM-generated summary of the complaint.
        photo_path: Relative path to an optionally attached photo, or None.
        status: One of "pending" (no eligible worker assigned yet — either just created with
            no ward, or every worker in its ward has rejected it), "assigned" (waiting on
            assigned_worker_id to accept or reject), "accepted" (that worker is actively on
            it), "resolved" (done).
        ward: The area this complaint is in; drives which worker(s) it can be assigned to.
        assigned_worker_id: The worker currently responsible for this complaint, or None if
            status is "pending". Reassigned automatically (see assignment_service.py) to the
            next eligible worker in the same ward whenever the current one rejects.
        feedback_rating: Citizen's 1-5 rating left after resolution, or None if not given yet.
        feedback_comment: Citizen's optional free-text feedback alongside the rating.
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
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="pending")
    ward: Mapped[str | None] = mapped_column(String(120), nullable=True)
    assigned_worker_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    feedback_rating: Mapped[int | None] = mapped_column(nullable=True)
    feedback_comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )


class ComplaintRejection(Base):
    """Records that a worker rejected a complaint, so reassignment never offers it to them again.

    Attributes:
        id: Primary key.
        complaint_id: The complaint that was rejected.
        worker_id: The worker who rejected it.
        created_at: UTC timestamp of the rejection.
    """

    __tablename__ = "complaint_rejections"
    __table_args__ = (UniqueConstraint("complaint_id", "worker_id", name="uq_complaint_rejection"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    complaint_id: Mapped[int] = mapped_column(ForeignKey("complaints.id"), nullable=False, index=True)
    worker_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )


class ComplaintTranslation(Base):
    """A cached translation of a complaint's canonical English text into one display language.

    `Complaint.translated_text` is always English (see ComplaintAgent) — this table is the
    on-demand cache for every other language a complaint gets viewed in, so the same
    complaint/language pair is only ever translated once via Sarvam, not on every read.

    Attributes:
        id: Primary key.
        complaint_id: The complaint this translation belongs to.
        language_code: Short language code the text is translated into, e.g. "hi".
        translated_text: The complaint's English text translated into language_code.
        translated_summary: The complaint's English AI summary translated into language_code.
            Nullable only because rows cached before this field existed won't have it; every
            row written from here on always populates both together.
        created_at: UTC timestamp of when this translation was cached.
    """

    __tablename__ = "complaint_translations"
    __table_args__ = (UniqueConstraint("complaint_id", "language_code", name="uq_complaint_translation_lang"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    complaint_id: Mapped[int] = mapped_column(ForeignKey("complaints.id"), nullable=False, index=True)
    language_code: Mapped[str] = mapped_column(String(8), nullable=False)
    translated_text: Mapped[str] = mapped_column(Text, nullable=False)
    translated_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
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

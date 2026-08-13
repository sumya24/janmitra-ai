"""ORM models for the JanSarthi AI database."""

from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from backend.database import Base


def _utcnow() -> datetime:
    """Shared default= for every created_at/updated_at below -- same value the pre-existing
    models already used inline, factored out once the location-hierarchy tables (added in the
    location migration) made repeating it seven more times not worth it."""
    return datetime.now(timezone.utc)


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
            assigned_worker_id to accept or reject), "accepted" (that worker has accepted but
            not yet started work), "in_progress" (worker has started work and submitted a
            mandatory initial assessment -- see ComplaintUpdate), "resolved" (worker has
            submitted a mandatory completion status -- see ComplaintUpdate -- and marked it
            done). Still a plain string, not a DB-level enum (unchanged from before "in_progress"
            was added) -- every transition is validated in routes/complaints.py, not by a column
            constraint.
        ward: The area this complaint is in (free text); drives which worker(s) it can be
            assigned to (see assignment_service.py). Kept as-is for backward compatibility --
            still populated the same way, from the citizen's dropdown pick at submission time.
        ward_id..locality_id: The SAME incident location, structured -- populated where it could
            be resolved (either by matching `ward` text against the wards table, or by
            LocationResolver from GPS coordinates), left null otherwise. Never backfilled from
            the citizen's account -- a complaint's location is always independent of any user
            profile field, by design (see docs/location_migration_plan.md §D/§6).
        latitude, longitude, gps_accuracy: Raw coordinates captured by the citizen's browser at
            submission time, if they granted permission and chose "use current location" --
            stored exactly as received, never derived/estimated when absent.
        address: Free-text address the citizen typed, or a resolver-provided formatted address --
            independent of the structured hierarchy fields, which may be partially or fully null
            even when this is populated.
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
    state_id: Mapped[int | None] = mapped_column(ForeignKey("states.id"), nullable=True)
    district_id: Mapped[int | None] = mapped_column(ForeignKey("districts.id"), nullable=True)
    sub_district_id: Mapped[int | None] = mapped_column(ForeignKey("sub_districts.id"), nullable=True)
    ulb_id: Mapped[int | None] = mapped_column(ForeignKey("ulbs.id"), nullable=True)
    zone_id: Mapped[int | None] = mapped_column(ForeignKey("zones.id"), nullable=True)
    ward_id: Mapped[int | None] = mapped_column(ForeignKey("wards.id"), nullable=True)
    locality_id: Mapped[int | None] = mapped_column(ForeignKey("localities.id"), nullable=True)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    gps_accuracy: Mapped[float | None] = mapped_column(Float, nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
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
        reason: Why the worker rejected it -- mandatory going forward (enforced in
            routes/complaints.py's reject_complaint(), not at the column level: this table
            predates the reason requirement, and a NOT NULL column would break loading any
            pre-existing row written before this migration; see
            scripts/migrate_worker_workflow.py). Nullable only for that backward-compatibility
            reason, not because a new rejection may omit it.
        created_at: UTC timestamp of the rejection.
    """

    __tablename__ = "complaint_rejections"
    __table_args__ = (UniqueConstraint("complaint_id", "worker_id", name="uq_complaint_rejection"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    complaint_id: Mapped[int] = mapped_column(ForeignKey("complaints.id"), nullable=False, index=True)
    worker_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )


class ComplaintStatusHistory(Base):
    """Append-only log of every status change a complaint goes through -- the data source for
    the timeline shown to both worker and citizen (see routes/complaints.py's
    GET /complaints/{id}/history). `Complaint.status` remains the single current-state field,
    unchanged -- this table only ever adds a row alongside a status change, it never becomes
    "the" place status lives (nothing reads current status from here).

    Attributes:
        id: Primary key.
        complaint_id: The complaint this event belongs to.
        from_status: The status before this change, or None for the complaint's creation event.
        to_status: The status after this change.
        actor_role: "citizen" | "worker" | "system" | "admin" -- who/what caused this transition.
            Assignment/reassignment is automatic ("system", see assignment_service.py); every
            other transition today is caused by the worker who's assigned to the complaint.
        actor_user_id: The user who caused it, or None for system-driven transitions.
        note: Optional short human-readable context (e.g. "Reassigned after rejection", "No
            eligible worker left in ward"). Deliberately never the full rejection reason --
            ComplaintRejection remains the single source of truth for that text, to avoid storing
            the same fact in two places.
        created_at: UTC timestamp of the transition.
    """

    __tablename__ = "complaint_status_history"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    complaint_id: Mapped[int] = mapped_column(ForeignKey("complaints.id"), nullable=False, index=True)
    from_status: Mapped[str | None] = mapped_column(String(16), nullable=True)
    to_status: Mapped[str] = mapped_column(String(16), nullable=False)
    actor_role: Mapped[str] = mapped_column(String(16), nullable=False)
    actor_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    note: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=_utcnow)


class ComplaintUpdate(Base):
    """A worker-authored update on a complaint: the mandatory initial assessment when work
    starts, an optional progress update while in progress, or the mandatory completion status
    when resolving. One table, discriminated by `update_type`, rather than three near-identical
    tables -- all three are "a worker wrote some text (and maybe a photo) about this complaint at
    a point in time", differing only in when they're allowed and whether they're required.

    Attributes:
        id: Primary key.
        complaint_id: The complaint this update belongs to.
        worker_id: The worker who wrote it.
        update_type: "INITIAL_ASSESSMENT" | "PROGRESS_UPDATE" | "COMPLETION".
        text: The worker's own words -- mandatory for INITIAL_ASSESSMENT and COMPLETION;
            PROGRESS_UPDATE rows are themselves optional (zero or more), but any row that does
            exist still has non-empty text (enforced in routes/complaints.py).
        photo_path: Optional evidence photo (relative filename, same storage/serving mechanism
            as citizen complaint photos -- see routes/complaints.py's _save_photo, reused
            unchanged). Only ever populated for PROGRESS_UPDATE or COMPLETION.
        created_at: UTC timestamp.
    """

    __tablename__ = "complaint_updates"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    complaint_id: Mapped[int] = mapped_column(ForeignKey("complaints.id"), nullable=False, index=True)
    worker_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    update_type: Mapped[str] = mapped_column(String(24), nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    photo_path: Mapped[str | None] = mapped_column(String(512), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=_utcnow)


class ComplaintEvidence(Base):
    """One uploaded evidence file (photo) on a complaint -- the multi-file evidence system
    (evidence upload phase). Supersedes `Complaint.photo_path` / `ComplaintUpdate.photo_path`
    (single-file columns, kept as-is for backward compatibility with rows written before this
    table existed -- see those models' own docstrings) as the storage for every *new* upload:
    a citizen's complaint photos, a worker's initial-assessment/progress/completion evidence.
    One row per file, rather than reusing/widening the old single-string columns, because a
    complaint or update can now have zero-to-many evidence files, not at most one.

    Storage itself is unchanged from the rest of the app: files still live on the local
    filesystem under settings.UPLOAD_FOLDER and are served from the existing unauthenticated
    `/uploads` static mount (see main.py) -- same posture as every photo already in production
    (unguessable uuid4().hex filenames, no per-request authorization check on the static route).
    This table only adds the metadata/reference layer on top of that unchanged mechanism; it
    does not introduce a new storage provider.

    Attributes:
        id: Primary key.
        complaint_id: The complaint this evidence belongs to.
        update_id: The specific ComplaintUpdate (initial assessment / progress update /
            completion) this evidence was attached to, or None for evidence attached at
            complaint-creation time (stage="CITIZEN_COMPLAINT", which precedes any update row).
        uploaded_by: The user who uploaded this file.
        uploader_role: "citizen" | "worker" -- denormalized at upload time (rather than joined
            from `uploaded_by` on every read) so evidence can be labeled by source even if the
            uploader's account is later modified; matches this phase's explicit requirement to
            keep citizen and worker evidence visibly distinguishable.
        file_name: Original filename as uploaded (display only, e.g. in a report or gallery
            caption) -- never used to construct a filesystem path.
        file_path: Relative filename in settings.UPLOAD_FOLDER (uuid4().hex + extension, from
            the same _save_photo() validation/storage helper every other photo in this app
            already uses) -- served via GET /uploads/{file_path}, same as photo_path elsewhere.
        file_type: The uploaded file's content-type (e.g. "image/jpeg").
        file_size: Size in bytes, as validated against settings.MAX_PHOTO_SIZE_BYTES at upload.
        stage: "CITIZEN_COMPLAINT" | "INITIAL_ASSESSMENT" | "PROGRESS_UPDATE" | "COMPLETION" --
            mirrors ComplaintUpdate.update_type for the three worker stages, plus one more value
            for evidence attached directly to the complaint at creation (before any update
            exists yet).
        created_at: UTC timestamp.
    """

    __tablename__ = "complaint_evidence"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    complaint_id: Mapped[int] = mapped_column(ForeignKey("complaints.id"), nullable=False, index=True)
    update_id: Mapped[int | None] = mapped_column(ForeignKey("complaint_updates.id"), nullable=True, index=True)
    uploaded_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    uploader_role: Mapped[str] = mapped_column(String(16), nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(512), nullable=False)
    file_type: Mapped[str] = mapped_column(String(64), nullable=False)
    file_size: Mapped[int] = mapped_column(nullable=False)
    stage: Mapped[str] = mapped_column(String(24), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=_utcnow)


class Notification(Base):
    """An in-app notification for a user -- workers get one for a new/reassigned complaint (see
    assignment_service.py's assign_next_worker()), and citizens get one for their own complaint's
    key status changes (see routes/complaints.py's accept_complaint/start_work/resolve_complaint,
    the three creation sites). Deliberately minimal: no push/SMS/email delivery, no per-user
    preferences -- just a row a user's own GET /notifications can list, and mark read
    individually.

    Attributes:
        id: Primary key.
        recipient_id: The user this notification is for.
        type: "NEW_ASSIGNMENT" | "REASSIGNED" (worker-facing) | "COMPLAINT_ACCEPTED" |
            "COMPLAINT_STARTED" | "COMPLAINT_RESOLVED" (citizen-facing). Deliberately no
            per-progress-update notification type -- a citizen would get one per optional worker
            update, which is noisy; ComplaintUpdatesTimeline already surfaces those on request
            instead of pushing a notification for each one.
        title: Short headline, already-formatted (e.g. "New complaint assigned").
        message: One-line detail (e.g. "Streetlight complaint — Ward 14").
        complaint_id: The complaint this notification is about, or None (kept nullable for
            forward compatibility; every notification generated today has one).
        created_at: UTC timestamp.
        read_at: UTC timestamp the recipient's client marked it read, or None while unread.
    """

    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    recipient_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    type: Mapped[str] = mapped_column(String(32), nullable=False)
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    message: Mapped[str] = mapped_column(String(255), nullable=False)
    complaint_id: Mapped[int | None] = mapped_column(ForeignKey("complaints.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=_utcnow)
    read_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


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


class State(Base):
    """One Indian state or union territory. Top of the administrative hierarchy.

    Seeded once, nationally, via scripts/seed_location_master_data.py -- see that script's
    docstring and reports/location_migration_report.md for sourcing.

    Attributes:
        id: Primary key.
        name: Full name, e.g. "Maharashtra".
        code: Short code, e.g. "MH". Unique.
        country_code: Always "IN" today; kept as a column (not hardcoded) so a future
            multi-country deployment wouldn't need a schema change, not because multi-country
            support is planned.
        is_union_territory: True for the 8 UTs, False for the 28 states.
        source_name, source_type, source_url: Provenance of this row (see below).
    """

    __tablename__ = "states"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    code: Mapped[str] = mapped_column(String(8), unique=True, nullable=False)
    country_code: Mapped[str] = mapped_column(String(2), nullable=False, default="IN")
    is_union_territory: Mapped[bool] = mapped_column(nullable=False, default=False)
    source_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    source_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    source_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=_utcnow, onupdate=_utcnow)


class District(Base):
    """One district within a state. Every district belongs to exactly one state."""

    __tablename__ = "districts"
    __table_args__ = (UniqueConstraint("state_id", "name", name="uq_district_state_name"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    state_id: Mapped[int] = mapped_column(ForeignKey("states.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[str | None] = mapped_column(String(16), nullable=True)
    source_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    source_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    source_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=_utcnow, onupdate=_utcnow)


class SubDistrict(Base):
    """One sub-district/tehsil/taluka within a district. Not every place this app knows about
    has one on record -- see ULB.sub_district_id, which is nullable for exactly that reason."""

    __tablename__ = "sub_districts"
    __table_args__ = (UniqueConstraint("district_id", "name", name="uq_subdistrict_district_name"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    district_id: Mapped[int] = mapped_column(ForeignKey("districts.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[str | None] = mapped_column(String(16), nullable=True)
    source_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    source_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    source_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=_utcnow, onupdate=_utcnow)


class ULB(Base):
    """An Urban Local Body -- Municipal Corporation, Municipality, or Notified Area Council/
    equivalent -- the level that actually runs civic services (the same level the RAG knowledge
    base's citizen-charter sources describe).

    Attributes:
        type: Free text, e.g. "Municipal Corporation", "Municipality", "NAC" -- not an enum,
            since the real terminology varies by state (see e.g. the Odisha RAG source's
            "Municipal Corporations / Municipalities / NACs" split) and forcing one canonical
            set here isn't this migration's job.
    """

    __tablename__ = "ulbs"
    __table_args__ = (UniqueConstraint("district_id", "name", name="uq_ulb_district_name"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    district_id: Mapped[int] = mapped_column(ForeignKey("districts.id"), nullable=False, index=True)
    sub_district_id: Mapped[int | None] = mapped_column(ForeignKey("sub_districts.id"), nullable=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    code: Mapped[str | None] = mapped_column(String(16), nullable=True)
    source_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    source_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    source_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=_utcnow, onupdate=_utcnow)


class Zone(Base):
    """An intra-ULB administrative zone (e.g. BBMP's zones). Not every ULB has one -- Ward.zone_id
    is nullable for exactly that reason; this table simply isn't populated for ULBs that don't."""

    __tablename__ = "zones"
    __table_args__ = (UniqueConstraint("ulb_id", "name", name="uq_zone_ulb_name"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    ulb_id: Mapped[int] = mapped_column(ForeignKey("ulbs.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[str | None] = mapped_column(String(16), nullable=True)
    source_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    source_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    source_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=_utcnow, onupdate=_utcnow)


class Ward(Base):
    """One ward within a ULB -- the level the app's existing assignment logic already operates
    on (see User.ward / Complaint.ward, both still free text; this table is the new structured
    counterpart, not a replacement -- see assignment_service.py and the location migration plan).

    A ward number/name is only unique *within its ULB* (e.g. "Ward 24" exists in many different
    cities) -- never treat `name` or `ward_number` as globally unique; see the unique constraint.
    """

    __tablename__ = "wards"
    __table_args__ = (UniqueConstraint("ulb_id", "name", name="uq_ward_ulb_name"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    ulb_id: Mapped[int] = mapped_column(ForeignKey("ulbs.id"), nullable=False, index=True)
    zone_id: Mapped[int | None] = mapped_column(ForeignKey("zones.id"), nullable=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    ward_number: Mapped[str | None] = mapped_column(String(16), nullable=True)
    code: Mapped[str | None] = mapped_column(String(16), nullable=True)
    source_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    source_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    source_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=_utcnow, onupdate=_utcnow)


class Locality(Base):
    """A named locality/area within a ward -- the finest granularity this app tracks. Not
    populated at all where no confident source exists (see the location migration report) --
    never fabricated to fill out the hierarchy."""

    __tablename__ = "localities"
    __table_args__ = (UniqueConstraint("ward_id", "name", name="uq_locality_ward_name"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    ward_id: Mapped[int] = mapped_column(ForeignKey("wards.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    pincode: Mapped[str | None] = mapped_column(String(10), nullable=True)
    code: Mapped[str | None] = mapped_column(String(16), nullable=True)
    source_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    source_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    source_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=_utcnow, onupdate=_utcnow)


class AiRequestLog(Base):
    """One row per Ask Sarthi request -- the local, always-available data source for the Admin
    "AI Monitoring" dashboard (see routes/admin.py's /admin/ai-monitoring endpoints and
    backend/repositories/ai_request_log_repository.py).

    Deliberately NOT read back from LangSmith: PostgreSQL remains the operational source of
    truth (see docs/ask_janmitra_langsmith_observability.md), and the admin dashboard must keep
    working even when LangSmith is unreachable or unconfigured (see
    backend/services/observability/tracing.py's module docstring). `langsmith_trace_id` is
    stored only as a pointer for the optional "View Trace" link -- this table is never populated
    *from* LangSmith, only alongside it, by the same request that (separately, best-effort)
    sends a trace there.

    Attributes:
        id: Primary key.
        request_id: Short correlation id, also used in this request's log lines (see
            orchestration/graph.py's run_graph()).
        langsmith_trace_id: Full UUID used as the LangSmith root run id for this request, or
            None if tracing was disabled/unavailable when this request ran.
        conversation_id: Client-supplied conversation identifier, if any -- currently always
            None (see AskJanMitraRequest/GraphState's conversation_id field; this app has no
            server-side session/conversation id yet, so this column is forward-compatible
            plumbing, not something populated today).
        intent: QuestionIntent.value the request was classified as, or None if the request
            failed before classification completed.
        service_category: ServiceCategory.value, or None.
        routed_to: Same value as AskJanMitraResponse.routed_to, or "ERROR" if the request raised
            an exception before a route was decided.
        success: False if handling this request raised an exception.
        error_type: The exception's class name only (e.g. "AIServiceError") -- never its message,
            so this column doesn't need the same per-field PII review traced text does (see
            tracing.py's docstring).
        latency_ms: Total wall-clock time for the request.
        created_at: UTC timestamp.
    """

    __tablename__ = "ai_request_logs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    request_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    langsmith_trace_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    conversation_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    intent: Mapped[str | None] = mapped_column(String(32), nullable=True)
    service_category: Mapped[str | None] = mapped_column(String(64), nullable=True)
    routed_to: Mapped[str] = mapped_column(String(32), nullable=False)
    success: Mapped[bool] = mapped_column(nullable=False, default=True)
    error_type: Mapped[str | None] = mapped_column(String(120), nullable=True)
    latency_ms: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=_utcnow)


class AiAlertState(Base):
    """Tracks the last time each AI-monitoring alert type fired -- the cooldown mechanism behind
    `ai_request_log_repository.check_and_fire_alerts()`. Without this, a sustained error-rate or
    latency problem would create a new admin Notification on every single request while it
    persists, instead of once per cooldown window.

    One row per alert type, created lazily the first time that type ever fires -- there is no
    seed data and no route that lists this table directly (it's internal alerting state, not
    something the Admin dashboard reads).

    Attributes:
        id: Primary key.
        alert_type: "HIGH_ERROR_RATE" | "HIGH_LATENCY" today -- see that function for where new
            types would be added.
        last_fired_at: UTC timestamp this alert type last actually notified admins.
    """

    __tablename__ = "ai_alert_states"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    alert_type: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    last_fired_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)


class User(Base):
    """A JanSarthi AI account: a citizen, a worker, or a super admin.

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
        ward: For a worker, the area they're responsible for (operational area). For a citizen,
            their own residence's ward -- mandatory, one-time-at-signup (see routes/auth.py's
            SignupRequest.ward; deliberately not editable later, no ward field on
            MeUpdateRequest), matched against the same free-text values workers use and the
            same list GET /complaints/wards already returns. Backs "My Area" (GET
            /complaints/area-summary): the ward-wide anonymized complaint view a citizen sees is
            just `Complaint.ward == citizen.ward`. Still unused for admins.
        state_id..locality_id: The structured counterpart of `ward` (operational area) --
            populated where `ward`'s free text could be resolved (see LocationResolver /
            scripts/migrate_existing_locations.py). Still unused for citizens/admins, same as
            `ward` itself. This is what assignment_service.py now prefers when set (falling back
            to the `ward` text match otherwise) -- see that module.
        home_state_id..home_locality_id: A DIFFERENT, still-unused concept -- reserved for a
            future *structured* citizen residence location (cascading state/district/.../ward
            picker), distinct from the simple free-text `ward` above, which already serves
            today's citizen-location need (signup + "My Area"). Not the same as `ward`/`ward_id`
            above (a worker's operational area) and not the same as any complaint's own incident
            location (Complaint.state_id etc, independent of both). Nothing currently backfills
            these for any existing account — they start, and today remain, entirely null for
            every user, including workers (whose location data is operational, not residential,
            and belongs in `ward`/`ward_id` instead).
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
    state_id: Mapped[int | None] = mapped_column(ForeignKey("states.id"), nullable=True)
    district_id: Mapped[int | None] = mapped_column(ForeignKey("districts.id"), nullable=True)
    sub_district_id: Mapped[int | None] = mapped_column(ForeignKey("sub_districts.id"), nullable=True)
    ulb_id: Mapped[int | None] = mapped_column(ForeignKey("ulbs.id"), nullable=True)
    zone_id: Mapped[int | None] = mapped_column(ForeignKey("zones.id"), nullable=True)
    ward_id: Mapped[int | None] = mapped_column(ForeignKey("wards.id"), nullable=True)
    locality_id: Mapped[int | None] = mapped_column(ForeignKey("localities.id"), nullable=True)
    home_state_id: Mapped[int | None] = mapped_column(ForeignKey("states.id"), nullable=True)
    home_district_id: Mapped[int | None] = mapped_column(ForeignKey("districts.id"), nullable=True)
    home_sub_district_id: Mapped[int | None] = mapped_column(ForeignKey("sub_districts.id"), nullable=True)
    home_ulb_id: Mapped[int | None] = mapped_column(ForeignKey("ulbs.id"), nullable=True)
    home_zone_id: Mapped[int | None] = mapped_column(ForeignKey("zones.id"), nullable=True)
    home_ward_id: Mapped[int | None] = mapped_column(ForeignKey("wards.id"), nullable=True)
    home_locality_id: Mapped[int | None] = mapped_column(ForeignKey("localities.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )

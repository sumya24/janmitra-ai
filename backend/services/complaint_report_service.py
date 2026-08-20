"""Builds a Complaint Resolution Report -- both the JSON shape ("View Report") and a downloadable
PDF ("Download Report") -- entirely from data already in the database (Complaint,
ComplaintStatusHistory, ComplaintUpdate). NEVER calls an LLM or invents any fact: the report is a
deterministic rendering of rows that already exist, matching this project's hard rule that a
report must reflect only what was actually recorded (see routes/complaints.py's report
endpoints, which refuse to generate one at all for a complaint that isn't `resolved`).

PDF generation uses `reportlab` (already a project dependency as of this phase -- see
requirements.txt) -- a plain, dependency-light choice: no headless browser, no system libraries
beyond pure Python, appropriate for a short, structured, single-page-ish document. No existing
report-generation infrastructure was found in this codebase before this phase (checked
requirements.txt and grepped for pdf/reportlab/weasyprint -- none present).
"""

from __future__ import annotations

import io
import logging
from dataclasses import dataclass, field
from datetime import datetime
from functools import partial
from pathlib import Path

from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas as pdfcanvas
from reportlab.platypus import BaseDocTemplate, Frame, Image as RLImage, PageTemplate, Paragraph, Spacer, Table, TableStyle
from sqlalchemy.orm import Session

from backend.config import settings
from backend.models import Complaint, ComplaintStatusHistory, ComplaintUpdate, District, State, ULB, User
from backend.repositories import complaint_workflow_repository, evidence_repository
from backend.services.complaint_translation_cache import get_display_text_and_summary
from backend.services.complaint_update_translation_cache import get_display_text as get_display_update_text
from backend.services.sarvam_client import AIServiceError
from backend.services.translation_service import TranslationService

logger = logging.getLogger(__name__)


@dataclass
class ComplaintReportData:
    """Everything the report shows -- one field per fact, so the JSON ("View Report") and PDF
    ("Download Report") renderers can't drift apart; both are built from this same object."""

    complaint_id: int
    display_id: str  # "JM-00042", matching the frontend's existing id formatting convention
    service_summary: str
    original_description: str
    created_at: datetime
    location_ward: str | None
    location_state: str | None
    location_district: str | None
    location_ulb: str | None
    location_address: str | None
    assigned_worker_name: str | None
    initial_assessment: str | None
    initial_assessment_at: datetime | None
    # [{text, photo_path, created_at, evidence: [file_path, ...]}] -- `evidence` is the
    # multi-file replacement for the old single `photo_path`, see ComplaintEvidence.
    progress_updates: list[dict] = field(default_factory=list)
    completion_status: str | None = None
    completion_evidence_photo: str | None = None  # legacy single-photo column, old rows only
    resolved_at: datetime | None = None
    timeline: list[dict] = field(default_factory=list)  # [{from_status, to_status, note, created_at}]
    # Evidence upload phase -- file_path lists from ComplaintEvidence, grouped by stage. Never
    # populated from the legacy single-photo columns (those stay in the fields above, for rows
    # written before this table existed).
    citizen_evidence: list[str] = field(default_factory=list)
    initial_assessment_evidence: list[str] = field(default_factory=list)
    completion_evidence: list[str] = field(default_factory=list)


def build_report_data(
    db: Session,
    complaint: Complaint,
    display_language: str | None = None,
    translation_service: TranslationService | None = None,
) -> ComplaintReportData:
    """Assembles a ComplaintReportData from the database. Caller (routes/complaints.py) is
    responsible for having already verified `complaint.status == "resolved"` and that the
    requester is authorized to see this complaint -- this function does no authorization/status
    checking itself, it only reads and shapes data.

    LIVE PRODUCT FINDING: `service_summary`/`original_description` used to always be the stored
    English text (`complaint.summary`/`complaint.translated_text`), even when every other view of
    the same complaint (the complaints list/detail endpoints, via `_to_response`'s own
    `get_display_text_and_summary` call) already translates them into the viewer's own language on
    read. Reported directly: a Marathi-speaking citizen saw the complaint LIST show her complaint
    in Marathi, but the Report/Summary view of that exact same complaint show it in raw English --
    a real, visible inconsistency, not a translation failure (the cache/translation mechanism
    already existed and already worked; the report just never called it).

    `display_language`/`translation_service` are both optional and default to None, matching this
    function's existing callers unchanged: `download_report` (the PDF) intentionally keeps
    passing neither, so the downloadable document's language is untouched by this fix -- only
    `view_report` (the JSON "View Report"/"Summary" data) now passes the viewer's own language.
    On any translation failure, falls back to the stored English text exactly like `_to_response`
    already does -- this must never turn a translation hiccup into a broken/missing report.
    """
    service_summary = complaint.summary
    original_description = complaint.translated_text
    if display_language and display_language != "en" and translation_service is not None:
        try:
            original_description, service_summary = get_display_text_and_summary(
                db, complaint, display_language, translation_service
            )
        except AIServiceError as exc:
            logger.error("On-read translation failed for complaint %s report: %s", complaint.id, exc)
            service_summary = complaint.summary
            original_description = complaint.translated_text

    def _display_update_text(update: ComplaintUpdate | None) -> str | None:
        """Same optional-translation-with-fallback shape as the block just above, applied to a
        worker-authored ComplaintUpdate instead of the complaint itself -- see
        complaint_update_translation_cache.py's own docstring for why this needs a DIFFERENT
        cache/lookup (no "always English" guarantee, source language is approximated per-update
        from the authoring worker's own preference)."""
        if update is None:
            return None
        if not display_language or display_language == "en" or translation_service is None:
            return update.text
        try:
            return get_display_update_text(db, update, display_language, translation_service)
        except AIServiceError as exc:
            logger.error("On-read translation failed for complaint update %s: %s", update.id, exc)
            return update.text

    location_state = location_district = location_ulb = None
    if complaint.state_id is not None:
        row = db.query(State).filter(State.id == complaint.state_id).first()
        location_state = row.name if row else None
    if complaint.district_id is not None:
        row = db.query(District).filter(District.id == complaint.district_id).first()
        location_district = row.name if row else None
    if complaint.ulb_id is not None:
        row = db.query(ULB).filter(ULB.id == complaint.ulb_id).first()
        location_ulb = row.name if row else None

    assigned_worker_name = None
    if complaint.assigned_worker_id is not None:
        worker = db.query(User).filter(User.id == complaint.assigned_worker_id).first()
        assigned_worker_name = worker.full_name if worker else None

    updates = complaint_workflow_repository.get_complaint_updates(db, complaint.id)
    initial = next((u for u in updates if u.update_type == "INITIAL_ASSESSMENT"), None)
    completion = next((u for u in updates if u.update_type == "COMPLETION"), None)
    progress = [u for u in updates if u.update_type == "PROGRESS_UPDATE"]

    history = complaint_workflow_repository.get_status_history(db, complaint.id)
    resolved_entry = next((h for h in reversed(history) if h.to_status == "resolved"), None)

    # Evidence upload phase: every ComplaintEvidence row for this complaint, grouped by stage
    # (and, for progress updates specifically, by which update it belongs to -- there can be
    # more than one). One query, grouped in Python, rather than one query per stage/update.
    all_evidence = evidence_repository.get_evidence_for_complaint(db, complaint.id)
    citizen_evidence = [e.file_path for e in all_evidence if e.stage == "CITIZEN_COMPLAINT"]
    initial_evidence = [e.file_path for e in all_evidence if e.stage == "INITIAL_ASSESSMENT"]
    completion_evidence = [e.file_path for e in all_evidence if e.stage == "COMPLETION"]
    evidence_by_update_id: dict[int, list[str]] = {}
    for e in all_evidence:
        if e.stage == "PROGRESS_UPDATE" and e.update_id is not None:
            evidence_by_update_id.setdefault(e.update_id, []).append(e.file_path)

    return ComplaintReportData(
        complaint_id=complaint.id,
        display_id=f"JM-{complaint.id:05d}",
        service_summary=service_summary,
        original_description=original_description,
        created_at=complaint.created_at,
        location_ward=complaint.ward,
        location_state=location_state,
        location_district=location_district,
        location_ulb=location_ulb,
        location_address=complaint.address,
        assigned_worker_name=assigned_worker_name,
        initial_assessment=_display_update_text(initial),
        initial_assessment_at=initial.created_at if initial else None,
        progress_updates=[
            {
                "text": _display_update_text(u), "photo_path": u.photo_path, "created_at": u.created_at,
                "evidence": evidence_by_update_id.get(u.id, []),
            }
            for u in progress
        ],
        completion_status=_display_update_text(completion),
        completion_evidence_photo=completion.photo_path if completion else None,
        resolved_at=resolved_entry.created_at if resolved_entry else None,
        timeline=[
            {"from_status": h.from_status, "to_status": h.to_status, "note": h.note, "created_at": h.created_at}
            for h in history
        ],
        citizen_evidence=citizen_evidence,
        initial_assessment_evidence=initial_evidence,
        completion_evidence=completion_evidence,
    )


def _fmt(dt: datetime | None) -> str:
    return dt.strftime("%d %b %Y, %I:%M %p") if dt else "—"


def _spaced(text: str) -> str:
    """Letter-track short uppercase labels (e.g. "COMPLAINT" -> "C O M P L A I N T") -- the
    tracked-caps look used throughout the reference report this template is styled after, for
    titles and section/panel headers only. Never applied to body text or values -- unreadable
    past a few words.

    Word gaps use a doubled non-breaking space rather than plain spaces: ReportLab's Paragraph
    parses text XML/HTML-style and collapses runs of plain whitespace to one space, which would
    otherwise erase the very word gap this is meant to add (multi-word labels rendered as one
    fused word). Plain single spaces between letters are unaffected since collapsing only touches
    multi-space runs.
    """
    return "  ".join(" ".join(word) for word in text.split(" "))


# ===== Brand palette -- mirrors frontend-react/src/styles/global.css's :root tokens exactly, so
# the PDF reads as the same product as the web app rather than an independently-designed sibling. =====
_NAVY = colors.HexColor("#0F2D6B")  # --accent / --brand-surface
_ORANGE = colors.HexColor("#F97316")  # --service-roads, used here as the report's accent stripe
_INK = colors.HexColor("#0F172A")  # --ink
_INK_2 = colors.HexColor("#475569")  # --ink-2
_INK_3 = colors.HexColor("#64748B")  # --ink-3
_LINE = colors.HexColor("#E2E8F0")  # --line
_RESOLVED_FG = colors.HexColor("#166534")  # darker than --status-resolved, for text on its own bg
_RESOLVED_BG = colors.HexColor("#DCFCE7")  # --status-resolved-bg

# Mirrors StatusBadge.tsx's NORMALIZED status->color mapping exactly, so a status reads the same
# color in the PDF as it does everywhere else in the app.
_STATUS_STYLES: dict[str, tuple[colors.Color, colors.Color]] = {
    "pending": (colors.HexColor("#B45309"), colors.HexColor("#FEF3C7")),
    "assigned": (colors.HexColor("#EA580C"), colors.HexColor("#FFEDD5")),
    "accepted": (colors.HexColor("#0284C7"), colors.HexColor("#E0F2FE")),
    "in_progress": (colors.HexColor("#0284C7"), colors.HexColor("#E0F2FE")),
    "resolved": (colors.HexColor("#16A34A"), colors.HexColor("#DCFCE7")),
    "rejected": (colors.HexColor("#DC2626"), colors.HexColor("#FEE2E2")),
    "escalated": (colors.HexColor("#DC2626"), colors.HexColor("#FEE2E2")),
    "cancelled": (_INK_3, colors.HexColor("#F1F5F9")),
}

_PAGE_W, _PAGE_H = A4
_MARGIN = 16 * mm
_CONTENT_W = _PAGE_W - 2 * _MARGIN
_HEADER_H = 27 * mm
_STRIPE_H = 2.2 * mm
_FOOTER_H = 14 * mm

_LOGO_PATH = Path(__file__).resolve().parents[2] / "frontend-react" / "public" / "brand" / "logo-mark.png"

_STYLES = getSampleStyleSheet()
_TITLE_STYLE = ParagraphStyle("JMTitle", fontName="Helvetica-Bold", fontSize=18, textColor=_NAVY, leading=21)
_META_STYLE = ParagraphStyle("JMMeta", fontName="Helvetica", fontSize=8.5, textColor=_INK_2, leading=12, alignment=2)
_PANEL_HEADER_STYLE = ParagraphStyle("JMPanelHeader", fontName="Helvetica-Bold", fontSize=8, textColor=colors.white)
_LABEL_STYLE = ParagraphStyle("JMLabel", fontName="Helvetica-Oblique", fontSize=8.5, textColor=_INK_3)
_VALUE_STYLE = ParagraphStyle("JMValue", fontName="Helvetica", fontSize=9, textColor=_INK, leading=12)
_SECTION_LABEL_STYLE = ParagraphStyle("JMSectionLabel", fontName="Helvetica-Bold", fontSize=9, textColor=_INK)
_BODY_STYLE = ParagraphStyle("JMBody", parent=_STYLES["BodyText"], fontName="Helvetica", fontSize=9.5, textColor=_INK, leading=13)
_MUTED_STYLE = ParagraphStyle("JMMuted", parent=_STYLES["BodyText"], fontName="Helvetica-Oblique", fontSize=8.5, textColor=_INK_3, leading=12)
_TIMESTAMP_STYLE = ParagraphStyle("JMTimestamp", fontName="Helvetica", fontSize=7.5, textColor=_INK_3, leading=10)
_BANNER_TITLE_STYLE = ParagraphStyle("JMBannerTitle", fontName="Helvetica-Bold", fontSize=11, textColor=_RESOLVED_FG)
_BANNER_SUB_STYLE = ParagraphStyle("JMBannerSub", fontName="Helvetica", fontSize=8, textColor=_RESOLVED_FG, leading=11)
_CHIP_STYLE = ParagraphStyle("JMChip", fontName="Helvetica-Bold", fontSize=7.5, leading=9)
_TH_STYLE = ParagraphStyle("JMTh", fontName="Helvetica-Bold", fontSize=7.5, textColor=colors.white)
_TD_STYLE = ParagraphStyle("JMTd", fontName="Helvetica", fontSize=8, textColor=_INK_2, leading=11)
_TD_DETAIL_STYLE = ParagraphStyle("JMTdDetail", fontName="Helvetica", fontSize=8.5, textColor=_INK, leading=11)


def _status_chip(status: str) -> Table:
    fg, bg = _STATUS_STYLES.get(status, (_INK_3, colors.HexColor("#F1F5F9")))
    style = ParagraphStyle("JMChipColored", parent=_CHIP_STYLE, textColor=fg)
    chip = Table([[Paragraph(status.replace("_", " ").upper(), style)]])
    chip.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), bg),
        ("LEFTPADDING", (0, 0), (-1, -1), 6), ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    return chip


def _section_header(label: str) -> Table:
    """A short accent-barred label (orange bar + tracked-caps text) marking off each report
    section -- the reference's own "TEST RESULTS — ..." heading style."""
    bar_w = 2.6 * mm
    t = Table([["", Paragraph(_spaced(label.upper()), _SECTION_LABEL_STYLE)]], colWidths=[bar_w, _CONTENT_W - bar_w])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, 0), _ORANGE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (0, 0), 0), ("RIGHTPADDING", (0, 0), (0, 0), 0),
        ("TOPPADDING", (0, 0), (0, 0), 0), ("BOTTOMPADDING", (0, 0), (0, 0), 0),
        ("LEFTPADDING", (1, 0), (1, 0), 6),
        ("TOPPADDING", (1, 0), (1, 0), 3), ("BOTTOMPADDING", (1, 0), (1, 0), 3),
    ]))
    return t


def _info_panel(title: str, rows: list[tuple[str, str]], width: float) -> Table:
    """A titled, bordered fact panel -- navy header bar + label/value rows -- matching the
    reference's "CLIENT & SITE" / "SAMPLE & PANEL" panels."""
    header = Table([[Paragraph(_spaced(title.upper()), _PANEL_HEADER_STYLE)]], colWidths=[width])
    header.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), _NAVY),
        ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
    ]))
    label_w = 30 * mm
    body_data = [[Paragraph(label, _LABEL_STYLE), Paragraph(value, _VALUE_STYLE)] for label, value in rows]
    body = Table(body_data, colWidths=[label_w, width - label_w])
    body.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 8), ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("LINEBELOW", (0, 0), (-1, -2), 0.4, _LINE),
    ]))
    wrapper = Table([[header], [body]], colWidths=[width])
    wrapper.setStyle(TableStyle([
        ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ("BOX", (0, 0), (-1, -1), 0.6, _LINE),
    ]))
    return wrapper


_EVIDENCE_THUMB_MAX = 78 * mm  # longest side of a thumbnail box
_EVIDENCE_THUMBS_PER_ROW = 2


def _evidence_thumbnails(file_paths: list[str]) -> Table | None:
    """Lays out evidence photos as rows of aspect-ratio-correct thumbnails, reading the real
    files from settings.UPLOAD_FOLDER (the same local-filesystem storage every other photo in
    this app already uses -- no new storage mechanism). Returns None if there's nothing to show,
    so callers can skip the surrounding section entirely rather than render an empty box.

    A file that's missing or unreadable is silently skipped (not an error) -- evidence is
    supplementary to the report's text content, and a single bad/corrupted file must never
    prevent a citizen or worker from getting their report at all.
    """
    if not file_paths:
        return None

    upload_dir = Path(settings.UPLOAD_FOLDER)
    thumbs = []
    for file_path in file_paths:
        full_path = upload_dir / file_path
        if not full_path.is_file():
            continue
        # Force a full decode now, eagerly, with PIL directly -- reportlab's Image flowable is
        # lazy: constructing it (and even reading .imageWidth/.imageHeight below) only touches
        # the header, not the actual pixel data, so a corrupt file's real decode error doesn't
        # surface until doc.build() draws it much later, by which point it's too late to skip
        # gracefully and the whole report generation crashes. Catching it here, before the file
        # is ever added to `thumbs`, is what actually makes "skip a bad file, don't break the
        # report" (this function's own contract, see docstring) true rather than aspirational.
        try:
            with PILImage.open(full_path) as probe:
                probe.load()
        except Exception:
            logger.warning("Evidence file %s could not be decoded as an image -- skipping it in the report.", file_path)
            continue
        try:
            img = RLImage(str(full_path))
            # Scale to fit within a square box, preserving aspect ratio -- RLImage(width=,
            # height=) alone would stretch a non-square photo instead of fitting it.
            ratio = min(_EVIDENCE_THUMB_MAX / img.imageWidth, _EVIDENCE_THUMB_MAX / img.imageHeight, 1.0)
            img.drawWidth = img.imageWidth * ratio
            img.drawHeight = img.imageHeight * ratio
        except Exception:
            continue
        thumbs.append(img)

    if not thumbs:
        return None

    rows = [thumbs[i : i + _EVIDENCE_THUMBS_PER_ROW] for i in range(0, len(thumbs), _EVIDENCE_THUMBS_PER_ROW)]
    if len(rows[-1]) < _EVIDENCE_THUMBS_PER_ROW:
        rows[-1] = rows[-1] + [""] * (_EVIDENCE_THUMBS_PER_ROW - len(rows[-1]))
    col_w = _CONTENT_W / _EVIDENCE_THUMBS_PER_ROW
    table = Table(rows, colWidths=[col_w] * _EVIDENCE_THUMBS_PER_ROW)
    table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 2), ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return table


def _draw_watermark(c: pdfcanvas.Canvas) -> None:
    """A faint, centered, medium-size logo mark behind the body content on every page -- a
    watermark sized to sit clear of the header band and footer line (see the size/centering math
    below), not a full-bleed background image."""
    if not _LOGO_PATH.exists():
        return
    size = 120 * mm
    c.saveState()
    c.setFillAlpha(0.06)
    c.drawImage(
        str(_LOGO_PATH), (_PAGE_W - size) / 2, (_PAGE_H - size) / 2,
        width=size, height=size, mask="auto", preserveAspectRatio=True,
    )
    c.restoreState()


def _draw_header(c: pdfcanvas.Canvas, _doc) -> None:
    """Drawn on every page (BaseDocTemplate's onPage callback) -- the watermark, navy brand band,
    orange accent stripe, and logo+wordmark lockup the reference report repeats on each page."""
    _draw_watermark(c)

    # Light green header background -- --service-waste-bg / --status-resolved-bg, this app's own
    # existing light-green token (already used for the resolved banner further down this same
    # report), reused here rather than inventing a new color. Still a light surface, so the
    # logo mark (unmodified original colors) keeps full contrast, same reasoning as before.
    c.saveState()
    c.setFillColor(colors.HexColor("#DCFCE7"))
    c.rect(0, _PAGE_H - _HEADER_H, _PAGE_W, _HEADER_H, stroke=0, fill=1)
    c.setFillColor(_ORANGE)
    c.rect(0, _PAGE_H - _HEADER_H - _STRIPE_H, _PAGE_W, _STRIPE_H, stroke=0, fill=1)

    center_y = _PAGE_H - _HEADER_H / 2

    # Mark pinned to the left edge, wordmark block pinned to the right edge -- two distinct
    # groups spanning the header's width, not a single tight lockup.
    mark_size = 20 * mm
    mark_x = _MARGIN
    if _LOGO_PATH.exists():
        c.drawImage(
            str(_LOGO_PATH), mark_x, center_y - mark_size / 2,
            width=mark_size, height=mark_size, mask="auto", preserveAspectRatio=True,
        )

    # Wordmark in the source logo's own "Jan"/"Mitra"/"AI" colors, unmodified -- navy/green/blue
    # all read correctly on this light surface, the same three brand colors (--accent, --primary,
    # --accent-fg) used everywhere else in the app on light surfaces.
    c.setFont("Helvetica-Bold", 19)
    segments = [("Jan", _NAVY), ("Mitra", colors.HexColor("#16A34A")), (" AI", colors.HexColor("#0284C7"))]
    total_w = sum(c.stringWidth(text, "Helvetica-Bold", 19) for text, _ in segments)
    text_x = _PAGE_W - _MARGIN - total_w  # right-align the wordmark's right edge to the margin
    cx = text_x
    for segment_text, color in segments:
        c.setFillColor(color)
        c.drawString(cx, center_y + 1.5 * mm, segment_text)
        cx += c.stringWidth(segment_text, "Helvetica-Bold", 19)

    c.setFillColor(_INK_3)
    c.setFont("Helvetica", 7.5)
    c.drawRightString(_PAGE_W - _MARGIN, center_y - 6 * mm, _spaced("MUNICIPAL GRIEVANCE REDRESSAL"))
    c.restoreState()


class _NumberedCanvas(pdfcanvas.Canvas):
    """Standard ReportLab two-pass pattern for a "Page X of Y" footer: total page count isn't
    known until the whole document has been laid out, so each page's drawing state is captured
    on `showPage()` and the footer is only actually drawn once, in `save()`, after every page has
    been seen."""

    def __init__(self, *args, report_id: str = "", **kwargs):
        pdfcanvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states: list[dict] = []
        self._report_id = report_id

    def showPage(self) -> None:
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self) -> None:
        total = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self._draw_footer(total)
            pdfcanvas.Canvas.showPage(self)
        pdfcanvas.Canvas.save(self)

    def _draw_footer(self, total: int) -> None:
        self.saveState()
        self.setStrokeColor(_LINE)
        self.setLineWidth(0.6)
        self.line(_MARGIN, _FOOTER_H - 3 * mm, _PAGE_W - _MARGIN, _FOOTER_H - 3 * mm)
        self.setFont("Helvetica", 6.8)
        self.setFillColor(_INK_3)
        self.drawString(
            _MARGIN, _FOOTER_H - 7 * mm,
            f"JANSARTHI AI — MUNICIPAL GRIEVANCE REDRESSAL   |   Reflects only actions recorded on Complaint {self._report_id}.",
        )
        self.setFont("Helvetica", 7.5)
        self.setFillColor(_INK_2)
        self.drawRightString(_PAGE_W - _MARGIN, _FOOTER_H - 7 * mm, f"Page {self._pageNumber} of {total}")
        self.restoreState()


def generate_pdf_bytes(data: ComplaintReportData) -> bytes:
    """Renders `data` into a PDF, returned as raw bytes (never written to disk -- the download
    route streams it directly). Pure formatting of already-assembled facts; no new data is
    computed here.

    One shared template for every viewer (admin, worker, citizen) -- the report describes the
    complaint, not the reader, and all three already see the same underlying `ComplaintReportData`
    (see routes/complaints.py's `_get_visible_complaint`), so a role-specific layout would just be
    the same facts re-skinned for no reason.

    Layout is styled after a reference lab-report PDF the user supplied (navy brand header with
    accent stripe, boxed two-column fact panels, a colored pass/fail-style status banner, and a
    running "Page X of Y" footer) -- reimplemented here with JanSarthi AI's own logo and palette
    (see the `frontend-react/src/styles/global.css` brand tokens mirrored in the color constants
    above), not the reference's.
    """
    buffer = io.BytesIO()
    doc = BaseDocTemplate(
        buffer, pagesize=A4,
        leftMargin=_MARGIN, rightMargin=_MARGIN, topMargin=_MARGIN, bottomMargin=_MARGIN,
    )
    frame = Frame(
        _MARGIN, _FOOTER_H,
        _CONTENT_W, _PAGE_H - _HEADER_H - _STRIPE_H - 4 * mm - _FOOTER_H,
        leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0,
    )
    doc.addPageTemplates([PageTemplate(id="report", frames=[frame], onPage=_draw_header)])

    story: list = []

    story.append(Table(
        [[Paragraph("Complaint Resolution Report", _TITLE_STYLE),
          Paragraph(f"<b>{data.display_id}</b><br/>Created {_fmt(data.created_at)}", _META_STYLE)]],
        colWidths=[_CONTENT_W - 55 * mm, 55 * mm],
        style=TableStyle([("VALIGN", (0, 0), (-1, -1), "BOTTOM")]),
    ))
    story.append(Spacer(1, 5 * mm))

    panel_gap = 4 * mm
    panel_w = (_CONTENT_W - panel_gap) / 2
    left_rows = [
        ("Complaint ID", data.display_id),
        ("Filed on", _fmt(data.created_at)),
        ("Resolved on", _fmt(data.resolved_at)),
        ("Assigned worker", data.assigned_worker_name or "—"),
    ]
    right_rows = [
        ("Ward", data.location_ward or "—"),
        ("ULB", data.location_ulb or "—"),
        ("District", data.location_district or "—"),
        ("State", data.location_state or "—"),
    ]
    if data.location_address:
        right_rows.append(("Address", data.location_address))
    story.append(Table(
        [[_info_panel("Complaint", left_rows, panel_w), "", _info_panel("Location", right_rows, panel_w)]],
        colWidths=[panel_w, panel_gap, panel_w],
        style=TableStyle([
            ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]),
    ))
    story.append(Spacer(1, 5 * mm))

    banner_chip_w = 30 * mm
    banner_text = Paragraph(
        "✓ COMPLAINT RESOLVED<br/>"
        f"<font name='Helvetica' size=8>Resolved on {_fmt(data.resolved_at)} — confirmed via recorded worker completion update.</font>",
        _BANNER_TITLE_STYLE,
    )
    resolved_chip_style = ParagraphStyle("JMResolvedChip", fontName="Helvetica-Bold", fontSize=9, textColor=_RESOLVED_FG, alignment=1)
    story.append(Table(
        [[banner_text, Paragraph("RESOLVED", resolved_chip_style)]],
        colWidths=[_CONTENT_W - banner_chip_w, banner_chip_w],
        style=TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), _RESOLVED_BG),
            ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#16A34A")),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN", (1, 0), (1, 0), "CENTER"),
            ("LEFTPADDING", (0, 0), (0, 0), 10), ("RIGHTPADDING", (1, 0), (1, 0), 10),
            ("TOPPADDING", (0, 0), (-1, -1), 8), ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ]),
    ))
    story.append(Spacer(1, 6 * mm))

    story.append(_section_header("Complaint Description"))
    story.append(Spacer(1, 3 * mm))
    story.append(Paragraph(data.service_summary or "—", _BODY_STYLE))
    if data.original_description and data.original_description != data.service_summary:
        story.append(Paragraph(f"<i>{data.original_description}</i>", _MUTED_STYLE))
    citizen_thumbs = _evidence_thumbnails(data.citizen_evidence)
    if citizen_thumbs is not None:
        story.append(Spacer(1, 3 * mm))
        story.append(citizen_thumbs)
    story.append(Spacer(1, 5 * mm))

    if data.initial_assessment:
        story.append(_section_header("Initial Assessment"))
        story.append(Spacer(1, 3 * mm))
        story.append(Paragraph(_fmt(data.initial_assessment_at), _TIMESTAMP_STYLE))
        story.append(Paragraph(data.initial_assessment, _BODY_STYLE))
        initial_thumbs = _evidence_thumbnails(data.initial_assessment_evidence)
        if initial_thumbs is not None:
            story.append(Spacer(1, 3 * mm))
            story.append(initial_thumbs)
        story.append(Spacer(1, 5 * mm))

    if data.progress_updates:
        story.append(_section_header("Progress Updates"))
        story.append(Spacer(1, 3 * mm))
        for u in data.progress_updates:
            story.append(Paragraph(_fmt(u["created_at"]), _TIMESTAMP_STYLE))
            story.append(Paragraph(u["text"], _BODY_STYLE))
            update_thumbs = _evidence_thumbnails(u.get("evidence", []))
            if update_thumbs is not None:
                story.append(Spacer(1, 2 * mm))
                story.append(update_thumbs)
            story.append(Spacer(1, 3 * mm))
        story.append(Spacer(1, 2 * mm))

    story.append(_section_header("Completion Notes"))
    story.append(Spacer(1, 3 * mm))
    story.append(Paragraph(data.completion_status or "Not recorded", _BODY_STYLE))
    completion_thumbs = _evidence_thumbnails(data.completion_evidence)
    if completion_thumbs is not None:
        story.append(Spacer(1, 3 * mm))
        story.append(completion_thumbs)
    story.append(Spacer(1, 6 * mm))

    story.append(_section_header("Status Timeline"))
    story.append(Spacer(1, 3 * mm))
    if data.timeline:
        col_time, col_status = 30 * mm, 28 * mm
        rows = [[Paragraph("TIME", _TH_STYLE), Paragraph("STATUS", _TH_STYLE), Paragraph("DETAILS", _TH_STYLE)]]
        for event in data.timeline:
            if event["note"]:
                detail = event["note"]
            else:
                from_label = (event["from_status"] or "filed").replace("_", " ").title()
                to_label = event["to_status"].replace("_", " ").title()
                detail = f"{from_label} → {to_label}"
            rows.append([
                Paragraph(_fmt(event["created_at"]), _TD_STYLE),
                _status_chip(event["to_status"]),
                Paragraph(detail, _TD_DETAIL_STYLE),
            ])
        timeline_table = Table(rows, colWidths=[col_time, col_status, _CONTENT_W - col_time - col_status], repeatRows=1)
        timeline_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), _NAVY),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("LINEBELOW", (0, 1), (-1, -1), 0.4, _LINE),
        ]))
        story.append(timeline_table)
    else:
        story.append(Paragraph("No status changes recorded.", _MUTED_STYLE))

    doc.build(story, canvasmaker=partial(_NumberedCanvas, report_id=data.display_id))
    return buffer.getvalue()

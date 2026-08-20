"""Transactional email via plain SMTP -- OTP-based email verification/forgot-password
(send_otp_email, routes/auth.py) and citizen-facing complaint-lifecycle updates
(send_complaint_status_email, routes/complaints.py).

Uses Python's stdlib `smtplib`/`email` -- no third-party email-provider account needed. Point
this at any SMTP-capable mailbox (Gmail, Outlook, a custom domain's mail server, etc.) by setting
SMTP_HOST/SMTP_PORT/SMTP_USERNAME/SMTP_PASSWORD/EMAIL_FROM_ADDRESS. For Gmail specifically:
SMTP_USERNAME is the full Gmail address, and SMTP_PASSWORD must be a 16-character Google "App
Password" (Google Account -> Security -> 2-Step Verification -> App passwords), NOT the normal
account password -- Gmail rejects plain-password SMTP login by default.

Same "off unless configured" posture as SarvamClient: if SMTP credentials aren't set, every call
raises EmailServiceError immediately rather than silently no-op-ing or fabricating a "sent"
response. What callers DO with that error differs by purpose, though: routes/auth.py's OTP call
sites turn it into a clear 503 (sending the code back IS the point of those requests), while
routes/complaints.py's lifecycle-email call sites catch it and just log -- the email there is a
best-effort side effect of an action (accept/start/resolve/create) that must succeed on its own
regardless of whether the email goes out.
"""

import logging
import smtplib
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import Literal

from backend.config import settings

logger = logging.getLogger(__name__)

_SMTP_TIMEOUT_SECONDS = 10

# A small (96x96) resized copy of frontend-react/public/brand/logo-mark.png -- kept as its own
# copy rather than reading the frontend's public/ dir directly, so this backend module doesn't
# implicitly depend on the frontend's directory layout. Sent as a CID-referenced inline
# attachment (see _build_message below), not a data: URI -- Gmail and other major clients
# unreliably render base64 data: URIs in received HTML mail, but universally support CID inline
# images, which is the standard way transactional email embeds a logo.
_LOGO_PATH = Path(__file__).resolve().parent.parent / "assets" / "email_logo_mark.png"
_LOGO_CID = "jansarthi-logo-mark"

_SUBJECTS: dict[str, str] = {
    "verify_email": "Your JanSarthi AI email verification code",
    "reset_password": "Your JanSarthi AI password reset code",
}
_HEADINGS: dict[str, str] = {
    "verify_email": "Verify your email address",
    "reset_password": "Reset your password",
}
_BODY_INTROS: dict[str, str] = {
    "verify_email": "Enter this code in JanSarthi AI to verify your email address.",
    "reset_password": "Enter this code in JanSarthi AI to reset your password.",
}
_FOOTER_NOTES: dict[str, str] = {
    "verify_email": "If you didn't request to add this email to a JanSarthi AI account, you can safely ignore this message.",
    "reset_password": "If you didn't request a password reset, you can safely ignore this message — your password won't change unless the code above is used.",
}

# Wordmark colors, matching frontend-react/src/components/AuthFormBrand.tsx's real "Jan"/
# "Sarthi"/"AI" coloring exactly (navy/green/blue, its own light-theme --accent-fg/--primary/
# --service-water) -- kept in sync by eye, not programmatically, since an email client can't read
# the app's CSS custom properties. The email always uses the light-theme values: unlike the app,
# there's no dark-mode concept for an inbox.
_BRAND_JAN = "#0F2D6B"
_BRAND_SARTHI = "#16A34A"
_BRAND_AI = "#0284C7"


def _render_html(heading: str, intro: str, code: str, footer_note: str) -> str:
    """Builds the OTP email body as an inline-styled HTML table -- table-based layout and inline
    styles (not classes/external CSS) because that's what actually renders consistently across
    real email clients (Gmail, Outlook, Apple Mail), unlike a plain web page. The header mirrors
    AuthFormBrand.tsx's logo-mark + colored "JanSarthi AI" wordmark exactly."""
    return f"""\
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#F1F5F9;padding:32px 16px;font-family:-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;">
  <tr>
    <td align="center">
      <table role="presentation" width="480" cellpadding="0" cellspacing="0" style="max-width:480px;width:100%;background-color:#FFFFFF;border-radius:12px;overflow:hidden;border:1px solid #E2E8F0;">
        <tr>
          <td align="center" style="padding:24px 32px;border-bottom:1px solid #E2E8F0;">
            <table role="presentation" cellpadding="0" cellspacing="0" align="center">
              <tr>
                <td style="padding-right:18px;white-space:nowrap;"><img src="cid:{_LOGO_CID}" width="100" height="100" alt="" style="display:block;" /></td>
                <td style="font-size:22px;font-weight:700;letter-spacing:-0.01em;white-space:nowrap;">
                  <span style="color:{_BRAND_JAN};">Jan</span><span style="color:{_BRAND_SARTHI};">Sarthi</span> <span style="color:{_BRAND_AI};">AI</span>
                </td>
              </tr>
            </table>
          </td>
        </tr>
        <tr>
          <td style="padding:32px;">
            <h1 style="margin:0 0 12px;color:#0F172A;font-size:20px;font-weight:700;">{heading}</h1>
            <p style="margin:0 0 24px;color:#334155;font-size:14px;line-height:1.6;">{intro}</p>
            <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#F1F5F9;border-radius:8px;margin-bottom:24px;">
              <tr>
                <td align="center" style="padding:20px;">
                  <span style="font-family:'Courier New',monospace;font-size:32px;font-weight:700;letter-spacing:8px;color:{_BRAND_SARTHI};">{code}</span>
                </td>
              </tr>
            </table>
            <p style="margin:0 0 24px;color:#64748B;font-size:13px;line-height:1.6;">
              This code expires in {settings.OTP_EXPIRE_MINUTES} minutes and can only be used once.
            </p>
            <hr style="border:none;border-top:1px solid #E2E8F0;margin:0 0 20px;" />
            <p style="margin:0;color:#94A3B8;font-size:12px;line-height:1.6;">{footer_note}</p>
          </td>
        </tr>
      </table>
      <p style="color:#94A3B8;font-size:11px;margin-top:16px;">Municipal grievance redressal, in every language.</p>
    </td>
  </tr>
</table>"""


_STATUS_SUBJECTS: dict[str, str] = {
    "created": "We received your complaint",
    "accepted": "A worker has accepted your complaint",
    "started": "Work has started on your complaint",
    "resolved": "Your complaint has been resolved",
}
_STATUS_HEADINGS: dict[str, str] = {
    "created": "We received your complaint",
    "accepted": "A worker has accepted your complaint",
    "started": "Work has started on your complaint",
    "resolved": "Your complaint has been resolved",
}
_STATUS_LABELS: dict[str, str] = {
    "created": "Submitted",
    "accepted": "Accepted",
    "started": "In progress",
    "resolved": "Resolved",
}
_STATUS_COLORS: dict[str, str] = {
    "created": "#0284C7",
    "accepted": _BRAND_SARTHI,
    "started": "#D97706",
    "resolved": _BRAND_SARTHI,
}


def _render_status_html(
    heading: str, status_label: str, status_color: str, complaint_display_id: str, summary: str, cta_url: str | None
) -> str:
    """Same header/footer chrome as _render_html (logo, wordmark, card shell) but swaps the OTP
    code block for a colored status badge + complaint reference -- see this module's own
    docstring on why this is a separate function rather than reshaping _render_html itself."""
    cta_html = ""
    if cta_url:
        cta_html = f"""
            <table role="presentation" cellpadding="0" cellspacing="0" style="margin:0 0 24px;">
              <tr>
                <td align="center" style="border-radius:8px;background-color:{_BRAND_JAN};">
                  <a href="{cta_url}" style="display:inline-block;padding:12px 24px;color:#FFFFFF;font-size:14px;font-weight:600;text-decoration:none;">View complaint</a>
                </td>
              </tr>
            </table>"""
    return f"""\
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#F1F5F9;padding:32px 16px;font-family:-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;">
  <tr>
    <td align="center">
      <table role="presentation" width="480" cellpadding="0" cellspacing="0" style="max-width:480px;width:100%;background-color:#FFFFFF;border-radius:12px;overflow:hidden;border:1px solid #E2E8F0;">
        <tr>
          <td align="center" style="padding:24px 32px;border-bottom:1px solid #E2E8F0;">
            <table role="presentation" cellpadding="0" cellspacing="0" align="center">
              <tr>
                <td style="padding-right:18px;white-space:nowrap;"><img src="cid:{_LOGO_CID}" width="100" height="100" alt="" style="display:block;" /></td>
                <td style="font-size:22px;font-weight:700;letter-spacing:-0.01em;white-space:nowrap;">
                  <span style="color:{_BRAND_JAN};">Jan</span><span style="color:{_BRAND_SARTHI};">Sarthi</span> <span style="color:{_BRAND_AI};">AI</span>
                </td>
              </tr>
            </table>
          </td>
        </tr>
        <tr>
          <td style="padding:32px;">
            <h1 style="margin:0 0 12px;color:#0F172A;font-size:20px;font-weight:700;">{heading}</h1>
            <table role="presentation" cellpadding="0" cellspacing="0" style="margin:0 0 16px;">
              <tr>
                <td style="border-radius:6px;background-color:{status_color}1A;padding:6px 12px;">
                  <span style="color:{status_color};font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:0.03em;">{status_label}</span>
                </td>
              </tr>
            </table>
            <p style="margin:0 0 24px;color:#334155;font-size:14px;line-height:1.6;">
              <strong>{complaint_display_id}</strong> — {summary}
            </p>{cta_html}
            <hr style="border:none;border-top:1px solid #E2E8F0;margin:0 0 20px;" />
            <p style="margin:0;color:#94A3B8;font-size:12px;line-height:1.6;">
              This is an automated update from JanSarthi AI's complaint tracking system.
            </p>
          </td>
        </tr>
      </table>
      <p style="color:#94A3B8;font-size:11px;margin-top:16px;">Municipal grievance redressal, in every language.</p>
    </td>
  </tr>
</table>"""


class EmailServiceError(Exception):
    """Raised when sending an email fails, including when SMTP isn't configured.

    Callers should catch this and return a clear error to the user instead of letting the
    failure crash the request or silently pretending the email was sent.
    """


def _require_smtp_configured() -> None:
    if not settings.SMTP_HOST or not settings.SMTP_USERNAME or not settings.SMTP_PASSWORD or not settings.EMAIL_FROM_ADDRESS:
        raise EmailServiceError(
            "Email sending is not configured (missing SMTP_HOST/SMTP_USERNAME/SMTP_PASSWORD/EMAIL_FROM_ADDRESS)."
        )


def _build_message(*, subject: str, to_email: str, html_body: str, text_body: str) -> MIMEMultipart:
    """Assembles the multipart message every email this service sends shares: a plain/HTML
    alternative pair plus the inline logo, wrapped in a "related" container. "related" (not
    "alternative") at the top level -- it wraps an "alternative" part (the plain-text/HTML
    choice) plus the inline logo image, which the HTML part references via cid:. "alternative"
    alone has nowhere to hang a same-message inline attachment."""
    message = MIMEMultipart("related")
    message["Subject"] = subject
    message["From"] = f"{settings.EMAIL_FROM_NAME} <{settings.EMAIL_FROM_ADDRESS}>"
    message["To"] = to_email

    alternative = MIMEMultipart("alternative")
    alternative.attach(MIMEText(text_body, "plain"))
    alternative.attach(MIMEText(html_body, "html"))
    message.attach(alternative)

    try:
        logo_bytes = _LOGO_PATH.read_bytes()
    except OSError:
        logo_bytes = None
    if logo_bytes is not None:
        logo_image = MIMEImage(logo_bytes)
        logo_image.add_header("Content-ID", f"<{_LOGO_CID}>")
        # No `filename=` here -- avoids Gmail treating this as a downloadable
        # "jansarthi-logo-mark.png" attachment rather than a purely inline image.
        logo_image.add_header("Content-Disposition", "inline")
        message.attach(logo_image)

    return message


def _deliver(message: MIMEMultipart, to_email: str, log_context: str) -> None:
    """The pure SMTP-send mechanics shared by every email this service sends -- login, deliver,
    raise EmailServiceError on any failure. Split out of send_otp_email so
    send_complaint_status_email can reuse the exact same delivery path without duplicating it;
    the higher-level message-building logic (which stays separate per email type) is unchanged."""
    try:
        # SMTP_SSL for port 465 (implicit TLS from the first byte); plain SMTP + STARTTLS for
        # every other port (587 -- Gmail's and most providers' standard submission port).
        if settings.SMTP_PORT == 465:
            with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT, timeout=_SMTP_TIMEOUT_SECONDS) as server:
                server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
                server.sendmail(settings.EMAIL_FROM_ADDRESS, [to_email], message.as_string())
        else:
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=_SMTP_TIMEOUT_SECONDS) as server:
                server.starttls()
                server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
                server.sendmail(settings.EMAIL_FROM_ADDRESS, [to_email], message.as_string())
    except (smtplib.SMTPException, OSError) as exc:
        logger.error("Failed to send %s email via SMTP: %s", log_context, exc)
        raise EmailServiceError(f"Failed to send email: {exc}") from exc


def send_otp_email(to_email: str, code: str, purpose: Literal["verify_email", "reset_password"]) -> None:
    """Send a one-time code to an email address over SMTP.

    Args:
        to_email: The recipient address.
        code: The plaintext 6-digit OTP to include in the email body.
        purpose: "verify_email" or "reset_password" -- selects the subject/body wording.

    Raises:
        EmailServiceError: If SMTP_HOST/SMTP_USERNAME/SMTP_PASSWORD/EMAIL_FROM_ADDRESS are not
            configured, or the SMTP send fails for any reason (auth error, connection error).
    """
    _require_smtp_configured()

    intro = _BODY_INTROS[purpose]
    footer_note = _FOOTER_NOTES[purpose]
    html_body = _render_html(_HEADINGS[purpose], intro, code, footer_note)
    text_body = (
        f"JanSarthi AI\n\n{_HEADINGS[purpose]}\n\n{intro}\n\nCode: {code}\n\n"
        f"This code expires in {settings.OTP_EXPIRE_MINUTES} minutes and can only be used once.\n\n{footer_note}"
    )
    message = _build_message(subject=_SUBJECTS[purpose], to_email=to_email, html_body=html_body, text_body=text_body)
    _deliver(message, to_email, log_context=purpose)


def send_complaint_status_email(
    to_email: str,
    event: Literal["created", "accepted", "started", "resolved"],
    complaint_display_id: str,
    summary: str,
    ward: str,
    cta_url: str | None = None,
) -> None:
    """Send a citizen a real email for one of their complaint's key lifecycle moments -- a
    receipt on filing, then one each for accepted/started/resolved. Deliberately never sent for
    workers/admins (their accounts don't have a verified email by default -- see
    routes/admin.py's create_worker and scripts/seed_admin.py, neither of which ever sets one),
    and never for a rejection (see routes/complaints.py's reject_complaint() -- citizens are
    never informed of rejections at all, by design).

    Unlike send_otp_email (where sending IS the point of the request), this is always a
    best-effort side effect of an action whose real job is the status change itself -- every
    caller in routes/complaints.py wraps this in try/except EmailServiceError and logs rather
    than failing the request, so a slow or failed SMTP send can never block a worker resolving a
    complaint, or a citizen filing one.

    Args:
        to_email: The citizen's verified email address.
        event: Which lifecycle moment this is -- selects subject/heading/status-badge wording.
        complaint_display_id: The citizen-facing reference, e.g. "JM-00053".
        summary: The complaint's own short summary, for context in the email body.
        ward: The ward the complaint was filed in.
        cta_url: A direct link to the complaint's detail page, or None to omit the "View
            complaint" button entirely -- see config.py's FRONTEND_BASE_URL, which is optional
            and blank by default (this degrades gracefully, the same posture this codebase
            already uses for Sentry/LangSmith: off unless configured, never a hard failure).

    Raises:
        EmailServiceError: If SMTP isn't configured or the send fails -- see this function's own
            docstring above on why every call site treats this as non-fatal.
    """
    _require_smtp_configured()

    heading = _STATUS_HEADINGS[event]
    status_label = _STATUS_LABELS[event]
    html_body = _render_status_html(heading, status_label, _STATUS_COLORS[event], complaint_display_id, summary, cta_url)
    text_lines = [
        "JanSarthi AI", "", heading, "", f"{complaint_display_id} ({status_label}) — {ward}", "", summary,
    ]
    if cta_url:
        text_lines += ["", f"View complaint: {cta_url}"]
    text_body = "\n".join(text_lines)

    message = _build_message(subject=_STATUS_SUBJECTS[event], to_email=to_email, html_body=html_body, text_body=text_body)
    _deliver(message, to_email, log_context=f"complaint_{event}")

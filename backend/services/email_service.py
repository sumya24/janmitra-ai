"""Transactional email via plain SMTP, for OTP-based email verification and forgot-password.

Uses Python's stdlib `smtplib`/`email` -- no third-party email-provider account needed. Point
this at any SMTP-capable mailbox (Gmail, Outlook, a custom domain's mail server, etc.) by setting
SMTP_HOST/SMTP_PORT/SMTP_USERNAME/SMTP_PASSWORD/EMAIL_FROM_ADDRESS. For Gmail specifically:
SMTP_USERNAME is the full Gmail address, and SMTP_PASSWORD must be a 16-character Google "App
Password" (Google Account -> Security -> 2-Step Verification -> App passwords), NOT the normal
account password -- Gmail rejects plain-password SMTP login by default.

Same "off unless configured" posture as SarvamClient: if SMTP credentials aren't set, every call
raises EmailServiceError immediately rather than silently no-op-ing or fabricating a "sent"
response -- callers (routes/auth.py) turn this into a clear 503.
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


class EmailServiceError(Exception):
    """Raised when sending an email fails, including when SMTP isn't configured.

    Callers should catch this and return a clear error to the user instead of letting the
    failure crash the request or silently pretending the email was sent.
    """


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
    if not settings.SMTP_HOST or not settings.SMTP_USERNAME or not settings.SMTP_PASSWORD or not settings.EMAIL_FROM_ADDRESS:
        raise EmailServiceError(
            "Email sending is not configured (missing SMTP_HOST/SMTP_USERNAME/SMTP_PASSWORD/EMAIL_FROM_ADDRESS)."
        )

    intro = _BODY_INTROS[purpose]
    footer_note = _FOOTER_NOTES[purpose]
    html_body = _render_html(_HEADINGS[purpose], intro, code, footer_note)
    text_body = (
        f"JanSarthi AI\n\n{_HEADINGS[purpose]}\n\n{intro}\n\nCode: {code}\n\n"
        f"This code expires in {settings.OTP_EXPIRE_MINUTES} minutes and can only be used once.\n\n{footer_note}"
    )

    # "related" (not "alternative") at the top level -- it wraps an "alternative" part (the
    # plain-text/HTML choice) plus the inline logo image, which the HTML part references via
    # cid:. "alternative" alone has nowhere to hang a same-message inline attachment.
    message = MIMEMultipart("related")
    message["Subject"] = _SUBJECTS[purpose]
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
        logger.error("Failed to send %s email via SMTP: %s", purpose, exc)
        raise EmailServiceError(f"Failed to send email: {exc}") from exc

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
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Literal

from backend.config import settings

logger = logging.getLogger(__name__)

_SMTP_TIMEOUT_SECONDS = 10

_SUBJECTS: dict[str, str] = {
    "verify_email": "Your JanSarthi AI email verification code",
    "reset_password": "Your JanSarthi AI password reset code",
}
_BODY_INTROS: dict[str, str] = {
    "verify_email": "Use this code to verify your email address:",
    "reset_password": "Use this code to reset your password:",
}


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
    html_body = (
        f"<p>{intro}</p>"
        f"<p style='font-size:28px;font-weight:bold;letter-spacing:4px'>{code}</p>"
        f"<p>This code expires in {settings.OTP_EXPIRE_MINUTES} minutes. "
        "If you didn't request this, you can safely ignore this email.</p>"
    )
    text_body = f"{intro} {code}\n\nThis code expires in {settings.OTP_EXPIRE_MINUTES} minutes."

    message = MIMEMultipart("alternative")
    message["Subject"] = _SUBJECTS[purpose]
    message["From"] = f"{settings.EMAIL_FROM_NAME} <{settings.EMAIL_FROM_ADDRESS}>"
    message["To"] = to_email
    message.attach(MIMEText(text_body, "plain"))
    message.attach(MIMEText(html_body, "html"))

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

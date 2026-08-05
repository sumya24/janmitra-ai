"""Orchestrates the end-to-end processing and storage of a citizen complaint."""

import logging

from sqlalchemy.orm import Session

from backend.config import to_bcp47
from backend.models import Complaint
from backend.services.normalization_service import NormalizationService
from backend.services.sarvam_client import AIServiceError, SarvamClient
from backend.services.summary_service import SummaryService
from backend.services.translation_service import TranslationService

logger = logging.getLogger(__name__)

# How much of the English text to keep as a fallback "summary" if AI summary generation
# fails or times out. A summary is a nice-to-have for skimming a long worklist; it should
# never be the reason a citizen's complaint fails to save.
_FALLBACK_SUMMARY_LENGTH = 200


class ComplaintAgent:
    """Receives a citizen complaint (voice or text) and stores it as a processed record.

    Responsibilities: transcribe audio if needed, translate to English, clean up
    obvious spelling mistakes, generate a summary, and persist the resulting
    complaint to the database.
    """

    def __init__(
        self,
        sarvam_client: SarvamClient | None = None,
        translation_service: TranslationService | None = None,
        summary_service: SummaryService | None = None,
        normalization_service: NormalizationService | None = None,
    ) -> None:
        """Initialize the agent, creating default service instances if none are given."""
        self._sarvam = sarvam_client or SarvamClient()
        self._translation = translation_service or TranslationService(self._sarvam)
        self._summary = summary_service or SummaryService()
        self._normalization = normalization_service or NormalizationService()

    def create_complaint(
        self,
        db: Session,
        citizen_id: str,
        language_code: str,
        text: str | None,
        audio_bytes: bytes | None,
        photo_path: str | None,
    ) -> Complaint:
        """Process citizen input and store a new complaint record.

        Exactly one of `text` or `audio_bytes` should be provided.

        Args:
            db: Active database session.
            citizen_id: Hardcoded citizen identifier.
            language_code: Short language code of the citizen's input, e.g. "mr".
            text: Typed complaint text, or None if voice was used.
            audio_bytes: Raw audio bytes of a spoken complaint, or None if text was used.
            photo_path: Relative path to an attached photo, or None.

        Returns:
            The newly created and persisted Complaint record.

        Raises:
            ValueError: If neither text nor audio is provided, or transcription is empty.
            AIServiceError: If transcription or translation fails. Summary generation is
                best-effort and never blocks storage; see `summary` handling below.
        """
        if audio_bytes is not None:
            logger.info("Complaint received (voice, citizen=%s, language=%s)", citizen_id, language_code)
            original_text = self._sarvam.transcribe(audio_bytes, to_bcp47(language_code))
        elif text is not None:
            logger.info("Complaint received (text, citizen=%s, language=%s)", citizen_id, language_code)
            original_text = text
        else:
            raise ValueError("Either text or audio_bytes must be provided.")

        original_text = original_text.strip()
        if not original_text:
            raise ValueError("Complaint text is empty.")

        # Clean up obvious spelling/typing mistakes in the citizen's own language before
        # translating, so a typo (in Marathi, Hindi, or English) doesn't produce a bad
        # English translation that then propagates into every future re-translation for
        # workers. `original_text` in storage stays exactly what the citizen wrote; only
        # this working copy, used as translation input, is normalized. Best-effort: falls
        # back to the untouched text on failure rather than blocking complaint submission.
        normalized_text = self._normalization.normalize(original_text, language_code)
        translated_text = self._translation.to_english(normalized_text, language_code)

        # Summary generation depends on a reasoning model whose internal "thinking" length
        # is unpredictable — no max_tokens/timeout budget can be proven sufficient for
        # every possible complaint. Treat it as best-effort: never let it block a citizen's
        # complaint from being saved. On failure, fall back to a truncated excerpt of the
        # translated text instead of a polished summary.
        try:
            summary = self._summary.summarize(translated_text)
        except AIServiceError as exc:
            logger.warning("Summary generation failed, storing complaint without an AI summary: %s", exc)
            summary = (
                translated_text
                if len(translated_text) <= _FALLBACK_SUMMARY_LENGTH
                else translated_text[:_FALLBACK_SUMMARY_LENGTH].rstrip() + "…"
            )

        complaint = Complaint(
            citizen_id=citizen_id,
            original_text=original_text,
            original_language=language_code,
            translated_text=translated_text,
            summary=summary,
            photo_path=photo_path,
            status="open",
        )
        db.add(complaint)
        db.commit()
        db.refresh(complaint)
        logger.info("Complaint stored (id=%s, citizen=%s)", complaint.id, citizen_id)
        return complaint

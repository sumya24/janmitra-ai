"""Orchestrates the end-to-end processing and storage of a citizen complaint."""

import logging

from sqlalchemy.orm import Session

from backend.config import to_bcp47
from backend.models import Complaint
from backend.services.sarvam_client import SarvamClient
from backend.services.summary_service import SummaryService
from backend.services.translation_service import TranslationService

logger = logging.getLogger(__name__)


class ComplaintAgent:
    """Receives a citizen complaint (voice or text) and stores it as a processed record.

    Responsibilities: transcribe audio if needed, translate to English, generate a
    summary, and persist the resulting complaint to the database.
    """

    def __init__(
        self,
        sarvam_client: SarvamClient | None = None,
        translation_service: TranslationService | None = None,
        summary_service: SummaryService | None = None,
    ) -> None:
        """Initialize the agent, creating default service instances if none are given."""
        self._sarvam = sarvam_client or SarvamClient()
        self._translation = translation_service or TranslationService(self._sarvam)
        self._summary = summary_service or SummaryService()

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
            AIServiceError: If transcription, translation, or summarization fails.
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

        translated_text = self._translation.to_english(original_text, language_code)
        summary = self._summary.summarize(translated_text)

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

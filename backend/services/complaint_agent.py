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

# Inserted into the transcript in place of a chunk that failed to transcribe even after a
# retry, so a citizen's complaint stays honest about a gap instead of silently reading as if
# nothing were missing (a dropped chunk could easily be the one with the actual location or
# key detail in it — see docs/ai_pipeline_limits.md for why chunks can fail at all).
_STT_GAP_MARKER = "[a few seconds of the recording could not be transcribed]"


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
        audio_chunks: list[bytes] | None,
        photo_path: str | None,
    ) -> Complaint:
        """Process citizen input and store a new complaint record.

        Exactly one of `text` or `audio_chunks` should be provided.

        Args:
            db: Active database session.
            citizen_id: Hardcoded citizen identifier.
            language_code: Short language code of the citizen's input, e.g. "mr".
            text: Typed complaint text, or None if voice was used.
            audio_chunks: Ordered raw-audio byte chunks of a spoken complaint, or None if
                text was used. A recording longer than Sarvam's 30-second-per-request STT
                cap arrives as multiple chunks — see
                frontend-react/src/lib/useAudioRecorder.ts, which splits recording into
                ~28s segments client-side for exactly this reason (see
                docs/ai_pipeline_limits.md for why 30s is a hard, actively-enforced limit).
            photo_path: Relative path to an attached photo, or None.

        Returns:
            The newly created and persisted Complaint record.

        Raises:
            ValueError: If neither text nor audio is provided, or transcription is empty.
            AIServiceError: If every audio chunk fails to transcribe, or translation or
                summarization fails.
        """
        if audio_chunks:
            logger.info(
                "Complaint received (voice, citizen=%s, language=%s, chunks=%d)",
                citizen_id, language_code, len(audio_chunks),
            )
            original_text = self._transcribe_chunks(audio_chunks, to_bcp47(language_code))
        elif text is not None:
            logger.info("Complaint received (text, citizen=%s, language=%s)", citizen_id, language_code)
            original_text = text
        else:
            raise ValueError("Either text or audio_chunks must be provided.")

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

    def _transcribe_chunks(self, audio_chunks: list[bytes], bcp47_language: str) -> str:
        """Transcribe each audio chunk in order and join the results into one transcript.

        Each chunk is sent as its own independent speech-to-text call. A chunk that fails
        is retried once — most STT failures are transient (a network blip, a momentary API
        hiccup), so a single retry recovers the majority of them before the citizen notices
        anything happened. If a chunk still fails after the retry, it's skipped and replaced
        with an explicit gap marker in the transcript, rather than either discarding the
        whole complaint or silently stitching the surviving chunks together as if nothing
        were missing.

        Args:
            audio_chunks: Ordered raw-audio byte chunks, each independently transcribable.
            bcp47_language: BCP-47 language code of the spoken audio, e.g. "mr-IN".

        Returns:
            The joined transcript, in chunk order, with `_STT_GAP_MARKER` in place of any
            chunk that could not be transcribed.

        Raises:
            AIServiceError: If every chunk fails to transcribe (nothing usable came back
                at all).
        """
        total = len(audio_chunks)
        pieces: list[str] = []
        succeeded = 0
        failed = 0

        for index, chunk in enumerate(audio_chunks, start=1):
            transcript: str | None = None
            for attempt in (1, 2):
                try:
                    logger.info("STT chunk %d/%d started (attempt %d/2)", index, total, attempt)
                    transcript = self._sarvam.transcribe(chunk, bcp47_language)
                    logger.info(
                        "STT chunk %d/%d succeeded (attempt %d/2, %d chars)",
                        index, total, attempt, len(transcript),
                    )
                    break
                except AIServiceError as exc:
                    if attempt == 1:
                        logger.warning(
                            "STT chunk %d/%d failed on attempt 1/2, retrying: %s", index, total, exc
                        )
                    else:
                        logger.error(
                            "STT chunk %d/%d failed on attempt 2/2, giving up on this chunk: %s",
                            index, total, exc,
                        )

            if transcript is not None:
                succeeded += 1
                # An empty-but-successful transcript (e.g. a near-silent trailing chunk) is
                # not a gap -- there was genuinely nothing to transcribe, so add nothing.
                if transcript.strip():
                    pieces.append(transcript.strip())
            else:
                failed += 1
                pieces.append(_STT_GAP_MARKER)

        logger.info(
            "STT chunking complete: %d/%d chunk(s) succeeded, %d gap(s) inserted", succeeded, total, failed
        )
        if succeeded == 0:
            raise AIServiceError("Speech-to-text service failed. Please try again.")

        return " ".join(pieces)

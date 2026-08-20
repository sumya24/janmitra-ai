"""Translation between citizen/worker languages and the canonical English storage format."""

import logging

from backend.config import to_bcp47
from backend.services.sarvam_client import SarvamClient

logger = logging.getLogger(__name__)


class TranslationService:
    """Translates complaint text to and from English using Sarvam AI."""

    def __init__(self, sarvam_client: SarvamClient | None = None) -> None:
        """Initialize the service with a SarvamClient instance (creates one if not given)."""
        self._sarvam = sarvam_client or SarvamClient()

    def to_english(self, text: str, source_language_code: str) -> str:
        """Translate complaint text into English, the canonical storage language.

        Args:
            text: Original complaint text.
            source_language_code: Short language code of the text, e.g. "mr".

        Returns:
            The text translated into English.
        """
        return self._sarvam.translate(
            text,
            source_language_code=to_bcp47(source_language_code),
            target_language_code=to_bcp47("en"),
        )

    def to_language(self, text: str, target_language_code: str) -> str:
        """Translate English complaint text into a worker's chosen display language.

        Args:
            text: English complaint text (as stored in the database).
            target_language_code: Short language code to translate into, e.g. "hi".

        Returns:
            The text translated into the target language.
        """
        return self._sarvam.translate(
            text,
            source_language_code=to_bcp47("en"),
            target_language_code=to_bcp47(target_language_code),
        )

    def translate(self, text: str, source_language_code: str, target_language_code: str) -> str:
        """Translate text between two arbitrary languages, neither of which has to be English --
        unlike `to_english`/`to_language`, which both assume one side is always English because
        `Complaint.translated_text` is always canonical English storage. Added for
        worker-authored free text (ComplaintUpdate.text -- initial assessment/progress/completion
        notes), which has no such "always English" guarantee (see
        complaint_update_translation_cache.py's own docstring for the full reasoning).

        Args:
            text: The text to translate, in source_language_code.
            source_language_code: Short language code the text is currently in, e.g. "mr".
            target_language_code: Short language code to translate into, e.g. "hi".

        Returns:
            The text translated into the target language.
        """
        return self._sarvam.translate(
            text,
            source_language_code=to_bcp47(source_language_code),
            target_language_code=to_bcp47(target_language_code),
        )

    def translate_auto_detecting_source(self, text: str, target_language_code: str) -> str:
        """Translate text into target_language_code without knowing its source language in
        advance -- Sarvam detects it for us. For worker-authored `ComplaintUpdate.text`, which
        (unlike `Complaint.translated_text`) is never forced into English at write time and has no
        stored source language at all, so there's nothing reliable to pass as a source (see
        complaint_update_translation_cache.py's docstring for the full reasoning, including why
        approximating it from the worker's own language preference turned out to be wrong).

        Args:
            text: Text to translate; its language is unknown/unstored.
            target_language_code: Short language code to translate into, e.g. "hi".

        Returns:
            The text translated into the target language.
        """
        return self._sarvam.translate(
            text,
            source_language_code="auto",
            target_language_code=to_bcp47(target_language_code),
        )

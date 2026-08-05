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

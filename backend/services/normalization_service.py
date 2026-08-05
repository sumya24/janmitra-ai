"""Spelling cleanup for complaint text, run once on the canonical English text.

Citizens can type or speak with typos (e.g. "ara" for "area"). Sarvam's translate
endpoint is literal and doesn't correct spelling, so an uncorrected typo in the
stored English text would get mistranslated afresh every time a worker views the
complaint in their own language. Cleaning the text up once, right after it's
translated to English, fixes it for every future read.
"""

import logging

from sarvamai import SarvamAI

from backend.config import get_prompt, settings

logger = logging.getLogger(__name__)


class NormalizationService:
    """Corrects obvious spelling/typing mistakes in English complaint text via Sarvam's chat API."""

    def __init__(self) -> None:
        """Initialize the underlying SarvamAI client, if an API key is configured."""
        self._client: SarvamAI | None = None
        if settings.LLM_API_KEY:
            self._client = SarvamAI(api_subscription_key=settings.LLM_API_KEY)
        else:
            logger.warning("LLM_API_KEY is not set; text normalization will be skipped.")

    def normalize(self, english_text: str) -> str:
        """Return a spelling-corrected version of English complaint text.

        This is a quality enhancement, not a critical step: any failure (missing API
        key, empty model response, network error) falls back to the original text
        unchanged rather than raising, so it never blocks complaint submission.

        Args:
            english_text: Complaint text already translated to English.

        Returns:
            The spelling-corrected text, or the original text if normalization
            could not be performed.
        """
        if self._client is None:
            return english_text

        try:
            prompt_template = get_prompt("normalize_prompt.txt")
            prompt = prompt_template.format(complaint_text=english_text)
            system_prompt = get_prompt("system_prompt.txt")

            logger.info("Text normalization started")
            response = self._client.chat.completions(
                model=settings.LLM_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=settings.LLM_MAX_TOKENS,
                reasoning_effort="low",
            )
            choice = response.choices[0]
            content = choice.message.content
            if not content or not content.strip():
                logger.warning(
                    "Text normalization returned no content (finish_reason=%s); using original text.",
                    choice.finish_reason,
                )
                return english_text
            logger.info("Text normalization completed")
            return content.strip()
        except Exception as exc:
            logger.warning("Text normalization failed, using original text unchanged: %s", exc, exc_info=True)
            return english_text

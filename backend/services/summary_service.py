"""Short summary generation for translated complaint text using Sarvam's chat completion API."""

import logging

from sarvamai import SarvamAI

from backend.config import get_prompt, settings
from backend.services.sarvam_client import AIServiceError

logger = logging.getLogger(__name__)


class SummaryService:
    """Generates a short 1-2 line summary of a complaint via Sarvam's chat completion API."""

    def __init__(self) -> None:
        """Initialize the underlying SarvamAI client, if an API key is configured."""
        self._client: SarvamAI | None = None
        if settings.LLM_API_KEY:
            self._client = SarvamAI(api_subscription_key=settings.LLM_API_KEY)
        else:
            logger.warning("LLM_API_KEY is not set; summary generation will fail until configured.")

    def summarize(self, english_text: str) -> str:
        """Generate a short summary of a complaint that has already been translated to English.

        Args:
            english_text: The complaint text in English.

        Returns:
            A 1-2 line summary of the complaint.

        Raises:
            AIServiceError: If the chat completion call fails for any reason.
        """
        if self._client is None:
            raise AIServiceError("Summary service is not configured (missing LLM_API_KEY).")

        logger.info("Summary generation started")
        try:
            prompt_template = get_prompt("summary_prompt.txt")
            prompt = prompt_template.format(complaint_text=english_text)
            system_prompt = get_prompt("system_prompt.txt")

            response = self._client.chat.completions(
                model=settings.LLM_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=150,
            )
            summary = response.choices[0].message.content.strip()
            logger.info("Summary generation completed")
            return summary
        except AIServiceError:
            raise
        except Exception as exc:
            logger.error("Summary generation failed: %s", exc, exc_info=True)
            raise AIServiceError("Summary service failed. Please try again.") from exc

"""Caches per-language translations of a worker-authored ComplaintUpdate's text (initial
assessment, progress update, or completion note).

Mirrors complaint_translation_cache.py's own shape deliberately -- same "look up, on a miss
translate live and cache it, so the same update/language pair only ever costs the translation
call once" pattern already established there for complaint text.

The one real difference: `Complaint.translated_text` is always canonical English (see
ComplaintAgent), so that cache always translates FROM English -- a fixed, known source. A
`ComplaintUpdate` has no such guarantee: `text` is stored exactly as the worker typed it, in
whatever language they used, and no original-language column is recorded for it at all. An
earlier version of this module approximated the source language as the authoring worker's CURRENT
`User.preferred_language`, but that's just a UI setting, not a record of what language any given
note was actually typed in -- live testing found a worker whose preference was Marathi but whose
stored note text was plain English, which the approximation then refused to translate at all.
Instead, this module leaves the source language unspecified and lets Sarvam detect it
(`TranslationService.translate_auto_detecting_source`, backed by Sarvam's mayura:v1 model), which
covers all of this app's SUPPORTED_LANGUAGES.
"""

import logging

from sqlalchemy.orm import Session

from backend.models import ComplaintUpdate, ComplaintUpdateTranslation
from backend.services.translation_service import TranslationService

logger = logging.getLogger(__name__)


def get_display_text(
    db: Session,
    update: ComplaintUpdate,
    language_code: str,
    translation_service: TranslationService,
) -> str:
    """Return `update.text` in `language_code`, translating/caching on first view.

    Args:
        db: Active database session.
        update: The ComplaintUpdate to display.
        language_code: Short language code to display it in, e.g. "hi".
        translation_service: Service used to translate (with source auto-detected) on a cache
            miss.

    Returns:
        The update's text in the requested language.

    Raises:
        AIServiceError: If there's no cached translation yet and a live translation call fails.
            Callers decide how to fall back (matching get_display_text_and_summary's own
            contract -- see routes/complaints.py and complaint_report_service.py).
    """
    cached = (
        db.query(ComplaintUpdateTranslation)
        .filter(
            ComplaintUpdateTranslation.complaint_update_id == update.id,
            ComplaintUpdateTranslation.language_code == language_code,
        )
        .first()
    )
    if cached is not None:
        return cached.translated_text

    # Cache miss: translate live (source auto-detected), then store it. A failed translation is
    # deliberately left uncached so the next view retries it, rather than getting permanently stuck.
    text = translation_service.translate_auto_detecting_source(update.text, language_code)

    db.add(
        ComplaintUpdateTranslation(
            complaint_update_id=update.id,
            language_code=language_code,
            translated_text=text,
        )
    )
    db.commit()
    logger.info(
        "Cached complaint update translation (update_id=%s, language=%s)", update.id, language_code
    )
    return text

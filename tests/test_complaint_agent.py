"""Unit tests for ComplaintAgent's orchestration of the AI pipeline."""

from unittest.mock import Mock

from backend.services.complaint_agent import ComplaintAgent
from backend.services.sarvam_client import AIServiceError


def _make_agent(summary_service: Mock, translated_text: str = "Garbage has not been collected.") -> ComplaintAgent:
    """Build a ComplaintAgent with fake normalization/translation and a given summary mock."""
    normalization_service = Mock()
    normalization_service.normalize.side_effect = lambda text, language_code: text
    translation_service = Mock()
    translation_service.to_english.return_value = translated_text
    return ComplaintAgent(
        sarvam_client=Mock(),
        translation_service=translation_service,
        summary_service=summary_service,
        normalization_service=normalization_service,
    )


def test_create_complaint_uses_ai_summary_when_available(db_session):
    """The happy path should store whatever SummaryService returns."""
    summary_service = Mock()
    summary_service.summarize.return_value = "Garbage not collected."
    agent = _make_agent(summary_service)
    db = db_session()

    complaint = agent.create_complaint(
        db, citizen_id="citizen_001", language_code="en", text="garbage issue", audio_bytes=None, photo_path=None
    )

    assert complaint.summary == "Garbage not collected."
    assert complaint.translated_text == "Garbage has not been collected."


def test_create_complaint_falls_back_to_excerpt_when_summary_fails(db_session):
    """If summary generation raises AIServiceError, the complaint should still be stored,
    with a truncated excerpt of the translated text used as the summary instead."""
    summary_service = Mock()
    summary_service.summarize.side_effect = AIServiceError("Summary service returned an empty response.")
    long_text = "Garbage has piled up near the market road for over two weeks now. " * 5
    agent = _make_agent(summary_service, translated_text=long_text)
    db = db_session()

    complaint = agent.create_complaint(
        db, citizen_id="citizen_001", language_code="en", text="garbage issue", audio_bytes=None, photo_path=None
    )

    assert complaint.summary  # never empty: Complaint.summary is non-nullable
    assert complaint.summary != long_text  # actually truncated, not the full text
    assert complaint.summary.startswith(long_text[:50])
    assert complaint.status == "open"


def test_create_complaint_falls_back_to_full_text_when_short_and_summary_fails(db_session):
    """If the translated text is already short, the fallback summary should use it as-is."""
    summary_service = Mock()
    summary_service.summarize.side_effect = AIServiceError("timed out")
    short_text = "Garbage not collected."
    agent = _make_agent(summary_service, translated_text=short_text)
    db = db_session()

    complaint = agent.create_complaint(
        db, citizen_id="citizen_001", language_code="en", text="garbage issue", audio_bytes=None, photo_path=None
    )

    assert complaint.summary == short_text

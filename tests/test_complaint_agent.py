"""Unit tests for ComplaintAgent's chunked speech-to-text handling.

A citizen's recording can exceed Sarvam's 30-second-per-request STT cap (see
docs/ai_pipeline_limits.md), so the frontend splits it into several chunks and the backend
transcribes each independently, retrying a failed chunk once before giving up on just that
chunk -- never on the whole complaint. These tests cover that orchestration directly.
"""

from unittest.mock import Mock

import pytest

from backend.services.complaint_agent import _STT_GAP_MARKER, ComplaintAgent
from backend.services.sarvam_client import AIServiceError


def _make_agent(transcribe_side_effect) -> ComplaintAgent:
    """Build a ComplaintAgent with a fake SarvamClient and passthrough downstream services."""
    sarvam_client = Mock()
    sarvam_client.transcribe.side_effect = transcribe_side_effect
    return ComplaintAgent(
        sarvam_client=sarvam_client,
        translation_service=Mock(),
        summary_service=Mock(),
        normalization_service=Mock(),
    )


def test_all_chunks_succeed_are_joined_in_order():
    agent = _make_agent(["Garbage near the market.", "It has been there for a week."])

    result = agent._transcribe_chunks([b"chunk1", b"chunk2"], "en-IN")

    assert result == "Garbage near the market. It has been there for a week."
    assert agent._sarvam.transcribe.call_count == 2


def test_failed_chunk_is_retried_once_before_giving_up():
    # Chunk 1's first attempt fails; the retry succeeds. Only 1 chunk total, 2 calls made.
    agent = _make_agent([AIServiceError("blip"), "Garbage near the market."])

    result = agent._transcribe_chunks([b"chunk1"], "en-IN")

    assert result == "Garbage near the market."
    assert agent._sarvam.transcribe.call_count == 2


def test_chunk_that_fails_twice_becomes_a_gap_marker_not_a_lost_complaint():
    # Chunk 1 fails both attempts; chunk 2 succeeds on its first attempt.
    agent = _make_agent(
        [AIServiceError("blip"), AIServiceError("still down"), "Please send someone soon."]
    )

    result = agent._transcribe_chunks([b"chunk1", b"chunk2"], "en-IN")

    assert result == f"{_STT_GAP_MARKER} Please send someone soon."
    assert agent._sarvam.transcribe.call_count == 3


def test_all_chunks_failing_raises_ai_service_error():
    agent = _make_agent(
        [
            AIServiceError("down"), AIServiceError("still down"),
            AIServiceError("down"), AIServiceError("still down"),
        ]
    )

    with pytest.raises(AIServiceError):
        agent._transcribe_chunks([b"chunk1", b"chunk2"], "en-IN")


def test_empty_successful_transcript_is_skipped_not_treated_as_a_gap():
    # A near-silent trailing chunk can legitimately transcribe to "" -- that's not a failure,
    # so it must not be replaced with the gap marker.
    agent = _make_agent(["Garbage near the market.", "  "])

    result = agent._transcribe_chunks([b"chunk1", b"chunk2"], "en-IN")

    assert result == "Garbage near the market."
    assert _STT_GAP_MARKER not in result


def test_create_complaint_from_audio_chunks_stores_the_joined_transcript(db_session):
    """End-to-end through create_complaint(): the joined transcript becomes original_text
    and flows through the rest of the (mocked) pipeline as usual."""
    sarvam_client = Mock()
    sarvam_client.transcribe.side_effect = ["Garbage near the market.", "Please send someone."]
    normalization_service = Mock()
    normalization_service.normalize.side_effect = lambda text, language_code: text
    translation_service = Mock()
    translation_service.to_english.side_effect = lambda text, language_code: text
    summary_service = Mock()
    summary_service.summarize.return_value = "Garbage complaint near the market."

    agent = ComplaintAgent(
        sarvam_client=sarvam_client,
        translation_service=translation_service,
        summary_service=summary_service,
        normalization_service=normalization_service,
    )
    db = db_session()

    complaint = agent.create_complaint(
        db,
        citizen_id="1",
        language_code="en",
        text=None,
        audio_chunks=[b"chunk1", b"chunk2"],
        photo_path=None,
    )

    assert complaint.original_text == "Garbage near the market. Please send someone."
    assert complaint.summary == "Garbage complaint near the market."

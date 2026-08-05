"""Regression tests for the AI pipeline's known real-world limits.

These document facts established by a live measurement sweep against the actual Sarvam
API (not guesses) run before the Milestone 1 hackathon submission. See
`docs/ai_pipeline_limits.md` for the full write-up and raw numbers; this file keeps the
two conclusions that matter as executable regression tests:

1. A realistic, "typical" spoken complaint (sized to what fits under Sarvam's own
   30-second hard cap on the synchronous speech-to-text endpoint we use — confirmed live
   and written up in docs/ai_pipeline_limits.md) completes normalization + summary
   successfully. This test hits the live API and is skipped by default (no network/API
   key dependency in normal test runs); run it explicitly with RUN_LIVE_AI_TESTS=1 when
   you want to re-verify against the real service.
2. When a complaint is too long for the AI pipeline to summarize in time, the fallback
   behavior built into ComplaintAgent (see backend/services/complaint_agent.py) kicks in
   and the complaint is still stored, never lost. This test is mocked and always runs.
"""

import os
import time
from unittest.mock import Mock

import pytest

from backend.services.complaint_agent import ComplaintAgent
from backend.services.normalization_service import NormalizationService
from backend.services.sarvam_client import AIServiceError
from backend.services.summary_service import SummaryService

# A realistic spoken complaint, sized to what a citizen could plausibly say in under 30
# seconds — the hard ceiling of Sarvam's synchronous speech-to-text endpoint (confirmed
# live: requests over 30s are rejected with a 400 "Audio duration exceeds the maximum
# limit of 30 seconds" error). At a normal speaking pace this is roughly 60-80 words, so
# nothing a citizen actually submits through the voice flow can exceed this by much.
TYPICAL_COMPLAINT_TEXT = (
    "There is a huge pile of garbage near the main road that has not been collected for "
    "over a week. The smell from the rotting waste is unbearable, especially in the "
    "evening. Stray dogs keep scattering the trash across the street, and children "
    "playing nearby are at risk of getting sick because of the flies. We have complained "
    "to the local ward office before but nobody has come to clear it. Please send someone "
    "to inspect the area near the old temple road as soon as possible."
)

# The maximum acceptable latency for a single AI step in a citizen-facing submit flow,
# per product judgment call, not a Sarvam-imposed limit.
ACCEPTABLE_LATENCY_SECONDS = 20

_RUN_LIVE = os.getenv("RUN_LIVE_AI_TESTS") == "1"
_skip_unless_live = pytest.mark.skipif(
    not _RUN_LIVE,
    reason="Live Sarvam API test; set RUN_LIVE_AI_TESTS=1 (and a configured LLM_API_KEY) to run it.",
)


@_skip_unless_live
class TestTypicalComplaintLatency:
    """Confirms a realistic complaint completes each AI step within an acceptable time.

    These hit the real Sarvam API and cost real API credits, so they're opt-in via
    RUN_LIVE_AI_TESTS=1 rather than part of the default `pytest` run.

    IMPORTANT — expected flakiness, not a test bug: a repeated live measurement (see
    docs/ai_pipeline_limits.md) found that at this exact input size, summary generation's
    latency ranged 6.7s-36.1s across 4 trials, missing a 20s bar in 2 of 4 (50%). This is
    real, measured variance in the underlying reasoning model's behavior — not something
    this test file can smooth over. A failure here means "the known risk materialized on
    this run," not "something regressed." Don't silence it by loosening the bar without
    re-reading that doc first.
    """

    def test_normalization_completes_within_acceptable_latency(self):
        service = NormalizationService()
        start = time.time()
        result = service.normalize(TYPICAL_COMPLAINT_TEXT, "en")
        elapsed = time.time() - start

        assert result  # never empty: falls back to original text on any failure
        assert elapsed < ACCEPTABLE_LATENCY_SECONDS, (
            f"Normalization took {elapsed:.1f}s on a typical {len(TYPICAL_COMPLAINT_TEXT.split())}"
            f"-word complaint; acceptable latency is {ACCEPTABLE_LATENCY_SECONDS}s. See "
            f"docs/ai_pipeline_limits.md — this may mean LLM_MAX_TOKENS/reasoning_effort "
            f"need revisiting, or the acceptable-latency bar itself needs resetting."
        )

    def test_summary_completes_within_acceptable_latency(self):
        service = SummaryService()
        start = time.time()
        result = service.summarize(TYPICAL_COMPLAINT_TEXT)
        elapsed = time.time() - start

        assert result
        assert elapsed < ACCEPTABLE_LATENCY_SECONDS, (
            f"Summary generation took {elapsed:.1f}s on a typical "
            f"{len(TYPICAL_COMPLAINT_TEXT.split())}-word complaint; acceptable latency is "
            f"{ACCEPTABLE_LATENCY_SECONDS}s. See docs/ai_pipeline_limits.md."
        )


class TestOversizedComplaintFallback:
    """Confirms ComplaintAgent never fails complaint submission when summary generation
    fails on an input too large/slow for the AI pipeline to handle in time.

    Mocked and deterministic — this is the actual regression test that should catch any
    future change that accidentally makes summary failures fatal again (as they were
    before the fix: the very failure mode this whole investigation started from).
    """

    def test_complaint_is_stored_when_summary_generation_fails(self, db_session):
        oversized_translated_text = "Garbage has piled up near the market road. " * 200  # ~1600 words

        normalization_service = _mock_normalization_passthrough()
        translation_service = _mock_translation(oversized_translated_text)
        summary_service = _mock_summary_failure()

        agent = ComplaintAgent(
            sarvam_client=_mock_sarvam_client(),
            translation_service=translation_service,
            summary_service=summary_service,
            normalization_service=normalization_service,
        )
        db = db_session()

        complaint = agent.create_complaint(
            db,
            citizen_id="citizen_001",
            language_code="en",
            text="a very long complaint",
            audio_bytes=None,
            photo_path=None,
        )

        # The complaint must still be stored — a citizen's report is never lost over the
        # summary (a nice-to-have for worker triage) failing.
        assert complaint.id is not None
        assert complaint.status == "open"
        assert complaint.translated_text == oversized_translated_text
        # summary is non-nullable in the schema; the fallback must produce *something*.
        assert complaint.summary
        # And it must actually be a truncated excerpt, not the full oversized text —
        # otherwise the fallback isn't doing its job of keeping the summary short.
        assert len(complaint.summary) < len(oversized_translated_text)


def _mock_sarvam_client():
    return Mock()


def _mock_normalization_passthrough():
    service = Mock()
    service.normalize.side_effect = lambda text, language_code: text
    return service


def _mock_translation(translated_text: str):
    service = Mock()
    service.to_english.return_value = translated_text
    return service


def _mock_summary_failure():
    service = Mock()
    service.summarize.side_effect = AIServiceError(
        "Summary service returned an empty response. Please try again."
    )
    return service

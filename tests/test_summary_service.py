"""Unit tests for SummaryService's use of Sarvam's chat completion API."""

from unittest.mock import Mock

import pytest

from backend.services.sarvam_client import AIServiceError
from backend.services.summary_service import SummaryService


def _fake_chat_response(text: str) -> Mock:
    """Build a fake response object matching Sarvam's chat completion shape."""
    message = Mock(content=text)
    choice = Mock(message=message)
    return Mock(choices=[choice])


def test_summarize_returns_stripped_model_output(monkeypatch):
    """summarize() should call chat.completions and return the trimmed reply text."""
    monkeypatch.setattr("backend.services.summary_service.settings.LLM_API_KEY", "fake-key")
    fake_client = Mock()
    fake_client.chat.completions.return_value = _fake_chat_response(
        "  Garbage not collected near the house.  "
    )
    monkeypatch.setattr(
        "backend.services.summary_service.SarvamAI", lambda api_subscription_key, timeout=None: fake_client
    )

    service = SummaryService()
    result = service.summarize("Garbage has not been collected near my house for three days.")

    assert result == "Garbage not collected near the house."
    fake_client.chat.completions.assert_called_once()


def test_summarize_without_api_key_raises_ai_service_error(monkeypatch):
    """With no LLM_API_KEY configured, summarize() should fail clearly, not crash."""
    monkeypatch.setattr("backend.services.summary_service.settings.LLM_API_KEY", "")

    service = SummaryService()

    with pytest.raises(AIServiceError):
        service.summarize("Garbage has not been collected.")


def test_summarize_wraps_unexpected_errors(monkeypatch):
    """Any unexpected exception from the client should be wrapped as AIServiceError."""
    monkeypatch.setattr("backend.services.summary_service.settings.LLM_API_KEY", "fake-key")
    fake_client = Mock()
    fake_client.chat.completions.side_effect = RuntimeError("network blip")
    monkeypatch.setattr(
        "backend.services.summary_service.SarvamAI", lambda api_subscription_key, timeout=None: fake_client
    )

    service = SummaryService()

    with pytest.raises(AIServiceError):
        service.summarize("Garbage has not been collected.")

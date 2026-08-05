"""Unit tests for NormalizationService's use of Sarvam's chat completion API."""

from unittest.mock import Mock

from backend.services.normalization_service import NormalizationService


def _fake_chat_response(text: str | None, finish_reason: str = "stop") -> Mock:
    """Build a fake response object matching Sarvam's chat completion shape."""
    message = Mock(content=text)
    choice = Mock(message=message, finish_reason=finish_reason)
    return Mock(choices=[choice])


def test_normalize_returns_stripped_model_output(monkeypatch):
    """normalize() should call chat.completions and return the trimmed corrected text."""
    monkeypatch.setattr("backend.services.normalization_service.settings.LLM_API_KEY", "fake-key")
    fake_client = Mock()
    fake_client.chat.completions.return_value = _fake_chat_response(
        "  There is garbage near my village, please check the area of Rukadi.  "
    )
    monkeypatch.setattr(
        "backend.services.normalization_service.SarvamAI", lambda api_subscription_key: fake_client
    )

    service = NormalizationService()
    result = service.normalize("there is the garbage so please check the ara of rukadi")

    assert result == "There is garbage near my village, please check the area of Rukadi."
    fake_client.chat.completions.assert_called_once()


def test_normalize_without_api_key_returns_original_text(monkeypatch):
    """With no LLM_API_KEY configured, normalize() should fall back, not raise."""
    monkeypatch.setattr("backend.services.normalization_service.settings.LLM_API_KEY", "")

    service = NormalizationService()
    result = service.normalize("check the ara of rukadi")

    assert result == "check the ara of rukadi"


def test_normalize_empty_model_response_returns_original_text(monkeypatch):
    """If the model returns no content, normalize() should fall back to the original text."""
    monkeypatch.setattr("backend.services.normalization_service.settings.LLM_API_KEY", "fake-key")
    fake_client = Mock()
    fake_client.chat.completions.return_value = _fake_chat_response(None, finish_reason="length")
    monkeypatch.setattr(
        "backend.services.normalization_service.SarvamAI", lambda api_subscription_key: fake_client
    )

    service = NormalizationService()
    result = service.normalize("check the ara of rukadi")

    assert result == "check the ara of rukadi"


def test_normalize_swallows_unexpected_errors(monkeypatch):
    """Any unexpected exception from the client should fall back, not raise."""
    monkeypatch.setattr("backend.services.normalization_service.settings.LLM_API_KEY", "fake-key")
    fake_client = Mock()
    fake_client.chat.completions.side_effect = RuntimeError("network blip")
    monkeypatch.setattr(
        "backend.services.normalization_service.SarvamAI", lambda api_subscription_key: fake_client
    )

    service = NormalizationService()
    result = service.normalize("check the ara of rukadi")

    assert result == "check the ara of rukadi"

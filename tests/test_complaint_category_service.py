"""Unit tests for ComplaintCategoryService's use of Sarvam's chat completion API.

Every test here exercises the "never raises, only returns None on failure" contract directly --
see the service's own module docstring for why: a slow/down Sarvam account must only ever
degrade classification quality (falling through to the wizard's keyword match / manual picker),
never block complaint submission the way SummaryService's AIServiceError-raising contract would.
"""

from unittest.mock import Mock

from backend.schemas.rag_knowledge import ServiceCategory
from backend.services.complaint_category_service import ComplaintCategoryService


def _fake_chat_response(text: str, finish_reason: str = "stop") -> Mock:
    """Build a fake response object matching Sarvam's chat completion shape."""
    message = Mock(content=text)
    choice = Mock(message=message, finish_reason=finish_reason)
    return Mock(choices=[choice])


def test_classify_returns_matching_category(monkeypatch):
    monkeypatch.setattr("backend.services.complaint_category_service.settings.LLM_API_KEY", "fake-key")
    fake_client = Mock()
    fake_client.chat.completions.return_value = _fake_chat_response("WATER_DRAINAGE")
    monkeypatch.setattr(
        "backend.services.complaint_category_service.SarvamAI",
        lambda api_subscription_key, timeout=None: fake_client,
    )

    service = ComplaintCategoryService()
    result = service.classify("There is a burst water pipe flooding the street outside my house.")

    assert result == ServiceCategory.WATER_DRAINAGE
    fake_client.chat.completions.assert_called_once()


def test_classify_returns_none_for_unsure_response(monkeypatch):
    monkeypatch.setattr("backend.services.complaint_category_service.settings.LLM_API_KEY", "fake-key")
    fake_client = Mock()
    fake_client.chat.completions.return_value = _fake_chat_response("UNSURE")
    monkeypatch.setattr(
        "backend.services.complaint_category_service.SarvamAI",
        lambda api_subscription_key, timeout=None: fake_client,
    )

    service = ComplaintCategoryService()
    result = service.classify("Something is wrong somewhere.")

    assert result is None


def test_classify_returns_none_for_unrecognized_response(monkeypatch):
    """A model that ignores instructions and returns something else entirely -- still a clean
    fallback, not a crash."""
    monkeypatch.setattr("backend.services.complaint_category_service.settings.LLM_API_KEY", "fake-key")
    fake_client = Mock()
    fake_client.chat.completions.return_value = _fake_chat_response("I think this is about garbage.")
    monkeypatch.setattr(
        "backend.services.complaint_category_service.SarvamAI",
        lambda api_subscription_key, timeout=None: fake_client,
    )

    service = ComplaintCategoryService()
    result = service.classify("The bin has not been emptied in a week.")

    assert result is None


def test_classify_returns_none_for_empty_response(monkeypatch):
    monkeypatch.setattr("backend.services.complaint_category_service.settings.LLM_API_KEY", "fake-key")
    fake_client = Mock()
    fake_client.chat.completions.return_value = _fake_chat_response("", finish_reason="length")
    monkeypatch.setattr(
        "backend.services.complaint_category_service.SarvamAI",
        lambda api_subscription_key, timeout=None: fake_client,
    )

    service = ComplaintCategoryService()
    result = service.classify("Some complaint text.")

    assert result is None


def test_classify_without_api_key_returns_none(monkeypatch):
    monkeypatch.setattr("backend.services.complaint_category_service.settings.LLM_API_KEY", "")

    service = ComplaintCategoryService()
    result = service.classify("Garbage has not been collected.")

    assert result is None


def test_classify_swallows_unexpected_errors(monkeypatch):
    monkeypatch.setattr("backend.services.complaint_category_service.settings.LLM_API_KEY", "fake-key")
    fake_client = Mock()
    fake_client.chat.completions.side_effect = RuntimeError("network blip")
    monkeypatch.setattr(
        "backend.services.complaint_category_service.SarvamAI",
        lambda api_subscription_key, timeout=None: fake_client,
    )

    service = ComplaintCategoryService()
    result = service.classify("Garbage has not been collected.")

    assert result is None


def test_classify_returns_none_for_blank_text(monkeypatch):
    """No point spending a real API call on empty input -- short-circuits before the client is
    ever touched."""
    monkeypatch.setattr("backend.services.complaint_category_service.settings.LLM_API_KEY", "fake-key")
    fake_client = Mock()
    monkeypatch.setattr(
        "backend.services.complaint_category_service.SarvamAI",
        lambda api_subscription_key, timeout=None: fake_client,
    )

    service = ComplaintCategoryService()
    result = service.classify("   ")

    assert result is None
    fake_client.chat.completions.assert_not_called()

"""Unit tests for TranslationService's language-code handling."""

from unittest.mock import Mock

import pytest

from backend.services.translation_service import TranslationService


def test_to_english_uses_correct_bcp47_codes():
    """to_english should translate from the source BCP-47 code to English's."""
    fake_sarvam = Mock()
    fake_sarvam.translate.return_value = "Garbage has not been collected."
    service = TranslationService(sarvam_client=fake_sarvam)

    result = service.to_english("कचरा उचलला नाही", "mr")

    fake_sarvam.translate.assert_called_once_with(
        "कचरा उचलला नाही", source_language_code="mr-IN", target_language_code="en-IN"
    )
    assert result == "Garbage has not been collected."


def test_to_language_uses_correct_bcp47_codes():
    """to_language should translate from English's BCP-47 code to the target's."""
    fake_sarvam = Mock()
    fake_sarvam.translate.return_value = "कचरा उचलला नाही।"
    service = TranslationService(sarvam_client=fake_sarvam)

    result = service.to_language("Garbage has not been collected.", "hi")

    fake_sarvam.translate.assert_called_once_with(
        "Garbage has not been collected.", source_language_code="en-IN", target_language_code="hi-IN"
    )
    assert result == "कचरा उचलला नाही।"


def test_unsupported_language_raises_value_error():
    """An unsupported language code should raise ValueError before calling Sarvam."""
    fake_sarvam = Mock()
    service = TranslationService(sarvam_client=fake_sarvam)

    with pytest.raises(ValueError):
        service.to_english("some text", "fr")

    fake_sarvam.translate.assert_not_called()

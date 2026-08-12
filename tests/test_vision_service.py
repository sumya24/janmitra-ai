"""Tests for backend/services/vision_service.py.

Never downloads/loads the real ~1.9B-param model in tests -- that would make the suite extremely
slow and network-dependent. Instead, `_model`/`_tokenizer` are set directly (bypassing
`_get_model()`) or the loading call is mocked, mirroring how ComplaintAgent's tests inject a fake
SarvamClient instead of hitting the real Sarvam API.
"""

from unittest.mock import Mock, patch

import pytest

from backend.services.vision_service import VisionService, VisionServiceError

# A minimal, genuinely valid 1x1 JPEG (not just fake bytes with a jpeg-ish prefix) -- same fixture
# used by frontend-react/e2e/evidence-upload.spec.ts, so image decoding is proven against a real
# image, not a stub.
import base64

JPEG_1PX = base64.b64decode(
    "/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAMCAgICAgMCAgIDAwMDBAYEBAQEBAgGBgUGCQgKCgkICQkKDA8MCgsOCwkJ"
    "DRENDg8QEBEQCgwSExIQEw8QEBD/2wBDAQMDAwQDBAgEBAgQCwkLEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQ"
    "EBAQEBAQEBAQEBAQEBAQEBAQEBAQEBD/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAj/xAAU"
    "EAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMB"
    "AAIRAxEAPwCdABmX/9k="
)


def _service_with_fake_model(answer: str = "A pothole in the middle of a paved road.") -> VisionService:
    service = VisionService(model_name="fake/model")
    fake_model = Mock()
    fake_model.encode_image.return_value = "encoded"
    fake_model.answer_question.return_value = answer
    service._model = fake_model
    service._tokenizer = Mock()
    return service


def test_describe_image_returns_caption_from_model():
    service = _service_with_fake_model("A large pothole in the road, partially filled with water.")

    caption = service.describe_image(JPEG_1PX)

    assert caption == "A large pothole in the road, partially filled with water."


def test_describe_image_strips_whitespace():
    service = _service_with_fake_model("  A broken streetlight.  \n")

    assert service.describe_image(JPEG_1PX) == "A broken streetlight."


def test_describe_image_invalid_bytes_raises_vision_service_error():
    service = _service_with_fake_model()

    with pytest.raises(VisionServiceError):
        service.describe_image(b"not a real image")


def test_describe_image_model_failure_raises_vision_service_error():
    service = VisionService(model_name="fake/model")
    fake_model = Mock()
    fake_model.encode_image.side_effect = RuntimeError("model exploded")
    service._model = fake_model
    service._tokenizer = Mock()

    with pytest.raises(VisionServiceError):
        service.describe_image(JPEG_1PX)


def test_get_model_wraps_load_failure_in_vision_service_error():
    service = VisionService(model_name="fake/model")

    with patch("transformers.AutoModelForCausalLM.from_pretrained", side_effect=OSError("no such model")):
        with pytest.raises(VisionServiceError):
            service.load()

    assert service._model is None


def test_model_name_defaults_from_settings():
    service = VisionService()

    assert service.model_name  # non-empty, pulled from backend.config.settings.VISION_MODEL_NAME

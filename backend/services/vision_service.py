"""Image understanding for Ask Sarthi, via a local open-source vision-language model.

Sarvam (this project's only other AI vendor) has no vision/image-understanding capability --
checked directly against the installed SDK's type stubs: `sarvam-105b` chat completions only
accept plain-string message content, and Sarvam's `doc_ai`/`document_intelligence` sub-clients are
document-OCR pipelines (printed/handwritten text extraction), not general photo/scene
understanding. Rather than add a new hosted vendor (Anthropic/OpenAI/Gemini) -- a new API key, a
new cost, a new dependency to trust -- the user chose a small local vision-language model, reusing
the `torch` dependency this project already installs for RAG embeddings.

**Model: `vikhyatk/moondream2`** (~1.9B params, via `transformers`, `trust_remote_code=True`) --
purpose-built for CPU-friendly image captioning/VQA, small enough to run without a GPU. This
project's deployment target (Oracle Cloud "Always Free" Arm VM, up to 24GB RAM -- see
docs/DEPLOYMENT.md) comfortably fits this model in fp32/fp16 on CPU; no quantization is required
for v1 (revisit only if real measured latency in production is a problem).

Loaded lazily (first load downloads/initializes real model weights -- real time, like
`SentenceTransformerEmbeddingProvider` in embedding_provider.py, the precedent this class
follows), so importing this module never pays that cost -- only actually using a `VisionService`
does.
"""

from __future__ import annotations

import io
import logging

logger = logging.getLogger(__name__)

_CAPTION_PROMPT = (
    "Describe this image in one or two sentences, focusing on any civic issue visible such as a "
    "pothole, garbage or waste, a water leak or drainage problem, or a broken streetlight. If "
    "there is no such issue visible, just describe what the image shows."
)


class VisionServiceError(Exception):
    """Raised when the local vision-language model fails to load or process an image.

    Callers should catch this and treat image understanding as best-effort: an image whose
    caption fails still gets attached to a complaint as evidence, it just won't enrich the
    citizen's text with a description (see orchestration/nodes.py's input_processing_node).
    """


class VisionService:
    """Wraps a local vision-language model to caption citizen-attached photos."""

    def __init__(self, model_name: str | None = None) -> None:
        from backend.config import settings

        self._model_name = model_name or settings.VISION_MODEL_NAME
        self._model = None  # lazy-loaded, see _get_model
        self._tokenizer = None

    @property
    def model_name(self) -> str:
        return self._model_name

    def load(self) -> None:
        """Forces the (slow, first-time) model load now rather than lazily on first call --
        useful for warming the model at process startup instead of on a citizen's first request."""
        self._get_model()

    def _get_model(self):
        if self._model is None:
            try:
                from transformers import AutoModelForCausalLM, AutoTokenizer
            except ImportError as exc:
                raise VisionServiceError(
                    "Vision model dependencies are not installed."
                ) from exc

            logger.info("Loading vision model %s (first load may take a while)...", self._model_name)
            try:
                self._model = AutoModelForCausalLM.from_pretrained(
                    self._model_name, trust_remote_code=True
                )
                self._tokenizer = AutoTokenizer.from_pretrained(self._model_name)
            except Exception as exc:
                self._model = None
                self._tokenizer = None
                logger.error("Failed to load vision model %s: %s", self._model_name, exc, exc_info=True)
                raise VisionServiceError("Vision model failed to load.") from exc
            logger.info("Vision model %s loaded", self._model_name)
        return self._model

    def describe_image(self, image_bytes: bytes) -> str:
        """Generate a short text caption for an attached photo.

        Args:
            image_bytes: Raw image file bytes (jpeg/png), already validated by the caller.

        Returns:
            A short text description of the image, tuned toward civic-issue photos.

        Raises:
            VisionServiceError: If the image can't be decoded or the model call fails.
        """
        try:
            from PIL import Image
        except ImportError as exc:
            raise VisionServiceError("Image decoding dependency is not installed.") from exc

        try:
            image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        except Exception as exc:
            logger.error("Failed to decode image for vision captioning: %s", exc, exc_info=True)
            raise VisionServiceError("Could not read the attached image.") from exc

        model = self._get_model()
        try:
            encoded_image = model.encode_image(image)
            caption = model.answer_question(encoded_image, _CAPTION_PROMPT, self._tokenizer)
            caption = (caption or "").strip()
        except Exception as exc:
            logger.error("Vision captioning failed: %s", exc, exc_info=True)
            raise VisionServiceError("Image understanding failed. Please try again.") from exc

        logger.info("Vision captioning completed (caption_length=%d)", len(caption))
        return caption

"""Tests for POST /ask-janmitra/image (Ask JanMitra image-attachment phases 3 and 4).

Phase 3 covered: the endpoint accepts, validates, and persists an attached image using the same
evidence_service.validate_and_write() every other photo upload in this app already uses.

Phase 4 (this file, updated): the image is now actually captioned via VisionService and threaded
into the graph's reasoning (see backend/services/orchestration/nodes.py) -- an image with no text
at all gets a real clarification question instead of a guess, a caption folds into the text every
downstream node consumes, and a complaint filed with an image gets a real `photo_path` plus a
real `ComplaintEvidence` row via the EXISTING evidence system.

VisionService is always swapped for a deterministic fake here (never the real ~1.9B-param model)
-- same reasoning as swapping AnswerGenerationService/ComplaintAgent below: no real network call
or heavy model load in tests. Follows the same fake-service/no-network-call pattern as
test_ask_janmitra.py (real ChromaDB retrieval, fake LLM answer generation, fake complaint agent)
and the same file-upload assertion style as test_evidence.py (real disk persistence, real
content-type/size validation).
"""

from pathlib import Path
from unittest.mock import Mock

import backend.routes.ask_janmitra as ask_janmitra_module
from backend.config import settings
from backend.models import Complaint, ComplaintEvidence
from backend.services.ask_janmitra_service import AskJanMitraService
from backend.services.embedding_provider import SentenceTransformerEmbeddingProvider
from backend.services.vector_store import ChromaVectorStore
from backend.services.vision_service import VisionServiceError

_JPEG_BYTES = b"\xff\xd8\xff" + b"fake jpeg content for testing" * 10
_PNG_BYTES = b"\x89PNG\r\n\x1a\n" + b"fake png content for testing" * 10
_FAKE_CAPTION = "A large pothole in the middle of a paved road."

_shared_store: ChromaVectorStore | None = None
_shared_provider: SentenceTransformerEmbeddingProvider | None = None


def _get_shared_chroma_deps():
    global _shared_store, _shared_provider
    if _shared_provider is None:
        _shared_provider = SentenceTransformerEmbeddingProvider()
        _shared_provider.load()
    if _shared_store is None:
        _shared_store = ChromaVectorStore(settings.CHROMA_PERSIST_DIR, settings.CHROMA_COLLECTION_NAME)
        _shared_store.load()
    return _shared_store, _shared_provider


class _FakeComplaintAgent:
    def create_complaint(self, db, citizen_id, language_code, text, audio_chunks, photo_path):
        complaint = Complaint(
            citizen_id=citizen_id,
            original_text=text or "",
            original_language=language_code,
            translated_text=text or "",
            summary=(text or "")[:80],
            photo_path=photo_path,
            status="open",
        )
        db.add(complaint)
        db.commit()
        db.refresh(complaint)
        return complaint


def _install_real_service(monkeypatch, *, caption: str | None = _FAKE_CAPTION, caption_error: bool = False) -> Mock:
    """Installs a real AskJanMitraService (real Chroma retrieval) with LLM/complaint/vision calls
    swapped for deterministic fakes. Returns the fake answer-generation Mock so tests can inspect
    exactly what query text reached it (proving/disproving caption-folding).
    """
    store, provider = _get_shared_chroma_deps()
    fake_answers = Mock()
    # Echoes the query text back as the "answer" -- lets tests assert on exactly what text
    # reached RAG (e.g. whether an image caption got folded into it), not just that *an* answer
    # came back.
    fake_answers.generate = Mock(side_effect=lambda q, chunks, lang: (q, False))

    fake_vision = Mock()
    if caption_error:
        fake_vision.describe_image = Mock(side_effect=VisionServiceError("model unavailable"))
    else:
        fake_vision.describe_image = Mock(return_value=caption)

    service = AskJanMitraService(
        vector_store=store,
        embedding_provider=provider,
        answer_service=fake_answers,
        complaint_agent=_FakeComplaintAgent(),
        vision_service=fake_vision,
    )
    monkeypatch.setattr(ask_janmitra_module, "_service", service)
    return fake_answers


def _ask_text(client, token, question, **kwargs):
    body = {"question": question, "language": "en", **kwargs}
    return client.post("/ask-janmitra", headers={"Authorization": f"Bearer {token}"}, json=body)


def _ask_image(client, token, question, image_bytes=_JPEG_BYTES, filename="photo.jpg", content_type="image/jpeg", **kwargs):
    data = {"question": question, "language": "en", **kwargs}
    return client.post(
        "/ask-janmitra/image",
        headers={"Authorization": f"Bearer {token}"},
        data=data,
        files=[("image", (filename, image_bytes, content_type))],
    )


def test_image_caption_is_folded_into_the_text_rag_actually_sees(client, monkeypatch, make_citizen):
    """Phase 4: an attached photo's caption is appended to the text every downstream node
    consumes -- proven by echoing the exact query text AnswerGenerationService.generate() received
    back as the answer (see _install_real_service's fake_answers), not just checking status 200.
    TYPE_B (information) phrasing deliberately, so this exercises rag_flow, not complaint_flow."""
    fake_answers = _install_real_service(monkeypatch)
    token, _ = make_citizen(phone="9000000101")

    response = _ask_image(client, token, "Who do I contact about road potholes in Nagpur?")

    assert response.status_code == 200, response.text
    assert _FAKE_CAPTION in response.json()["answer"]
    called_text = fake_answers.generate.call_args[0][0]
    assert "Who do I contact about road potholes in Nagpur?" in called_text
    assert _FAKE_CAPTION in called_text


def test_image_without_any_text_asks_a_real_clarification_not_a_guess(client, monkeypatch, make_citizen):
    """Phase 4's core anti-guessing rule: an image with NO text at all must never be silently
    treated as a complaint or an information request -- it gets a real clarification question."""
    _install_real_service(monkeypatch)
    token, _ = make_citizen(phone="9000000109")

    response = _ask_image(client, token, "")

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["follow_up_required"] is True
    assert body["routed_to"] == "NONE_CLARIFICATION_NEEDED"
    assert "report an issue" in body["answer"].lower() or "report an issue" in [o.lower() for o in body["follow_up_options"]]
    # The caption is used to make the clarification question itself more specific.
    assert _FAKE_CAPTION in body["answer"]


def test_image_without_text_still_asks_clarification_when_captioning_fails(client, monkeypatch, make_citizen):
    """Vision captioning is best-effort -- a failure must not block the request or silently guess;
    it just makes the same clarification question slightly less specific."""
    _install_real_service(monkeypatch, caption_error=True)
    token, _ = make_citizen(phone="9000000110")

    response = _ask_image(client, token, "")

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["follow_up_required"] is True
    assert body["routed_to"] == "NONE_CLARIFICATION_NEEDED"


def test_image_plus_complaint_creates_real_photo_path_and_evidence_row(client, monkeypatch, make_citizen, db_session):
    """Phase 4: filing a complaint with an attached image must reuse the EXISTING ComplaintEvidence
    system exactly -- a real Complaint.photo_path AND a real ComplaintEvidence row (stage
    CITIZEN_COMPLAINT), not a second image-storage system."""
    _install_real_service(monkeypatch)
    token, _ = make_citizen(phone="9000000111")

    response = _ask_image(client, token, "Street light near my home is not working.", location_text="Mohali")

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["routed_to"] == "COMPLAINT_CREATED"
    complaint_id = body["complaint_id"]
    assert complaint_id is not None

    db = db_session()
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).one()
    assert complaint.photo_path is not None

    evidence = db.query(ComplaintEvidence).filter(ComplaintEvidence.complaint_id == complaint_id).all()
    assert len(evidence) == 1
    assert evidence[0].stage == "CITIZEN_COMPLAINT"
    assert evidence[0].uploader_role == "citizen"
    assert evidence[0].file_path == complaint.photo_path
    db.close()

    on_disk = Path(settings.UPLOAD_FOLDER) / complaint.photo_path
    assert on_disk.is_file()
    assert on_disk.read_bytes() == _JPEG_BYTES


def test_image_is_actually_persisted_on_disk(client, monkeypatch, make_citizen):
    """Not a UI-only mock -- proves the uploaded bytes really land in settings.UPLOAD_FOLDER,
    matching the same real-persistence guarantee test_evidence.py already proves for /complaints."""
    _install_real_service(monkeypatch)
    token, _ = make_citizen(phone="9000000102")

    before = set(Path(settings.UPLOAD_FOLDER).glob("*")) if Path(settings.UPLOAD_FOLDER).exists() else set()
    response = _ask_image(client, token, "Who do I contact about street lights in Mohali?")
    assert response.status_code == 200, response.text
    after = set(Path(settings.UPLOAD_FOLDER).glob("*"))

    new_files = after - before
    assert len(new_files) == 1
    assert new_files.pop().read_bytes() == _JPEG_BYTES


def test_image_rejects_unsupported_content_type(client, monkeypatch, make_citizen):
    _install_real_service(monkeypatch)
    token, _ = make_citizen(phone="9000000103")

    response = _ask_image(
        client, token, "What is this?",
        image_bytes=b"not an image", filename="file.txt", content_type="text/plain",
    )

    assert response.status_code == 400
    assert "Unsupported photo type" in response.json()["detail"]


def test_image_rejects_oversized_file(client, monkeypatch, make_citizen):
    _install_real_service(monkeypatch)
    token, _ = make_citizen(phone="9000000104")

    oversized = b"\xff\xd8\xff" + b"x" * (settings.MAX_PHOTO_SIZE_BYTES + 1)
    response = _ask_image(client, token, "What is this?", image_bytes=oversized)

    assert response.status_code == 400
    assert "exceeds the maximum allowed size" in response.json()["detail"]


def test_image_endpoint_allows_empty_question(client, monkeypatch, make_citizen):
    """Unlike the plain JSON endpoint (AskJanMitraRequest.question requires non-empty text), the
    image endpoint must allow an empty question -- an image with no text at all is a real,
    supported case (see the clarification tests above for what actually happens to it)."""
    _install_real_service(monkeypatch)
    token, _ = make_citizen(phone="9000000105")

    response = _ask_image(client, token, "")

    assert response.status_code == 200, response.text


def test_image_endpoint_rejects_unsupported_language(client, monkeypatch, make_citizen):
    _install_real_service(monkeypatch)
    token, _ = make_citizen(phone="9000000106")

    response = _ask_image(client, token, "hello", language="fr")

    assert response.status_code == 400


def test_image_endpoint_rejects_malformed_conversation_history(client, monkeypatch, make_citizen):
    _install_real_service(monkeypatch)
    token, _ = make_citizen(phone="9000000107")

    response = _ask_image(client, token, "hello", conversation_history="not json")

    assert response.status_code == 400


def test_image_endpoint_requires_authentication(client, monkeypatch):
    _install_real_service(monkeypatch)

    response = client.post(
        "/ask-janmitra/image",
        data={"question": "hello", "language": "en"},
        files=[("image", ("photo.jpg", _JPEG_BYTES, "image/jpeg"))],
    )

    assert response.status_code in (401, 403)


def test_image_endpoint_accepts_png(client, monkeypatch, make_citizen):
    _install_real_service(monkeypatch)
    token, _ = make_citizen(phone="9000000108")

    response = _ask_image(
        client, token, "Who do I contact about street lights in Mohali?",
        image_bytes=_PNG_BYTES, filename="photo.png", content_type="image/png",
    )

    assert response.status_code == 200, response.text

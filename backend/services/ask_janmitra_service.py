"""Orchestrates the full Ask JanMitra pipeline via the LangGraph orchestrator in
`backend/services/orchestration/` -- intent -> location -> conditional routing -> (RAG retrieval
-> answer generation -> citations) OR (complaint creation + worker assignment) OR (complaint-
status lookup) OR (clarification) OR (out-of-scope) -> structured response.

This class is now a thin adapter around `orchestration.graph.run_graph()`: it builds the graph
once (cheap, pure structure), builds the shared `GraphDeps` once (the actually-expensive parts --
the Chroma collection, the embedding model -- are unchanged from before this phase), and on every
`ask()` call builds a per-request `RequestContext` + initial `GraphState`, invokes the graph, and
translates the final state back into `AskJanMitraResponse`. See
`backend/services/orchestration/graph.py`'s module docstring for the full node/edge diagram and
`docs/ask_janmitra_orchestration.md` for the architectural writeup -- this docstring only covers
what's still true about this class's own responsibilities (the public API surface).

Source routing (unchanged rule, now enforced by the graph's edges rather than this class's own
if/else): TYPE_C (personal complaint status) is answered EXCLUSIVELY from the existing
`complaints` table — it never touches the RAG retriever. TYPE_B (service info) is answered
EXCLUSIVELY via RAG retrieval. TYPE_A (complaint) now creates a real complaint via the existing
`ComplaintAgent`/`assign_next_worker` services (a deliberate behavior change made this phase, see
`orchestration/nodes.py`'s module docstring) — it never touches RAG or the status lookup.
"""

from __future__ import annotations

import logging
import time
import uuid

from fastapi import UploadFile
from sqlalchemy.orm import Session

from backend.config import settings, to_bcp47
from backend.models import User
from backend.repositories import ai_request_log_repository
from backend.schemas.ask_janmitra import (
    AskJanMitraRequest,
    AskJanMitraResponse,
    AskVoiceResponse,
    Citation,
    ConversationTurn,
    LocationInfo,
)
from backend.services.answer_generation_service import AnswerGenerationService
from backend.services.complaint_agent import ComplaintAgent
from backend.services.embedding_provider import SentenceTransformerEmbeddingProvider
from backend.services.evidence_service import SavedFile, validate_and_write
from backend.services.location_extractor import LocationExtractor, RagGazetteer
from backend.services.location_resolver import LocationResolver
from backend.services.observability import tracing
from backend.services.orchestration.graph import build_graph, run_graph
from backend.services.orchestration.nodes import GraphDeps, RequestContext
from backend.services.orchestration.state import GraphState
from backend.services.rag_retriever import RagRetriever
from backend.services.sarvam_client import AIServiceError, SarvamClient
from backend.services.stt_service import transcribe_chunks
from backend.services.vector_store import ChromaVectorStore
from backend.services.vision_service import VisionService, VisionServiceError

logger = logging.getLogger(__name__)

_LANGUAGE_NAMES = {code: info["name"] for code, info in settings.SUPPORTED_LANGUAGES.items()}


class AskJanMitraService:
    """Constructor-injected, matching this codebase's existing service pattern (e.g.
    TranslationService's injected SarvamClient) — every dependency can be swapped for a test
    double, so tests never make a real network call or need the real 1.5MB embeddings index."""

    def __init__(
        self,
        vector_store: object | None = None,
        embedding_provider: object | None = None,
        location_extractor: LocationExtractor | None = None,
        answer_service: AnswerGenerationService | None = None,
        top_k: int | None = None,
        relevance_threshold: float | None = None,
        complaint_agent: ComplaintAgent | None = None,
        location_resolver: LocationResolver | None = None,
        vision_service: VisionService | None = None,
        sarvam_client: SarvamClient | None = None,
    ) -> None:
        self._vector_store = vector_store or self._load_default_store()
        self._embedding_provider = embedding_provider or self._load_default_embedding_provider()
        self._retriever = RagRetriever(
            self._vector_store,
            self._embedding_provider,
            top_k=top_k if top_k is not None else settings.RAG_TOP_K,
            relevance_threshold=relevance_threshold if relevance_threshold is not None else settings.RAG_EMBEDDING_RELEVANCE_THRESHOLD,
        )
        self._location_extractor = location_extractor or self._build_default_extractor()
        self._answer_service = answer_service or AnswerGenerationService()
        self._complaint_agent = complaint_agent or ComplaintAgent()
        self._location_resolver = location_resolver or LocationResolver()
        # Lazily loaded (see VisionService's own docstring) -- constructing this is cheap, the
        # real ~1.9B-param model only loads on the first attached image, matching this class's
        # existing "never pay startup cost for an optional AI feature" pattern (see
        # _load_default_embedding_provider's docstring for the same reasoning).
        self._vision_service = vision_service or VisionService()
        # Shared for both STT (voice-assistant input) and TTS (voice-assistant output) -- one
        # Sarvam client, matching how ComplaintAgent already owns its own single SarvamClient
        # instance for the same two purposes (STT there; translation here for TTS as well).
        self._sarvam_client = sarvam_client or SarvamClient()

        self._deps = GraphDeps(
            retriever=self._retriever,
            location_extractor=self._location_extractor,
            answer_service=self._answer_service,
            complaint_agent=self._complaint_agent,
            location_resolver=self._location_resolver,
        )
        self._graph = build_graph()

    @staticmethod
    def _load_default_store() -> ChromaVectorStore:
        store = ChromaVectorStore(settings.CHROMA_PERSIST_DIR, settings.CHROMA_COLLECTION_NAME)
        try:
            store.load()
        except Exception as exc:
            # Matches this codebase's "never crash the whole app over an optional AI feature"
            # philosophy (see e.g. SarvamClient's __init__ warning-not-raising on a missing API
            # key) — Ask JanMitra will report RAG-unavailable per-request rather than the app
            # failing to start if the Chroma collection hasn't been built yet (see §33's
            # empty/missing-store test coverage).
            logger.warning("Chroma vector store could not be loaded: %s", exc)
        return store

    @staticmethod
    def _load_default_embedding_provider() -> SentenceTransformerEmbeddingProvider:
        # Deliberately NOT eagerly loaded here (SentenceTransformerEmbeddingProvider's model load
        # is itself lazy, see that class) -- constructing AskJanMitraService must stay cheap and
        # never fail just because the embedding model hasn't been downloaded/cached yet; the
        # first real query pays that cost once, not every app startup.
        return SentenceTransformerEmbeddingProvider()

    @staticmethod
    def _build_default_extractor() -> LocationExtractor:
        gazetteer = RagGazetteer(settings.RAG_DATA_DIR / "chunks" / "chunks.json")
        return LocationExtractor(gazetteer)

    def ask(self, db: Session, user: User, request: AskJanMitraRequest) -> AskJanMitraResponse:
        """Builds the initial graph state from the request, runs the LangGraph orchestrator, and
        translates the final state back into `AskJanMitraResponse`. See
        `backend/services/orchestration/graph.py` for the actual routing/flow logic — this method
        is deliberately thin.

        Also records one `AiRequestLog` row per call (see backend/repositories/
        ai_request_log_repository.py) — the Admin "AI Monitoring" dashboard's data source — on
        both the success and failure path. This is separate from (and does not depend on)
        LangSmith tracing: `langsmith_trace_id` is stored alongside purely as a pointer for the
        dashboard's optional "View Trace" link; the metrics themselves always come from this row,
        never from LangSmith, so the dashboard keeps working even when LangSmith doesn't (see
        docs/ask_janmitra_langsmith_observability.md).
        """
        ctx = RequestContext(
            db=db,
            user=user,
            latitude=request.latitude,
            longitude=request.longitude,
            location_text=request.location_text,
        )
        initial_state = self._build_initial_state(
            question=request.question,
            language=request.language,
            conversation_history=request.conversation_history,
            input_mode="TEXT",
        )
        return self._run(db, ctx, initial_state, request.language)

    def ask_with_image(
        self,
        db: Session,
        user: User,
        *,
        question: str,
        language: str,
        latitude: float | None,
        longitude: float | None,
        location_text: str | None,
        conversation_history: list[ConversationTurn],
        image: UploadFile,
    ) -> AskJanMitraResponse:
        """Same pipeline as `ask()`, plus an attached image. Validates and saves the image to
        disk via the same `evidence_service.validate_and_write()` every other photo upload in
        this app already uses (see backend/services/evidence_service.py) -- no second
        image-storage system -- then captions it via `VisionService` and threads both the saved
        file and the caption into the graph run (see orchestration/nodes.py's
        input_processing_node/complaint_flow_node for how each is used).

        Captioning is best-effort: a `VisionServiceError` (model unavailable, decode failure) is
        logged and swallowed, not raised -- an image that fails to caption still gets attached to
        a complaint as real evidence, it just doesn't enrich the text (matches this codebase's
        "never crash over an optional AI feature" pattern, e.g. SentenceTransformerEmbeddingProvider/
        ChromaVectorStore's own load-failure handling above).
        """
        saved, image_description = self._process_image(image)

        ctx = RequestContext(
            db=db,
            user=user,
            latitude=latitude,
            longitude=longitude,
            location_text=location_text,
            image_saved=saved,
        )
        initial_state = self._build_initial_state(
            question=question,
            language=language,
            conversation_history=conversation_history,
            input_mode="IMAGE",
            has_image=True,
            image_description=image_description,
        )
        return self._run(db, ctx, initial_state, language)

    def ask_voice(
        self,
        db: Session,
        user: User,
        *,
        audio_segments: list[bytes],
        language: str,
        latitude: float | None,
        longitude: float | None,
        location_text: str | None,
        conversation_history: list[ConversationTurn],
        image: UploadFile | None = None,
    ) -> AskVoiceResponse:
        """Voice-to-voice: transcribes the citizen's spoken turn via the same chunked-STT
        pipeline `ComplaintAgent`'s voice-complaint flow already uses (see
        `stt_service.transcribe_chunks`), runs it through the exact same graph every other entry
        point uses, then synthesizes the AI's text answer into real spoken audio via Sarvam TTS.
        An optional attached image is accepted too (combined voice+image turns) -- validated and
        captioned exactly like `ask_with_image()`, via the same shared `_process_image()` helper.

        STT failure (every audio chunk unusable) is NOT swallowed -- there is no text to answer
        at all, so `AIServiceError` propagates as a real error for the route to surface honestly
        (never a fabricated/empty answer). TTS failure IS best-effort: a synthesis failure is
        logged and swallowed, not raised -- the citizen still gets the real text answer with
        `audio_base64=None` (never fake/placeholder audio) rather than the whole turn failing.
        """
        if not audio_segments:
            raise ValueError("At least one audio segment is required.")

        bcp47 = to_bcp47(language)
        question = transcribe_chunks(self._sarvam_client, audio_segments, bcp47)

        saved, image_description = self._process_image(image)
        has_image = saved is not None

        ctx = RequestContext(
            db=db,
            user=user,
            latitude=latitude,
            longitude=longitude,
            location_text=location_text,
            image_saved=saved,
        )
        initial_state = self._build_initial_state(
            question=question,
            language=language,
            conversation_history=conversation_history,
            input_mode="VOICE_ASSISTANT",
            has_image=has_image,
            image_description=image_description,
        )
        base_response = self._run(db, ctx, initial_state, language)

        audio_base64: str | None = None
        try:
            audio_base64 = self._sarvam_client.synthesize_speech(base_response.answer, bcp47)
        except AIServiceError as exc:
            logger.warning("Ask JanMitra voice flow: TTS failed, returning text-only: %s", exc)

        return AskVoiceResponse(**base_response.model_dump(), question=question, audio_base64=audio_base64)

    def _process_image(self, image: UploadFile | None) -> tuple[SavedFile | None, str | None]:
        """Shared by `ask_with_image()`/`ask_voice()`: validates+saves an optional attached image
        (via the same `evidence_service.validate_and_write()` every photo upload in this app
        already uses) and captions it best-effort via `VisionService`. Returns `(None, None)` if
        no image was actually attached (an empty/filename-less `UploadFile` counts as none, same
        as every other optional-photo endpoint in this codebase, e.g. routes/complaints.py's
        `photo`/`photos` handling)."""
        if image is None or not image.filename:
            return None, None

        # validate_and_write() consumes image.file via .read() -- read our own copy first (for
        # VisionService, which needs the raw bytes) and rewind before handing it off, so the save
        # step still sees the full file.
        image_bytes = image.file.read()
        image.file.seek(0)
        saved = validate_and_write(image)

        image_description: str | None = None
        try:
            image_description = self._vision_service.describe_image(image_bytes)
        except VisionServiceError as exc:
            logger.warning("Ask JanMitra: captioning failed, continuing without a description: %s", exc)

        return saved, image_description

    @staticmethod
    def _build_initial_state(
        *,
        question: str,
        language: str,
        conversation_history: list[ConversationTurn],
        input_mode: str,
        has_image: bool = False,
        image_description: str | None = None,
    ) -> GraphState:
        state: GraphState = {
            "user_message": question,
            "original_language": language,
            "input_type": "text",
            "conversation_history": [{"role": t.role, "content": t.content} for t in conversation_history],
            "input_mode": input_mode,
        }
        if has_image:
            state["has_image"] = True
            if image_description:
                state["image_description"] = image_description
        return state

    def _run(
        self,
        db: Session,
        ctx: RequestContext,
        initial_state: GraphState,
        language: str,
    ) -> AskJanMitraResponse:
        """Shared tail end of `ask()`/`ask_with_image()`: run the graph, record the AiRequestLog
        row, translate the final state into `AskJanMitraResponse`. Extracted so every Ask JanMitra
        entry point invokes the exact same `run_graph()` call and logs identically -- no parallel
        pipeline per input mode."""
        trace_id = uuid.uuid4()
        start = time.perf_counter()

        try:
            final_state = run_graph(
                self._graph, self._deps, ctx, initial_state, request_id=trace_id.hex[:12], trace_id=trace_id
            )
        except Exception as exc:
            latency_ms = (time.perf_counter() - start) * 1000
            # A mid-request exception may have left `db`'s transaction in a failed state (e.g. a
            # DB error inside a node) -- roll back before attempting to write the log row, so that
            # write doesn't itself fail because of the earlier one.
            db.rollback()
            ai_request_log_repository.record_ai_request(
                db,
                request_id=trace_id.hex[:12],
                langsmith_trace_id=str(trace_id) if tracing.is_enabled() else None,
                conversation_id=None,
                intent=None,
                service_category=None,
                routed_to="ERROR",
                success=False,
                error_type=type(exc).__name__,
                latency_ms=latency_ms,
            )
            # Checked on the failure path too -- a string of failing requests is exactly the
            # sustained-error-rate case admins most need alerted on. Best-effort, see that
            # function's own docstring; never masks the exception being re-raised below.
            ai_request_log_repository.check_and_fire_alerts(db)
            raise

        latency_ms = (time.perf_counter() - start) * 1000
        ai_request_log_repository.record_ai_request(
            db,
            request_id=trace_id.hex[:12],
            langsmith_trace_id=str(trace_id) if tracing.is_enabled() else None,
            conversation_id=final_state.get("conversation_id"),
            intent=final_state.get("intent"),
            service_category=final_state.get("service_category"),
            routed_to=final_state.get("routed_to", "NONE_OUT_OF_SCOPE"),
            success=True,
            error_type=None,
            latency_ms=latency_ms,
        )
        ai_request_log_repository.check_and_fire_alerts(db)

        location = None
        if "location_city" in final_state or "location_state" in final_state:
            location = LocationInfo(
                city=final_state.get("location_city"),
                state=final_state.get("location_state"),
                source=final_state.get("location_source", "none"),
                is_ambiguous=final_state.get("location_is_ambiguous", False),
                ambiguous_candidates=final_state.get("location_ambiguous_candidates", []),
            )

        sources = [Citation(**s) for s in final_state.get("sources", [])]

        return AskJanMitraResponse(
            answer=final_state.get("response_text", "I'm not sure how to help with that yet."),
            intent=final_state.get("intent", "TYPE_A_COMPLAINT"),
            service_category=final_state.get("service_category"),
            language=language,
            location=location,
            sources=sources,
            verification_status=final_state.get("verification_status"),
            follow_up_required=final_state.get("follow_up_required", False),
            follow_up_question=final_state.get("follow_up_question"),
            follow_up_options=final_state.get("follow_up_options", []),
            insufficient_knowledge=final_state.get("insufficient_knowledge", False),
            routed_to=final_state.get("routed_to", "NONE_OUT_OF_SCOPE"),
            answer_was_llm_generated=final_state.get("answer_was_llm_generated", False),
            complaint_id=final_state.get("complaint_id"),
        )

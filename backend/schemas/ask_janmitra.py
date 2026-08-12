"""Request/response contracts for POST /ask-janmitra.

Field names/shapes deliberately mirror frontend-react/src/lib/ragTypes.ts's existing
`SourceRecord`/`AskJanMitraResponse` interfaces (authored by a separate frontend session ahead of
this backend) wherever they overlap, so wiring the real API to that existing UI is closer to a
drop-in than a remap — see that file's own docstring, which states the same intent in reverse.
"""

from pydantic import BaseModel, Field

from backend.services.intent_classifier import QuestionIntent


class ConversationTurn(BaseModel):
    """One prior turn in a multi-turn Ask JanMitra exchange. The caller (frontend) resends the
    full history with each request — this API is stateless server-side (see
    docs/ask_janmitra_rag_architecture.md's "why no server-side conversation store" note), which
    keeps this phase's scope to the retrieval pipeline itself rather than also building session
    storage."""

    role: str  # "user" | "assistant"
    content: str


class AskJanMitraRequest(BaseModel):
    question: str = Field(min_length=1)
    language: str = "en"
    latitude: float | None = None
    longitude: float | None = None
    # Explicit location the citizen typed/picked (e.g. via a "select city" clarification step) —
    # distinct from a location mentioned inline in `question`'s own text; checked first since
    # it's the most deliberate signal (see ask_janmitra_service.py's location-resolution order).
    location_text: str | None = None
    conversation_history: list[ConversationTurn] = Field(default_factory=list)


class Citation(BaseModel):
    """Matches frontend-react/src/lib/ragTypes.ts's SourceRecord exactly (see that file) — built
    directly from Chunk metadata, never from LLM output (see answer_generation_service.py's
    docstring for why)."""

    source_id: str
    source_title: str
    source_organization: str
    source_url: str | None
    source_type: str
    verification_status: str
    geographic_scope: str


class LocationInfo(BaseModel):
    city: str | None = None
    state: str | None = None
    source: str = "none"  # "text" | "gps" | "none"
    is_ambiguous: bool = False
    ambiguous_candidates: list[str] = Field(default_factory=list)


class AskJanMitraResponse(BaseModel):
    answer: str
    intent: QuestionIntent
    service_category: str | None = None
    language: str
    location: LocationInfo | None = None
    sources: list[Citation] = Field(default_factory=list)
    # Overall status label for the answer: "VERIFIED" if every source is VERIFIED, "SYNTHETIC" if
    # every source is SYNTHETIC, "MIXED" if both appear, None if there are no sources at all
    # (insufficient-knowledge / status-routed / out-of-scope responses).
    verification_status: str | None = None
    follow_up_required: bool = False
    follow_up_question: str | None = None
    follow_up_options: list[str] = Field(default_factory=list)
    insufficient_knowledge: bool = False
    # Which subsystem actually produced `answer` — lets the frontend (and tests) verify TYPE_C
    # never got its answer from RAG, per this phase's hard requirement.
    routed_to: str = "RAG"  # "RAG" | "COMPLAINT_CREATED" | "COMPLAINT_STATUS_API" |
                            # "NONE_OUT_OF_SCOPE" | "NONE_CLARIFICATION_NEEDED"
    answer_was_llm_generated: bool = False
    # Set only when routed_to == "COMPLAINT_CREATED" (see the LangGraph orchestrator's
    # complaint_flow node, backend/services/orchestration/nodes.py) — a TYPE_A complaint-shaped
    # message with enough information (service category + location) now files a real complaint
    # through the existing ComplaintAgent/assign_next_worker services, the same way the dedicated
    # complaint form does, and reports the resulting ID back here so the frontend/citizen can
    # look it up (e.g. via the existing GET /complaints or a future TYPE_C status question).
    complaint_id: int | None = None


class AskVoiceResponse(AskJanMitraResponse):
    """Response for POST /ask-janmitra/voice (the voice-to-voice assistant) — everything
    AskJanMitraResponse already has, plus the citizen's own transcribed speech (so the overlay
    can show a real "you said" transcript, not a guess) and the AI's spoken reply as real
    synthesized audio (see backend/services/sarvam_client.py's synthesize_speech()).
    `audio_base64` is None only when TTS itself failed (a real, honest failure, never faked) —
    the frontend still has `answer` as text to fall back to display in that case."""

    question: str
    audio_base64: str | None = None
    audio_format: str = "wav"

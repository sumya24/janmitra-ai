"""Shared graph state for the Ask JanMitra LangGraph orchestrator.

One `GraphState` flows through every node (see `graph.py`). It is a `TypedDict` (not a Pydantic
model) because LangGraph's `StateGraph` natively merges partial dict returns from each node into
the running state -- a Pydantic model would need an extra reducer step for no real benefit here,
since nothing in this state needs field-level validation (each field is already validated at its
*source* -- `AskJanMitraRequest`, `ClassificationResult`, `LocationResolution` -- before it's
copied into the graph state as a plain value).

`total=False`: every field is optional. A field simply isn't present until the node that
produces it has run -- e.g. `intent` doesn't exist until `intent_node` runs, `sources` doesn't
exist unless the `rag_flow` node ran. Nodes read with `state.get(...)`, never `state[...]`, so a
not-yet-populated field never raises.

Deliberately excludes fields the spec's example list mentions but that this codebase doesn't
actually need as separate state: `user_id` (available via the `config["configurable"]["user"]`
side-channel, since it never changes mid-graph and every node that needs it can read it from
there -- see graph.py's `GraphDeps`), `location_confidence` (redundant with
`location_is_ambiguous` + `location_city`/`location_state` being present or not -- a fourth field
encoding the same information would just be another way for state to drift out of sync with
itself), `error` as a single field is kept, but no per-node error fields -- one place for "the
graph could not complete normally" is enough at this scope.
"""

from __future__ import annotations

from typing import Any, TypedDict


class ConversationTurnDict(TypedDict):
    role: str
    content: str


class GraphState(TypedDict, total=False):
    # --- input (input_processing_node) ---
    user_message: str
    original_language: str
    normalized_message: str
    input_type: str  # "text" | "voice" -- both already arrive as text by the time the graph
                      # runs (STT happens upstream, see backend/services/complaint_agent.py's
                      # _transcribe_chunks); this field records which one it was, for logging.
    conversation_id: str | None
    conversation_history: list[ConversationTurnDict]

    # --- image (optional; captioning happens upstream in ask_janmitra_service.py, same
    #     precedent as input_type's STT-happens-upstream note above) ---
    has_image: bool  # an image was attached at all, regardless of whether captioning succeeded
    image_description: str | None  # VisionService's best-effort caption, or None
    input_mode: str  # "TEXT" | "STT" | "VOICE_ASSISTANT" | "IMAGE" -- LangSmith metadata only

    # --- classification (intent_node) ---
    intent: str  # QuestionIntent.value, e.g. "TYPE_A_COMPLAINT"
    service_category: str | None  # ServiceCategory.value, or None
    out_of_scope_service: str | None  # "ELECTRICITY" | "NEW_SERVICE_CONNECTION" | None
    requests_new_connection: bool  # see intent_classifier.ClassificationResult's own docstring

    # --- location (location_node) ---
    location_city: str | None
    location_state: str | None
    location_source: str  # "text" | "gps" | "conversation_history" | "none"
    location_is_ambiguous: bool
    location_ambiguous_candidates: list[str]

    # --- routing (route_intent conditional edge) ---
    route: str  # "complaint" | "rag" | "status" | "clarification" | "out_of_scope"
    needs_clarification: bool
    clarification_reason: str | None  # "category" | "location" | "status_number" | None

    # --- RAG flow results ---
    retrieved_chunks: list[dict[str, Any]]  # serialized ScoredChunk-shaped dicts
    sources: list[dict[str, Any]]  # serialized Citation-shaped dicts
    verification_status: str | None
    insufficient_knowledge: bool
    answer_was_llm_generated: bool

    # --- complaint flow results ---
    complaint_id: int | None
    complaint_data: dict[str, Any] | None
    worker_assignment: dict[str, Any] | None

    # --- status flow results ---
    # (status text is written straight to response_text -- no dedicated field needed beyond that)

    # --- final response (every flow node sets these; response_generation_node only logs) ---
    response_text: str
    response_language: str
    follow_up_required: bool
    follow_up_question: str | None
    follow_up_options: list[str]
    routed_to: str  # "RAG" | "COMPLAINT_CREATED" | "COMPLAINT_STATUS_API" | "NONE_OUT_OF_SCOPE" |
                     # "NONE_CLARIFICATION_NEEDED"
    error: str | None

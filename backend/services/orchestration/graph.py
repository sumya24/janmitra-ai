"""Builds and runs the Ask JanMitra LangGraph orchestrator.

```
START
  |
  v
input_processing  (normalize whitespace; preserve original message/language)
  |
  v
language_detection  (identity -- language already validated by the route)
  |
  +-- image attached, no text at all ----------------> clarification_flow (never guess intent
  |                                                     from an image alone -- see nodes.py's
  |                                                     input_processing_node/
  |                                                     clarification_flow_node)
  v
intent_classification  (wraps intent_classifier.classify() -- unchanged)
  |
  +-- TYPE_C_STATUS --------------------------------> status_flow
  +-- out_of_scope_service set ---------------------> out_of_scope_flow
  +-- else ------------------------------------------> location_resolution
                                                             |
                                                             v
                              +----------------------------------------------------------+
                              |  TYPE_A_COMPLAINT -----------------------> complaint_flow  |
                              |  TYPE_B_SERVICE_INFO, location OK -------> rag_flow         |
                              |  TYPE_B_SERVICE_INFO, location missing --> clarification_flow|
                              +----------------------------------------------------------+
                                                             |
                             complaint_flow --(needs_clarification)--> clarification_flow
                             complaint_flow --(else)-------------------> response_generation
                                     |
                                     v
        rag_flow / status_flow / clarification_flow / out_of_scope_flow / complaint_flow
                                     |
                                     v
                            response_generation
                                     |
                                     v
                                    END
```

This graph REPLACES `AskJanMitraService`'s previous single-method if/else routing
(`_answer_knowledge_question`/`_answer_status_question`) with the same logic decomposed into
LangGraph nodes -- every node calls an existing service (see `nodes.py`'s module docstring); no
routing/business logic was duplicated to build this. `AskJanMitraService.ask()` (see
`ask_janmitra_service.py`) is now a thin adapter: build the initial `GraphState`, invoke this
compiled graph, translate the final state back into `AskJanMitraResponse` -- the public API
contract is unchanged (see `docs/ask_janmitra_orchestration.md`).
"""

from __future__ import annotations

import logging
import time
import uuid
from typing import Any

from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from backend.services.intent_classifier import QuestionIntent
from backend.services.observability import tracing
from backend.services.orchestration.nodes import (
    GraphDeps,
    RequestContext,
    clarification_flow_node,
    complaint_flow_node,
    input_processing_node,
    intent_node,
    language_node,
    location_node,
    out_of_scope_flow_node,
    rag_flow_node,
    response_generation_node,
    status_flow_node,
)
from backend.services.orchestration.state import GraphState

logger = logging.getLogger(__name__)


def _route_after_language(state: GraphState) -> str:
    """Only new branch this phase: an image with no text at all skips intent classification
    entirely and goes straight to a real clarification question (see nodes.py's
    input_processing_node/clarification_flow_node) -- there is no text to classify, and
    classifying an empty string would just be a disguised guess. Every existing text/Mic-1
    request has no `clarification_reason` set at this point, so this is purely additive -- the
    default branch is the exact same unconditional edge this replaces."""
    if state.get("clarification_reason") == "image_no_text":
        return "clarification_flow"
    return "intent_classification"


def _route_after_intent(state: GraphState) -> str:
    if state.get("intent") == QuestionIntent.TYPE_C_STATUS.value:
        return "status_flow"
    if state.get("out_of_scope_service"):
        return "out_of_scope_flow"
    return "location_resolution"


def _route_after_location(state: GraphState) -> str:
    intent = state.get("intent")
    if intent == QuestionIntent.TYPE_A_COMPLAINT.value:
        # complaint_flow decides for itself whether it still needs a category or a location
        # (see nodes.py's complaint_flow_node) -- it always runs first so a complaint that
        # already has both proceeds straight to creation without a wasted clarification hop.
        return "complaint_flow"
    # TYPE_B_SERVICE_INFO (RAG-answerable) -- gated by the same location-clarification check the
    # pre-graph AskJanMitraService applied before ever calling the retriever.
    if state.get("location_is_ambiguous") or (state.get("location_city") is None and state.get("location_state") is None):
        return "clarification_flow"
    return "rag_flow"


def _route_after_complaint(state: GraphState) -> str:
    if state.get("needs_clarification"):
        return "clarification_flow"
    return "response_generation"


def build_graph() -> CompiledStateGraph:
    """Builds and compiles the graph once -- cheap (pure graph-structure construction, no model
    loading or I/O), called once per `AskJanMitraService` instance and reused for every request,
    exactly like that service already does for `RagRetriever`/`ChromaVectorStore`."""
    graph = StateGraph(GraphState)

    graph.add_node("input_processing", input_processing_node)
    graph.add_node("language_detection", language_node)
    graph.add_node("intent_classification", intent_node)
    graph.add_node("location_resolution", location_node)
    graph.add_node("complaint_flow", complaint_flow_node)
    graph.add_node("rag_flow", rag_flow_node)
    graph.add_node("status_flow", status_flow_node)
    graph.add_node("clarification_flow", clarification_flow_node)
    graph.add_node("out_of_scope_flow", out_of_scope_flow_node)
    graph.add_node("response_generation", response_generation_node)

    graph.add_edge(START, "input_processing")
    graph.add_edge("input_processing", "language_detection")
    graph.add_conditional_edges(
        "language_detection",
        _route_after_language,
        {"intent_classification": "intent_classification", "clarification_flow": "clarification_flow"},
    )

    graph.add_conditional_edges(
        "intent_classification",
        _route_after_intent,
        {"status_flow": "status_flow", "out_of_scope_flow": "out_of_scope_flow", "location_resolution": "location_resolution"},
    )
    graph.add_conditional_edges(
        "location_resolution",
        _route_after_location,
        {"complaint_flow": "complaint_flow", "rag_flow": "rag_flow", "clarification_flow": "clarification_flow"},
    )
    graph.add_conditional_edges(
        "complaint_flow",
        _route_after_complaint,
        {"clarification_flow": "clarification_flow", "response_generation": "response_generation"},
    )

    graph.add_edge("rag_flow", "response_generation")
    graph.add_edge("status_flow", "response_generation")
    graph.add_edge("clarification_flow", "response_generation")
    graph.add_edge("out_of_scope_flow", "response_generation")
    graph.add_edge("response_generation", END)

    return graph.compile()


def run_graph(
    compiled_graph: CompiledStateGraph,
    deps: GraphDeps,
    ctx: RequestContext,
    initial_state: GraphState,
    request_id: str | None = None,
    trace_id: uuid.UUID | None = None,
) -> GraphState:
    """Runs one full graph invocation and returns the final merged state.

    Observability (per the spec's §24): streams node-by-node (`stream_mode="updates"`) rather
    than a single opaque `.invoke()`, logging each node's name and latency as it completes, plus
    one summary line at the end with the resolved intent/route/total latency. Never logs message
    text, location coordinates, or any request field beyond the request ID/intent/route/timings --
    see the per-node log line below, which deliberately logs only `list(update.keys())` (field
    NAMES a node changed, not their values) for exactly this reason.

    LangSmith tracing (see backend/services/observability/tracing.py): starts one root span for
    the whole graph run, made available to nodes as `config["configurable"]["trace_root"]` so
    `rag_flow_node`/`complaint_flow_node` (see nodes.py) can attach their own child spans for RAG
    retrieval, LLM answer generation, and complaint creation. Deliberately NOT the same thing as
    the per-node text log above -- that log already existed and stays exactly as it was; this
    only ADDS curated, redacted LangSmith spans alongside it (see tracing.py's module docstring
    for why this is manual/curated rather than automatic full-state tracing). A no-op with zero
    behavior change whenever tracing is disabled/unconfigured -- `tracing.start_root_run()`
    returns `None` in that case, and every other `tracing.*` call treats `None` as a no-op.
    """
    request_id = request_id or uuid.uuid4().hex[:12]
    root_run = tracing.start_root_run(
        "ask_janmitra_graph",
        run_id=trace_id,
        inputs={
            "question": tracing.redact_text(initial_state.get("user_message")),
            "language": initial_state.get("original_language"),
            "input_type": initial_state.get("input_type"),
            "conversation_turns": len(initial_state.get("conversation_history") or []),
        },
        metadata={
            "request_id": request_id,
            # Categorical signals only -- never the raw image/caption itself (see
            # docs/ask_janmitra_langsmith_observability.md's redaction policy).
            "input_mode": initial_state.get("input_mode", "TEXT"),
            "has_image": bool(initial_state.get("has_image")),
        },
        tags=["ask_janmitra"],
    )
    config = {"configurable": {"deps": deps, "ctx": ctx, "trace_root": root_run}}

    merged: dict[str, Any] = dict(initial_state)
    start = time.perf_counter()
    try:
        for step in compiled_graph.stream(initial_state, config=config, stream_mode="updates"):
            for node_name, update in step.items():
                # LangGraph's "updates" stream can include bookkeeping keys (e.g. "__interrupt__")
                # whose value isn't a state-update dict -- only merge/log genuine node updates.
                if not isinstance(update, dict):
                    continue
                node_elapsed_ms = (time.perf_counter() - start) * 1000
                logger.info(
                    "ask_janmitra_graph request_id=%s node=%s fields_updated=%s elapsed_ms=%.1f",
                    request_id, node_name, list(update.keys()), node_elapsed_ms,
                )
                merged.update(update)
    except Exception as exc:
        logger.exception("ask_janmitra_graph request_id=%s failed unexpectedly", request_id)
        tracing.end_run(root_run, error=str(exc))
        raise

    total_ms = (time.perf_counter() - start) * 1000
    logger.info(
        "ask_janmitra_graph request_id=%s complete intent=%s routed_to=%s total_ms=%.1f",
        request_id, merged.get("intent"), merged.get("routed_to"), total_ms,
    )
    tracing.end_run(
        root_run,
        outputs={
            "intent": merged.get("intent"),
            "routed_to": merged.get("routed_to"),
            "service_category": merged.get("service_category"),
            "verification_status": merged.get("verification_status"),
            "insufficient_knowledge": merged.get("insufficient_knowledge"),
            "follow_up_required": merged.get("follow_up_required"),
            "complaint_id": merged.get("complaint_id"),
            "answer": tracing.redact_text(merged.get("response_text")),
            "total_ms": round(total_ms, 1),
        },
    )

    # A knowledge-base-gap review queue (see tracing.py's enqueue_for_review()): every trace
    # where the pipeline genuinely couldn't answer -- either it ran out of relevant knowledge, or
    # the classifier detected a known-but-unsupported service -- is a real citizen question the
    # KB should potentially cover. Routed here, not scored/blocked in any way; a no-op whenever
    # tracing is disabled.
    if merged.get("insufficient_knowledge") or merged.get("routed_to") == "NONE_OUT_OF_SCOPE":
        tracing.enqueue_for_review(root_run, reason=merged.get("routed_to") or "insufficient_knowledge")

    return merged  # type: ignore[return-value]

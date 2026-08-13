"""LangGraph node functions for the Ask JanMitra orchestrator.

Every node is a thin adapter: it reads what it needs from `GraphState`/the injected deps and
calls into an EXISTING service (`classify()`, `LocationExtractor`, `LocationResolver`,
`RagRetriever`, `AnswerGenerationService`, `ComplaintAgent`, `assign_next_worker`, `Complaint` DB
queries) -- no node contains business logic that didn't already exist somewhere in this codebase
before this phase. See `graph.py`'s module docstring for the full node/edge list, and
`docs/ask_janmitra_orchestration.md` for the architectural reasoning.

**Deliberate behavior change, confirmed with the user before implementing (see git history /
session transcript)**: previously, a TYPE_A_COMPLAINT-classified question ("Street light not
working near me") was answered by RAG, the same as a TYPE_B question -- Ask JanMitra could not
yet act on a complaint-shaped message, only describe relevant civic-service information about it.
This phase closes that gap: TYPE_A_COMPLAINT now routes to `complaint_flow_node`, which files a
real complaint via the existing `ComplaintAgent`/`assign_next_worker` services and returns a
complaint ID -- matching this phase's own spec, whose worked complaint-flow example ("Streetlight
near my home is not working.") is itself a TYPE_A-shaped sentence. TYPE_B_SERVICE_INFO ("who do I
contact for X", "how do I apply for Y") still routes to `rag_flow_node`, unchanged. This
necessarily changes several previously-tested TYPE_A cases -- see tests/test_ask_janmitra.py's
updated assertions and the final report for the full list.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import Any

from langchain_core.runnables import RunnableConfig
from sqlalchemy.orm import Session

from backend.models import User
from backend.repositories import complaint_repository, evidence_repository
from backend.schemas.rag_knowledge import ServiceCategory
from backend.services.answer_generation_service import AnswerGenerationService
from backend.services.assignment_service import assign_next_worker
from backend.services.complaint_agent import ComplaintAgent
from backend.services.evidence_service import SavedFile
from backend.services.intent_classifier import QuestionIntent, classify
from backend.services.location_extractor import LocationExtractor, LocationResolution
from backend.services.location_resolver import LocationResolver
from backend.services.observability import tracing
from backend.services.orchestration.state import GraphState
from backend.services.rag_retriever import RagRetriever
from backend.services.sarvam_client import AIServiceError
from backend.services.translation_service import TranslationService

logger = logging.getLogger(__name__)

_COMPLAINT_NUMBER_PATTERN = re.compile(r"(?:complaint|complain)\s*#?\s*(\d+)|#(\d+)|\b(\d{2,6})\b", re.IGNORECASE)

_OUT_OF_SCOPE_TOPIC_NAMES = {
    "ELECTRICITY": "electricity connection/meter",
    # Only reached for a bare "new connection" with no utility named -- "new water connection"/
    # "new sewerage connection" now have real coverage for some cities and route to RAG instead
    # (see intent_classifier.py's _NEW_CONNECTION_KEYWORDS docstring for why this list shrank).
    "NEW_SERVICE_CONNECTION": "new utility connections without a specified service (please say which service — e.g. water or sewerage connection)",
}

# Human-readable category clarification options -- matches the spec's own §13 wording. The value
# the user actually picks/types comes back as a normal next-turn message and is reclassified by
# the existing `classify()` the same as any other input; these labels are chosen to contain the
# same keywords `_CATEGORY_KEYWORDS` (intent_classifier.py) already matches, so a straight
# pass-through of the picked label continues to classify correctly with zero new code.
_CATEGORY_CLARIFICATION_OPTIONS = ["Garbage", "Water", "Road", "Streetlight", "Other"]
_LOCATION_CLARIFICATION_OPTIONS = ["Use current location", "Enter location", "Select location"]


@dataclass
class GraphDeps:
    """Static, shared-across-requests dependencies -- built once (expensive: the embedding model
    load, the Chroma collection open) and reused for every graph invocation, matching this
    codebase's existing "construct once in the service constructor" pattern (see
    ask_janmitra_service.py, which this class's fields were lifted from unchanged)."""

    retriever: RagRetriever
    location_extractor: LocationExtractor
    answer_service: AnswerGenerationService
    complaint_agent: ComplaintAgent
    location_resolver: LocationResolver
    # Optional (defaults to None, matching RequestContext.image_saved's own optional-field
    # precedent below) so existing tests that build GraphDeps with only the five fields above
    # keep working unchanged. When unset, `_localize()` just returns text untranslated -- the
    # same honest degradation as a translation call that fails.
    translation_service: TranslationService | None = None


@dataclass
class RequestContext:
    """Per-request context: everything that legitimately differs between two invocations of the
    same compiled graph. Passed via LangGraph's `config["configurable"]`, not folded into
    `GraphState` -- this is request plumbing (a DB session, the authenticated user, raw GPS
    coordinates), not conversation data that the graph itself reasons about or that should be
    logged/serialized as part of the graph's own state."""

    db: Session
    user: User
    latitude: float | None
    longitude: float | None
    location_text: str | None
    # Set only by ask_janmitra_service.ask_with_image() -- the already-validated-and-written
    # image file (see backend/services/evidence_service.py), if one was attached. Request
    # plumbing, not conversation data the graph reasons about (same rationale as latitude/
    # longitude above) -- complaint_flow_node reads this to attach real complaint evidence.
    image_saved: SavedFile | None = None


def _deps(config: RunnableConfig) -> GraphDeps:
    return config["configurable"]["deps"]


def _ctx(config: RunnableConfig) -> RequestContext:
    return config["configurable"]["ctx"]


def _localize(text: str, state: GraphState, config: RunnableConfig) -> str:
    """Translates a hardcoded English response (clarification questions, out-of-scope notices)
    into the citizen's `response_language`, via the existing `TranslationService`/`SarvamClient`
    (same service `complaint_agent.py`/`ask_janmitra_service.py` already use for worker-facing
    complaint translation -- no new client, no new logic). Unlike `rag_flow_node`'s answers,
    these strings never went through an LLM prompted to answer in the target language in the
    first place, so without this they stay in English even in a fully Marathi/Hindi/etc.
    conversation -- confirmed via a live Marathi voice-assistant session where the transcript and
    every UI label were in Marathi but this exact clarification text came back in English.

    English is a no-op (skips a needless network call on the common case). A translation failure
    degrades to the original English text -- same honest fallback `AnswerGenerationService` and
    the voice flow's own TTS step already use -- never blocks the response."""
    language = state.get("response_language") or "en"
    if language == "en":
        return text
    deps = _deps(config)
    if deps.translation_service is None:
        return text
    try:
        return deps.translation_service.to_language(text, language)
    except AIServiceError as exc:
        logger.warning("Ask JanMitra: localizing response text to %s failed, keeping English: %s", language, exc)
        return text


def _trace_root(config: RunnableConfig):
    """The current request's LangSmith root span (see graph.py's `run_graph()`), or `None` if
    tracing is disabled/unavailable. `.get(...)`, not `[...]` -- unlike `deps`/`ctx`, this key is
    optional plumbing a direct unit test of a node function is not required to provide (every
    `tracing.*` call already treats `None` as a no-op, see that module)."""
    return config["configurable"].get("trace_root")


# ------------------------------------------------------------------
# input_processing / language -- both effectively identity nodes; kept as separate graph nodes
# (rather than folded together) because the spec calls them out as distinct architectural stages,
# and because a real normalization/detection step has exactly one place to be added later without
# touching any other node.
# ------------------------------------------------------------------


def input_processing_node(state: GraphState, config: RunnableConfig) -> dict[str, Any]:
    """Normalizes whitespace only -- never alters wording/meaning. The original message is kept
    untouched in `user_message`; `normalized_message` is a separate field so nothing downstream
    that wants the citizen's exact original words (e.g. `Complaint.original_text`) ever reads the
    normalized copy by accident.

    Also where an attached image (captioned upstream, see state.py's `image_description`) is
    folded into the text every downstream node already consumes -- unless there's no text at all,
    in which case this sets `clarification_reason="image_no_text"` so the graph routes straight to
    a real clarification question instead of guessing intent from an image alone (see
    `_route_after_language` in graph.py and `clarification_flow_node` below)."""
    message = state.get("user_message", "").strip()
    has_image = bool(state.get("has_image"))
    image_description = state.get("image_description")

    if not message and has_image:
        return {
            "normalized_message": "",
            "input_type": state.get("input_type") or "text",
            "clarification_reason": "image_no_text",
        }

    if image_description:
        message = f"{message}\n\n[Attached photo shows: {image_description}]"

    return {
        "normalized_message": message,
        "input_type": state.get("input_type") or "text",
    }


def language_node(state: GraphState, config: RunnableConfig) -> dict[str, Any]:
    """Identity node: `original_language` already arrives validated (`AskJanMitraRequest.language`
    is checked against `settings.SUPPORTED_LANGUAGES` by the route before the graph ever runs) --
    re-detecting it would just re-derive a value the caller already gave us authoritatively. Real
    translation/normalization already happens inside the flow nodes that need it (e.g.
    `AnswerGenerationService` receives the target language name directly) -- this node's only job
    is to seed `response_language` from the request so every downstream node can read one
    consistent field name."""
    return {"response_language": state.get("original_language") or "en"}


# ------------------------------------------------------------------
# intent
# ------------------------------------------------------------------


def intent_node(state: GraphState, config: RunnableConfig) -> dict[str, Any]:
    """Wraps the EXISTING `intent_classifier.classify()` -- no reimplementation, no new keyword
    lists. See this module's docstring for how the `QuestionIntent` values map onto this graph's
    routes."""
    text = state.get("normalized_message") or state.get("user_message", "")
    result = classify(text)
    intent = result.intent
    ctx = config.get("configurable", {}).get("ctx")
    has_gps = bool(ctx and ctx.latitude is not None and ctx.longitude is not None)
    if intent == QuestionIntent.UNCLEAR and (state.get("conversation_history") or state.get("has_image") or has_gps):
        # classify() is deliberately a pure, single-turn, text-only function (see its own
        # docstring) -- it has no way to see that a short reply like "Streetlight." or "Use my
        # current location." carries real meaning from the conversation so far, that a vague
        # caption-only message has an attached photo behind it, or that "Use my current
        # location." arrived with real GPS coordinates attached. Zero keyword signal in THIS
        # turn's text alone isn't the same as the request being genuinely unclear in these three
        # cases, so this falls back to TYPE_A_COMPLAINT -- handing off to machinery that already
        # exists for exactly this: complaint_flow_node's _recover_category_from_history for the
        # conversation case, clarification_flow_node's _image_context_prefix for the image case,
        # and location_node's existing GPS-resolution path for the coordinates case. A real
        # regression this exact override was added for: without it, EVERY reply in a multi-turn
        # complaint conversation whose own text has no keyword ("Use my current location.") broke
        # out of the flow entirely (caught by
        # test_multi_turn_complaint_filing_category_then_location), and a GPS-only "use current
        # location" message never reached location_resolution at all (caught by
        # test_scenario_5_use_current_location_resolves_via_gps). A genuinely fresh, standalone,
        # no-context, no-image, no-GPS message (e.g. "What is my name?") has none of these and
        # correctly stays UNCLEAR.
        intent = QuestionIntent.TYPE_A_COMPLAINT
    return {
        "intent": intent.value,
        "service_category": result.service_category.value if result.service_category else None,
        "out_of_scope_service": result.out_of_scope_service,
        "requests_new_connection": result.requests_new_connection,
    }


# ------------------------------------------------------------------
# location
# ------------------------------------------------------------------


def _resolve_location(state: GraphState, config: RunnableConfig) -> LocationResolution:
    """Same priority order as the pre-graph `AskJanMitraService._resolve_location()` this
    replaces, plus one addition: explicit `location_text` > location named in the message text >
    GPS > a location mentioned in `conversation_history` > the citizen's own registered ward.
    Reuses `LocationExtractor` exactly as before -- this function only sequences the existing
    calls, it performs no resolution itself.

    The last step (citizen's own ward) is a deliberate final fallback, not a new resolution
    method: a citizen's `ward` free text (set once at signup, see models.User.ward) almost always
    contains their city name (e.g. "Ward 22 -- Kothrud, Pune"), so running it through the same
    `resolve_from_text` used for message text/conversation history lets a logged-in citizen who
    doesn't name a place get an answer scoped to where they actually live, instead of an
    unnecessary "no information for this area" when every earlier signal was silent. Workers and
    admins are unaffected in practice (their `ward` is an operational area string, not used here
    any differently) -- this only changes behavior for QUESTION_RAG intents where nothing else
    resolved a location."""
    deps = _deps(config)
    ctx = _ctx(config)
    extractor = deps.location_extractor

    if ctx.location_text:
        resolved = extractor.resolve_from_text(ctx.location_text)
        if resolved.city or resolved.state or resolved.is_ambiguous:
            return resolved

    text = state.get("normalized_message") or state.get("user_message", "")
    resolved = extractor.resolve_from_text(text)
    if resolved.city or resolved.state or resolved.is_ambiguous:
        return resolved

    if ctx.latitude is not None and ctx.longitude is not None:
        resolved = extractor.resolve_from_coordinates(ctx.latitude, ctx.longitude)
        if resolved.city or resolved.state:
            return resolved

    for turn in reversed(state.get("conversation_history", [])):
        if turn.get("role") != "user":
            continue
        resolved = extractor.resolve_from_text(turn.get("content", ""))
        if resolved.city or resolved.state or resolved.is_ambiguous:
            resolved.source = "conversation_history"
            return resolved

    if ctx.user.ward:
        resolved = extractor.resolve_from_text(ctx.user.ward)
        if resolved.city or resolved.state or resolved.is_ambiguous:
            resolved.source = "citizen_home_ward"
            return resolved

    return LocationResolution(source="none")


def location_node(state: GraphState, config: RunnableConfig) -> dict[str, Any]:
    resolution = _resolve_location(state, config)
    return {
        "location_city": resolution.city,
        "location_state": resolution.state,
        "location_source": resolution.source,
        "location_is_ambiguous": resolution.is_ambiguous,
        "location_ambiguous_candidates": resolution.ambiguous_candidates,
    }


# ------------------------------------------------------------------
# out_of_scope flow
# ------------------------------------------------------------------


def out_of_scope_flow_node(state: GraphState, config: RunnableConfig) -> dict[str, Any]:
    """A known-but-unsupported service (electricity, new-connection) was detected by the
    classifier -- an honest "don't have that" response, never a fabricated answer or a fallback
    to an unrelated RAG record (see intent_classifier.py's module docstring for the exact false
    positive this prevents)."""
    topic = _OUT_OF_SCOPE_TOPIC_NAMES.get(
        state.get("out_of_scope_service") or "", (state.get("out_of_scope_service") or "").lower()
    )
    text = (
        f"I don't currently have reliable information for {topic} in JanMitra. "
        f"This may be available in a future update."
    )
    return {
        "response_text": _localize(text, state, config),
        "routed_to": "NONE_OUT_OF_SCOPE",
        "insufficient_knowledge": True,
        "sources": [],
    }


# ------------------------------------------------------------------
# capabilities flow -- "what can you do?" is a real, in-domain, fully-answerable question about
# JanMitra's own scope (see QuestionIntent.CAPABILITIES's docstring). A static, accurate answer,
# not a RAG lookup -- what JanMitra supports is a fixed fact about this deployment, not something
# to search a knowledge base for.
# ------------------------------------------------------------------


def capabilities_flow_node(state: GraphState, config: RunnableConfig) -> dict[str, Any]:
    text = (
        "I can help you report a civic issue (garbage or waste, water or drainage, roads or "
        "potholes, and streetlights), check the status of a complaint you've already filed, or "
        "answer questions about local civic services. What would you like help with?"
    )
    return {
        "response_text": _localize(text, state, config),
        "routed_to": "NONE_CAPABILITIES",
        "sources": [],
    }


# ------------------------------------------------------------------
# unclear flow -- genuinely no signal matched (see QuestionIntent.UNCLEAR's own docstring for the
# bug this replaces: every unrecognized question, regardless of what it actually asked, used to
# get the exact same complaint-shaped "what issue would you like to report?" clarification).
# ------------------------------------------------------------------


def unclear_flow_node(state: GraphState, config: RunnableConfig) -> dict[str, Any]:
    question = (
        "I'm not sure I understood that. I can help you report a civic issue (garbage, water, "
        "roads, or streetlights), check the status of a complaint, or answer questions about "
        "local civic services. What would you like help with?"
    )
    return {
        "response_text": _localize(question, state, config),
        # Genuinely ends in a question the citizen is expected to answer next -- same
        # follow_up_required semantics clarification_flow_node already uses, not a one-shot
        # answer like rag_flow_node's.
        "follow_up_required": True,
        "follow_up_question": question,
        "routed_to": "NONE_UNCLEAR",
        "insufficient_knowledge": True,
        "sources": [],
    }


# ------------------------------------------------------------------
# clarification flow
# ------------------------------------------------------------------


def _image_context_prefix(state: GraphState) -> str:
    """A short, honest acknowledgment of an attached image, prepended to whichever clarification
    question actually fires while an image is attached. Without this, a citizen who attached a
    photo but got routed to the category/location/location_ambiguous reason (because they also
    typed text, so the `image_no_text` case below never triggers) would see a generic question
    with no sign the photo was looked at at all -- even though it genuinely was (VisionService
    already ran, see ask_janmitra_service.py's `_process_image()`). Real, not padding: says
    honestly that the read wasn't clear if captioning failed, never invents a description."""
    if not state.get("has_image"):
        return ""
    description = state.get("image_description")
    if description:
        return f"I can see the photo you attached (it looks like: {description}). "
    return "I can see you've attached a photo, though I couldn't get a clear read on it. "


def clarification_flow_node(state: GraphState, config: RunnableConfig) -> dict[str, Any]:
    """Builds a follow-up question. `clarification_reason` (set by whichever flow node routed
    here) decides which question to ask -- category (complaint flow, missing service type),
    location (complaint or RAG flow, missing city/area), or an ambiguous multi-city state match
    (RAG flow, e.g. "Punjab" matches both Mohali and Patiala)."""
    reason = state.get("clarification_reason")

    if reason == "image_no_text":
        # An image with no text at all -- never guess whether it's a complaint or an information
        # request (see this module's docstring's image-handling note). image_description may be
        # None if captioning failed -- the question still works either way, it's just less
        # specific (matches VisionService's own best-effort-only contract).
        description = state.get("image_description")
        prompt = (
            f"I can see the photo you attached (it looks like: {description}). "
            if description
            else "I can see you've attached a photo. "
        )
        question = prompt + "Would you like to report an issue, or would you like information about what's shown?"
        return {
            "response_text": _localize(question, state, config),
            "follow_up_required": True,
            "follow_up_question": question,
            "follow_up_options": ["Report an issue", "What is this?"],
            "routed_to": "NONE_CLARIFICATION_NEEDED",
            "sources": [],
        }

    if reason == "category":
        question = "What issue would you like to report?"
        return {
            "response_text": _localize(_image_context_prefix(state) + question, state, config),
            "follow_up_required": True,
            "follow_up_question": question,
            "follow_up_options": _CATEGORY_CLARIFICATION_OPTIONS,
            "routed_to": "NONE_CLARIFICATION_NEEDED",
            "sources": [],
        }

    if reason == "location_ambiguous":
        candidates = state.get("location_ambiguous_candidates", [])
        question = f"Which city are you asking about — {', '.join(candidates)}?"
        return {
            "response_text": _localize(_image_context_prefix(state) + question, state, config),
            "follow_up_required": True,
            "follow_up_question": "Which city/area are you in?",
            "follow_up_options": candidates,
            "routed_to": "NONE_CLARIFICATION_NEEDED",
            "sources": [],
        }

    # Default: location missing entirely.
    question = "What is the location? This helps me give you the correct local information."
    return {
        "response_text": _localize(_image_context_prefix(state) + question, state, config),
        "follow_up_required": True,
        "follow_up_question": "What is the location?",
        "follow_up_options": _LOCATION_CLARIFICATION_OPTIONS,
        "routed_to": "NONE_CLARIFICATION_NEEDED",
        "sources": [],
    }


# ------------------------------------------------------------------
# status flow -- NEVER touches RAG, matches the pre-graph service's hardest rule exactly
# ------------------------------------------------------------------


def status_flow_node(state: GraphState, config: RunnableConfig) -> dict[str, Any]:
    ctx = _ctx(config)
    db, user = ctx.db, ctx.user
    text = state.get("normalized_message") or state.get("user_message", "")

    match = _COMPLAINT_NUMBER_PATTERN.search(text)
    if not match:
        question = "Which complaint would you like the status of? Please give the complaint number, or check your complaints list."
        return {
            "response_text": _localize(question, state, config),
            "follow_up_required": True,
            "follow_up_question": "What is your complaint number?",
            "routed_to": "COMPLAINT_STATUS_API",
            "sources": [],
        }

    complaint_id = int(next(g for g in match.groups() if g))
    complaint = complaint_repository.get_complaint_by_id(db, complaint_id)
    if complaint is None or (user.role == "citizen" and complaint.citizen_id != str(user.id)):
        # Same message for "doesn't exist" and "not yours" -- never leaks which IDs exist to a
        # citizen who isn't the owner.
        return {
            "response_text": _localize(f"I couldn't find complaint #{complaint_id} for your account.", state, config),
            "routed_to": "COMPLAINT_STATUS_API",
            "sources": [],
        }

    status_text = {
        "pending": "still pending — not yet assigned to a worker.",
        "assigned": "assigned to a worker, awaiting their acceptance.",
        "accepted": "accepted and being worked on.",
        "resolved": "marked resolved.",
    }.get(complaint.status, complaint.status)
    return {
        "response_text": _localize(f"Complaint #{complaint.id} is {status_text}", state, config),
        "routed_to": "COMPLAINT_STATUS_API",
        "sources": [],
    }


# ------------------------------------------------------------------
# RAG flow -- unchanged retrieval pipeline (see docs/ask_janmitra_rag_architecture.md), this node
# only orchestrates the existing RagRetriever + AnswerGenerationService calls.
# ------------------------------------------------------------------

_LANGUAGE_NAMES = {"en": "English", "hi": "Hindi", "mr": "Marathi", "or": "Odia", "gu": "Gujarati", "bn": "Bengali"}


def rag_flow_node(state: GraphState, config: RunnableConfig) -> dict[str, Any]:
    deps = _deps(config)
    root = _trace_root(config)
    text = state.get("normalized_message") or state.get("user_message", "")
    category = state.get("service_category")
    category_enum = ServiceCategory(category) if category else None
    language_name = _LANGUAGE_NAMES.get(state.get("original_language") or "en", "English")

    retrieval_span = tracing.start_child_run(
        root, "rag_retrieval", "retriever",
        inputs={
            "query": tracing.redact_text(text),
            "service_category": category,
            "city": state.get("location_city"),
            "state": state.get("location_state"),
        },
    )
    outcome = deps.retriever.retrieve(text, category_enum, state.get("location_city"), state.get("location_state"))
    tracing.end_run(
        retrieval_span,
        outputs={
            "result_count": len(outcome.results),
            "insufficient_knowledge": outcome.insufficient_knowledge,
            "reason": outcome.reason,
            "top_score": outcome.results[0].score if outcome.results else None,
        },
    )

    # Post-retrieval topic filter for "new connection" questions -- measured, real reason this
    # exists (KB-expansion phase): once real new-water/sewerage-connection records existed for
    # Mohali/Patiala/Odisha, the classifier's out-of-scope short-circuit for those phrases was
    # removed (see intent_classifier.py's _NEW_CONNECTION_KEYWORDS docstring) so they could reach
    # RAG. But a city with NO new-connection record (e.g. Nagpur, synthetic-only) still passed the
    # category+location filter and the relevance threshold on its generic leak/repair chunk --
    # topically similar enough ("water supply") to score above threshold despite answering a
    # completely different question. Verified directly before this fix: Nagpur's synthetic
    # WATER_SUPPLY_DRAINAGE_NAGPUR leak-repair chunk scored 0.849 against "new water connection in
    # Nagpur", comfortably above the 0.79 relevance threshold. This filter closes that gap without
    # touching RagRetriever itself (its filtering/threshold/rerank logic is unchanged) -- it only
    # narrows the already-retrieved candidates to ones actually about a new connection (service_id
    # prefix "WATER_NEW_", the naming convention every new-connection record uses), and reports
    # insufficient_knowledge honestly if none qualify, exactly like any other unanswerable case.
    if state.get("requests_new_connection") and outcome.results:
        new_connection_results = [r for r in outcome.results if r.metadata.get("service_id", "").startswith("WATER_NEW_")]
        if new_connection_results:
            outcome.results = new_connection_results
        else:
            outcome.results = []
            outcome.insufficient_knowledge = True
            outcome.reason = "No new-connection record exists for this location -- only existing-issue repair/complaint records are covered here."

    if outcome.insufficient_knowledge or not outcome.results:
        reason = outcome.reason or "No information available."
        place = state.get("location_city") or state.get("location_state") or "this area"
        text = f"I don't currently have reliable information for this in {place}. ({reason})"
        return {
            "response_text": _localize(text, state, config),
            "routed_to": "RAG",
            "insufficient_knowledge": True,
            "sources": [],
        }

    context_chunks = [r.metadata["content"] for r in outcome.results]
    answer_span = tracing.start_child_run(
        root, "answer_generation", "llm",
        inputs={"question": tracing.redact_text(text), "language": language_name, "context_chunk_count": len(context_chunks)},
    )
    answer_text, was_llm_generated = deps.answer_service.generate(text, context_chunks, language_name)
    tracing.end_run(
        answer_span,
        outputs={"answer_was_llm_generated": was_llm_generated, "answer": tracing.redact_text(answer_text)},
    )

    sources = []
    seen: set[str] = set()
    for r in outcome.results:
        source_id = r.metadata.get("source_id")
        if source_id in seen:
            continue
        seen.add(source_id)
        sources.append({
            "source_id": source_id,
            "source_title": r.metadata.get("source_title"),
            "source_organization": r.metadata.get("source_organization"),
            "source_url": r.metadata.get("source_url"),
            "source_type": r.metadata.get("source_type"),
            "verification_status": r.metadata.get("verification_status"),
            "geographic_scope": r.metadata.get("geographic_scope"),
        })

    statuses = {s["verification_status"] for s in sources}
    overall_status = "MIXED" if len(statuses) > 1 else next(iter(statuses), None)

    return {
        "response_text": answer_text,
        "sources": sources,
        "verification_status": overall_status,
        "routed_to": "RAG",
        "answer_was_llm_generated": was_llm_generated,
    }


# ------------------------------------------------------------------
# complaint flow -- NEW this phase: actually files a complaint via the existing
# ComplaintAgent/assign_next_worker services (see this module's docstring for the confirmed
# behavior-change rationale).
# ------------------------------------------------------------------


def _recover_category_from_history(state: GraphState) -> ServiceCategory | None:
    """If the CURRENT message doesn't name a service category (e.g. a bare "Streetlight." reply
    already does, via the existing classifier -- but a later turn like "Use my current location."
    does not), scan prior USER turns, most recent first, through the same `classify()` used by
    `intent_node` for one that did. Mirrors the location node's own conversation_history fallback
    (`_resolve_location` above) -- same idiom, applied to category instead of place, so a
    multi-turn complaint conversation doesn't lose the issue type the citizen already gave."""
    for turn in reversed(state.get("conversation_history", [])):
        if turn.get("role") != "user":
            continue
        result = classify(turn.get("content", ""))
        if result.service_category is not None:
            return result.service_category
    return None


def complaint_flow_node(state: GraphState, config: RunnableConfig) -> dict[str, Any]:
    deps = _deps(config)
    ctx = _ctx(config)
    root = _trace_root(config)
    text = state.get("normalized_message") or state.get("user_message", "")

    category_value = state.get("service_category")
    category = ServiceCategory(category_value) if category_value else _recover_category_from_history(state)

    if category is None:
        return {
            "needs_clarification": True,
            "clarification_reason": "category",
            "route": "clarification",
        }

    if state.get("location_is_ambiguous"):
        return {
            "needs_clarification": True,
            "clarification_reason": "location_ambiguous",
            "route": "clarification",
        }

    if state.get("location_city") is None and state.get("location_state") is None:
        return {
            "needs_clarification": True,
            "clarification_reason": "location",
            "route": "clarification",
        }

    # Everything required is present -- file the complaint via the EXISTING complaint pipeline.
    # An attached image (see ctx.image_saved, set by ask_janmitra_service.ask_with_image()) is
    # threaded through exactly like the dedicated complaint form does: the legacy single-photo
    # column for backward compatibility, and a real ComplaintEvidence row via the EXISTING
    # evidence_repository -- no second image-storage system (see this module's docstring).
    creation_span = tracing.start_child_run(
        root, "complaint_creation", "tool",
        inputs={"service_category": category.value, "language": state.get("original_language")},
    )
    try:
        complaint = deps.complaint_agent.create_complaint(
            db=ctx.db,
            citizen_id=str(ctx.user.id),
            language_code=state.get("original_language") or "en",
            text=text,
            audio_chunks=None,
            photo_path=ctx.image_saved.filename if ctx.image_saved else None,
        )
    except (ValueError, AIServiceError) as exc:
        logger.warning("Ask JanMitra complaint_flow: complaint creation failed: %s", exc)
        tracing.end_run(creation_span, error=str(exc))
        text = "I couldn't file that complaint right now. Please try again, or use the complaint form directly."
        return {
            "response_text": _localize(text, state, config),
            "routed_to": "COMPLAINT_CREATION_FAILED",
            "error": str(exc),
            "sources": [],
        }
    tracing.end_run(creation_span, outputs={"complaint_id": complaint.id, "status": complaint.status})

    if ctx.image_saved is not None:
        # The file is already validated and written to disk (see ask_with_image()) -- this only
        # records the ComplaintEvidence row, the exact same primitive _save_evidence_files()
        # itself calls, so this doesn't re-validate/re-write a file that's already safely saved.
        evidence_repository.add_evidence(
            ctx.db,
            complaint_id=complaint.id,
            update_id=None,
            uploaded_by=ctx.user.id,
            uploader_role="citizen",
            file_name=ctx.image_saved.original_name,
            file_path=ctx.image_saved.filename,
            file_type=ctx.image_saved.content_type,
            file_size=ctx.image_saved.size,
            stage="CITIZEN_COMPLAINT",
        )

    # Resolve ward-level location for assignment -- deliberately the app's OWN LocationResolver
    # (state/district/ULB/WARD hierarchy, what assignment_service.py actually keys on), not the
    # RAG gazetteer's city/state (that's only ever used for RAG's metadata filtering, a separate,
    # coarser-grained concern -- see location_extractor.py's module docstring). Same calls
    # routes/complaints.py already makes; nothing new invented here.
    #
    # `complaint.ward` (plain free text) is set directly from the citizen's own explicit location
    # text FIRST, exactly like routes/complaints.py's `ward` form field -- this is what
    # assign_next_worker's fallback path matches on (`User.ward == complaint.ward`, see
    # assignment_service.py's module docstring on the two ward-matching paths). Structured
    # resolution (`resolve_ward_by_text`, which only understands this app's own "Ward N —
    # Locality, City" convention) is attempted ADDITIONALLY, as a richer, more precise match when
    # the text happens to be in that exact format -- it augments, never replaces, the plain-text
    # ward already set.
    try:
        resolved_ward = None
        if ctx.location_text:
            resolved_ward = deps.location_resolver.resolve_ward_by_text(ctx.db, ctx.location_text)

        if resolved_ward is not None:
            chain = deps.location_resolver.location_chain_for_ward(ctx.db, resolved_ward)
            complaint_repository.save_complaint_location(ctx.db, complaint, ward=resolved_ward.name, location_chain=chain)
        elif ctx.location_text:
            complaint_repository.save_complaint_location(ctx.db, complaint, ward=ctx.location_text.strip())
        elif ctx.latitude is not None and ctx.longitude is not None:
            resolved = deps.location_resolver.resolve_coordinates(ctx.latitude, ctx.longitude)
            ids = deps.location_resolver.normalize_location(ctx.db, resolved)
            complaint_repository.save_complaint_location(
                ctx.db, complaint, location_chain=ids, formatted_address=resolved.formatted_address
            )
    except Exception:
        # Best-effort, exactly like routes/complaints.py's own equivalent try/except -- a
        # location-resolution failure must never fail complaint creation, which has already
        # succeeded and committed above.
        logger.exception("Ask JanMitra complaint_flow: ward resolution failed for complaint %s; continuing unassigned by ward.", complaint.id)

    assign_next_worker(ctx.db, complaint)
    ctx.db.refresh(complaint)

    worker_assignment = None
    if complaint.assigned_worker_id is not None:
        worker = complaint_repository.get_user_by_id(ctx.db, complaint.assigned_worker_id)
        worker_assignment = {
            "worker_id": complaint.assigned_worker_id,
            "worker_name": worker.full_name if worker else None,
            "status": complaint.status,
        }

    category_label = category.value.replace("_", " ").title()
    if complaint.status == "assigned":
        response_text = f"Your {category_label} complaint has been filed (complaint #{complaint.id}) and assigned to a worker."
    else:
        response_text = f"Your {category_label} complaint has been filed (complaint #{complaint.id}). It's pending assignment to a worker in your area."

    return {
        "response_text": _localize(response_text, state, config),
        "routed_to": "COMPLAINT_CREATED",
        "complaint_id": complaint.id,
        "complaint_data": {"id": complaint.id, "status": complaint.status, "ward": complaint.ward},
        "worker_assignment": worker_assignment,
        "sources": [],
        # Write back even when recovered from conversation_history (e.g. category came from an
        # earlier turn, not the current message) -- otherwise the API response's own
        # `service_category` field would silently disagree with what was actually just filed,
        # even though the complaint itself was created correctly using the recovered value.
        "service_category": category.value,
    }


# ------------------------------------------------------------------
# response_generation -- terminal node. Every flow node above already sets response_text/
# routed_to/etc.; this node's job is purely observability (see graph.py) plus filling in any
# field a flow node didn't set, so AskJanMitraResponse construction never has to guess.
# ------------------------------------------------------------------


def response_generation_node(state: GraphState, config: RunnableConfig) -> dict[str, Any]:
    defaults: dict[str, Any] = {}
    if "response_text" not in state:
        defaults["response_text"] = _localize("I'm not sure how to help with that yet.", state, config)
    if "sources" not in state:
        defaults["sources"] = []
    if "routed_to" not in state:
        defaults["routed_to"] = "NONE_OUT_OF_SCOPE"
    return defaults

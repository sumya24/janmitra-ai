"""Tests for the LangGraph orchestration layer itself (backend/services/orchestration/) --
node-level unit tests and routing-function unit tests that don't need the full HTTP/RAG stack,
plus the multi-turn clarification scenario from the spec's own worked example. End-to-end
routing/RAG/complaint-creation behavior through the real `/ask-janmitra` endpoint is covered by
tests/test_ask_janmitra.py; this file focuses on the graph's own structure and state handling.
"""

from __future__ import annotations

from unittest.mock import Mock

import backend.routes.ask_janmitra as ask_janmitra_module
from backend.models import Complaint
from backend.schemas.ask_janmitra import ConversationTurn
from backend.services.intent_classifier import QuestionIntent
from backend.services.orchestration.graph import (
    _route_after_complaint,
    _route_after_intent,
    _route_after_location,
    build_graph,
)
from backend.services.orchestration.nodes import (
    input_processing_node,
    intent_node,
    language_node,
)
from tests.test_ask_janmitra import _ask, _install_real_service, _real_ask_janmitra_service


# --- node-level unit tests (no DB/config needed for these three) ---


def test_input_processing_node_normalizes_whitespace_preserves_original():
    state = {"user_message": "  Street light not working.  "}
    update = input_processing_node(state, config={})
    assert update["normalized_message"] == "Street light not working."
    assert update["input_type"] == "text"
    assert state["user_message"] == "  Street light not working.  "  # untouched


def test_input_processing_node_preserves_explicit_input_type():
    update = input_processing_node({"user_message": "x", "input_type": "voice"}, config={})
    assert update["input_type"] == "voice"


def test_language_node_is_identity_seeds_response_language():
    update = language_node({"original_language": "hi"}, config={})
    assert update["response_language"] == "hi"


def test_language_node_defaults_to_english_when_missing():
    update = language_node({}, config={})
    assert update["response_language"] == "en"


def test_intent_node_wraps_existing_classifier():
    update = intent_node({"normalized_message": "I need a new electricity connection"}, config={})
    assert update["out_of_scope_service"] == "ELECTRICITY"
    assert update["service_category"] is None


# --- routing function unit tests (pure functions, no I/O) ---


def test_route_after_intent_status_first():
    assert _route_after_intent({"intent": QuestionIntent.TYPE_C_STATUS.value}) == "status_flow"


def test_route_after_intent_out_of_scope_before_location():
    state = {"intent": QuestionIntent.TYPE_B_SERVICE_INFO.value, "out_of_scope_service": "ELECTRICITY"}
    assert _route_after_intent(state) == "out_of_scope_flow"


def test_route_after_intent_else_goes_to_location():
    state = {"intent": QuestionIntent.TYPE_A_COMPLAINT.value, "out_of_scope_service": None}
    assert _route_after_intent(state) == "location_resolution"


def test_route_after_intent_capabilities():
    assert _route_after_intent({"intent": QuestionIntent.CAPABILITIES.value, "out_of_scope_service": None}) == "capabilities_flow"


def test_route_after_intent_unclear():
    assert _route_after_intent({"intent": QuestionIntent.UNCLEAR.value, "out_of_scope_service": None}) == "unclear_flow"


def test_route_after_location_type_a_always_goes_to_complaint_flow():
    """Even with no location resolved yet -- complaint_flow decides for itself whether it still
    needs category/location (see nodes.py's complaint_flow_node)."""
    state = {"intent": QuestionIntent.TYPE_A_COMPLAINT.value, "location_city": None, "location_state": None}
    assert _route_after_location(state) == "complaint_flow"


def test_route_after_location_type_b_missing_location_asks_clarification():
    state = {"intent": QuestionIntent.TYPE_B_SERVICE_INFO.value, "location_city": None, "location_state": None}
    assert _route_after_location(state) == "clarification_flow"


def test_route_after_location_type_b_ambiguous_asks_clarification():
    state = {"intent": QuestionIntent.TYPE_B_SERVICE_INFO.value, "location_is_ambiguous": True}
    assert _route_after_location(state) == "clarification_flow"


def test_route_after_location_type_b_with_location_goes_to_rag():
    state = {"intent": QuestionIntent.TYPE_B_SERVICE_INFO.value, "location_city": "Mumbai", "location_state": "Maharashtra"}
    assert _route_after_location(state) == "rag_flow"


def test_route_after_complaint_needs_clarification():
    assert _route_after_complaint({"needs_clarification": True}) == "clarification_flow"


def test_route_after_complaint_done():
    assert _route_after_complaint({"needs_clarification": False}) == "response_generation"


# --- graph structure ---


def test_graph_compiles_with_expected_nodes():
    graph = build_graph()
    nodes = set(graph.get_graph().nodes.keys())
    expected = {
        "__start__", "input_processing", "language_detection", "intent_classification",
        "location_resolution", "complaint_flow", "rag_flow", "status_flow",
        "clarification_flow", "out_of_scope_flow", "capabilities_flow", "unclear_flow",
        "response_generation", "__end__",
    }
    assert nodes == expected


# --- multi-turn clarification: the exact scenario from the orchestration spec's own example ---


def test_multi_turn_complaint_filing_category_then_location(client, monkeypatch, db_session, make_citizen, make_worker):
    """TURN 1: 'I want to file a complaint.' -> asks for the issue.
    TURN 2: 'Streetlight.' -> asks for the location (category now known from THIS turn alone).
    TURN 3: 'Use my current location.' (+ explicit location_text, standing in for a real
    'use current location' UI action) -> resolves, category recovered from TURN 2's history,
    complaint filed. Verifies the graph "does not lose previously collected information"
    (spec's own wording) across three separate, stateless HTTP requests -- exactly how this
    codebase's multi-turn conversation support already worked pre-graph (client-resent
    conversation_history, see docs/ask_janmitra_rag_architecture.md's "why no server-side
    conversation store" note) -- the graph adds routing/state structure on top, not a new
    persistence mechanism.
    """
    _install_real_service(monkeypatch)
    make_worker(phone="9100099002", ward="Mohali")
    token, _ = make_citizen(phone="9100000030")

    turn1 = _ask(client, token, "I want to file a complaint.")
    assert turn1.status_code == 200
    body1 = turn1.json()
    assert body1["follow_up_required"] is True
    assert body1["follow_up_question"] == "What issue would you like to report?"
    assert body1.get("complaint_id") is None

    history = [
        ConversationTurn(role="user", content="I want to file a complaint.").model_dump(),
        ConversationTurn(role="assistant", content=body1["answer"]).model_dump(),
    ]
    turn2 = _ask(client, token, "Streetlight.", conversation_history=history)
    assert turn2.status_code == 200
    body2 = turn2.json()
    assert body2["follow_up_required"] is True
    assert body2["follow_up_question"] == "What is the location?"
    assert body2.get("complaint_id") is None

    history.append(ConversationTurn(role="user", content="Streetlight.").model_dump())
    history.append(ConversationTurn(role="assistant", content=body2["answer"]).model_dump())
    turn3 = _ask(client, token, "Use my current location.", conversation_history=history, location_text="Mohali")
    assert turn3.status_code == 200
    body3 = turn3.json()
    assert body3["routed_to"] == "COMPLAINT_CREATED"
    assert body3["service_category"] == "STREETLIGHTS"  # recovered from turn 2, not lost
    assert body3["complaint_id"] is not None

    db = db_session()
    complaint = db.query(Complaint).filter(Complaint.id == body3["complaint_id"]).first()
    assert complaint is not None
    assert complaint.ward == "Mohali"
    assert complaint.status == "assigned"
    db.close()


def test_category_recovered_across_turns_even_when_current_turn_has_none():
    """Unit-level check of the exact carryover helper used by complaint_flow_node (see
    _recover_category_from_history in nodes.py) -- isolates the logic from the full HTTP path."""
    from backend.schemas.rag_knowledge import ServiceCategory
    from backend.services.orchestration.nodes import _recover_category_from_history

    state = {
        "conversation_history": [
            {"role": "user", "content": "I want to file a complaint."},
            {"role": "assistant", "content": "What issue would you like to report?"},
            {"role": "user", "content": "Streetlight."},
        ]
    }
    assert _recover_category_from_history(state) == ServiceCategory.STREETLIGHTS


def test_category_recovery_returns_none_when_history_has_no_category():
    from backend.services.orchestration.nodes import _recover_category_from_history

    state = {"conversation_history": [{"role": "user", "content": "I want to file a complaint."}]}
    assert _recover_category_from_history(state) is None


# --- error handling: a node exception must not silently produce a fabricated answer ---


def test_complaint_agent_failure_returns_honest_error_not_a_fake_complaint_id(client, monkeypatch, make_citizen):
    fake_answers = Mock()
    fake_answers.generate = lambda q, chunks, lang: ("x", False)

    class _RaisingComplaintAgent:
        def create_complaint(self, **kwargs):
            raise ValueError("simulated complaint-agent failure")

    service = _real_ask_janmitra_service(complaint_agent=_RaisingComplaintAgent())
    monkeypatch.setattr(ask_janmitra_module, "_service", service)

    token, _ = make_citizen(phone="9100000031")
    resp = _ask(client, token, "Street light not working in Mohali.", location_text="Mohali")
    assert resp.status_code == 200  # handled gracefully, not a 500
    body = resp.json()
    assert body["routed_to"] == "COMPLAINT_CREATION_FAILED"
    assert body.get("complaint_id") is None
    assert "couldn't file" in body["answer"].lower()

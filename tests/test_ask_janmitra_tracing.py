"""Integration-level tests for LangSmith tracing exercised through the real LangGraph
orchestrator (backend/services/orchestration/graph.py, nodes.py) and the real /ask-janmitra
endpoint (backend/services/ask_janmitra_service.py) -- as opposed to
tests/test_langsmith_tracing.py's isolated unit tests of the tracing module itself.

Covers (see the LangSmith integration task's own test-plan numbering):
  3. LangGraph trace creation (run_graph starts/ends one root span per request)
  4. RAG trace creation (rag_flow_node's retrieval/answer-generation child spans)
  5. Error tracing (a node exception still ends the root span, with `error` set, before re-raising)
  7. Application behavior when LangSmith is unavailable (the real HTTP pipeline keeps working
     even when every LangSmith call fails)

None of these tests need a real LangSmith account -- `tracing.start_root_run`/`start_child_run`/
`end_run` are monkeypatched directly (matching this module's "tracing must be invisible to
correctness" design -- see tracing.py's docstring), so what's actually verified is that graph.py/
nodes.py call them with the right shape at the right times, not LangSmith's own behavior.
"""

from __future__ import annotations

from unittest.mock import Mock

import pytest

import backend.services.orchestration.graph as graph_module
import backend.services.orchestration.nodes as nodes_module
from backend.services.location_extractor import LocationResolution
from backend.services.orchestration.graph import build_graph, run_graph
from backend.services.orchestration.nodes import GraphDeps, RequestContext
from tests.test_ask_janmitra import _ask, _install_real_service


class _FakeLocationExtractor:
    """Deterministic stand-in for LocationExtractor -- unlike a bare Mock(), attribute access on
    its return value doesn't itself produce truthy Mock objects that would confuse the graph's
    own `if resolved.city or ...` branching."""

    def resolve_from_text(self, text: str) -> LocationResolution:
        return LocationResolution(city="Mohali", state="Punjab", source="text", is_ambiguous=False)

    def resolve_from_coordinates(self, lat: float, lon: float) -> LocationResolution:
        return LocationResolution(source="none")


def _minimal_deps(**overrides) -> GraphDeps:
    kwargs = dict(
        retriever=Mock(),
        location_extractor=_FakeLocationExtractor(),
        answer_service=Mock(),
        complaint_agent=Mock(),
        location_resolver=Mock(),
    )
    kwargs.update(overrides)
    return GraphDeps(**kwargs)


def _minimal_ctx(**overrides) -> RequestContext:
    kwargs = dict(db=Mock(), user=Mock(id=1, role="citizen"), latitude=None, longitude=None, location_text=None)
    kwargs.update(overrides)
    return RequestContext(**kwargs)


# --- 3: LangGraph trace creation ---


def test_run_graph_starts_and_ends_one_root_span_per_request(monkeypatch):
    start_calls = []
    end_calls = []
    monkeypatch.setattr(graph_module.tracing, "start_root_run", lambda name, **kw: start_calls.append((name, kw)) or "FAKE_ROOT")
    monkeypatch.setattr(graph_module.tracing, "end_run", lambda run, **kw: end_calls.append((run, kw)))

    compiled = build_graph()
    initial_state = {
        "user_message": "I need a new electricity connection",
        "original_language": "en",
        "input_type": "text",
        "conversation_history": [],
    }
    final_state = run_graph(compiled, _minimal_deps(), _minimal_ctx(), initial_state)

    assert len(start_calls) == 1
    name, kwargs = start_calls[0]
    assert name == "ask_janmitra_graph"
    assert kwargs["inputs"]["question"] == "I need a new electricity connection"
    assert kwargs["inputs"]["language"] == "en"
    assert kwargs["tags"] == ["ask_janmitra"]

    assert len(end_calls) == 1
    run, end_kwargs = end_calls[0]
    assert run == "FAKE_ROOT"
    assert end_kwargs["outputs"]["routed_to"] == final_state["routed_to"] == "NONE_OUT_OF_SCOPE"
    assert "total_ms" in end_kwargs["outputs"]


def test_run_graph_passes_trace_root_to_nodes_via_config(monkeypatch):
    """The root span object returned by start_root_run must reach node functions through
    config["configurable"]["trace_root"] -- this is how rag_flow_node/complaint_flow_node create
    their own child spans (see nodes.py's _trace_root())."""
    sentinel_root = object()
    monkeypatch.setattr(graph_module.tracing, "start_root_run", lambda name, **kw: sentinel_root)
    monkeypatch.setattr(graph_module.tracing, "end_run", lambda run, **kw: None)

    seen_roots = []
    real_intent_node = nodes_module.intent_node

    def spying_intent_node(state, config):
        seen_roots.append(config["configurable"].get("trace_root"))
        return real_intent_node(state, config)

    monkeypatch.setattr(nodes_module, "intent_node", spying_intent_node)
    # graph.py imported intent_node by name at module load time -- patch its own reference too.
    monkeypatch.setattr(graph_module, "intent_node", spying_intent_node)

    compiled = build_graph()
    initial_state = {"user_message": "hello", "original_language": "en", "input_type": "text", "conversation_history": []}
    run_graph(compiled, _minimal_deps(), _minimal_ctx(), initial_state)

    assert seen_roots == [sentinel_root]


# --- 5: error tracing ---


def test_node_exception_ends_root_span_with_error_then_reraises(monkeypatch):
    end_calls = []
    monkeypatch.setattr(graph_module.tracing, "start_root_run", lambda name, **kw: "FAKE_ROOT")
    monkeypatch.setattr(graph_module.tracing, "end_run", lambda run, **kw: end_calls.append(kw))

    class _RaisingComplaintAgent:
        def create_complaint(self, **kwargs):
            raise RuntimeError("simulated complaint-agent crash")

    compiled = build_graph()
    deps = _minimal_deps(complaint_agent=_RaisingComplaintAgent())
    initial_state = {
        "user_message": "Street light not working in Mohali.",
        "original_language": "en",
        "input_type": "text",
        "conversation_history": [],
    }

    with pytest.raises(RuntimeError, match="simulated complaint-agent crash"):
        run_graph(compiled, deps, _minimal_ctx(), initial_state)

    assert len(end_calls) == 1
    assert end_calls[0]["error"] == "simulated complaint-agent crash"


def test_complaint_creation_span_records_error_without_crashing_the_graph(monkeypatch):
    """A ValueError/AIServiceError from complaint_agent is handled gracefully by
    complaint_flow_node itself (an honest "couldn't file that complaint" response, see
    nodes.py) -- the complaint_creation child span must record that error too, and the graph
    must still complete normally (not raise), matching that existing behavior."""
    span_errors = []

    def fake_start_child_run(parent, name, run_type="chain", **kw):
        return name

    def fake_end_run(run, **kw):
        if run == "complaint_creation" and "error" in kw:
            span_errors.append(kw["error"])

    monkeypatch.setattr(graph_module.tracing, "start_root_run", lambda name, **kw: "FAKE_ROOT")
    monkeypatch.setattr(graph_module.tracing, "end_run", fake_end_run)
    monkeypatch.setattr(nodes_module.tracing, "start_child_run", fake_start_child_run)
    monkeypatch.setattr(nodes_module.tracing, "end_run", fake_end_run)

    class _RaisingComplaintAgent:
        def create_complaint(self, **kwargs):
            from backend.services.sarvam_client import AIServiceError

            raise AIServiceError("simulated Sarvam failure")

    compiled = build_graph()
    deps = _minimal_deps(complaint_agent=_RaisingComplaintAgent())
    initial_state = {
        "user_message": "Street light not working in Mohali.",
        "original_language": "en",
        "input_type": "text",
        "conversation_history": [],
    }

    final_state = run_graph(compiled, deps, _minimal_ctx(), initial_state)  # must not raise

    assert final_state["routed_to"] == "COMPLAINT_CREATION_FAILED"
    assert span_errors == ["simulated Sarvam failure"]


# --- 4: RAG trace creation ---


def test_rag_flow_creates_retrieval_and_answer_generation_spans(client, monkeypatch, make_citizen):
    span_names = []
    monkeypatch.setattr(nodes_module.tracing, "start_child_run", lambda parent, name, run_type="chain", **kw: span_names.append(name) or name)
    monkeypatch.setattr(nodes_module.tracing, "end_run", lambda run, **kw: None)

    _install_real_service(monkeypatch)
    token, _ = make_citizen(phone="9100000098")
    resp = _ask(client, token, "What is the procedure to apply for a new water connection in Mohali?")

    assert resp.status_code == 200
    body = resp.json()
    assert body["insufficient_knowledge"] is False  # proven RAG-answerable query (see test_ask_janmitra.py)
    assert "rag_retrieval" in span_names
    assert "answer_generation" in span_names


def test_rag_retrieval_span_still_created_when_knowledge_is_insufficient(monkeypatch):
    """The retrieval span must exist even when nothing relevant was found -- that's exactly the
    kind of thing LangSmith tracing should make visible (see the integration task's requirement
    to trace "retrieval operations" generally, not only successful ones). Uses a fake retriever
    (rather than a real-but-obscure query against the live KB) so this doesn't depend on the KB's
    current contents to reliably produce a miss."""
    from backend.services.rag_retriever import RetrievalOutcome

    span_names = []
    monkeypatch.setattr(graph_module.tracing, "start_root_run", lambda name, **kw: "FAKE_ROOT")
    monkeypatch.setattr(graph_module.tracing, "end_run", lambda run, **kw: None)
    monkeypatch.setattr(nodes_module.tracing, "start_child_run", lambda parent, name, run_type="chain", **kw: span_names.append(name) or name)
    monkeypatch.setattr(nodes_module.tracing, "end_run", lambda run, **kw: None)

    class _EmptyRetriever:
        def retrieve(self, *args, **kwargs):
            return RetrievalOutcome(insufficient_knowledge=True, reason="No sufficiently relevant knowledge found for this question.")

    compiled = build_graph()
    deps = _minimal_deps(retriever=_EmptyRetriever())
    initial_state = {
        "user_message": "Who should I contact for garbage collection in Mohali?",
        "original_language": "en",
        "input_type": "text",
        "conversation_history": [],
    }
    final_state = run_graph(compiled, deps, _minimal_ctx(), initial_state)

    assert final_state["routed_to"] == "RAG"
    assert final_state["insufficient_knowledge"] is True
    assert "rag_retrieval" in span_names
    assert "answer_generation" not in span_names  # never called when there's nothing to answer from


# --- Annotation Queue: knowledge-base-gap review routing ---


def test_insufficient_knowledge_is_enqueued_for_review(monkeypatch):
    from backend.services.rag_retriever import RetrievalOutcome

    monkeypatch.setattr(graph_module.tracing, "start_root_run", lambda name, **kw: "FAKE_ROOT")
    monkeypatch.setattr(graph_module.tracing, "end_run", lambda run, **kw: None)
    monkeypatch.setattr(nodes_module.tracing, "start_child_run", lambda parent, name, run_type="chain", **kw: None)
    monkeypatch.setattr(nodes_module.tracing, "end_run", lambda run, **kw: None)

    enqueued = []
    monkeypatch.setattr(graph_module.tracing, "enqueue_for_review", lambda run, reason: enqueued.append((run, reason)))

    class _EmptyRetriever:
        def retrieve(self, *args, **kwargs):
            return RetrievalOutcome(insufficient_knowledge=True, reason="No sufficiently relevant knowledge found.")

    compiled = build_graph()
    deps = _minimal_deps(retriever=_EmptyRetriever())
    initial_state = {
        "user_message": "Who should I contact for garbage collection in Mohali?",
        "original_language": "en",
        "input_type": "text",
        "conversation_history": [],
    }
    run_graph(compiled, deps, _minimal_ctx(), initial_state)

    assert len(enqueued) == 1
    assert enqueued[0] == ("FAKE_ROOT", "RAG")


def test_out_of_scope_is_enqueued_for_review(monkeypatch):
    monkeypatch.setattr(graph_module.tracing, "start_root_run", lambda name, **kw: "FAKE_ROOT")
    monkeypatch.setattr(graph_module.tracing, "end_run", lambda run, **kw: None)

    enqueued = []
    monkeypatch.setattr(graph_module.tracing, "enqueue_for_review", lambda run, reason: enqueued.append((run, reason)))

    compiled = build_graph()
    initial_state = {
        "user_message": "I need a new electricity connection",
        "original_language": "en",
        "input_type": "text",
        "conversation_history": [],
    }
    run_graph(compiled, _minimal_deps(), _minimal_ctx(), initial_state)

    assert len(enqueued) == 1
    assert enqueued[0] == ("FAKE_ROOT", "NONE_OUT_OF_SCOPE")


def test_successful_answer_is_not_enqueued_for_review(client, monkeypatch, make_citizen):
    """A question the pipeline COULD answer must never end up in the knowledge-base-gap queue --
    only genuine misses/out-of-scope routes should."""
    monkeypatch.setattr(graph_module.tracing, "enqueue_for_review", lambda run, reason: (_ for _ in ()).throw(
        AssertionError(f"should not have enqueued a successfully-answered request (reason={reason})")
    ))

    from tests.test_ask_janmitra import _install_real_service, _ask

    _install_real_service(monkeypatch)
    token, _ = make_citizen(phone="9100000095")
    resp = _ask(client, token, "What is the procedure to apply for a new water connection in Mohali?")

    assert resp.status_code == 200
    assert resp.json()["insufficient_knowledge"] is False


# --- 7: application behavior when LangSmith is unavailable ---


def test_ask_janmitra_endpoint_works_when_every_langsmith_call_raises(client, monkeypatch, make_citizen):
    """Simulates a total LangSmith outage -- every tracing.* call raises internally -- by making
    the module's own safety net fail open anyway: tracing.py already swallows every exception
    from the LangSmith SDK itself (see tests/test_langsmith_tracing.py), so patching the
    underlying `_LangSmithClient` to always raise, with tracing genuinely enabled, is the most
    realistic way to prove the *whole* HTTP request/response cycle is unaffected."""
    from backend.config import settings
    from backend.services.observability import tracing

    monkeypatch.setattr(settings, "LANGSMITH_TRACING", True)
    monkeypatch.setattr(settings, "LANGSMITH_API_KEY", "ls-test-key")
    monkeypatch.setattr(tracing, "_LangSmithClient", Mock(side_effect=RuntimeError("LangSmith is down")))
    monkeypatch.setattr(tracing, "_client", None)
    monkeypatch.setattr(tracing, "_client_unavailable", False)

    _install_real_service(monkeypatch)
    token, _ = make_citizen(phone="9100000096")
    resp = _ask(client, token, "Who should I contact for garbage collection in Mohali?")

    assert resp.status_code == 200
    body = resp.json()
    assert body["routed_to"] == "RAG"

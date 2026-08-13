"""LangSmith observability for the Ask Sarthi LangGraph pipeline.

**Manual, curated spans -- not automatic autotracing.** LangGraph's compiled graph is a
LangChain `Runnable`, so simply setting `LANGSMITH_TRACING=true`/`LANGCHAIN_TRACING_V2=true` as
environment variables would make LangChain's own callback-based tracer capture and upload the
*entire* `GraphState` (see `orchestration/state.py`) at every node transition -- including
`user_message`/`normalized_message`/`conversation_history`, i.e. the citizen's raw complaint
text, which can contain names, phone numbers, or addresses. That's exactly the "unnecessary
citizen PII" this integration was asked not to send. So this module never enables that global
callback tracer; instead, `orchestration/graph.py` and `orchestration/nodes.py` call the small
API below to create explicit spans around specific points (the whole graph run, RAG retrieval,
LLM answer generation, complaint creation) with a hand-picked, redacted payload -- the same
"log field NAMES/categorical values, not raw content" philosophy `run_graph()`'s own pre-existing
per-node log line already used (see that function's docstring), just extended to LangSmith.

**Non-blocking, fail-open.** Every public function here returns `None`/no-ops instead of raising
if: the `langsmith` package is missing, tracing is disabled or unconfigured (no API key), the
LangSmith client can't be constructed, or any individual call to it fails (auth error, network
error, timeout). Callers (graph.py, nodes.py) never need their own try/except around these calls
-- a LangSmith outage or misconfiguration must never break RAG, complaint creation, complaint
status, or the LangGraph pipeline itself (see docs/ask_janmitra_langsmith_observability.md's
"failure behavior" section). The `langsmith` SDK itself also batches/uploads runs on a background
thread rather than blocking the caller on network I/O -- this module's own try/except is
defense-in-depth on top of that, not a replacement for it.

**Redaction.** `redact_text()` masks email addresses and long digit runs (phone numbers, most
ID-like numbers) and caps length before any free text is attached to a span. This is a
best-effort regex filter, not a guarantee -- a citizen's message that includes a name or street
address in prose won't be caught by it. Documented as a known limitation, not hidden (see the
docs file's privacy section). The stronger control is architectural: callers of this module
choose exactly which fields to pass in the first place (see graph.py/nodes.py), so most
inherently-safe fields (intent, routed_to, service_category, location city/state, verification
status, latency) are sent as-is with no redaction needed, and only the handful of genuinely
free-text fields (the citizen's question, the generated answer) are routed through
`redact_text()` at all.
"""

from __future__ import annotations

import logging
import re
import uuid
from typing import Any

from backend.config import settings

logger = logging.getLogger(__name__)

try:
    from langsmith import Client as _LangSmithClient
    from langsmith.run_trees import RunTree as _RunTree
except Exception:  # pragma: no cover -- defensive: package genuinely missing/broken
    _LangSmithClient = None  # type: ignore[assignment,misc]
    _RunTree = None  # type: ignore[assignment,misc]

_EMAIL_RE = re.compile(r"[\w.+-]+@[\w.-]+\.\w+")
_LONG_DIGIT_RUN_RE = re.compile(r"\d{7,}")  # phone numbers, most long ID-like numbers
_MAX_TEXT_LEN = 2000

_client: "_LangSmithClient | None" = None
_client_unavailable = False
_review_queue_id: "uuid.UUID | None" = None
_review_queue_unavailable = False


def redact_text(text: str | None) -> str | None:
    """Best-effort PII scrubbing for free text before it's attached to a trace: masks email
    addresses and 7+ digit runs, and caps length. See this module's docstring for what this
    does and does not catch."""
    if not text:
        return text
    redacted = _EMAIL_RE.sub("[REDACTED_EMAIL]", text)
    redacted = _LONG_DIGIT_RUN_RE.sub("[REDACTED_NUMBER]", redacted)
    if len(redacted) > _MAX_TEXT_LEN:
        redacted = redacted[:_MAX_TEXT_LEN] + "...[TRUNCATED]"
    return redacted


def is_enabled() -> bool:
    """True only when the `langsmith` package imported successfully AND the operator has both
    turned tracing on and provided an API key -- matches SarvamClient's own "warn, don't crash"
    treatment of optional external services (see that module)."""
    return bool(_RunTree is not None and settings.LANGSMITH_TRACING and settings.LANGSMITH_API_KEY)


def _get_client() -> "_LangSmithClient | None":
    global _client, _client_unavailable
    if not is_enabled() or _client_unavailable:
        return None
    if _client is not None:
        return _client
    try:
        _client = _LangSmithClient(api_key=settings.LANGSMITH_API_KEY, api_url=settings.LANGSMITH_ENDPOINT)
    except Exception:
        logger.warning("LangSmith client could not be initialized; tracing disabled for this process.", exc_info=True)
        _client_unavailable = True
        return None
    return _client


def start_root_run(
    name: str,
    *,
    run_id: uuid.UUID | None = None,
    inputs: dict[str, Any] | None = None,
    metadata: dict[str, Any] | None = None,
    tags: list[str] | None = None,
) -> "_RunTree | None":
    """Starts (and immediately posts the "run started" event for) a new root trace.

    Returns `None` -- never raises -- if tracing is disabled/unconfigured or the LangSmith call
    fails for any reason. Callers pass the returned value straight into `start_child_run()`/
    `end_run()`, both of which treat `None` as a no-op, so call sites never need to branch on
    whether tracing is actually active.
    """
    client = _get_client()
    if client is None:
        return None
    try:
        run = _RunTree(
            name=name,
            run_type="chain",
            inputs=inputs or {},
            id=run_id or uuid.uuid4(),
            ls_client=client,
            session_name=settings.LANGSMITH_PROJECT,
            tags=tags or [],
            extra={"metadata": metadata or {}},
        )
        run.post()
        return run
    except Exception:
        logger.warning("LangSmith: failed to start trace %r", name, exc_info=True)
        return None


def start_child_run(
    parent: "_RunTree | None",
    name: str,
    run_type: str = "chain",
    *,
    inputs: dict[str, Any] | None = None,
    tags: list[str] | None = None,
    metadata: dict[str, Any] | None = None,
) -> "_RunTree | None":
    """Starts a child span under `parent` (e.g. RAG retrieval, LLM answer generation, complaint
    creation). A no-op returning `None` if `parent` is `None` (tracing was disabled/unavailable
    when the parent trace would have started) or the call fails."""
    if parent is None:
        return None
    try:
        child = parent.create_child(
            name=name,
            run_type=run_type,  # type: ignore[arg-type]
            inputs=inputs or {},
            tags=tags,
            extra={"metadata": metadata} if metadata else None,
        )
        child.post()
        return child
    except Exception:
        logger.warning("LangSmith: failed to start span %r", name, exc_info=True)
        return None


def end_run(run: "_RunTree | None", *, outputs: dict[str, Any] | None = None, error: str | None = None) -> None:
    """Finishes a run started by `start_root_run()`/`start_child_run()`. A no-op if `run` is
    `None` or the call fails -- never raises."""
    if run is None:
        return
    try:
        run.end(outputs=outputs, error=error)
        run.patch()
    except Exception:
        logger.warning("LangSmith: failed to finish run %r", getattr(run, "name", "?"), exc_info=True)


def _get_review_queue_id() -> "uuid.UUID | None":
    """Looks up (and caches for the life of this process) the id of the Annotation Queue named
    `settings.LANGSMITH_REVIEW_QUEUE_NAME`, creating it if it doesn't exist yet. `None` -- never
    raises -- if tracing is disabled or the lookup/creation fails."""
    global _review_queue_id, _review_queue_unavailable
    if _review_queue_id is not None:
        return _review_queue_id
    if _review_queue_unavailable:
        return None
    client = _get_client()
    if client is None:
        return None
    try:
        existing = next(iter(client.list_annotation_queues(name=settings.LANGSMITH_REVIEW_QUEUE_NAME)), None)
        if existing is not None:
            _review_queue_id = existing.id
            return _review_queue_id
        created = client.create_annotation_queue(
            name=settings.LANGSMITH_REVIEW_QUEUE_NAME,
            description=(
                "Ask Sarthi requests where the knowledge base couldn't answer -- either "
                "insufficient_knowledge or an out-of-scope service. Each one is a real citizen "
                "question the KB should potentially cover. See docs/"
                "ask_janmitra_langsmith_observability.md's Annotation Queue section."
            ),
        )
        _review_queue_id = created.id
        return _review_queue_id
    except Exception:
        logger.warning("LangSmith: could not look up/create the review annotation queue.", exc_info=True)
        _review_queue_unavailable = True
        return None


def enqueue_for_review(run: "_RunTree | None", reason: str) -> None:
    """Adds `run` (the Ask Sarthi request's root span) to the knowledge-base-gap review queue
    -- see `_get_review_queue_id()`. A no-op if `run` is `None` (tracing was disabled/unavailable)
    or the call fails; never raises. `reason` is logged locally only (not sent to LangSmith --
    the run itself already carries its own `routed_to`/`insufficient_knowledge` outputs, see
    graph.py's run_graph())."""
    if run is None:
        return
    queue_id = _get_review_queue_id()
    if queue_id is None:
        return
    try:
        client = _get_client()
        if client is None:
            return
        client.add_runs_to_annotation_queue(queue_id, run_ids=[run.id])
    except Exception:
        logger.warning("LangSmith: failed to enqueue run %s for review (%s)", getattr(run, "id", "?"), reason, exc_info=True)


def get_trace_url(trace_id: str | None) -> str | None:
    """Builds an Admin-dashboard deep link to a trace from `LANGSMITH_TRACE_URL_TEMPLATE` (see
    config.py), or `None` if that's not configured or `trace_id` is falsy. Deliberately does not
    call the LangSmith API to resolve a link (that would put a network call on the admin
    dashboard's read path) -- the template is a one-time manual copy from the LangSmith UI (see
    docs/ask_janmitra_langsmith_observability.md's setup section)."""
    if not trace_id or not settings.LANGSMITH_TRACE_URL_TEMPLATE:
        return None
    try:
        return settings.LANGSMITH_TRACE_URL_TEMPLATE.format(trace_id=trace_id)
    except Exception:
        logger.warning("LANGSMITH_TRACE_URL_TEMPLATE is misconfigured (expected a {trace_id} placeholder).")
        return None

"""Retrieval layer: combines metadata filtering (service category + location) with semantic
vector search, then a lightweight relevance/rerank pass -- the component everything else in the
Ask Sarthi pipeline calls to actually get chunks back.

Filtering happens BEFORE ranking, always. This is the single most important design decision in
this file: a chunk that doesn't match the requested service category or location is never a
candidate at all, regardless of how textually similar its content happens to be to the query.
This is what prevents the exact failure mode observed while building this module -- an
unfiltered search for "new electricity connection" returned a WATER_DRAINAGE chunk (shared words
like "new"/"connection") as its top hit. With category filtering active, a question correctly
classified as being about an unsupported service (electricity) never reaches vector search at
all (see ask_janmitra_service.py, which checks `out_of_scope_service` first).

Provider-agnostic by design: this class works unchanged against either
`(SentenceTransformerEmbeddingProvider, ChromaVectorStore)` (the active default) or
`(TfidfEmbeddingProvider, FlatVectorStore)` (legacy/comparison) -- both provider pairs implement
the same `embed_query`/`search` shape, and `service_category` is now a real, exact-match-able
metadata field on every chunk (added during the ChromaDB migration -- see
backend/schemas/rag_knowledge.py's Chunk docstring), not inferred from a `service_id` string
prefix as the original TF-IDF-era version of this file did.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Protocol

from backend.schemas.rag_knowledge import ServiceCategory
from backend.services.vector_store import ScoredChunk

logger = logging.getLogger(__name__)


class _EmbeddingProvider(Protocol):
    def embed_query(self, text: str) -> Any: ...


class _VectorStore(Protocol):
    def search(self, query_vector: Any, top_k: int, metadata_filter: dict[str, str] | None) -> list[ScoredChunk]: ...


@dataclass
class RetrievalOutcome:
    """What retrieve() found -- always returned, never raises. `results` is empty and
    `insufficient_knowledge` is True whenever nothing usable was found, with `reason` explaining
    why (no location, no category match, no results above the relevance threshold) so the caller
    (ask_janmitra_service.py) can compose an honest response instead of a generic failure."""

    results: list[ScoredChunk] = field(default_factory=list)
    insufficient_knowledge: bool = False
    reason: str | None = None


class RagRetriever:
    def __init__(
        self,
        vector_store: _VectorStore,
        embedding_provider: _EmbeddingProvider,
        top_k: int = 5,
        relevance_threshold: float = 0.79,
    ) -> None:
        self._store = vector_store
        self._embedding_provider = embedding_provider
        self._top_k = top_k
        self._relevance_threshold = relevance_threshold

    def retrieve(
        self,
        query: str,
        service_category: ServiceCategory | None,
        city: str | None,
        state: str | None,
    ) -> RetrievalOutcome:
        metadata_filter: dict[str, str] = {}
        if service_category is not None:
            metadata_filter["service_category"] = service_category.value
        if city is not None:
            metadata_filter["city"] = city
        elif state is not None:
            metadata_filter["state"] = state

        query_vector = self._embedding_provider.embed_query(query)
        # Ask the store for more than top_k so the VERIFIED-preference rerank below has something
        # to work with beyond the raw top_k by score alone.
        candidates = self._store.search(query_vector, top_k=self._top_k * 3, metadata_filter=metadata_filter or None)

        if not candidates:
            reason = "No knowledge records exist for this service/location combination."
            logger.info("RAG retrieval: no candidates (category=%s, city=%s, state=%s)", service_category, city, state)
            return RetrievalOutcome(insufficient_knowledge=True, reason=reason)

        above_threshold = [c for c in candidates if c.score >= self._relevance_threshold]
        if not above_threshold:
            reason = "No sufficiently relevant knowledge found for this question."
            logger.info(
                "RAG retrieval: %d candidate(s) but none above threshold %.3f (best score %.3f)",
                len(candidates), self._relevance_threshold, candidates[0].score,
            )
            return RetrievalOutcome(insufficient_knowledge=True, reason=reason)

        # Lightweight rerank (documented as a heuristic, not an ML reranker -- see
        # docs/ask_janmitra_rag_architecture.md's reranking section for why this was judged
        # sufficient rather than adding a trained cross-encoder): among results within a small
        # score band of the top result, prefer VERIFIED over SYNTHETIC -- never lets a SYNTHETIC
        # chunk outrank a near-equally-relevant VERIFIED one, without ever promoting a SYNTHETIC
        # chunk that scored meaningfully lower.
        top_score = above_threshold[0].score
        band = 0.03  # narrower than the old TF-IDF-era 0.05 -- real embedding scores cluster
                     # much tighter (see the threshold-selection notes in the architecture doc)
        def sort_key(c: ScoredChunk) -> tuple[int, float]:
            verified_bonus = 1 if (c.metadata["verification_status"] == "VERIFIED" and c.score >= top_score - band) else 0
            return (verified_bonus, c.score)
        above_threshold.sort(key=sort_key, reverse=True)

        return RetrievalOutcome(results=above_threshold[: self._top_k])

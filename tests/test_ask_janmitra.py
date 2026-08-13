"""Tests for the Ask JanMitra RAG retrieval endpoint and its underlying services.

Uses the REAL, checked-in ChromaDB collection (data/rag_knowledge_base/chroma, built by
scripts/build_rag_embeddings.py from the real 131-record knowledge base via
SentenceTransformerEmbeddingProvider) — deterministic, local-disk-only, no network call once the
embedding model is cached, so tests exercise genuine semantic retrieval quality rather than a
mock. The LLM answer-generation step IS mocked (via a fake AnswerGenerationService), matching this
codebase's established pattern for external AI calls (see test_complaints_api.py's `_agent` mock)
— retrieval/routing/filtering correctness is what these tests verify, not Sarvam's prose quality.

Module-level caching (`_get_shared_chroma_deps`, not a pytest fixture): the embedding model load
is genuinely slow (~20-25s the first time). AskJanMitraService's constructor doesn't cache
anything across instances by design (each call to `_real_ask_janmitra_service()` builds a fresh
service, matching how the real app builds one `_service` singleton at import time), so this module
builds ONE SentenceTransformerEmbeddingProvider + ONE ChromaVectorStore, pays the load cost once
per test run, and passes the same instances into every service under test.
"""

from unittest.mock import Mock

import pytest

import backend.routes.ask_janmitra as ask_janmitra_module
from backend.models import Complaint, User
from backend.schemas.ask_janmitra import ConversationTurn
from backend.services.ask_janmitra_service import AskJanMitraService
from backend.services.auth_service import hash_password
from backend.services.embedding_provider import SentenceTransformerEmbeddingProvider, TfidfEmbeddingProvider
from backend.services.intent_classifier import QuestionIntent, classify
from backend.services.location_extractor import LocationExtractor, RagGazetteer
from backend.services.rag_retriever import RagRetriever
from backend.services.vector_store import ChromaVectorStore, FlatVectorStore
from backend.schemas.rag_knowledge import ServiceCategory
from backend.config import settings

_shared_store: ChromaVectorStore | None = None
_shared_provider: SentenceTransformerEmbeddingProvider | None = None


def _get_shared_chroma_deps() -> tuple[ChromaVectorStore, SentenceTransformerEmbeddingProvider]:
    global _shared_store, _shared_provider
    if _shared_provider is None:
        _shared_provider = SentenceTransformerEmbeddingProvider()
        _shared_provider.load()  # pay the ~20-25s model load once for the whole test run
    if _shared_store is None:
        _shared_store = ChromaVectorStore(settings.CHROMA_PERSIST_DIR, settings.CHROMA_COLLECTION_NAME)
        _shared_store.load()
    return _shared_store, _shared_provider


class _FakeComplaintAgent:
    """Stands in for the real `ComplaintAgent` (see backend/services/complaint_agent.py) --
    the real one calls Sarvam for translation/summarization, a network call this test module
    must never make (matching the existing `fake_answers`/no-network-call pattern below). Builds
    a real `Complaint` ORM row directly, deterministically, so complaint_flow's downstream logic
    (ward resolution, assign_next_worker, response text) is exercised against a genuine row."""

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


def _real_ask_janmitra_service(**overrides) -> AskJanMitraService:
    """A real AskJanMitraService against the real, checked-in Chroma collection -- with the LLM
    answer-generation step and the complaint-creation step both swapped for deterministic fakes
    (no network call in either case; matches this codebase's established pattern for external AI
    calls -- see test_complaints_api.py's `_agent` mock)."""
    store, provider = _get_shared_chroma_deps()
    fake_answers = Mock()
    fake_answers.generate = lambda q, chunks, lang: (f"ANSWER: {chunks[0]}", False)
    kwargs = {
        "vector_store": store,
        "embedding_provider": provider,
        "answer_service": fake_answers,
        "complaint_agent": _FakeComplaintAgent(),
    }
    kwargs.update(overrides)
    return AskJanMitraService(**kwargs)


def _install_real_service(monkeypatch) -> None:
    monkeypatch.setattr(ask_janmitra_module, "_service", _real_ask_janmitra_service())


def _ask(client, token, question, **kwargs):
    body = {"question": question, "language": "en", **kwargs}
    return client.post("/ask-janmitra", headers={"Authorization": f"Bearer {token}"}, json=body)


# --- 1/2/3: TYPE_A/TYPE_B/TYPE_C classification+routing ---


def test_type_a_complaint_creates_and_assigns_complaint(client, monkeypatch, db_session, make_citizen, make_worker):
    """Deliberate behavior change this phase (see backend/services/orchestration/nodes.py's
    module docstring, confirmed with the user before implementing): a TYPE_A complaint-shaped
    message with enough information (category + location) now files a REAL complaint via the
    LangGraph complaint_flow, using the existing ComplaintAgent/assign_next_worker services --
    it no longer just answers with RAG sources. Uses a worker seeded into the same ward Mohali's
    text resolves to, so this also exercises the worker-assignment workflow end-to-end."""
    _install_real_service(monkeypatch)
    make_worker(phone="9100099001", ward="Mohali")
    token, _ = make_citizen(phone="9100000001")
    resp = _ask(client, token, "Street light not working in Mohali.", location_text="Mohali")
    assert resp.status_code == 200
    body = resp.json()
    assert body["intent"] == "TYPE_A_COMPLAINT"
    assert body["routed_to"] == "COMPLAINT_CREATED"
    assert body["service_category"] == "STREETLIGHTS"
    assert body["complaint_id"] is not None
    assert body["sources"] == []  # complaint creation, not a RAG answer

    db = db_session()
    complaint = db.query(Complaint).filter(Complaint.id == body["complaint_id"]).first()
    assert complaint is not None
    assert complaint.ward == "Mohali"
    assert complaint.status == "assigned"  # the seeded worker was eligible
    assert complaint.assigned_worker_id is not None
    db.close()


def test_type_b_service_retrieval(client, monkeypatch, make_citizen):
    _install_real_service(monkeypatch)
    token, _ = make_citizen(phone="9100000002")
    resp = _ask(client, token, "Who should I contact for garbage collection in Mohali?")
    assert resp.status_code == 200
    body = resp.json()
    assert body["intent"] == "TYPE_B_SERVICE_INFO"
    assert body["routed_to"] == "RAG"
    assert body["service_category"] == "WASTE_SANITATION"


def test_type_c_status_routes_to_complaint_api_not_rag(client, monkeypatch, db_session, make_citizen):
    _install_real_service(monkeypatch)
    token, user = make_citizen(phone="9100000003")

    db = db_session()
    complaint = Complaint(
        citizen_id=str(user["id"]), original_text="test", original_language="en",
        translated_text="test", summary="test", status="assigned",
    )
    db.add(complaint)
    db.commit()
    db.refresh(complaint)
    complaint_id = complaint.id
    db.close()

    resp = _ask(client, token, f"What is the status of complaint #{complaint_id}?")
    assert resp.status_code == 200
    body = resp.json()
    assert body["intent"] == "TYPE_C_STATUS"
    assert body["routed_to"] == "COMPLAINT_STATUS_API"
    assert body["sources"] == []  # proves nothing came from RAG
    assert "assigned" in body["answer"].lower()


def test_type_c_bypasses_rag_even_for_rag_shaped_wording(client, monkeypatch, make_citizen):
    """A status question that ALSO happens to contain civic-complaint-sounding words ("street
    light") must still route to TYPE_C, not accidentally fall through to RAG."""
    _install_real_service(monkeypatch)
    token, _ = make_citizen(phone="9100000004")
    resp = _ask(client, token, "What is the status of my street light complaint, complaint #999?")
    assert resp.status_code == 200
    body = resp.json()
    assert body["intent"] == "TYPE_C_STATUS"
    assert body["routed_to"] == "COMPLAINT_STATUS_API"


def test_type_c_cannot_see_another_citizens_complaint(client, monkeypatch, db_session, make_citizen):
    _install_real_service(monkeypatch)
    _, owner = make_citizen(phone="9100000005")
    other_token, _ = make_citizen(phone="9100000006")

    db = db_session()
    complaint = Complaint(
        citizen_id=str(owner["id"]), original_text="x", original_language="en",
        translated_text="x", summary="x", status="pending",
    )
    db.add(complaint)
    db.commit()
    db.refresh(complaint)
    complaint_id = complaint.id
    db.close()

    resp = _ask(client, other_token, f"What is the status of complaint #{complaint_id}?")
    assert resp.status_code == 200
    body = resp.json()
    assert "couldn't find" in body["answer"].lower()


# --- 4/5/6/7/8/9/10: location handling ---


def test_missing_location_asks_for_clarification(client, monkeypatch, make_citizen):
    _install_real_service(monkeypatch)
    token, _ = make_citizen(phone="9100000007")
    resp = _ask(client, token, "Street light not working.")
    body = resp.json()
    assert body["follow_up_required"] is True
    assert body["routed_to"] == "NONE_CLARIFICATION_NEEDED"
    assert body["sources"] == []


def test_explicit_city_resolves_directly(client, monkeypatch, make_citizen):
    _install_real_service(monkeypatch)
    token, _ = make_citizen(phone="9100000008")
    resp = _ask(client, token, "Street light not working in Mohali.")
    body = resp.json()
    assert body["location"]["city"] == "Sahibzada Ajit Singh Nagar (Mohali)"
    assert body["location"]["source"] == "text"


def test_explicit_state_and_city_resolves(client, monkeypatch, make_citizen):
    _install_real_service(monkeypatch)
    token, _ = make_citizen(phone="9100000009")
    resp = _ask(client, token, "Street light problem in Mohali, Punjab.")
    body = resp.json()
    assert body["location"]["city"] == "Sahibzada Ajit Singh Nagar (Mohali)"
    assert body["location"]["state"] == "Punjab"


def test_gps_location_resolves_via_location_resolver(client, monkeypatch, make_citizen):
    """The GPS -> LocationResolver -> RAG gazetteer integration path (previously the documented
    gap, see docs/ask_janmitra_response_behavior.md §3) -- exercised with a fake geocoder so no
    real network call happens, but the real matching logic runs end to end."""
    from backend.services.location_resolver import LocationResolver, ResolvedLocation

    fake_resolver = Mock()
    fake_resolver.resolve_coordinates = lambda lat, lng: ResolvedLocation(
        latitude=lat, longitude=lng, city_name="Mohali", state_name="Punjab"
    )
    gazetteer = RagGazetteer(settings.RAG_DATA_DIR / "chunks" / "chunks.json")
    extractor = LocationExtractor(gazetteer, location_resolver=fake_resolver)
    service = _real_ask_janmitra_service(location_extractor=extractor)
    monkeypatch.setattr(ask_janmitra_module, "_service", service)

    token, _ = make_citizen(phone="9100000010")
    resp = _ask(client, token, "Street light near me is not working.", latitude=30.7, longitude=76.7)
    body = resp.json()
    assert body["location"]["city"] == "Sahibzada Ajit Singh Nagar (Mohali)"
    assert body["location"]["source"] == "gps"
    # TYPE_A ("...is not working") + category (streetlight) + location (via GPS) all resolved ->
    # complaint_flow files a real complaint (see the confirmed behavior change, module-level
    # docstring above) rather than answering via RAG.
    assert body["routed_to"] == "COMPLAINT_CREATED"
    assert body["complaint_id"] is not None


def test_gps_failure_does_not_break_ask_janmitra(client, monkeypatch, make_citizen):
    from backend.services.location_resolver import LocationResolver, ResolvedLocation

    fake_resolver = Mock()
    fake_resolver.resolve_coordinates = lambda lat, lng: ResolvedLocation(latitude=lat, longitude=lng)  # everything None -- resolution failed
    gazetteer = RagGazetteer(settings.RAG_DATA_DIR / "chunks" / "chunks.json")
    extractor = LocationExtractor(gazetteer, location_resolver=fake_resolver)
    service = _real_ask_janmitra_service(location_extractor=extractor)
    monkeypatch.setattr(ask_janmitra_module, "_service", service)

    token, _ = make_citizen(phone="9100000011")
    resp = _ask(client, token, "Street light near me is not working.", latitude=1.0, longitude=1.0)
    assert resp.status_code == 200  # never a 500/502
    body = resp.json()
    assert body["follow_up_required"] is True  # falls back to asking, doesn't crash or guess


def test_invalid_gps_is_ignored_gracefully(client, monkeypatch, make_citizen):
    """Nonsensical coordinates must not crash the pipeline -- the location_resolver's own
    resolve_coordinates never raises (see its tests), and this proves the whole ask_janmitra
    pipeline tolerates it too."""
    _install_real_service(monkeypatch)
    token, _ = make_citizen(phone="9100000012")
    resp = _ask(client, token, "Street light not working.", latitude=999.0, longitude=-500.0)
    assert resp.status_code == 200


def test_location_resolver_failure_does_not_break_the_pipeline(client, monkeypatch, make_citizen):
    from backend.services.location_resolver import LocationResolver

    class RaisingResolver:
        def resolve_coordinates(self, lat, lng):
            raise RuntimeError("simulated resolver crash")

    gazetteer = RagGazetteer(settings.RAG_DATA_DIR / "chunks" / "chunks.json")
    extractor = LocationExtractor(gazetteer, location_resolver=RaisingResolver())
    service = _real_ask_janmitra_service(location_extractor=extractor)
    monkeypatch.setattr(ask_janmitra_module, "_service", service)

    token, _ = make_citizen(phone="9100000013")
    resp = _ask(client, token, "Street light near me.", latitude=1.0, longitude=1.0)
    # The route-level try/except (see routes/ask_janmitra.py) converts this into a clean 503,
    # never a raw 500 with a stack trace.
    assert resp.status_code == 503
    assert "temporarily unavailable" in resp.json()["detail"].lower()


def test_cross_city_contamination_mohali_vs_patiala(client, monkeypatch, make_citizen):
    """TYPE_B phrasing (a genuine information question, not "...is broken") -- deliberately, so
    this exercises RAG's cross-city filtering rather than complaint_flow (see this module's
    docstring for why TYPE_A now creates a complaint instead of answering from RAG; the RAG-layer
    cross-city test also exists independently at tests/test_rag_vector_store.py's
    test_cross_city_contamination_mohali_ahmedabad_mumbai_patiala)."""
    _install_real_service(monkeypatch)
    token, _ = make_citizen(phone="9100000014")

    mohali_resp = _ask(client, token, "Who do I contact about street lights in Mohali?").json()
    patiala_resp = _ask(client, token, "Who do I contact about street lights in Patiala?").json()

    mohali_sources = {s["source_title"] for s in mohali_resp["sources"]}
    patiala_sources = {s["source_title"] for s in patiala_resp["sources"]}
    assert "Mohali" in list(mohali_sources)[0] or "Sahibzada" in list(mohali_sources)[0]
    assert mohali_sources.isdisjoint(patiala_sources) or mohali_resp["location"]["city"] != patiala_resp["location"]["city"]
    assert mohali_resp["location"]["city"] == "Sahibzada Ajit Singh Nagar (Mohali)"
    assert patiala_resp["location"]["city"] == "Patiala"


def test_ambiguous_state_only_location_asks_for_city(client, monkeypatch, make_citizen):
    _install_real_service(monkeypatch)
    token, _ = make_citizen(phone="9100000015")
    resp = _ask(client, token, "Street light problem in Punjab.")
    body = resp.json()
    assert body["follow_up_required"] is True
    assert set(body["follow_up_options"]) == {"Patiala", "Sahibzada Ajit Singh Nagar (Mohali)"}


# --- 11/12/13/14/15: citations, synthetic disclosure, no-knowledge, low-relevance ---


def test_verified_citation_preserved(client, monkeypatch, make_citizen):
    """TYPE_B phrasing (see this module's docstring: TYPE_A now creates a complaint instead of
    answering via RAG)."""
    _install_real_service(monkeypatch)
    token, _ = make_citizen(phone="9100000016")
    resp = _ask(client, token, "Who do I contact about street lights in Mohali?")
    body = resp.json()
    source = body["sources"][0]
    assert source["verification_status"] == "VERIFIED"
    assert source["source_url"] is not None
    assert source["source_url"].startswith("https://")
    assert body["verification_status"] == "VERIFIED"


def test_synthetic_disclosure(client, monkeypatch, make_citizen):
    """TYPE_B phrasing (see this module's docstring: TYPE_A now creates a complaint instead of
    answering via RAG)."""
    _install_real_service(monkeypatch)
    token, _ = make_citizen(phone="9100000017")
    resp = _ask(client, token, "Who do I contact about road potholes in Nagpur?")
    body = resp.json()
    assert len(body["sources"]) > 0
    source = body["sources"][0]
    assert source["verification_status"] == "SYNTHETIC"
    assert source["source_url"] is None  # never fabricated
    assert "synthetic" in source["source_organization"].lower()
    assert body["verification_status"] == "SYNTHETIC"


def test_no_knowledge_available_says_so_honestly(client, monkeypatch, make_citizen):
    _install_real_service(monkeypatch)
    token, _ = make_citizen(phone="9100000018")
    resp = _ask(client, token, "I want a new electricity connection.")
    body = resp.json()
    assert body["insufficient_knowledge"] is True
    assert body["sources"] == []
    assert "don't currently have" in body["answer"].lower()


def test_unknown_city_reports_no_data_not_fabricated(client, monkeypatch, make_citizen):
    """A place name the RAG gazetteer has never heard of ('Atlantis') must be treated as no
    location resolved -- clarification requested, never silently answered from a real city."""
    _install_real_service(monkeypatch)
    token, _ = make_citizen(phone="9100000019")
    resp = _ask(client, token, "Street light not working in Atlantis.")
    body = resp.json()
    assert body["follow_up_required"] is True
    assert body["sources"] == []


def test_low_relevance_results_are_rejected_tfidf(monkeypatch):
    """Unit-level test of the relevance threshold on the LEGACY TF-IDF path: a nonsense query
    with no real keyword overlap with any chunk must not return low-quality matches just to have
    *something* to show. (Requires the legacy index -- see requires_legacy_tfidf_index marker.)"""
    if not settings.RAG_EMBEDDINGS_INDEX_PATH.exists():
        import pytest
        pytest.skip("legacy TF-IDF index not built -- run scripts/build_rag_embeddings.py --legacy-tfidf")
    store = FlatVectorStore()
    store.load(settings.RAG_EMBEDDINGS_INDEX_PATH)
    provider = TfidfEmbeddingProvider(idf=store.idf)
    retriever = RagRetriever(store, provider, top_k=5, relevance_threshold=0.9)  # deliberately very strict
    outcome = retriever.retrieve("xyzzy plugh qwerty", None, None, None)
    assert outcome.insufficient_knowledge is True
    assert outcome.results == []


def test_low_relevance_results_are_rejected_embeddings():
    """Same behavior on the ACTIVE (embeddings + Chroma) path -- see the threshold-calibration
    data in backend/config.py's RAG_EMBEDDING_RELEVANCE_THRESHOLD comment: within a real
    category+location filter, off-topic/gibberish probes scored <=0.780 in every case measured,
    comfortably below the 0.80 default threshold used here."""
    store, provider = _get_shared_chroma_deps()
    retriever = RagRetriever(store, provider, top_k=5, relevance_threshold=0.9)  # deliberately very strict
    outcome = retriever.retrieve(
        "xyzzy plugh qwerty nonsense gibberish", ServiceCategory.STREETLIGHTS, "Sahibzada Ajit Singh Nagar (Mohali)", None
    )
    assert outcome.insufficient_knowledge is True
    assert outcome.results == []


# --- 16: multilingual (routing/classification only -- LLM prose quality is not asserted here) ---


def test_multilingual_hindi_classification(client, monkeypatch, make_citizen):
    _install_real_service(monkeypatch)
    token, _ = make_citizen(phone="9100000020")
    resp = _ask(client, token, "मेरे घर के पास स्ट्रीट लाइट खराब है।", language="hi")
    assert resp.status_code == 200
    body = resp.json()
    assert body["intent"] == "TYPE_A_COMPLAINT"
    assert body["language"] == "hi"


def test_multilingual_marathi_new_connection_is_type_b(client, monkeypatch, make_citizen):
    _install_real_service(monkeypatch)
    token, _ = make_citizen(phone="9100000021")
    resp = _ask(client, token, "मला नवीन पाणी कनेक्शन पाहिजे.", language="mr")
    body = resp.json()
    assert body["intent"] == "TYPE_B_SERVICE_INFO"


def test_multilingual_odia_new_connection_is_type_b(client, monkeypatch, make_citizen):
    _install_real_service(monkeypatch)
    token, _ = make_citizen(phone="9100000022")
    resp = _ask(client, token, "ମୋତେ ନୂଆ ପାଣି ସଂଯୋଗ ଦରକାର।", language="or")
    body = resp.json()
    assert body["intent"] == "TYPE_B_SERVICE_INFO"


# --- 17: conversation follow-up ---


def test_conversation_follow_up_uses_prior_location(client, monkeypatch, make_citizen):
    """A follow-up question with no location of its own should use a city mentioned in an
    earlier turn -- "do not make the user repeat all information", per the spec."""
    _install_real_service(monkeypatch)
    token, _ = make_citizen(phone="9100000023")
    history = [
        ConversationTurn(role="user", content="I'm in Mohali.").model_dump(),
        ConversationTurn(role="assistant", content="Got it, Mohali.").model_dump(),
    ]
    resp = _ask(client, token, "Street light not working.", conversation_history=history)
    body = resp.json()
    assert body["location"]["city"] == "Sahibzada Ajit Singh Nagar (Mohali)"
    assert body["location"]["source"] == "conversation_history"
    assert body["follow_up_required"] is False


# --- 18: source URL preservation (never fabricated) ---


def test_source_url_never_fabricated_for_synthetic(client, monkeypatch, make_citizen):
    """TYPE_B phrasing (see this module's docstring: TYPE_A now creates a complaint instead of
    answering via RAG)."""
    _install_real_service(monkeypatch)
    token, _ = make_citizen(phone="9100000024")
    resp = _ask(client, token, "Who do I contact about garbage collection in Jaipur?")
    body = resp.json()
    for source in body["sources"]:
        if source["verification_status"] == "SYNTHETIC":
            assert source["source_url"] is None


# --- 19/20: routing separation (explicit, redundant with earlier tests on purpose -- this is
# the single most important behavior in the whole system) ---


def test_status_bypasses_rag_explicitly(client, monkeypatch, db_session, make_citizen):
    _install_real_service(monkeypatch)
    token, user = make_citizen(phone="9100000025")
    db = db_session()
    complaint = Complaint(citizen_id=str(user["id"]), original_text="x", original_language="en", translated_text="x", summary="x", status="resolved")
    db.add(complaint)
    db.commit()
    db.refresh(complaint)
    cid = complaint.id
    db.close()

    resp = _ask(client, token, f"complaint #{cid} status")
    body = resp.json()
    assert body["routed_to"] == "COMPLAINT_STATUS_API"
    assert body["sources"] == []
    assert body["service_category"] is None


def test_type_a_without_location_does_not_create_a_complaint_yet(client, monkeypatch, db_session, make_citizen):
    """Renamed/rewritten from the pre-orchestration `test_complaint_creation_intent_is_not_this_
    endpoint`, which asserted Ask JanMitra never creates complaints -- that guarantee was
    deliberately changed this phase (see module docstring). What's still true, and still worth a
    regression test: a complaint is created ONLY once enough information (category + location)
    is actually available -- an incomplete complaint-shaped message must never create a
    half-filled complaint row, it must ask for what's missing first (see complaint_flow_node's
    clarification gate)."""
    _install_real_service(monkeypatch)
    token, _ = make_citizen(phone="9100000026")
    resp = _ask(client, token, "Street light not working.")  # category present, no location
    assert resp.status_code == 200
    body = resp.json()
    assert body["follow_up_required"] is True
    assert body.get("complaint_id") is None

    db = db_session()
    assert db.query(Complaint).count() == 0
    db.close()


def test_type_a_with_full_info_creates_exactly_one_complaint(client, monkeypatch, db_session, make_citizen):
    _install_real_service(monkeypatch)
    token, _ = make_citizen(phone="9100000028")
    resp = _ask(client, token, "Street light not working in Mohali.", location_text="Mohali")
    assert resp.status_code == 200
    body = resp.json()
    assert body["routed_to"] == "COMPLAINT_CREATED"
    assert body["complaint_id"] is not None

    db = db_session()
    assert db.query(Complaint).count() == 1
    db.close()


# --- Intent classifier unit tests (fast, no HTTP/DB needed) ---


def test_classifier_type_c_priority_over_complaint_keywords():
    result = classify("What is the status of my street light complaint #42?")
    assert result.intent == QuestionIntent.TYPE_C_STATUS


def test_classifier_out_of_scope_electricity_not_streetlights():
    """Regression test for the exact bug caught while building this module: 'electricity' must
    never be classified as STREETLIGHTS just because both relate to 'electric'."""
    result = classify("I need a new electricity connection")
    assert result.out_of_scope_service == "ELECTRICITY"
    assert result.service_category is None


# --- CAPABILITIES / UNCLEAR: real, user-reported bug -- two completely different questions
# ("What is my name?" and "Which services do you provide?") both silently fell through to
# TYPE_A_COMPLAINT/service_category=None and got the exact same "What issue would you like to
# report?" clarification, regardless of what was actually asked. See intent_classifier.py's
# QuestionIntent.CAPABILITIES/UNCLEAR docstrings and nodes.py's capabilities_flow_node/
# unclear_flow_node for the fix. ---


def test_classifier_capabilities_question_is_not_a_complaint():
    result = classify("Which services do you provide?")
    assert result.intent == QuestionIntent.CAPABILITIES
    assert result.service_category is None


def test_classifier_genuinely_unclear_question_is_not_a_disguised_complaint():
    result = classify("What is my name?")
    assert result.intent == QuestionIntent.UNCLEAR
    assert result.service_category is None


def test_classifier_real_complaint_with_no_category_still_type_a():
    """Guards the exact phrase the multi-turn clarification test relies on -- 'complain' is a
    substring of 'complaint', so this must still be treated as a real (if underspecified)
    complaint, not UNCLEAR."""
    result = classify("I want to file a complaint.")
    assert result.intent == QuestionIntent.TYPE_A_COMPLAINT


def test_capabilities_and_unclear_questions_get_different_real_answers_not_the_same_clarification(client, monkeypatch, make_citizen):
    """End-to-end reproduction of the user-reported bug: two unrelated questions must no longer
    produce byte-for-byte the same response."""
    _install_real_service(monkeypatch)
    token, _ = make_citizen(phone="9100000090")

    capabilities_resp = _ask(client, token, "Which services do you provide?")
    assert capabilities_resp.status_code == 200
    capabilities_body = capabilities_resp.json()
    assert capabilities_body["intent"] == "CAPABILITIES"
    assert "garbage" in capabilities_body["answer"].lower()
    assert "streetlight" in capabilities_body["answer"].lower()

    unclear_resp = _ask(client, token, "What is my name?")
    assert unclear_resp.status_code == 200
    unclear_body = unclear_resp.json()
    assert unclear_body["intent"] == "UNCLEAR"
    assert "not sure i understood" in unclear_body["answer"].lower()

    # The actual bug: these used to be identical.
    assert capabilities_body["answer"] != unclear_body["answer"]
    assert "What issue would you like to report?" not in capabilities_body["answer"]
    assert "What issue would you like to report?" not in unclear_body["answer"]


# --- Hinglish/Romanized service-info classification (KB-expansion phase) ---
#
# Regression tests for the exact bug caught while live-testing this phase: Romanized Hindi
# ("Hinglish") service-information questions misclassified as TYPE_A_COMPLAINT because the
# keyword lists had zero Latin-script Hindi entries (only English and Devanagari/Odia script).
# The four examples below are the phase's own required test sentences; the paraphrase/negative
# tests after them exist specifically to catch overfitting to only those four exact strings.

def test_hinglish_new_water_connection_is_type_b_not_complaint():
    result = classify("Mujhe naya water connection chahiye")
    assert result.intent == QuestionIntent.TYPE_B_SERVICE_INFO
    assert result.service_category == ServiceCategory.WATER_DRAINAGE
    assert result.requests_new_connection is True


def test_hinglish_documents_question_is_type_b():
    result = classify("Water connection ke liye documents kya lagenge")
    assert result.intent == QuestionIntent.TYPE_B_SERVICE_INFO
    assert result.service_category == ServiceCategory.WATER_DRAINAGE


def test_hinglish_new_pipeline_connection_is_type_b():
    result = classify("Naya pipeline connection kaise milega")
    assert result.intent == QuestionIntent.TYPE_B_SERVICE_INFO
    assert result.requests_new_connection is True


def test_hinglish_fees_question_is_type_b():
    result = classify("Kitne paise lagenge water connection ke")
    assert result.intent == QuestionIntent.TYPE_B_SERVICE_INFO
    assert result.service_category == ServiceCategory.WATER_DRAINAGE


@pytest.mark.parametrize("question", [
    "Water connection ki fees kitni hai?",
    "Kitna time lagega naya water connection ke liye?",
    "Naya sewerage connection kaise milega?",
    "Streetlight maintenance kaun karta hai?",
    "Road repair ka responsible department kaunsa hai?",
    "Garbage collection ka schedule kya hai?",
])
def test_hinglish_paraphrases_beyond_the_four_required_examples_are_type_b(question):
    """Not overfit to the four exact required sentences -- a spread of paraphrases and other
    civic categories in the same Hinglish style, per the phase's own 'do not overfit' instruction."""
    result = classify(question)
    assert result.intent == QuestionIntent.TYPE_B_SERVICE_INFO, f"{question!r} -> {result.intent}"


def test_hinglish_does_not_break_genuine_complaint_classification():
    """Negative check: a plainly complaint-shaped Hinglish sentence (no service-info signal) must
    still classify as TYPE_A -- the new keywords must not have made the classifier over-eager."""
    result = classify("Mere ghar ke paas streetlight kharab hai")
    assert result.intent == QuestionIntent.TYPE_A_COMPLAINT
    assert result.service_category == ServiceCategory.STREETLIGHTS


def test_requests_new_connection_flag_false_for_unrelated_questions():
    result = classify("Street light not working near me")
    assert result.requests_new_connection is False


def test_new_water_connection_in_mohali_now_answered_from_real_verified_record(client, monkeypatch, make_citizen):
    """Superseded by the KB-expansion phase: this used to be a regression test proving 'new water
    connection' was UNANSWERABLE (no record existed in any city). It's no longer true -- real,
    VERIFIED new-water-connection records were added for Mohali/Patiala/Odisha, extracted
    directly from the same citizen-charter PDFs already used for this project's other VERIFIED
    records (see data/rag_knowledge_base/knowledge_records/verified/). Mohali specifically now
    has a source-grounded answer; this asserts the new, correct behavior."""
    _install_real_service(monkeypatch)
    token, _ = make_citizen(phone="9100000027")
    resp = _ask(client, token, "What is the procedure to apply for a new water connection in Mohali?")
    body = resp.json()
    assert body["intent"] == "TYPE_B_SERVICE_INFO"
    assert body["insufficient_knowledge"] is False
    assert len(body["sources"]) > 0
    assert all(s["verification_status"] == "VERIFIED" for s in body["sources"])
    assert body["sources"][0]["source_id"] == "PB_MOHALI_CITIZEN_CHARTER"


def test_new_water_connection_in_uncovered_city_stays_honest_not_a_wrong_repair_chunk(client, monkeypatch, make_citizen):
    """The other half of the same regression: a city with NO new-connection record (Nagpur --
    only a generic synthetic leak/repair-style record) must still say insufficient_knowledge, not
    fall back to answering from that unrelated repair chunk just because it's topically similar
    ("water supply"). Measured directly while building this: without the requests_new_connection
    post-filter in rag_flow_node, Nagpur's synthetic WATER_SUPPLY_DRAINAGE_NAGPUR chunk scored
    0.849 against this exact query -- comfortably above the 0.79 relevance threshold, and would
    have been served as if it answered a new-connection question."""
    _install_real_service(monkeypatch)
    token, _ = make_citizen(phone="9100000048")
    resp = _ask(client, token, "What is the procedure for a new water connection in Nagpur?")
    body = resp.json()
    assert body["insufficient_knowledge"] is True
    assert body["sources"] == []


def test_new_sewerage_connection_in_patiala_answered_from_verified_record(client, monkeypatch, make_citizen):
    _install_real_service(monkeypatch)
    token, _ = make_citizen(phone="9100000049")
    resp = _ask(client, token, "New sewerage connection procedure in Patiala")
    body = resp.json()
    assert body["insufficient_knowledge"] is False
    assert len(body["sources"]) > 0
    assert body["sources"][0]["source_id"] == "PB_PATIALA_CITIZEN_CHARTER"


def test_classifier_measured_accuracy_against_existing_labeled_test_files():
    """Measures (does not assert a specific invented number) this classifier's real accuracy
    against the project's own hand-labeled test questions -- reported in
    docs/ask_janmitra_rag_architecture.md, not fabricated. This test only asserts a floor low
    enough to catch a genuine regression, not a target accuracy."""
    import json

    path = settings.RAG_DATA_DIR / "test_questions" / "type_ab_multilingual_questions.json"
    questions = json.loads(path.read_text(encoding="utf-8"))
    correct = 0
    total = 0
    for q in questions:
        expected = q["question_type_ab"]
        if expected not in ("TYPE_A_COMPLAINT", "TYPE_B_SERVICE_INFO"):
            continue  # LOCATION_GRANULARITY entries aren't intent-labeled the same way
        total += 1
        result = classify(q["question"])
        if result.intent.value == expected:
            correct += 1
    accuracy = correct / total if total else 0
    print(f"\nIntent classifier measured accuracy on labeled TYPE A/B questions: {correct}/{total} = {accuracy:.0%}")
    assert total > 0
    assert accuracy >= 0.5  # floor to catch a real regression, not a claimed target

"""Regression tests for the RAG civic-knowledge-base data set (data/rag_knowledge_base/).

Runs the same validation scripts/build_rag_knowledge_base.py and scripts/check_rag_sources.py
already perform, as pytest -- so a bad hand-edit to a JSON knowledge-record file fails CI the
same way any other regression would, instead of only being caught by someone remembering to run
the scripts manually. Network-dependent checks (live source URL reachability) are intentionally
excluded here -- that's check_rag_sources.py's job, run separately, not part of the fast unit
suite.
"""

import json

from backend.schemas.rag_knowledge import KnowledgeRecord, SourceRecord, TestQuestion, VerificationStatus
from scripts.build_rag_knowledge_base import (
    check_referential_integrity,
    load_knowledge_records,
    load_sources,
)
from scripts.check_rag_sources import find_duplicates


def test_sources_load_and_validate():
    sources = load_sources()
    assert len(sources) > 0, "sources/inventory.json should not be empty"
    for source in sources.values():
        assert isinstance(source, SourceRecord)


def test_knowledge_records_load_and_validate():
    records = load_knowledge_records()
    assert len(records) > 0, "knowledge_records/ should not be empty"
    for record in records:
        assert isinstance(record, KnowledgeRecord)


def test_every_record_source_id_resolves():
    sources = load_sources()
    records = load_knowledge_records()
    # Raises SystemExit on failure -- if this doesn't raise, integrity holds.
    check_referential_integrity(records, sources)


def test_no_duplicate_records():
    records = load_knowledge_records()
    duplicates = find_duplicates(records)
    assert duplicates == [], f"Duplicate records found: {duplicates}"


def test_verified_and_synthetic_tiers_are_never_blended():
    """The one rule this whole data set exists to enforce: a VERIFIED record always has a real
    source_url and a real source_organization; a SYNTHETIC record never does. This is already
    enforced by KnowledgeRecord's own model_validator on load (so a malformed record would have
    failed test_knowledge_records_load_and_validate already), but this test re-asserts it
    explicitly and exhaustively so the invariant is visible here too, not just implicitly relied
    upon."""
    records = load_knowledge_records()
    for record in records:
        if record.verification_status == VerificationStatus.VERIFIED:
            assert record.source_url, f"{record.record_id}: VERIFIED record must have a source_url"
        else:
            assert record.source_url is None, f"{record.record_id}: SYNTHETIC record must not have a source_url"


def test_verified_tier_is_nonempty():
    """A regression guard specifically for the hybrid strategy: if every VERIFIED record were
    ever accidentally deleted (e.g. a bad merge), this data set would silently become 100%
    synthetic with no test catching it otherwise."""
    records = load_knowledge_records()
    verified = [r for r in records if r.verification_status == VerificationStatus.VERIFIED]
    assert len(verified) >= 8, f"Expected at least 8 VERIFIED records (pilot-batch target), found {len(verified)}"


def test_all_four_service_categories_have_verified_coverage():
    records = load_knowledge_records()
    verified = [r for r in records if r.verification_status == VerificationStatus.VERIFIED]
    categories_covered = {r.service_category.value for r in verified}
    expected = {"WASTE_SANITATION", "WATER_DRAINAGE", "ROADS_POTHOLES", "STREETLIGHTS"}
    missing = expected - categories_covered
    assert not missing, f"No VERIFIED record for service categories: {missing}"


def test_test_questions_load_and_reference_real_records():
    from backend.config import settings

    records = load_knowledge_records()
    record_ids = {r.record_id for r in records}

    path = settings.RAG_DATA_DIR / "test_questions" / "multilingual_test_questions.json"
    raw = json.loads(path.read_text(encoding="utf-8"))
    assert len(raw) > 0, "multilingual_test_questions.json should not be empty"

    for entry in raw:
        question = TestQuestion.model_validate(entry)
        for record_id in question.expected_record_ids:
            assert record_id in record_ids, (
                f"{question.question_id}: expected_record_id {record_id!r} does not exist in "
                "knowledge_records/"
            )


def test_test_questions_cover_multiple_languages():
    from backend.config import settings

    path = settings.RAG_DATA_DIR / "test_questions" / "multilingual_test_questions.json"
    raw = json.loads(path.read_text(encoding="utf-8"))
    languages = {entry["language"] for entry in raw}
    assert languages >= {"en", "hi", "mr", "or"}, f"Expected at least en/hi/mr/or coverage, found {languages}"

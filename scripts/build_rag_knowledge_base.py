"""Deterministic assembly for the RAG civic-knowledge-base data set.

Reads every hand-authored KnowledgeRecord under data/rag_knowledge_base/knowledge_records/
(both verified/ and synthetic/), validates each against the Pydantic schema and cross-checks its
source_id against sources/inventory.json, then renders GENERATED documents.json, chunks.json,
and schema/*.schema.json from that input. This script's outputs are always a pure function of
knowledge_records/ + sources/inventory.json — every run overwrites documents/ and chunks/
completely, there's no additive state to go stale (unlike e.g. scripts/seed_multi_ward_data.py,
which seeds accumulating test data on purpose).

Usage:
    python scripts/build_rag_knowledge_base.py            # full build
    python scripts/build_rag_knowledge_base.py --check     # validate only, no output written
    python scripts/build_rag_knowledge_base.py --stats     # print counts by tier/category/city
"""

import argparse
import json
import sys
from datetime import date, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pydantic import ValidationError

from backend.config import settings
from backend.schemas.rag_knowledge import Chunk, Document, KnowledgeRecord, SourceRecord


def _json_default(obj: object) -> str:
    if isinstance(obj, (date, datetime)):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


def load_sources() -> dict[str, SourceRecord]:
    """Load sources/inventory.json into a dict keyed by source_id, validating each entry."""
    path = settings.RAG_DATA_DIR / "sources" / "inventory.json"
    if not path.exists():
        return {}
    raw = json.loads(path.read_text(encoding="utf-8"))
    sources: dict[str, SourceRecord] = {}
    errors: list[str] = []
    for entry in raw:
        try:
            source = SourceRecord.model_validate(entry)
        except ValidationError as exc:
            errors.append(f"{path.name} (source_id={entry.get('source_id', '?')}): {exc}")
            continue
        if source.source_id in sources:
            errors.append(f"{path.name}: duplicate source_id {source.source_id!r}")
        sources[source.source_id] = source
    if errors:
        for err in errors:
            print(f"  ERROR (sources/inventory.json): {err}")
        raise SystemExit(f"Aborting: {len(errors)} error(s) in sources/inventory.json")
    return sources


def load_knowledge_records() -> list[KnowledgeRecord]:
    """Glob every knowledge_records/**/*.json file and validate each entry as a KnowledgeRecord.

    Aborts loudly (file + record_id + error) on any validation failure, matching
    scripts/build_i18n_ts.py's "don't silently produce a partially-broken artifact" style.
    """
    kb_dir = settings.RAG_DATA_DIR / "knowledge_records"
    records: list[KnowledgeRecord] = []
    errors: list[str] = []
    seen_ids: set[str] = set()

    for path in sorted(kb_dir.glob("**/*.json")):
        raw = json.loads(path.read_text(encoding="utf-8"))
        for entry in raw:
            rid = entry.get("record_id", "?")
            try:
                record = KnowledgeRecord.model_validate(entry)
            except ValidationError as exc:
                errors.append(f"{path.relative_to(kb_dir)} (record_id={rid}): {exc}")
                continue
            if record.record_id in seen_ids:
                errors.append(f"{path.relative_to(kb_dir)}: duplicate record_id {record.record_id!r}")
                continue
            seen_ids.add(record.record_id)
            records.append(record)

    if errors:
        for err in errors:
            print(f"  ERROR: {err}")
        raise SystemExit(f"Aborting: {len(errors)} error(s) in knowledge_records/")
    return records


def check_referential_integrity(records: list[KnowledgeRecord], sources: dict[str, SourceRecord]) -> None:
    """Every record.source_id must resolve to a real entry in sources/inventory.json."""
    errors = [
        f"{r.record_id}: source_id {r.source_id!r} not found in sources/inventory.json"
        for r in records
        if r.source_id not in sources
    ]
    if errors:
        for err in errors:
            print(f"  ERROR: {err}")
        raise SystemExit(f"Aborting: {len(errors)} referential-integrity error(s)")


def render_document(record: KnowledgeRecord) -> Document:
    """Render one KnowledgeRecord's structured fields into readable prose."""
    parts = [record.description.strip()]
    if record.procedure:
        parts.append(f"Procedure: {record.procedure.strip()}")
    if record.required_information:
        parts.append("Required information: " + "; ".join(record.required_information))
    if record.required_documents:
        parts.append("Required documents: " + "; ".join(record.required_documents))
    if record.sla:
        parts.append(f"Service level: {record.sla}")
    if record.expected_response_time:
        parts.append(f"Expected response time: {record.expected_response_time}")
    if record.expected_resolution_time:
        parts.append(f"Expected resolution time: {record.expected_resolution_time}")
    if record.complaint_channel:
        parts.append("Complaint channels: " + "; ".join(record.complaint_channel))
    if record.contact_information:
        parts.append(f"Contact: {record.contact_information}")
    if record.escalation_procedure:
        parts.append(f"Escalation: {record.escalation_procedure}")
    if record.escalation_authority:
        parts.append(f"Escalation authority: {record.escalation_authority}")
    if record.citizen_guidance:
        parts.append(f"Guidance: {record.citizen_guidance}")
    for item in record.faq:
        parts.append(f"Q: {item.question} A: {item.answer}")

    # record.city is None for genuinely state-wide records (see KnowledgeRecord.city's
    # docstring) -- fall back to "<state>, state-wide" rather than letting an f-string render
    # the literal text "(None)" into the title.
    place = record.city or f"{record.state}, state-wide"
    return Document(
        document_id=f"DOC_{record.record_id}",
        record_id=record.record_id,
        title=f"{record.service_name} — {record.sub_service} ({place})",
        content="\n\n".join(parts),
        state=record.state,
        district=record.district,
        city=record.city,
        municipality=record.municipality,
        zone=record.zone,
        ward=record.ward,
        area=record.area,
        geographic_scope=record.geographic_scope,
        service_category=record.service_category,
        service_id=record.service_id,
        sub_service=record.sub_service,
        department=record.department,
        source_id=record.source_id,
        source_title=record.source_title,
        source_organization=record.source_organization,
        source_url=record.source_url,
        source_type=record.source_type,
        verification_status=record.verification_status,
    )


def chunk_document(document: Document, record: KnowledgeRecord) -> list[Chunk]:
    """Split one Document into retrieval-ready chunks, grouped by field family:
    description+procedure / required-info+docs+SLA / escalation / FAQ. Each chunk carries the
    full citation block so it's self-sufficient for a future retrieval pipeline."""
    groups: list[str] = []

    lead = record.description.strip()
    if record.procedure:
        lead += f"\n\nProcedure: {record.procedure.strip()}"
    groups.append(lead)

    mid_parts = []
    if record.required_information:
        mid_parts.append("Required information: " + "; ".join(record.required_information))
    if record.required_documents:
        mid_parts.append("Required documents: " + "; ".join(record.required_documents))
    if record.sla:
        mid_parts.append(f"Service level: {record.sla}")
    if record.expected_response_time:
        mid_parts.append(f"Expected response time: {record.expected_response_time}")
    if record.expected_resolution_time:
        mid_parts.append(f"Expected resolution time: {record.expected_resolution_time}")
    if mid_parts:
        groups.append("\n".join(mid_parts))

    esc_parts = []
    if record.complaint_channel:
        esc_parts.append("Complaint channels: " + "; ".join(record.complaint_channel))
    if record.contact_information:
        esc_parts.append(f"Contact: {record.contact_information}")
    if record.escalation_procedure:
        esc_parts.append(f"Escalation: {record.escalation_procedure}")
    if record.escalation_authority:
        esc_parts.append(f"Escalation authority: {record.escalation_authority}")
    if esc_parts:
        groups.append("\n".join(esc_parts))

    if record.faq:
        groups.append("\n".join(f"Q: {i.question} A: {i.answer}" for i in record.faq))

    chunks = []
    for i, content in enumerate(groups, start=1):
        if not content.strip():
            continue
        chunks.append(Chunk(
            chunk_id=f"{document.document_id}_C{i}",
            document_id=document.document_id,
            content=content.strip(),
            state=document.state,
            district=document.district,
            city=document.city,
            municipality=document.municipality,
            zone=document.zone,
            ward=document.ward,
            area=document.area,
            geographic_scope=document.geographic_scope,
            service_category=document.service_category,
            service_id=document.service_id,
            sub_service=document.sub_service,
            department=document.department,
            source_id=document.source_id,
            source_title=document.source_title,
            source_organization=document.source_organization,
            source_url=document.source_url,
            source_type=document.source_type,
            verification_status=document.verification_status,
        ))
    return chunks


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=_json_default), encoding="utf-8")


def print_stats(records: list[KnowledgeRecord]) -> None:
    from collections import Counter
    by_tier = Counter(r.verification_status.value for r in records)
    by_category = Counter(r.service_category.value for r in records)
    by_city = Counter(f"{r.city}, {r.state}" if r.city else f"{r.state} (state-wide, no single city)" for r in records)

    print(f"\nTotal knowledge records: {len(records)}")
    print("By verification tier:")
    for tier, count in sorted(by_tier.items()):
        print(f"  {tier}: {count}")
    print("By service category:")
    for cat, count in sorted(by_category.items()):
        print(f"  {cat}: {count}")
    print(f"Cities covered: {len(by_city)}")
    for city, count in sorted(by_city.items()):
        print(f"  {city}: {count}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Validate only, write nothing.")
    parser.add_argument("--stats", action="store_true", help="Print counts by tier/category/city.")
    args = parser.parse_args()

    sources = load_sources()
    records = load_knowledge_records()
    check_referential_integrity(records, sources)
    print(f"Loaded {len(sources)} source(s), {len(records)} knowledge record(s). All valid.")

    if args.stats:
        print_stats(records)

    if args.check:
        print("--check: validation passed, nothing written.")
        return

    documents = [render_document(r) for r in records]
    chunks = [c for d, r in zip(documents, records) for c in chunk_document(d, r)]

    write_json(settings.RAG_DATA_DIR / "documents" / "documents.json", [d.model_dump(mode="json") for d in documents])
    write_json(settings.RAG_DATA_DIR / "chunks" / "chunks.json", [c.model_dump(mode="json") for c in chunks])

    write_json(settings.RAG_DATA_DIR / "schema" / "knowledge_record.schema.json", KnowledgeRecord.model_json_schema())
    write_json(settings.RAG_DATA_DIR / "schema" / "source_record.schema.json", SourceRecord.model_json_schema())
    write_json(settings.RAG_DATA_DIR / "schema" / "chunk.schema.json", Chunk.model_json_schema())

    print(f"Wrote {len(documents)} document(s), {len(chunks)} chunk(s), 3 schema file(s).")


if __name__ == "__main__":
    main()

"""One-off generator for the SYNTHETIC tier of the RAG civic-knowledge-base data set.

Purpose: the VERIFIED tier (data/rag_knowledge_base/knowledge_records/verified/) is small and
slow to grow by design -- every fact in it is individually checked against a real, live
government source (see sources/candidate_urls.md for how much research one VERIFIED record
costs). Most Indian municipalities do not publish structured citizen-charter data online at all,
so "30+ cities, fully verified" is not achievable (confirmed with the user, see the approved
plan). This script is how the requested city/state *breadth* is achieved instead: four
representative templates (one per ServiceCategory), grounded in the SLA ranges and department/
escalation patterns actually observed across the VERIFIED batch (Odisha, Mohali, Patiala -- see
those files), stamped across a target list of Indian cities. Every output record is unmistakably
SYNTHETIC_REPRESENTATIVE: source_url=None, source_organization is the fixed
SYNTHETIC_SOURCE_ORGANIZATION string, geographic_scope=CITY but the department/officer/SLA
wording is generic and representative -- never copied from one specific city's real charter and
relabeled as another city's synthetic data.

This is a ONE-OFF generator, not part of the deterministic build pipeline (unlike
build_rag_knowledge_base.py, which regenerates documents/chunks from knowledge_records/ on every
run): it is run once, writes JSON files under knowledge_records/synthetic/, and those files are
then committed and hand-editable like any other knowledge record. Re-running it overwrites those
files with fresh output (same content, new retrieved_at/created_at timestamps) -- fine for a
full regeneration, but don't run it if you've since hand-edited a synthetic file you want to keep.

Usage:
    python scripts/generate_synthetic_rag_records.py
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.config import settings
from backend.schemas.rag_knowledge import (
    SYNTHETIC_SOURCE_ORGANIZATION,
    KnowledgeRecord,
    SourceType,
    VerificationStatus,
)

SYNTHETIC_SOURCE_ID = "SYNTHETIC_REPRESENTATIVE_DATA"

# (state, [cities]) -- 28 cities across 15 states/UTs, chosen for breadth across regions of
# India, deliberately disjoint from the VERIFIED tier's Odisha/Punjab coverage so the combined
# data set (14 VERIFIED + this SYNTHETIC batch) spans 17 states/UTs and 30 cities.
TARGET_CITIES: list[tuple[str, list[str]]] = [
    ("Maharashtra", ["Mumbai", "Nagpur"]),
    ("Karnataka", ["Bengaluru", "Mysuru"]),
    ("Tamil Nadu", ["Chennai", "Coimbatore"]),
    ("Telangana", ["Hyderabad", "Warangal"]),
    ("Andhra Pradesh", ["Vijayawada", "Visakhapatnam"]),
    ("Gujarat", ["Ahmedabad", "Surat"]),
    ("Rajasthan", ["Jaipur", "Jodhpur"]),
    ("Uttar Pradesh", ["Lucknow", "Varanasi"]),
    ("West Bengal", ["Kolkata", "Howrah"]),
    ("Madhya Pradesh", ["Bhopal", "Indore"]),
    ("Bihar", ["Patna", "Gaya"]),
    ("Kerala", ["Kochi", "Thiruvananthapuram"]),
    ("Haryana", ["Gurugram", "Faridabad"]),
    ("Delhi", ["New Delhi"]),
    ("Assam", ["Guwahati"]),
]


def _slug(text: str) -> str:
    return text.lower().replace(" ", "_").replace(".", "").replace("(", "").replace(")", "")


def _now() -> datetime:
    return datetime.now(timezone.utc)


def waste_record(state: str, city: str, now: datetime) -> KnowledgeRecord:
    return KnowledgeRecord(
        record_id=f"SYN_{_slug(state)}_{_slug(city)}_WASTE",
        service_id=f"WASTE_SOLID_WASTE_{_slug(city).upper()}",
        service_name="Solid Waste Collection & Sanitation Complaints",
        sub_service="Collection & disposal of municipal solid waste from roads / streets / localities",
        problem_type="Garbage not collected / solid waste not removed from a street or locality",
        service_category="WASTE_SANITATION",
        state=state,
        district=None,
        city=city,
        municipality=f"{city} Municipal Corporation",
        geographic_scope="CITY",
        department=f"{city} Municipal Corporation -- Solid Waste Management / Sanitation Department (representative structure; exact department name for {city} not individually verified)",
        authority="Ward-level Sanitary Inspector",
        description=(
            f"Representative service description for solid waste / garbage collection complaints in {city}, {state}. "
            "This is a SYNTHETIC record: it follows the same general shape and SLA range observed across the "
            "VERIFIED tier's real citizen charters (Odisha, Mohali, Patiala) but has not been individually checked "
            f"against a real {city} government source. Do not present any figure below as {city}'s actual official SLA."
        ),
        procedure=(
            "Typical process (representative, not city-specific): (1) Register the complaint via the municipal "
            "corporation's helpline/toll-free number, its online grievance portal, or a mobile complaint app, if "
            "available, or in person at the ward office / zonal office. (2) Provide the locality/ward and a contact "
            "phone number. (3) Note the complaint/reference number issued. (4) Track status via the same channel "
            "used to register."
        ),
        required_information=["Locality / ward", "Phone number of the complainant"],
        required_documents=[],
        sla="Representative range: 2-3 days, based on patterns observed in verified citizen charters (not city-specific).",
        expected_response_time=None,
        expected_resolution_time="2-3 days (representative range, not verified for this city)",
        complaint_channel=[
            "Municipal Corporation helpline / toll-free number (city-specific; not individually verified)",
            "Online citizen grievance portal or mobile app, if available for this city",
            "In person at the ward office or Municipal Corporation zonal office",
        ],
        contact_information=f"Contact the {city} Municipal Corporation's ward office or public helpline for this locality (specific number not verified for this synthetic record).",
        escalation_procedure=(
            "Representative escalation pattern observed across verified charters: Ward-level Sanitary Inspector -> "
            "Zonal / Assistant Health Officer -> Municipal Commissioner. Exact levels, officer titles, and time "
            f"norms for {city} have not been individually verified."
        ),
        escalation_authority="Representative chain: Sanitary Inspector -> Zonal/Assistant Health Officer -> Municipal Commissioner (not verified for this city).",
        faq=[
            {
                "question": f"Is this the official SLA for solid waste complaints in {city}?",
                "answer": "No -- this is a synthetic, representative record based on patterns seen in other cities' verified citizen charters, not a figure confirmed from an official source for this city.",
            }
        ],
        citizen_guidance="Confirm the exact helpline number and current SLA with your local municipal corporation, as this record is representative, not independently verified for this city.",
        source_id=SYNTHETIC_SOURCE_ID,
        source_title="Synthetic Representative Civic-Service Record",
        source_organization=SYNTHETIC_SOURCE_ORGANIZATION,
        source_url=None,
        source_type="SYNTHETIC_REPRESENTATIVE",
        verification_status="SYNTHETIC",
        publication_date=None,
        last_updated=None,
        retrieved_at=now,
        created_at=now,
    )


def water_record(state: str, city: str, now: datetime) -> KnowledgeRecord:
    return KnowledgeRecord(
        record_id=f"SYN_{_slug(state)}_{_slug(city)}_WATER",
        service_id=f"WATER_SUPPLY_DRAINAGE_{_slug(city).upper()}",
        service_name="Water Supply & Drainage Complaints",
        sub_service="Water supply pipeline leakage / sewerage or drainage blockage / overflow",
        problem_type="Water pipeline leakage, sewerage blockage, or storm-water drainage overflow",
        service_category="WATER_DRAINAGE",
        state=state,
        district=None,
        city=city,
        municipality=f"{city} Municipal Corporation",
        geographic_scope="CITY",
        department=f"{city} Municipal Corporation / Water Supply & Sewerage Board -- Public Health Engineering wing (representative structure; exact department name for {city} not individually verified)",
        authority="Junior Engineer (ward/zone-level)",
        description=(
            f"Representative service description for water supply and drainage complaints in {city}, {state}. "
            "This is a SYNTHETIC record following the general shape and SLA range observed across the VERIFIED "
            f"tier's real citizen charters, not individually checked against a real {city} government source."
        ),
        procedure=(
            "Typical process (representative, not city-specific): (1) Register the complaint via the water board's "
            "or municipal corporation's helpline/toll-free number, online portal, or mobile app, if available, or "
            "in person at the water works / engineering division office. (2) Provide the exact location and a "
            "contact phone number. (3) Note the complaint/reference number issued. (4) Track status via the same "
            "channel used to register."
        ),
        required_information=["Location of the leak / blockage / overflow", "Phone number of the complainant"],
        required_documents=[],
        sla="Representative range: 2-4 days for a leakage/blockage complaint, based on patterns observed in verified citizen charters (not city-specific).",
        expected_response_time=None,
        expected_resolution_time="2-4 days (representative range, not verified for this city)",
        complaint_channel=[
            "Water board / Municipal Corporation helpline (city-specific; not individually verified)",
            "Online citizen grievance portal or mobile app, if available for this city",
            "In person at the water works / engineering division office",
        ],
        contact_information=f"Contact the {city} Municipal Corporation's water supply/engineering division for this locality (specific number not verified for this synthetic record).",
        escalation_procedure=(
            "Representative escalation pattern observed across verified charters: Junior Engineer -> Assistant/"
            f"Executive Engineer -> Municipal Commissioner. Exact levels and time norms for {city} have not been "
            "individually verified."
        ),
        escalation_authority="Representative chain: Junior Engineer -> Assistant/Executive Engineer -> Municipal Commissioner (not verified for this city).",
        faq=[
            {
                "question": f"Is this the official SLA for water/drainage complaints in {city}?",
                "answer": "No -- this is a synthetic, representative record based on patterns seen in other cities' verified citizen charters, not a figure confirmed from an official source for this city.",
            }
        ],
        citizen_guidance="Confirm the exact helpline number and current SLA with your local water board or municipal corporation, as this record is representative, not independently verified for this city.",
        source_id=SYNTHETIC_SOURCE_ID,
        source_title="Synthetic Representative Civic-Service Record",
        source_organization=SYNTHETIC_SOURCE_ORGANIZATION,
        source_url=None,
        source_type="SYNTHETIC_REPRESENTATIVE",
        verification_status="SYNTHETIC",
        publication_date=None,
        last_updated=None,
        retrieved_at=now,
        created_at=now,
    )


def roads_record(state: str, city: str, now: datetime) -> KnowledgeRecord:
    return KnowledgeRecord(
        record_id=f"SYN_{_slug(state)}_{_slug(city)}_ROADS",
        service_id=f"ROADS_POTHOLES_{_slug(city).upper()}",
        service_name="Road & Pothole Repair Complaints",
        sub_service="Pothole / road surface damage repair",
        problem_type="Pothole or damaged road surface needing repair",
        service_category="ROADS_POTHOLES",
        state=state,
        district=None,
        city=city,
        municipality=f"{city} Municipal Corporation",
        geographic_scope="CITY",
        department=f"{city} Municipal Corporation -- Engineering (Civil) Department (representative structure; exact department name for {city} not individually verified)",
        authority="Junior Engineer, Civil (ward/zone-level)",
        description=(
            f"Representative service description for pothole/road-damage complaints in {city}, {state}. This is a "
            "SYNTHETIC record following the general shape and SLA range observed across the VERIFIED tier's real "
            f"citizen charters, not individually checked against a real {city} government source."
        ),
        procedure=(
            "Typical process (representative, not city-specific): (1) Register the complaint via the municipal "
            "corporation's helpline/toll-free number, online portal, or mobile app, if available, or in person at "
            "the ward engineering office. (2) Provide the exact road/location and a contact phone number. (3) Note "
            "the complaint/reference number issued. (4) Track status via the same channel used to register."
        ),
        required_information=["Exact road / location of the pothole or damage", "Phone number of the complainant"],
        required_documents=[],
        sla="Representative range: 7-15 days, based on patterns observed in verified citizen charters (not city-specific).",
        expected_response_time=None,
        expected_resolution_time="7-15 days (representative range, not verified for this city)",
        complaint_channel=[
            "Municipal Corporation helpline / toll-free number (city-specific; not individually verified)",
            "Online citizen grievance portal or mobile app, if available for this city",
            "In person at the ward engineering office",
        ],
        contact_information=f"Contact the {city} Municipal Corporation's engineering (civil) division for this locality (specific number not verified for this synthetic record).",
        escalation_procedure=(
            "Representative escalation pattern observed across verified charters: Junior Engineer (Civil) -> "
            f"Executive Engineer -> City Engineer / Municipal Commissioner. Exact levels and time norms for {city} "
            "have not been individually verified."
        ),
        escalation_authority="Representative chain: Junior Engineer (Civil) -> Executive Engineer -> City Engineer/Municipal Commissioner (not verified for this city).",
        faq=[
            {
                "question": f"Is this the official SLA for pothole repair in {city}?",
                "answer": "No -- this is a synthetic, representative record based on patterns seen in other cities' verified citizen charters, not a figure confirmed from an official source for this city.",
            }
        ],
        citizen_guidance="Confirm the exact helpline number and current SLA with your local municipal corporation, as this record is representative, not independently verified for this city.",
        source_id=SYNTHETIC_SOURCE_ID,
        source_title="Synthetic Representative Civic-Service Record",
        source_organization=SYNTHETIC_SOURCE_ORGANIZATION,
        source_url=None,
        source_type="SYNTHETIC_REPRESENTATIVE",
        verification_status="SYNTHETIC",
        publication_date=None,
        last_updated=None,
        retrieved_at=now,
        created_at=now,
    )


def streetlight_record(state: str, city: str, now: datetime) -> KnowledgeRecord:
    return KnowledgeRecord(
        record_id=f"SYN_{_slug(state)}_{_slug(city)}_STREETLIGHTS",
        service_id=f"STREETLIGHTS_{_slug(city).upper()}",
        service_name="Street Light Repair / Not Working Complaints",
        sub_service="Street light not working / damaged, repair or replacement",
        problem_type="Street light not working or damaged",
        service_category="STREETLIGHTS",
        state=state,
        district=None,
        city=city,
        municipality=f"{city} Municipal Corporation",
        geographic_scope="CITY",
        department=f"{city} Municipal Corporation -- Engineering (Electrical) Department (representative structure; exact department name for {city} not individually verified)",
        authority="Junior Engineer, Electrical (ward/zone-level)",
        description=(
            f"Representative service description for street light complaints in {city}, {state}. This is a "
            "SYNTHETIC record following the general shape and SLA range observed across the VERIFIED tier's real "
            f"citizen charters, not individually checked against a real {city} government source."
        ),
        procedure=(
            "Typical process (representative, not city-specific): (1) Register the complaint via the municipal "
            "corporation's helpline/toll-free number, online portal, or mobile app, if available, or in person at "
            "the ward electrical engineering office. (2) Provide the locality/pole number, if known, and a contact "
            "phone number. (3) Note the complaint/reference number issued. (4) Track status via the same channel "
            "used to register."
        ),
        required_information=["Locality / pole number, if known", "Phone number of the complainant"],
        required_documents=[],
        sla="Representative range: 7-10 days, based on patterns observed in verified citizen charters (not city-specific).",
        expected_response_time=None,
        expected_resolution_time="7-10 days (representative range, not verified for this city)",
        complaint_channel=[
            "Municipal Corporation helpline / toll-free number (city-specific; not individually verified)",
            "Online citizen grievance portal or mobile app, if available for this city",
            "In person at the ward electrical engineering office",
        ],
        contact_information=f"Contact the {city} Municipal Corporation's engineering (electrical) division for this locality (specific number not verified for this synthetic record).",
        escalation_procedure=(
            "Representative escalation pattern observed across verified charters: Junior Engineer (Electrical) -> "
            f"Assistant Executive Engineer -> Municipal Commissioner. Exact levels and time norms for {city} have "
            "not been individually verified."
        ),
        escalation_authority="Representative chain: Junior Engineer (Electrical) -> Assistant Executive Engineer -> Municipal Commissioner (not verified for this city).",
        faq=[
            {
                "question": f"Is this the official SLA for street light repair in {city}?",
                "answer": "No -- this is a synthetic, representative record based on patterns seen in other cities' verified citizen charters, not a figure confirmed from an official source for this city.",
            }
        ],
        citizen_guidance="Confirm the exact helpline number and current SLA with your local municipal corporation, as this record is representative, not independently verified for this city.",
        source_id=SYNTHETIC_SOURCE_ID,
        source_title="Synthetic Representative Civic-Service Record",
        source_organization=SYNTHETIC_SOURCE_ORGANIZATION,
        source_url=None,
        source_type="SYNTHETIC_REPRESENTATIVE",
        verification_status="SYNTHETIC",
        publication_date=None,
        last_updated=None,
        retrieved_at=now,
        created_at=now,
    )


def main() -> None:
    now = _now()
    out_dir = settings.RAG_DATA_DIR / "knowledge_records" / "synthetic"
    total_records = 0
    total_cities = 0

    for state, cities in TARGET_CITIES:
        state_dir = out_dir / _slug(state)
        for city in cities:
            records = [
                waste_record(state, city, now),
                water_record(state, city, now),
                roads_record(state, city, now),
                streetlight_record(state, city, now),
            ]
            path = state_dir / f"{_slug(city)}.json"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(
                json.dumps([r.model_dump(mode="json") for r in records], ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            total_records += len(records)
            total_cities += 1

    print(f"Wrote {total_records} synthetic knowledge record(s) across {total_cities} cities in {len(TARGET_CITIES)} states/UTs.")


if __name__ == "__main__":
    main()

"""Seeds the location-hierarchy master data (states/districts/ulbs/wards/localities).

Two very different rigor levels are deliberately mixed here, and each row's source_type says
which applies:

1. STATES (all 36): the full, canonical list of Indian states/UTs. This is settled
   constitutional/administrative fact (not a claim requiring per-record live-source
   verification the way RAG civic-service SLA data does) -- confirmed live against the National
   Portal of India during this session (see source_url on every row: HTTP 200, checked
   2026-08-10). source_type="OFFICIAL_NATIONAL_REFERENCE".

2. DISTRICTS/ULBs for the 6 real cities that actually appear in this project's live
   users/complaints ward data (queried fresh from janmitra.db, not assumed) -- which state/
   district/ULB a major Indian city belongs to is treated as well-established public knowledge,
   not independently re-verified against a live URL this session, and is labeled as such
   (source_type="WELL_ESTABLISHED_PUBLIC_GEOGRAPHY", source_url=None -- no URL fabricated).

3. WARDS/LOCALITIES for those same 6 cities: these ward-number-to-locality pairings come from
   this project's OWN pre-existing demo/seed data (scripts/seed_multi_ward_data.py), authored
   for development purposes, NOT independently verified against any official ward-delimitation
   source (ward boundaries are redrawn periodically; nobody has checked whether "Ward 22" is
   still, today, officially Kothrud). Labeled source_type="UNVERIFIED_APP_SEED_DATA" so nothing
   downstream mistakes these for verified administrative fact.

Deliberately NOT seeded here: "Ward 14 -- Rukadi Road" and "Ward 9 -- Shivaji Nagar" (both
present in the live database) have no city recorded anywhere in this project (checked
test_accounts.csv and the DB itself) -- creating a ULB/ward for them would require guessing
which city, so they are left entirely unmapped. See reports/location_migration_report.md.

Also NOT seeded here: the RAG knowledge base's verified cities (Odisha state-wide, Mohali,
Patiala) -- real and already verified in data/rag_knowledge_base/, but not part of the
*application's* current location needs (no user/worker/complaint currently references them), so
adding them to this table now would be outside this migration's explicit scope
("start with the location coverage actually required by the existing application/demo data").
Left as an explicit gap for a future pass, not silently merged in.

Idempotent: every insert checks for an existing row first (by natural key), so re-running this
adds nothing new on a second run.

Usage:
    python scripts/seed_location_master_data.py
"""

import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy.orm import Session

from backend.database import SessionLocal
from backend.models import ULB, District, Locality, State, Ward

NOW = datetime.now(timezone.utc)

OFFICIAL_NATIONAL_SOURCE = {
    "source_name": "National Portal of India (India.gov.in) -- Explore India / States & UTs",
    "source_type": "OFFICIAL_NATIONAL_REFERENCE",
    "source_url": "https://www.india.gov.in/explore-india",
}
WELL_KNOWN_GEOGRAPHY_SOURCE = {
    "source_name": "Well-established public administrative geography (which state/district a "
    "major Indian city belongs to) -- not independently re-verified against a fetched live URL "
    "this session; no URL is claimed to avoid fabricating one.",
    "source_type": "WELL_ESTABLISHED_PUBLIC_GEOGRAPHY",
    "source_url": None,
}
UNVERIFIED_SEED_SOURCE = {
    "source_name": "Existing Sarthi demo/seed data (scripts/seed_multi_ward_data.py) -- "
    "ward-number-to-locality mapping authored for development purposes, NOT independently "
    "verified against an official ward-delimitation source.",
    "source_type": "UNVERIFIED_APP_SEED_DATA",
    "source_url": None,
}

# (name, code, is_union_territory)
STATES_AND_UTS: list[tuple[str, str, bool]] = [
    ("Andhra Pradesh", "AP", False),
    ("Arunachal Pradesh", "AR", False),
    ("Assam", "AS", False),
    ("Bihar", "BR", False),
    ("Chhattisgarh", "CG", False),
    ("Goa", "GA", False),
    ("Gujarat", "GJ", False),
    ("Haryana", "HR", False),
    ("Himachal Pradesh", "HP", False),
    ("Jharkhand", "JH", False),
    ("Karnataka", "KA", False),
    ("Kerala", "KL", False),
    ("Madhya Pradesh", "MP", False),
    ("Maharashtra", "MH", False),
    ("Manipur", "MN", False),
    ("Meghalaya", "ML", False),
    ("Mizoram", "MZ", False),
    ("Nagaland", "NL", False),
    ("Odisha", "OD", False),
    ("Punjab", "PB", False),
    ("Rajasthan", "RJ", False),
    ("Sikkim", "SK", False),
    ("Tamil Nadu", "TN", False),
    ("Telangana", "TG", False),
    ("Tripura", "TR", False),
    ("Uttar Pradesh", "UP", False),
    ("Uttarakhand", "UK", False),
    ("West Bengal", "WB", False),
    ("Andaman and Nicobar Islands", "AN", True),
    ("Chandigarh", "CH", True),
    ("Dadra and Nagar Haveli and Daman and Diu", "DN", True),
    ("Delhi", "DL", True),
    ("Jammu and Kashmir", "JK", True),
    ("Ladakh", "LA", True),
    ("Lakshadweep", "LD", True),
    ("Puducherry", "PY", True),
]
assert len(STATES_AND_UTS) == 36, f"Expected 36 states/UTs, got {len(STATES_AND_UTS)}"
assert sum(1 for _, _, ut in STATES_AND_UTS if not ut) == 28
assert sum(1 for _, _, ut in STATES_AND_UTS if ut) == 8

# Real cities that actually appear in janmitra.db's live users/complaints ward strings today
# (queried fresh from the database, not assumed -- see reports/location_migration_report.md).
# (state_code, district_name, ulb_name, ulb_type, [(ward_number, ward_name_as_seeded, locality_name)])
CITIES: list[tuple[str, str, str, str, list[tuple[str, str, str]]]] = [
    ("MH", "Pune", "Pune Municipal Corporation", "Municipal Corporation",
     [("22", "Ward 22", "Kothrud")]),
    ("UP", "Kanpur Nagar", "Kanpur Municipal Corporation", "Municipal Corporation",
     [("8", "Ward 8", "Civil Lines")]),
    ("OD", "Khordha", "Bhubaneswar Municipal Corporation", "Municipal Corporation",
     [("5", "Ward 5", "Saheed Nagar")]),
    ("GJ", "Ahmedabad", "Ahmedabad Municipal Corporation", "Municipal Corporation",
     [("11", "Ward 11", "Navrangpura")]),
    ("WB", "Kolkata", "Kolkata Municipal Corporation", "Municipal Corporation",
     [("6", "Ward 6", "Salt Lake")]),
    ("KA", "Bengaluru Urban", "Bruhat Bengaluru Mahanagara Palike (BBMP)", "Municipal Corporation",
     [("3", "Ward 3", "Indiranagar")]),
]


def get_or_create_state(db: Session, name: str, code: str, is_ut: bool) -> State:
    existing = db.query(State).filter(State.code == code).first()
    if existing:
        return existing
    state = State(
        name=name, code=code, country_code="IN", is_union_territory=is_ut,
        created_at=NOW, updated_at=NOW, **OFFICIAL_NATIONAL_SOURCE,
    )
    db.add(state)
    db.flush()
    return state


def get_or_create_district(db: Session, state: State, name: str) -> District:
    existing = db.query(District).filter(District.state_id == state.id, District.name == name).first()
    if existing:
        return existing
    district = District(
        state_id=state.id, name=name, created_at=NOW, updated_at=NOW, **WELL_KNOWN_GEOGRAPHY_SOURCE,
    )
    db.add(district)
    db.flush()
    return district


def get_or_create_ulb(db: Session, district: District, name: str, ulb_type: str) -> ULB:
    existing = db.query(ULB).filter(ULB.district_id == district.id, ULB.name == name).first()
    if existing:
        return existing
    ulb = ULB(
        district_id=district.id, name=name, type=ulb_type,
        created_at=NOW, updated_at=NOW, **WELL_KNOWN_GEOGRAPHY_SOURCE,
    )
    db.add(ulb)
    db.flush()
    return ulb


def get_or_create_ward(db: Session, ulb: ULB, name: str, ward_number: str) -> Ward:
    existing = db.query(Ward).filter(Ward.ulb_id == ulb.id, Ward.name == name).first()
    if existing:
        return existing
    ward = Ward(
        ulb_id=ulb.id, name=name, ward_number=ward_number,
        created_at=NOW, updated_at=NOW, **UNVERIFIED_SEED_SOURCE,
    )
    db.add(ward)
    db.flush()
    return ward


def get_or_create_locality(db: Session, ward: Ward, name: str) -> Locality:
    existing = db.query(Locality).filter(Locality.ward_id == ward.id, Locality.name == name).first()
    if existing:
        return existing
    locality = Locality(
        ward_id=ward.id, name=name, created_at=NOW, updated_at=NOW, **UNVERIFIED_SEED_SOURCE,
    )
    db.add(locality)
    db.flush()
    return locality


def main() -> None:
    db = SessionLocal()
    try:
        print(f"Seeding {len(STATES_AND_UTS)} states/UTs...")
        states_by_code: dict[str, State] = {}
        for name, code, is_ut in STATES_AND_UTS:
            states_by_code[code] = get_or_create_state(db, name, code, is_ut)
        db.commit()
        print(f"  {db.query(State).count()} state/UT rows now in the database.")

        print(f"\nSeeding {len(CITIES)} cities' district/ULB/ward/locality (from live app data)...")
        for state_code, district_name, ulb_name, ulb_type, wards in CITIES:
            state = states_by_code[state_code]
            district = get_or_create_district(db, state, district_name)
            ulb = get_or_create_ulb(db, district, ulb_name, ulb_type)
            for ward_number, ward_name, locality_name in wards:
                ward = get_or_create_ward(db, ulb, ward_name, ward_number)
                get_or_create_locality(db, ward, locality_name)
            print(f"  {state.name} > {district.name} > {ulb.name}: {len(wards)} ward(s)")
        db.commit()

        print(
            f"\nFinal counts: {db.query(State).count()} states/UTs, "
            f"{db.query(District).count()} districts, {db.query(ULB).count()} ULBs, "
            f"{db.query(Ward).count()} wards, {db.query(Locality).count()} localities."
        )
        print(
            "\nNOT seeded (see this script's docstring + reports/location_migration_report.md): "
            "'Ward 14 -- Rukadi Road', 'Ward 9 -- Shivaji Nagar' (no city recorded anywhere), "
            "and all 'Tracking Test Ward <timestamp>' entries (Playwright test artifacts)."
        )
    finally:
        db.close()


if __name__ == "__main__":
    main()

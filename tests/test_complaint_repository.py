"""Tests for the repository layer introduced in the SERVICE FLOW + SELECTIVE LANGCHAIN
INTEGRATION phase (backend/repositories/complaint_repository.py) -- see that module's docstring
for the LangGraph -> service -> repository -> database layering this enforces.
"""

from __future__ import annotations

from backend.models import Complaint, User
from backend.repositories import complaint_repository
from backend.services.auth_service import hash_password


def test_get_complaint_by_id_found(db_session):
    db = db_session()
    complaint = Complaint(citizen_id="1", original_text="x", original_language="en", translated_text="x", summary="x", status="pending")
    db.add(complaint)
    db.commit()
    db.refresh(complaint)
    cid = complaint.id
    db.close()

    db = db_session()
    found = complaint_repository.get_complaint_by_id(db, cid)
    assert found is not None
    assert found.id == cid
    db.close()


def test_get_complaint_by_id_not_found_returns_none(db_session):
    db = db_session()
    assert complaint_repository.get_complaint_by_id(db, 999999) is None
    db.close()


def test_get_user_by_id_found_and_missing(db_session):
    db = db_session()
    user = User(full_name="Test Worker", phone="9111111111", password_hash=hash_password("x"), role="worker", preferred_language="en")
    db.add(user)
    db.commit()
    db.refresh(user)
    uid = user.id
    db.close()

    db = db_session()
    assert complaint_repository.get_user_by_id(db, uid).full_name == "Test Worker"
    assert complaint_repository.get_user_by_id(db, 999999) is None
    db.close()


def test_save_complaint_location_sets_ward_only(db_session):
    db = db_session()
    complaint = Complaint(citizen_id="1", original_text="x", original_language="en", translated_text="x", summary="x", status="pending")
    db.add(complaint)
    db.commit()
    db.refresh(complaint)

    complaint_repository.save_complaint_location(db, complaint, ward="Mohali")
    assert complaint.ward == "Mohali"
    db.close()


def test_save_complaint_location_applies_structured_chain(db_session):
    db = db_session()
    complaint = Complaint(citizen_id="1", original_text="x", original_language="en", translated_text="x", summary="x", status="pending")
    db.add(complaint)
    db.commit()
    db.refresh(complaint)

    chain = {"state_id": 1, "district_id": None, "sub_district_id": None, "ulb_id": 2, "zone_id": None, "ward_id": 3, "locality_id": None}
    complaint_repository.save_complaint_location(db, complaint, ward="Ward 3 — Sector 70, Mohali", location_chain=chain)
    assert complaint.state_id == 1
    assert complaint.ulb_id == 2
    assert complaint.ward_id == 3
    assert complaint.ward == "Ward 3 — Sector 70, Mohali"
    db.close()


def test_save_complaint_location_never_overwrites_existing_address(db_session):
    """A resolver-provided formatted address must never clobber a citizen-typed one -- same rule
    routes/complaints.py's own equivalent logic already enforces."""
    db = db_session()
    complaint = Complaint(
        citizen_id="1", original_text="x", original_language="en", translated_text="x", summary="x",
        status="pending", address="123 Citizen-typed Street",
    )
    db.add(complaint)
    db.commit()
    db.refresh(complaint)

    complaint_repository.save_complaint_location(db, complaint, formatted_address="Resolver Address, Somewhere")
    assert complaint.address == "123 Citizen-typed Street"
    db.close()


def test_save_complaint_location_fills_address_when_absent(db_session):
    db = db_session()
    complaint = Complaint(citizen_id="1", original_text="x", original_language="en", translated_text="x", summary="x", status="pending")
    db.add(complaint)
    db.commit()
    db.refresh(complaint)

    complaint_repository.save_complaint_location(db, complaint, formatted_address="Resolver Address, Somewhere")
    assert complaint.address == "Resolver Address, Somewhere"
    db.close()

"""Tests for the read-only cascading location lookup endpoints (backend/routes/locations.py) --
backs the optional State/City/Ward/Area picker on Signup. Reuses `_seed_full_hierarchy` from
test_location_system.py (same real State->District->ULB->Ward->Locality chain already used
there) rather than duplicating seed logic.
"""

from backend.models import District, State
from tests.test_location_system import _seed_full_hierarchy


def test_list_states_returns_seeded_states(client, db_session):
    db = db_session()
    _seed_full_hierarchy(db)
    db.close()

    response = client.get("/locations/states")
    assert response.status_code == 200
    names = [s["name"] for s in response.json()]
    assert "Test State" in names


def test_list_states_is_unauthenticated(client, db_session):
    """No Authorization header at all -- Signup needs this before a citizen has a token."""
    response = client.get("/locations/states")
    assert response.status_code == 200


def test_list_cities_for_state_returns_real_districts(client, db_session):
    db = db_session()
    chain = _seed_full_hierarchy(db)
    state_id = chain["state"].id
    db.close()

    response = client.get(f"/locations/states/{state_id}/cities")
    assert response.status_code == 200
    names = [c["name"] for c in response.json()]
    assert names == ["Test District"]


def test_list_cities_for_state_with_no_districts_returns_empty_list_not_error(client, db_session):
    """A state with zero seeded cities (30 of 36 states today) must return an honest empty
    list -- never an error, and never a fabricated city."""
    db = db_session()
    state = State(name="Empty State", code="ES", country_code="IN", is_union_territory=False)
    db.add(state)
    db.commit()
    state_id = state.id
    db.close()

    response = client.get(f"/locations/states/{state_id}/cities")
    assert response.status_code == 200
    assert response.json() == []


def test_list_cities_for_nonexistent_state_is_404(client, db_session):
    response = client.get("/locations/states/999999/cities")
    assert response.status_code == 404


def test_list_wards_for_city_returns_real_wards(client, db_session):
    db = db_session()
    chain = _seed_full_hierarchy(db)
    district_id = chain["district"].id
    db.close()

    response = client.get(f"/locations/cities/{district_id}/wards")
    assert response.status_code == 200
    names = [w["name"] for w in response.json()]
    assert names == ["Ward 99 — Testville, Test City"]


def test_list_wards_for_city_with_no_ulb_returns_empty_list(client, db_session):
    db = db_session()
    chain = _seed_full_hierarchy(db)
    state_id = chain["state"].id
    district = District(state_id=state_id, name="No-ULB District")
    db.add(district)
    db.commit()
    district_id = district.id
    db.close()

    response = client.get(f"/locations/cities/{district_id}/wards")
    assert response.status_code == 200
    assert response.json() == []


def test_list_wards_for_nonexistent_city_is_404(client, db_session):
    response = client.get("/locations/cities/999999/wards")
    assert response.status_code == 404


def test_list_localities_for_ward_returns_real_localities(client, db_session):
    db = db_session()
    chain = _seed_full_hierarchy(db)
    ward_id = chain["ward"].id
    db.close()

    response = client.get(f"/locations/wards/{ward_id}/localities")
    assert response.status_code == 200
    names = [l["name"] for l in response.json()]
    assert names == ["Testville"]


def test_list_localities_for_nonexistent_ward_is_404(client, db_session):
    response = client.get("/locations/wards/999999/localities")
    assert response.status_code == 404

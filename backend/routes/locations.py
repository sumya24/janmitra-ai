"""Read-only cascading lookups over the structured location hierarchy (State -> District (shown
to citizens as "city") -> ULB -> Ward -> Locality, see models.py). Backs the optional
State/City/Ward/Area picker on the signup form (routes/auth.py's SignupRequest) -- entirely
additive: nothing here changes what the existing free-text `ward` field does, and no other part
of the app reads `User.home_*_id` yet (see that field's own docstring in models.py).

Deliberately unauthenticated, same reasoning as GET /complaints/wards: this needs to work before
a citizen has a token, from the signup page itself.

Deliberately never fabricates data: only 6 of India's 36 states/UTs have real seeded
district/ULB/ward/locality data today (see scripts/seed_multi_ward_data*.py) -- every endpoint
here just returns whatever real rows exist, including an empty list for a state/city/ward that
has nothing under it yet. The frontend falls back to free-text entry in that case, exactly like
the existing ward field already does when GET /complaints/wards comes back empty.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import District, Locality, State, ULB, Ward

router = APIRouter(prefix="/locations", tags=["locations"])


class LocationOption(BaseModel):
    """One selectable node at any level of the hierarchy -- deliberately the same shape at every
    level (id + display name) so the frontend can use one generic picker component for all four
    steps."""

    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


@router.get("/states", response_model=list[LocationOption])
def list_states(db: Session = Depends(get_db)) -> list[State]:
    return db.query(State).order_by(State.name).all()


@router.get("/states/{state_id}/cities", response_model=list[LocationOption])
def list_cities(state_id: int, db: Session = Depends(get_db)) -> list[District]:
    """"City" here is a District row -- the level whose `name` is the citizen-recognizable city
    name (e.g. "Pune"), as opposed to ULB.name, the formal civic-body name (e.g. "Pune Municipal
    Corporation") that a citizen wouldn't naturally search for."""
    if db.query(State).filter(State.id == state_id).first() is None:
        raise HTTPException(status_code=404, detail="State not found.")
    return db.query(District).filter(District.state_id == state_id).order_by(District.name).all()


@router.get("/cities/{district_id}/wards", response_model=list[LocationOption])
def list_wards(district_id: int, db: Session = Depends(get_db)) -> list[Ward]:
    if db.query(District).filter(District.id == district_id).first() is None:
        raise HTTPException(status_code=404, detail="City not found.")
    ulb_ids = [row[0] for row in db.query(ULB.id).filter(ULB.district_id == district_id).all()]
    if not ulb_ids:
        return []
    return db.query(Ward).filter(Ward.ulb_id.in_(ulb_ids)).order_by(Ward.name).all()


@router.get("/wards/{ward_id}/localities", response_model=list[LocationOption])
def list_localities(ward_id: int, db: Session = Depends(get_db)) -> list[Locality]:
    if db.query(Ward).filter(Ward.id == ward_id).first() is None:
        raise HTTPException(status_code=404, detail="Ward not found.")
    return db.query(Locality).filter(Locality.ward_id == ward_id).order_by(Locality.name).all()

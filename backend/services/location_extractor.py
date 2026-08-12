"""Resolves a question's location for RAG retrieval -- from explicit text, or from GPS via the
existing LocationResolver -- against the RAG knowledge base's OWN gazetteer of city/state names.

This closes a gap the prior location-migration audit explicitly flagged as unintegrated
(docs/ask_janmitra_response_behavior.md §3): `LocationResolver.resolve_coordinates()` resolves
GPS to a city/state *name* matched against the app's `states/districts/ulbs` tables (6 cities);
the RAG knowledge base's `state`/`city` fields are separate, denormalized text on each `Chunk`
(30 cities). Nothing previously matched one against the other. `resolve_from_coordinates()` below
is that missing matching step -- it re-resolves the GPS-derived city NAME (not ID) against the
RAG gazetteer specifically, so RAG's own (broader, 30-city) coverage is usable via GPS, not just
the app's own (narrower, 6-city) location-hierarchy tables.

Gazetteer built directly from data/rag_knowledge_base/chunks/chunks.json's own distinct
state/city values -- never a hand-typed list that could drift from what's actually retrievable.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

from backend.services.location_resolver import LocationResolver

# Aliases for RAG gazetteer entries whose canonical chunk-metadata name a citizen would rarely
# type verbatim (e.g. nobody types "Sahibzada Ajit Singh Nagar (Mohali)" -- they say "Mohali").
_CITY_ALIASES: dict[str, str] = {
    "mohali": "Sahibzada Ajit Singh Nagar (Mohali)",
    "sas nagar": "Sahibzada Ajit Singh Nagar (Mohali)",
    "delhi": "New Delhi",
    "bangalore": "Bengaluru",
    "mysore": "Mysuru",
    "trivandrum": "Thiruvananthapuram",
}


@dataclass
class LocationResolution:
    """What could be determined about a question's location, and how."""

    city: str | None = None  # exact RAG-gazetteer city name (canonical, not the alias typed)
    state: str | None = None  # exact RAG-gazetteer state name
    source: str = "none"  # "text" | "gps" | "conversation_history" | "none"
    is_ambiguous: bool = False
    ambiguous_candidates: list[str] = field(default_factory=list)  # candidate city names, if is_ambiguous
    warnings: list[str] = field(default_factory=list)


class RagGazetteer:
    """The set of city/state names actually present in the RAG knowledge base -- loaded once
    from chunks.json, not hand-maintained, so it can never silently drift out of sync with what
    the retriever can actually serve."""

    def __init__(self, chunks_path: Path) -> None:
        chunks = json.loads(chunks_path.read_text(encoding="utf-8"))
        self.cities: set[str] = {c["city"] for c in chunks if c["city"]}
        self.states: set[str] = {c["state"] for c in chunks}
        # state -> set of its cities actually present in the corpus (for ambiguity detection --
        # e.g. Odisha's records are all state-wide/city=None, so it has zero "cities" here, while
        # Punjab has two: Mohali and Patiala).
        self.cities_by_state: dict[str, set[str]] = {}
        for c in chunks:
            if c["city"]:
                self.cities_by_state.setdefault(c["state"], set()).add(c["city"])

    def find_city(self, text: str) -> str | None:
        lowered = text.lower()
        for alias, canonical in _CITY_ALIASES.items():
            if re.search(rf"\b{re.escape(alias)}\b", lowered):
                return canonical
        for city in self.cities:
            if re.search(rf"\b{re.escape(city.lower())}\b", lowered):
                return city
        return None

    def find_state(self, text: str) -> str | None:
        lowered = text.lower()
        for state in self.states:
            if re.search(rf"\b{re.escape(state.lower())}\b", lowered):
                return state
        return None


class LocationExtractor:
    """Combines text matching and GPS resolution against the RAG gazetteer."""

    def __init__(self, gazetteer: RagGazetteer, location_resolver: LocationResolver | None = None) -> None:
        self._gazetteer = gazetteer
        self._location_resolver = location_resolver or LocationResolver()

    def resolve_from_text(self, text: str) -> LocationResolution:
        """City wins over state when both are found in the text (more specific). If only a state
        is found and that state has more than one city in the RAG corpus, flags ambiguous rather
        than silently picking one -- exactly the "Street light problem in Punjab" case from the
        spec (Mohali and Patiala both have real, different figures)."""
        city = self._gazetteer.find_city(text)
        if city:
            # Recover which state this city belongs to, for completeness in the response.
            state = next((s for s, cities in self._gazetteer.cities_by_state.items() if city in cities), None)
            return LocationResolution(city=city, state=state, source="text")

        state = self._gazetteer.find_state(text)
        if state:
            candidates = sorted(self._gazetteer.cities_by_state.get(state, set()))
            if len(candidates) > 1:
                return LocationResolution(
                    state=state, source="text", is_ambiguous=True, ambiguous_candidates=candidates,
                    warnings=[f"Multiple cities with data exist in {state}: {', '.join(candidates)}."],
                )
            if len(candidates) == 1:
                return LocationResolution(city=candidates[0], state=state, source="text")
            # State matched but has no city-level records (e.g. Odisha -- all state-wide) --
            # a genuinely usable, unambiguous resolution, not a gap.
            return LocationResolution(state=state, source="text")

        return LocationResolution(source="none")

    def resolve_from_coordinates(self, latitude: float, longitude: float) -> LocationResolution:
        """GPS -> LocationResolver (state/district/city names, best-effort, never raises) ->
        re-matched against the RAG gazetteer specifically. A city LocationResolver returns that
        isn't in the RAG gazetteer (e.g. GPS resolves to a real Indian city this knowledge base
        simply has no coverage for) correctly yields city=None, source="gps" -- NOT a fabricated
        match to the nearest-sounding RAG city."""
        resolved = self._location_resolver.resolve_coordinates(latitude, longitude)
        warnings = list(resolved.warnings)
        if resolved.city_name:
            gazetteer_city = self._gazetteer.find_city(resolved.city_name)
            if gazetteer_city:
                state = next((s for s, cities in self._gazetteer.cities_by_state.items() if gazetteer_city in cities), None)
                return LocationResolution(city=gazetteer_city, state=state, source="gps", warnings=warnings)
            warnings.append(
                f"GPS resolved to '{resolved.city_name}', which has no records in this knowledge base."
            )
        return LocationResolution(source="gps", warnings=warnings)

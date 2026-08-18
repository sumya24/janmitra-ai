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

# Python's `\b` word boundary is defined off `\w`, which (in Unicode mode) only covers each
# script's CONSONANTS and INDEPENDENT vowels (Unicode category Lo) -- not the dependent vowel
# signs/matras (Devanagari ा/ी/ू/ौ/ृ, Bengali া/ি/ী/ু, Gujarati ા/ી/ુ, Odia ା/ୀ/ୁ, ..., category
# Mc) that most real words in these scripts actually end with, since the inherent-vowel convention
# common to all four means a bare word rarely ends on a plain consonant. `\bमोहाली\b` therefore
# fails to match "मोहाली." at all: `\b` requires a \w/non-\w transition exactly at the end of the
# word, but "ी" (Mc) isn't \w, so no such transition exists there. Real, measured bug -- caught by
# testing this fix's own alias list: every failure ended in a matra, every success ended in a
# consonant or independent vowel (चेन्नई/लखनऊ, both Lo). `_WORD_CHAR_CLASS` extends the boundary
# definition to the full Unicode block of each of this project's supported non-Latin scripts
# (Devanagari for hi/mr, Bengali for bn, Gujarati for gu, Odia for or -- consonants + independent
# vowels + combining signs together), so a word ending in a matra gets a correct boundary in any
# of them -- Latin-script matching is unaffected (still governed by \w exactly as before, since \w
# is included verbatim).
_WORD_CHAR_CLASS = r"[\wऀ-ॿঀ-৿઀-૿଀-୿]"


def _bounded_search(needle: str, haystack: str) -> bool:
    pattern = rf"(?<!{_WORD_CHAR_CLASS}){re.escape(needle)}(?!{_WORD_CHAR_CLASS})"
    return re.search(pattern, haystack) is not None

# Aliases for RAG gazetteer entries whose canonical chunk-metadata name a citizen would rarely
# type verbatim (e.g. nobody types "Sahibzada Ajit Singh Nagar (Mohali)" -- they say "Mohali").
#
# Non-Latin entries below close a real, measured gap found while investigating a live bug report:
# a citizen replying "मोहाली." to "what is the location?" kept getting asked the SAME question
# again. Root cause was structural, not a missing keyword or two -- `find_city`/`find_state` only
# ever compared against this file's (and the gazetteer's) purely Latin-script names via `.lower()`,
# so a non-Latin city name could never match at all, no matter how it was spelled. Every one of
# the 30 RAG-gazetteer cities and 17 states got an alias in every one of this project's 6
# supported UI languages (see frontend-react/src/lib/i18n.ts) -- en, hi, mr (Devanagari, shared
# with hi), or (Odia), gu (Gujarati), bn (Bengali) -- not just Mohali/Devanagari, once the root
# cause was understood to be "no non-Latin-script support exists at all," not "one city's alias is
# missing." Every alias's matching behavior (including the word-boundary fix above, needed for all
# four non-Latin scripts, not just Devanagari) was verified live against this project's own
# gazetteer, not merely typed and assumed -- see the fix's own test run.
_CITY_ALIASES: dict[str, str] = {
    "mohali": "Sahibzada Ajit Singh Nagar (Mohali)",
    "sas nagar": "Sahibzada Ajit Singh Nagar (Mohali)",
    "delhi": "New Delhi",
    "bangalore": "Bengaluru",
    "mysore": "Mysuru",
    "trivandrum": "Thiruvananthapuram",
    # Devanagari (hi + mr) -- see module-level comment above.
    "अहमदाबाद": "Ahmedabad",
    "बंगळुरू": "Bengaluru", "बंगलुरु": "Bengaluru", "बेंगलुरू": "Bengaluru", "बेंगलुरु": "Bengaluru", "बंगलोर": "Bengaluru",
    "भोपाळ": "Bhopal", "भोपाल": "Bhopal",
    "चेन्नई": "Chennai",
    "कोईम्बतूर": "Coimbatore", "कोयंबतूर": "Coimbatore",
    "फरीदाबाद": "Faridabad",
    "गया": "Gaya",
    "पटना": "Patna",
    "गुरुग्राम": "Gurugram", "गुडगाव": "Gurugram", "गुड़गांव": "Gurugram",
    "गुवाहाटी": "Guwahati",
    "हावडा": "Howrah", "हावड़ा": "Howrah",
    "हैदराबाद": "Hyderabad",
    "इंदौर": "Indore", "इंदोर": "Indore",
    "जयपूर": "Jaipur", "जयपुर": "Jaipur",
    "जोधपूर": "Jodhpur", "जोधपुर": "Jodhpur",
    "कोची": "Kochi", "कोचीन": "Kochi",
    "कोलकाता": "Kolkata", "कलकत्ता": "Kolkata",
    "लखनौ": "Lucknow", "लखनऊ": "Lucknow",
    "मुंबई": "Mumbai",
    "म्हैसूर": "Mysuru", "मैसूर": "Mysuru",
    "नागपूर": "Nagpur", "नागपुर": "Nagpur",
    "नवी दिल्ली": "New Delhi", "नई दिल्ली": "New Delhi",
    "पटियाला": "Patiala",
    "मोहाली": "Sahibzada Ajit Singh Nagar (Mohali)", "साहिबज़ादा अजीत सिंह नगर": "Sahibzada Ajit Singh Nagar (Mohali)",
    "सुरत": "Surat",
    "तिरुवनंतपुरम": "Thiruvananthapuram", "त्रिवेंद्रम": "Thiruvananthapuram",
    "वाराणसी": "Varanasi", "बनारस": "Varanasi",
    "विजयवाडा": "Vijayawada",
    "विशाखापट्टणम": "Visakhapatnam", "विशाखापट्टनम": "Visakhapatnam", "विजाग": "Visakhapatnam",
    "वारंगल": "Warangal",
    # Odia (or)
    "ଅହମଦାବାଦ": "Ahmedabad",
    "ବେଙ୍ଗାଲୁରୁ": "Bengaluru", "ବାଙ୍ଗାଲୋର୍": "Bengaluru",
    "ଭୋପାଳ": "Bhopal",
    "ଚେନ୍ନାଇ": "Chennai",
    "କୋଏମ୍ବାଟୁର୍": "Coimbatore",
    "ଫରିଦାବାଦ": "Faridabad",
    "ଗୟା": "Gaya",
    "ପାଟନା": "Patna",
    "ଗୁରୁଗ୍ରାମ": "Gurugram",
    "ଗୁହାଟି": "Guwahati", "ଗୌହାଟି": "Guwahati",
    "ହାୱଡ଼ା": "Howrah", "ହାଓଡ଼ା": "Howrah",
    "ହାଇଦରାବାଦ": "Hyderabad",
    "ଇନ୍ଦୋର": "Indore",
    "ଜୟପୁର": "Jaipur",
    "ଯୋଧପୁର": "Jodhpur",
    "କୋଚି": "Kochi",
    "କୋଲକାତା": "Kolkata",
    "ଲକ୍ଷ୍ନୌ": "Lucknow",
    "ମୁମ୍ବାଇ": "Mumbai",
    "ମାଇସୁରୁ": "Mysuru", "ମହିଶୂର": "Mysuru",
    "ନାଗପୁର": "Nagpur",
    "ନୂଆ ଦିଲ୍ଲୀ": "New Delhi",
    "ପାଟିଆଲା": "Patiala",
    "ମୋହାଲି": "Sahibzada Ajit Singh Nagar (Mohali)",
    "ସୁରଟ": "Surat",
    "ତିରୁଅନନ୍ତପୁରମ": "Thiruvananthapuram",
    "ବାରାଣାସୀ": "Varanasi",
    "ବିଜୟୱାଡ଼ା": "Vijayawada",
    "ବିଶାଖାପାଟଣା": "Visakhapatnam",
    "ୱାରାଙ୍ଗଲ": "Warangal",
    # Gujarati (gu)
    "અમદાવાદ": "Ahmedabad",
    "બેંગલુરુ": "Bengaluru", "બેંગ્લોર": "Bengaluru",
    "ભોપાલ": "Bhopal",
    "ચેન્નાઈ": "Chennai",
    "કોઈમ્બતુર": "Coimbatore",
    "ફરીદાબાદ": "Faridabad",
    "ગયા": "Gaya",
    "પટના": "Patna",
    "ગુરુગ્રામ": "Gurugram",
    "ગુવાહાટી": "Guwahati",
    "હાવડા": "Howrah",
    "હૈદરાબાદ": "Hyderabad",
    "ઇન્દોર": "Indore",
    "જયપુર": "Jaipur",
    "જોધપુર": "Jodhpur",
    "કોચી": "Kochi",
    "કોલકાતા": "Kolkata",
    "લખનૌ": "Lucknow",
    "મુંબઈ": "Mumbai",
    "મૈસુર": "Mysuru",
    "નાગપુર": "Nagpur",
    "નવી દિલ્હી": "New Delhi",
    "પટિયાલા": "Patiala",
    "મોહાલી": "Sahibzada Ajit Singh Nagar (Mohali)",
    "સુરત": "Surat",
    "તિરુવનંતપુરમ": "Thiruvananthapuram",
    "વારાણસી": "Varanasi",
    "વિજયવાડા": "Vijayawada",
    "વિશાખાપટ્ટનમ": "Visakhapatnam",
    "વારંગલ": "Warangal",
    # Bengali (bn)
    "আহমেদাবাদ": "Ahmedabad",
    "বেঙ্গালুরু": "Bengaluru",
    "ভোপাল": "Bhopal",
    "চেন্নাই": "Chennai",
    "কোয়েম্বাটোর": "Coimbatore",
    "ফরিদাবাদ": "Faridabad",
    "গয়া": "Gaya",
    "পাটনা": "Patna",
    "গুরুগ্রাম": "Gurugram",
    "গুয়াহাটি": "Guwahati",
    "হাওড়া": "Howrah",
    "হায়দ্রাবাদ": "Hyderabad",
    "ইন্দোর": "Indore",
    "জয়পুর": "Jaipur",
    "যোধপুর": "Jodhpur",
    "কোচি": "Kochi",
    "কলকাতা": "Kolkata",
    "লখনউ": "Lucknow",
    "মুম্বাই": "Mumbai",
    "মহীশূর": "Mysuru", "মাইসুরু": "Mysuru",
    "নাগপুর": "Nagpur",
    "নয়াদিল্লি": "New Delhi",
    "পাতিয়ালা": "Patiala",
    "মোহালি": "Sahibzada Ajit Singh Nagar (Mohali)",
    "সুরাট": "Surat",
    "তিরুবনন্তপুরম": "Thiruvananthapuram",
    "বারাণসী": "Varanasi",
    "বিজয়ওয়াড়া": "Vijayawada",
    "বিশাখাপত্তনম": "Visakhapatnam",
    "ওয়ারাঙ্গল": "Warangal",
}


def known_aliases_for_city(canonical_city: str) -> list[str]:
    """BUG FIX (live Hindi validation): the reverse of what `_CITY_ALIASES` itself encodes --
    every alias string, in every language this file has one for, that maps TO `canonical_city`.

    Exists to bridge two independently-maintained naming conventions for the same real place:
    this file's RAG gazetteer uses each city's full official name (e.g. "Sahibzada Ajit Singh
    Nagar (Mohali)"), while `backend/services/location_resolver.py`'s worker-ward matching
    (`find_worker_ward_text`) only ever sees whatever informal string a worker was actually
    registered with (e.g. plain "Mohali") -- and does its own exact/substring matching with no
    alias awareness of its own (see that function's own docstring: "never guesses beyond
    substring city-name matching"). A citizen typing "मोहाली" resolves correctly to the
    canonical gazetteer name via `_CITY_ALIASES` above, but that canonical name then fails to
    match a worker registered as "Mohali" -- live-reproduced, not hypothetical: a real Hindi
    complaint for a real, staffed city was incorrectly told no workers were available there.

    Not Mohali-specific: several gazetteer entries have a canonical name that differs from their
    common Latin-script alias (Delhi -> "New Delhi", Bangalore -> "Bengaluru", Mysore ->
    "Mysuru", Trivandrum -> "Thiruvananthapuram", ...) -- any of these could hit the identical
    gap if a worker were ever registered under the informal name (as this project's own seed
    data and tests already do for Mohali). Returned aliases include the plain-Latin form (e.g.
    "mohali") whenever one exists in `_CITY_ALIASES`, since that is what an informally-registered
    worker ward is expected to look like in this codebase's own established convention -- see
    orchestration/nodes.py's `_resolve_worker_ward_text` for the caller that uses this."""
    needle = canonical_city.strip().lower()
    if not needle:
        return []
    return [alias for alias, canonical in _CITY_ALIASES.items() if canonical.lower() == needle]


# Same alias idiom as _CITY_ALIASES above, for states -- `find_state` previously had NO alias
# layer at all, only a direct lowered-substring match against the gazetteer's own (Latin-script)
# state names, so it shared the exact same "no non-Latin-script support" gap city matching had.
_STATE_ALIASES: dict[str, str] = {
    "आंध्र प्रदेश": "Andhra Pradesh",
    "आसाम": "Assam", "असम": "Assam",
    "बिहार": "Bihar",
    "दिल्ली": "Delhi",
    "गुजरात": "Gujarat",
    "हरियाणा": "Haryana", "हरयाणा": "Haryana",
    "कर्नाटक": "Karnataka",
    "केरळ": "Kerala", "केरल": "Kerala",
    "मध्य प्रदेश": "Madhya Pradesh",
    "महाराष्ट्र": "Maharashtra",
    "ओडिशा": "Odisha", "उड़ीसा": "Odisha",
    "पंजाब": "Punjab",
    "राजस्थान": "Rajasthan",
    "तमिळनाडू": "Tamil Nadu", "तमिलनाडु": "Tamil Nadu",
    "तेलंगणा": "Telangana", "तेलंगाना": "Telangana",
    "उत्तर प्रदेश": "Uttar Pradesh",
    "पश्चिम बंगाल": "West Bengal",
    # Odia (or)
    "ଆନ୍ଧ୍ର ପ୍ରଦେଶ": "Andhra Pradesh",
    "ଆସାମ": "Assam",
    "ବିହାର": "Bihar",
    "ଦିଲ୍ଲୀ": "Delhi",
    "ଗୁଜରାଟ": "Gujarat",
    "ହରିୟାଣା": "Haryana",
    "କର୍ଣ୍ଣାଟକ": "Karnataka",
    "କେରଳ": "Kerala",
    "ମଧ୍ୟ ପ୍ରଦେଶ": "Madhya Pradesh",
    "ମହାରାଷ୍ଟ୍ର": "Maharashtra",
    "ଓଡ଼ିଶା": "Odisha",
    "ପଞ୍ଜାବ": "Punjab",
    "ରାଜସ୍ଥାନ": "Rajasthan",
    "ତାମିଲନାଡୁ": "Tamil Nadu",
    "ତେଲଙ୍ଗାନା": "Telangana",
    "ଉତ୍ତର ପ୍ରଦେଶ": "Uttar Pradesh",
    "ପଶ୍ଚିମ ବଙ୍ଗ": "West Bengal",
    # Gujarati (gu)
    "આંધ્ર પ્રદેશ": "Andhra Pradesh",
    "આસામ": "Assam",
    "બિહાર": "Bihar",
    "દિલ્હી": "Delhi",
    "ગુજરાત": "Gujarat",
    "હરિયાણા": "Haryana",
    "કર્ણાટક": "Karnataka",
    "કેરળ": "Kerala",
    "મધ્ય પ્રદેશ": "Madhya Pradesh",
    "મહારાષ્ટ્ર": "Maharashtra",
    "ઓડિશા": "Odisha",
    "પંજાબ": "Punjab",
    "રાજસ્થાન": "Rajasthan",
    "તમિલનાડુ": "Tamil Nadu",
    "તેલંગાણા": "Telangana",
    "ઉત્તર પ્રદેશ": "Uttar Pradesh",
    "પશ્ચિમ બંગાળ": "West Bengal",
    # Bengali (bn)
    "অন্ধ্র প্রদেশ": "Andhra Pradesh",
    "অসম": "Assam",
    "বিহার": "Bihar",
    "দিল্লি": "Delhi",
    "গুজরাট": "Gujarat",
    "হরিয়ানা": "Haryana",
    "কর্ণাটক": "Karnataka",
    "কেরালা": "Kerala",
    "মধ্য প্রদেশ": "Madhya Pradesh",
    "মহারাষ্ট্র": "Maharashtra",
    "ওড়িশা": "Odisha",
    "পাঞ্জাব": "Punjab",
    "রাজস্থান": "Rajasthan",
    "তামিলনাড়ু": "Tamil Nadu",
    "তেলেঙ্গানা": "Telangana",
    "উত্তর প্রদেশ": "Uttar Pradesh",
    "পশ্চিমবঙ্গ": "West Bengal",
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
            if _bounded_search(alias, lowered):
                return canonical
        for city in self.cities:
            if _bounded_search(city.lower(), lowered):
                return city
            # LOCATION NORMALIZATION FIX (live Hindi validation): the check above only ever finds
            # a match when the SHORTER, already-known city/alias name appears somewhere inside the
            # (typically longer) query text -- it never handles the reverse, where the query IS
            # the shorter, official-name-minus-qualifier form of a longer canonical entry, e.g. a
            # citizen typing just "Sahibzada Ajit Singh Nagar" (the official name) rather than the
            # full gazetteer entry "Sahibzada Ajit Singh Nagar (Mohali)" (official name + common-
            # name qualifier in parentheses). General for any gazetteer city with an "Official
            # Name (Common Name)" shape -- not specific to Mohali, the only entry with this shape
            # today; a future one would be covered automatically, no new keyword/city needed.
            if "(" in city:
                official_prefix = city.split("(", 1)[0].strip().lower()
                if official_prefix and _bounded_search(official_prefix, lowered):
                    return city
        return None

    def find_state(self, text: str) -> str | None:
        lowered = text.lower()
        for alias, canonical in _STATE_ALIASES.items():
            if _bounded_search(alias, lowered):
                return canonical
        for state in self.states:
            if _bounded_search(state.lower(), lowered):
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

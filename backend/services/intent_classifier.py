"""Classifies an Ask JanMitra question into TYPE_A (complaint), TYPE_B (service info), or
TYPE_C (personal complaint status/tracking) — and, for TYPE_A/TYPE_B, which civic ServiceCategory
it's about, if any.

Design choice: rule-based keyword matching, not an LLM call. This project already uses Sarvam's
LLM (see summary_service.py/normalization_service.py) — deliberately NOT reused here, because
intent routing is exactly the kind of decision that should be fast, free, deterministic, and
directly unit-testable without a network call or nondeterministic model output (see §46 of the
implementation spec: "correctness, testability, clarity, replaceability -- not framework/API-call
count"). The LLM is reserved for what it's actually needed for: turning retrieved knowledge into
natural-language prose (see ask_janmitra_service.py's answer-generation step).

Honest limitation: this is keyword matching, not true NLU. It will misclassify phrasings that
don't share vocabulary with its keyword lists — measured accuracy against this project's own
labeled test question files is reported in docs/ask_janmitra_rag_architecture.md, not asserted
here as some claimed percentage.

TYPE_C (status/tracking) is checked FIRST and takes priority over everything else — misrouting a
personal-status question into RAG (which has no way to know about any specific citizen's
complaint) is the single most important thing this classifier must never do (see the module's
test coverage in tests/test_ask_janmitra.py).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum

from backend.schemas.rag_knowledge import ServiceCategory


class QuestionIntent(str, Enum):
    TYPE_A_COMPLAINT = "TYPE_A_COMPLAINT"
    TYPE_B_SERVICE_INFO = "TYPE_B_SERVICE_INFO"
    TYPE_C_STATUS = "TYPE_C_STATUS"


@dataclass
class ClassificationResult:
    intent: QuestionIntent
    service_category: ServiceCategory | None
    # True when the question clearly names a *known but unsupported* service (electricity is the
    # only one in this data set today) -- lets the caller return an honest "don't have that"
    # response immediately, without ever running a vector search that might turn up an
    # unrelated-but-textually-similar chunk (see the module docstring's WATER_DRAINAGE example).
    out_of_scope_service: str | None
    matched_keywords: list[str]
    # True when the question is specifically about applying for a NEW water/sewerage connection
    # (as opposed to a fault/repair on an existing one). Added in the KB-expansion phase alongside
    # real new-connection KnowledgeRecords for Mohali/Patiala/Odisha (see
    # _NEW_CONNECTION_TOPIC_KEYWORDS below) -- lets the RAG flow apply a stricter post-retrieval
    # filter for exactly this topic, so a city with no new-connection record still answers
    # honestly instead of returning a semantically-similar-but-wrong repair/leak chunk (see
    # rag_flow_node's docstring for the measured false positive this closes).
    requests_new_connection: bool = False


# --- TYPE_C: personal complaint status/tracking -- checked first, highest priority ---
_STATUS_KEYWORDS: dict[str, list[str]] = {
    "en": ["status", "track", "tracking", "has my complaint", "when will my", "assigned to",
           "complaint id", "complaint number", "complaint #", "resolved yet", "my complaint"],
    "hi": ["स्थिति", "ट्रैक", "मेरी शिकायत", "मेरा कंप्लेंट"],
    "mr": ["स्थिती", "माझी तक्रार", "ट्रॅक"],
    "or": ["ସ୍ଥିତି", "ମୋ ଅଭିଯୋଗ", "ଟ୍ରାକ୍"],
}
_STATUS_NUMBER_PATTERN = re.compile(r"complaint\s*#?\s*\d+|#\d+", re.IGNORECASE)

# --- TYPE_B: service/information request (new connection, documents, contact, application) ---
_SERVICE_INFO_KEYWORDS: dict[str, list[str]] = {
    "en": ["new connection", "new water connection", "new electricity connection", "new pipeline",
           # "new sewerage connection" was missing even before this phase (only water/electricity/
           # pipeline were listed) -- surfaced by this phase's own new VERIFIED sewerage-connection
           # records (Mohali/Patiala), which need this to classify as TYPE_B like their water
           # counterpart already does. Caught by test_new_sewerage_connection_in_patiala_answered_
           # from_verified_record, a real measured failure, not a hypothetical.
           "new sewerage connection", "new sewer connection",
           "apply", "application", "documents required", "which department", "who should i contact",
           "who handles", "who do i contact", "official website", "contact number", "download",
           "application form", "how can i get", "how do i get", "i am new here", "i want a new",
           "i need a new",
           # "documents required" (above) doesn't match the more natural question form a citizen
           # actually types -- caught via the service-flow phase's own worked example ("What
           # documents do I need for a water connection?"), which measurably misclassified as
           # TYPE_A_COMPLAINT (falls to the "something is wrong" default, no service-info keyword
           # matched) instead of TYPE_B_SERVICE_INFO before this fix. Same category of real,
           # measured false negative as the NEW_CONNECTION_KEYWORDS fix below -- not hypothetical.
           "what documents", "which documents", "documents do i need", "documents needed",
           # Romanized/Hinglish phrasing -- caught via the KB-expansion phase's live testing:
           # "Mujhe naya water connection chahiye, documents kya lagenge?" misclassified as
           # TYPE_A_COMPLAINT because none of the keyword lists above have any Latin-script Hindi
           # entries at all, only English and Devanagari/Odia script. This project's classifier has
           # no language-specific routing (classify() checks every list regardless of the request's
           # declared `language`, see _any_match below), so these entries work for romanized input
           # without any other change. Deliberately phrases, not single generic words (e.g. not a
           # bare "chahiye", which means "want/need" and would false-positive on unrelated
           # complaint sentences) -- see tests/test_ask_janmitra.py's Hinglish regression tests for
           # the non-overfitting checks (paraphrases beyond the exact four example sentences, and a
           # confirmation that a plain complaint sentence is unaffected).
           "naya water connection", "nayi water connection", "naya pipeline connection",
           "nayi pipeline connection", "naya sewerage connection", "nayi sewerage connection",
           "naya connection chahiye", "nayi connection chahiye",
           "documents kya lagenge", "kya lagenge", "kya lagega", "kaise milega", "kaise milegi",
           "kahan se milega", "kaha se milega", "kahan milega",
           "kitne paise", "kitna paisa", "paise lagenge", "fees kitni", "kitni fees",
           "kaunsa department", "department kaunsa", "responsible department",
           "schedule kya hai", "kya schedule hai", "maintenance kaun karta hai", "kaun karta hai"],
    "hi": ["नया कनेक्शन", "नया पानी कनेक्शन", "आवेदन", "दस्तावेज", "संपर्क नंबर", "कैसे लगवाएं"],
    "mr": ["नवीन कनेक्शन", "नवीन पाणी कनेक्शन", "अर्ज", "कागदपत्रे"],
    # "ନୂଆ ପାଣି ସଂଯୋଗ" ("new water connection") is NOT just "ନୂଆ ସଂଯୋଗ" ("new connection") with a
    # word removed -- the service noun sits between "new" and "connection" in natural Odia
    # phrasing, same as English/Hindi/Marathi. A bare "ନୂଆ ସଂଯୋଗ" substring never matches real
    # sentences and was a genuine bug (caught by test_multilingual_odia_new_connection_is_type_b),
    # not a hypothetical -- list the full phrases actually used instead of assuming adjacency.
    "or": ["ନୂଆ ପାଣି ସଂଯୋଗ", "ନୂଆ ସଂଯୋଗ", "ଆବେଦନ"],
}

# --- TYPE_A: complaint/issue -- "something is wrong" phrasing ---
_COMPLAINT_VERB_KEYWORDS: dict[str, list[str]] = {
    "en": ["not working", "broken", "not collected", "problem", "issue", "report", "complain",
           "leaking", "leak", "overflow", "near my house", "near my home", "near me"],
    "hi": ["काम नहीं कर रहा", "खराब है", "शिकायत", "टूटा"],
    "mr": ["काम करत नाही", "तक्रार", "बंद आहे"],
    "or": ["କାମ କରୁନାହିଁ", "ଅଭିଯୋଗ", "ଖରାପ"],
}

# --- Service category detection (own keyword sets, deliberately NOT reusing
# frontend-react/src/lib/serviceCategories.tsx's looser list -- that list includes bare
# "electric" under STREETLIGHTS, which would make "new ELECTRICITY connection" misclassify as a
# streetlight question. Precision matters more here than in a client-side UI hint.) ---
_CATEGORY_KEYWORDS: dict[ServiceCategory, dict[str, list[str]]] = {
    ServiceCategory.WASTE_SANITATION: {
        "en": ["garbage", "waste", "trash", "sanitation", "dump", "litter", "rubbish"],
        "hi": ["कचरा", "कूड़ा"], "mr": ["कचरा"], "or": ["ଆବର୍ଜନା"],
    },
    ServiceCategory.WATER_DRAINAGE: {
        "en": ["water", "drain", "drainage", "sewage", "sewer", "pipeline", "pipe connection", "flood"],
        "hi": ["पानी", "नाला", "पाइप"], "mr": ["पाणी"], "or": ["ପାଣି"],
    },
    ServiceCategory.ROADS_POTHOLES: {
        "en": ["road", "pothole", "footpath", "pavement", "civil work"],
        "hi": ["सड़क", "गड्ढा"], "mr": ["रस्ता", "खड्डा"], "or": ["ରାସ୍ତା"],
    },
    ServiceCategory.STREETLIGHTS: {
        "en": ["streetlight", "street light", "street lamp", "lamp post"],
        "hi": ["स्ट्रीट लाइट", "बत्ती"], "mr": ["स्ट्रीट लाइट", "दिवा"], "or": ["ଆଲୋକ"],
    },
}

# Known-but-unsupported services -- checked explicitly so "electricity" never gets silently
# absorbed into STREETLIGHTS (they share the word "electric" in casual English) or ignored
# entirely (which would let a generic vector search return an unrelated WATER/ROADS chunk).
_OUT_OF_SCOPE_KEYWORDS: dict[str, list[str]] = {
    "en": ["electricity", "electric connection", "electric meter", "power connection", "power supply"],
    "hi": ["बिजली"], "mr": ["वीज"], "or": ["ବିଦ୍ୟୁତ"],
}

# Bare "new connection" (utility unspecified) -- checked separately from the category detector
# above. Originally (RAG phase) this list also caught "new water connection"/"new pipeline
# connection"/"new sewer(age) connection" specifically, because this knowledge base had zero
# new-connection-application records in any city -- routing those phrases to RAG would have let
# the retriever return an unrelated water-LEAK-repair chunk as if it answered a new-connection
# question (a real, measured false positive; see docs/ask_janmitra_rag_architecture.md's
# evaluation section for the before/after numbers).
#
# That's no longer true for water/sewerage specifically: the KB-expansion phase added real,
# VERIFIED new-water-connection and new-sewerage-connection records for Mohali, Patiala, and
# (water only) Odisha, extracted directly from the same citizen-charter PDFs already used for
# this project's other VERIFIED records (see data/rag_knowledge_base/knowledge_records/verified/).
# Short-circuiting those phrases to a canned "don't have that" response would now be actively
# wrong for exactly the cities that DO have this data -- so "new water connection"/"new pipeline
# connection"/"new sewerage connection" (and their Hindi/Marathi/Odia equivalents) were removed
# from this list and now flow to TYPE_B_SERVICE_INFO -> RAG like any other service-info question.
# RagRetriever's own category+location filtering and relevance threshold already handle the
# "not covered for this specific city" case honestly (insufficient_knowledge=True, never a
# fabricated or unrelated-chunk answer) -- the same mechanism that protects every other question
# this system answers, not a special case for this one.
#
# Bare "new connection" (no stated utility) stays here deliberately: it's still genuinely
# ambiguous (water? sewerage? electricity, still out of scope? gas, never in scope?) and this
# project has no data for most of those, so routing it to a canned "which service?" response
# remains the honest choice pending a real disambiguation step this phase didn't build.
_NEW_CONNECTION_KEYWORDS: dict[str, list[str]] = {
    "en": ["new connection"],
    "hi": ["नया कनेक्शन"],
    "mr": ["नवीन कनेक्शन"],
    "or": ["ନୂଆ ସଂଯୋଗ"],
}

# Detects "this question is specifically about a NEW water/sewerage connection" regardless of
# which city it's asked about -- the phrases moved out of _NEW_CONNECTION_KEYWORDS above (they no
# longer force out-of-scope) are reused here for a different purpose: flagging
# ClassificationResult.requests_new_connection so rag_flow_node can apply a stricter filter after
# retrieval (see that flag's own docstring). Deliberately a superset of what
# _SERVICE_INFO_KEYWORDS needs for TYPE_B classification -- this list only has to be *specific*
# enough to reliably mean "new connection", not exhaustive of every info-seeking phrase.
_NEW_CONNECTION_TOPIC_KEYWORDS: dict[str, list[str]] = {
    "en": ["new water connection", "new sewerage connection", "new pipeline connection", "new pipeline",
           "naya water connection", "nayi water connection", "naya pipeline connection",
           "nayi pipeline connection", "naya sewerage connection", "nayi sewerage connection"],
    "hi": ["नया पानी कनेक्शन"],
    "mr": ["नवीन पाणी कनेक्शन"],
    "or": ["ନୂଆ ପାଣି ସଂଯୋଗ"],
}


def _any_match(text: str, keyword_lists: dict[str, list[str]]) -> list[str]:
    lowered = text.lower()
    return [kw for kws in keyword_lists.values() for kw in kws if kw.lower() in lowered]


def classify(question: str) -> ClassificationResult:
    """Classifies one question. Never raises -- an unrecognized question falls through to
    TYPE_A_COMPLAINT with service_category=None (the safest default: routes to RAG, which will
    then correctly report "insufficient knowledge" rather than guessing, per rag_retriever.py)."""
    text = question.strip()
    requests_new_connection = bool(_any_match(text, _NEW_CONNECTION_TOPIC_KEYWORDS))

    status_matches = _any_match(text, _STATUS_KEYWORDS)
    if _STATUS_NUMBER_PATTERN.search(text):
        status_matches.append("<complaint-number-pattern>")
    if status_matches:
        return ClassificationResult(
            intent=QuestionIntent.TYPE_C_STATUS,
            service_category=None,
            out_of_scope_service=None,
            matched_keywords=status_matches,
            requests_new_connection=requests_new_connection,
        )

    out_of_scope_matches = _any_match(text, _OUT_OF_SCOPE_KEYWORDS)
    out_of_scope_label = "ELECTRICITY" if out_of_scope_matches else None

    new_connection_matches = _any_match(text, _NEW_CONNECTION_KEYWORDS)
    if not out_of_scope_matches and new_connection_matches:
        out_of_scope_matches = new_connection_matches
        out_of_scope_label = "NEW_SERVICE_CONNECTION"

    service_info_matches = _any_match(text, _SERVICE_INFO_KEYWORDS)
    complaint_matches = _any_match(text, _COMPLAINT_VERB_KEYWORDS)

    category = None
    category_matches: list[str] = []
    for cat, lang_keywords in _CATEGORY_KEYWORDS.items():
        matches = _any_match(text, lang_keywords)
        if matches:
            category = cat
            category_matches = matches
            break  # first match wins -- categories are kept mutually distinct by keyword choice

    if out_of_scope_matches:
        # A service-info-shaped OR complaint-shaped question about a service this KB doesn't
        # cover -- still classified (TYPE_B is the more common shape for "I want a new X"), but
        # flagged so the caller skips retrieval entirely.
        intent = QuestionIntent.TYPE_B_SERVICE_INFO if service_info_matches or not complaint_matches else QuestionIntent.TYPE_A_COMPLAINT
        return ClassificationResult(
            intent=intent,
            service_category=None,
            out_of_scope_service=out_of_scope_label,
            matched_keywords=out_of_scope_matches,
            requests_new_connection=requests_new_connection,
        )

    if service_info_matches and not complaint_matches:
        return ClassificationResult(
            intent=QuestionIntent.TYPE_B_SERVICE_INFO,
            service_category=category,
            out_of_scope_service=None,
            matched_keywords=service_info_matches + category_matches,
            requests_new_connection=requests_new_connection,
        )

    # Default: TYPE_A. Covers explicit complaint-verb matches AND the "no signal either way"
    # fallback -- the safest default, since RAG will honestly report insufficient knowledge
    # rather than fabricate an answer either way (see rag_retriever.py).
    return ClassificationResult(
        intent=QuestionIntent.TYPE_A_COMPLAINT,
        service_category=category,
        out_of_scope_service=None,
        matched_keywords=complaint_matches + category_matches,
        requests_new_connection=requests_new_connection,
    )

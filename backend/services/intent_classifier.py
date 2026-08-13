"""Classifies an Ask Sarthi question into TYPE_A (complaint), TYPE_B (service info), or
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
    # "What services do you provide?" / "What can you help with?" -- a real, answerable question
    # about Sarthi's own scope, not a complaint or a RAG-answerable civic-service question. Kept
    # distinct from TYPE_A's "no signal either way" fallback (see classify()'s docstring) so it
    # gets its own accurate, static answer instead of being asked "what issue would you like to
    # report?" as if it were an unspecified complaint.
    CAPABILITIES = "CAPABILITIES"
    # Genuinely no signal matched anything (not a complaint verb, not a named service category,
    # not a service-info phrase, not a status/tracking phrase, not a known-unsupported service,
    # not a capabilities question) -- e.g. "What is my name?" or unrelated small talk. Previously
    # silently fell through to TYPE_A_COMPLAINT/service_category=None, which asked "what issue
    # would you like to report?" as if the question had been about filing a complaint -- a real,
    # user-reported bug (every off-topic question got that same complaint-shaped clarification,
    # regardless of what was actually asked). UNCLEAR gets its own honest "I didn't understand
    # that" response instead (see nodes.py's unclear_flow_node).
    UNCLEAR = "UNCLEAR"


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
# gu/bn added after a live stress-test survey found this project's 6 supported UI languages
# (see frontend-react/src/lib/i18n.ts) only ever had keyword coverage for 4 of them (en/hi/mr/or)
# -- Gujarati and Bengali had ZERO entries in every dict in this file, so a clear complaint typed
# in either language (e.g. "મારા ઘર પાસે સ્ટ્રીટ લાઈટ બંધ છે" -- "the streetlight near my house is
# off") fell all the way through to UNCLEAR. Real, measured gap, not hypothetical -- reproduced
# live against the running backend before this fix.
_STATUS_KEYWORDS: dict[str, list[str]] = {
    "en": ["status", "track", "tracking", "has my complaint", "when will my", "assigned to",
           "complaint id", "complaint number", "complaint #", "resolved yet", "my complaint"],
    "hi": ["स्थिति", "ट्रैक", "मेरी शिकायत", "मेरा कंप्लेंट"],
    "mr": ["स्थिती", "माझी तक्रार", "ट्रॅक"],
    "or": ["ସ୍ଥିତି", "ମୋ ଅଭିଯୋଗ", "ଟ୍ରାକ୍"],
    "gu": ["સ્થિતિ", "ટ્રેક", "મારી ફરિયાદ"],
    "bn": ["অবস্থা", "ট্র্যাক", "আমার অভিযোগ"],
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
           # Plain English fee/cost questions ("What is the water connection fee in Patiala?")
           # had NO English keyword at all here -- only the Hinglish equivalents below ("kitni
           # fees") were covered. A real, measured failure caught by this project's own live
           # testing: with zero service-info match and zero complaint-verb match, such a question
           # fell to classify()'s bare-category-only default (TYPE_A_COMPLAINT) and ACTUALLY FILED
           # A COMPLAINT for someone who only asked what something costs. `complaint_matches` still
           # wins if a genuine complaint mentions a fee too (e.g. "I was overcharged, please look
           # into this") -- classify() checks `service_info_matches and not complaint_matches`
           # before falling here, so this fix only catches pure info-seeking phrasing.
           "fee", "fees", "cost of", "how much does", "how much is", "how much will", "charges for",
           "what does it cost", "what is the cost", "what is the charge", "price of",
           # Same gap, same fix pattern, for schedule/timing questions -- "When does garbage
           # collection resume?" is exactly as info-seeking as a fee question, but had the
           # identical zero-English-keyword gap (only the Hinglish "schedule kya hai" below was
           # covered). Real, measured: caught live filing an actual phantom complaint for someone
           # who only asked when a service runs. "when will" is intentionally NOT added bare here
           # -- it's already a TYPE_C status keyword ("when will my"), checked first in classify()
           # and would win regardless, so adding it here would be redundant, not a fix.
           "when does", "what time does", "what time is", "how often does", "how often is",
           "resume collection", "collection schedule", "pickup schedule", "next collection",
           "when is collection", "maintenance schedule", "cleaning schedule",
           # Same gap, same fix pattern, caught by testing this project's own built-in suggested
           # prompts (frontend-react/src/lib/i18n.ts's "ask.suggested.pothole"/"garbage"/
           # "streetlight", shown to every new user) -- process/policy questions with zero
           # matching keyword, so a bare category match ("garbage"/"pothole") alone forced
           # TYPE_A_COMPLAINT.
           "how are potholes prioritized", "prioritized for repair", "how is repair prioritized",
           "collection was skipped", "garbage collection was skipped", "if collection is skipped",
           "how long does a repair take", "how long does repair take", "how long does a streetlight repair take",
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
    "hi": ["नया कनेक्शन", "नया पानी कनेक्शन", "आवेदन", "दस्तावेज", "संपर्क नंबर", "कैसे लगवाएं",
           # Same class of bug as the English fee/schedule fixes above, caught the same way (this
           # time by testing the app's own built-in "How are potholes prioritized for repair?" /
           # "What if garbage collection was skipped?" / "How long does a streetlight repair
           # take?" suggested prompts, shown to every new user, in every one of this project's 6
           # languages -- not hypothetical). These are genuine info-seeking process/policy
           # questions with no English-style keyword coverage at all for any non-English language,
           # so a bare category match ("कचरा"/"गड्ढा"/...) alone forced TYPE_A_COMPLAINT, or
           # nothing matched at all and it fell through to UNCLEAR.
           "प्राथमिकता कैसे तय होती है", "संग्रह छूट जाए", "छूट जाए तो क्या करें",
           "मरम्मत में कितना समय लगता है", "कितना समय लगता है"],
    "mr": ["नवीन कनेक्शन", "नवीन पाणी कनेक्शन", "अर्ज", "कागदपत्रे",
           "प्राधान्य कसे ठरवले जाते", "संकलन चुकल्यास", "चुकल्यास काय करावे",
           "दुरुस्तीला किती वेळ लागतो", "किती वेळ लागतो"],
    # "ନୂଆ ପାଣି ସଂଯୋଗ" ("new water connection") is NOT just "ନୂଆ ସଂଯୋଗ" ("new connection") with a
    # word removed -- the service noun sits between "new" and "connection" in natural Odia
    # phrasing, same as English/Hindi/Marathi. A bare "ନୂଆ ସଂଯୋଗ" substring never matches real
    # sentences and was a genuine bug (caught by test_multilingual_odia_new_connection_is_type_b),
    # not a hypothetical -- list the full phrases actually used instead of assuming adjacency.
    "or": ["ନୂଆ ପାଣି ସଂଯୋଗ", "ନୂଆ ସଂଯୋଗ", "ଆବେଦନ",
           "କିପରି ପ୍ରାଥମିକତା ସ୍ଥିର ହୁଏ", "ସଂଗ୍ରହ ଛାଡ଼ି", "ଛାଡ଼ି ଦିଆଗଲେ କଣ କରିବି",
           "ମରାମତିରେ କେତେ ସମୟ ଲାଗେ", "କେତେ ସମୟ ଲାଗେ"],
    "gu": ["નવું પાણી જોડાણ", "નવું જોડાણ", "અરજી", "દસ્તાવેજો", "સંપર્ક નંબર",
           "કેવી રીતે પ્રાથમિકતા અપાય છે", "ઉપાડવાનું ચૂકી", "ચૂકી ગયું હોય તો શું કરવું",
           "સમારકામમાં કેટલો સમય લાગે છે", "કેટલો સમય લાગે છે"],
    "bn": ["নতুন পানির সংযোগ", "নতুন সংযোগ", "আবেদন", "কাগজপত্র", "যোগাযোগ নম্বর",
           "কীভাবে অগ্রাধিকার ঠিক করা হয়", "সংগ্রহ বাদ পড়লে", "বাদ পড়লে কী করব",
           "মেরামত করতে কত সময় লাগে", "কত সময় লাগে"],
}

# --- CAPABILITIES: "what can this app do?" -- a real, in-domain, answerable question about
# Sarthi's own scope. Deliberately specific multi-word phrases, not bare "help" or "services"
# (which appear in genuine complaint/service-info sentences too, e.g. "please help fix this
# pothole" or "water services in my area are cut off") -- see _any_match's substring matching,
# which would otherwise false-positive on those. ---
_CAPABILITIES_KEYWORDS: dict[str, list[str]] = {
    "en": ["what services", "which services", "what can you do", "what can you help",
           "what do you do", "what all can you", "list of services", "services do you provide",
           "services do you offer", "services you provide", "services you offer",
           "what is janmitra", "what is jansarthi", "what is sarthi", "what is this app", "how can you help", "what kind of help",
           "what type of complaints", "what type of issues", "what can i report",
           "what can i complain about"],
    "hi": ["आप क्या कर सकते हैं", "कौन सी सेवाएं", "कौनसी सेवाएं", "जनमित्र क्या है"],
    "mr": ["तुम्ही काय करू शकता", "कोणत्या सेवा", "जनमित्र म्हणजे काय"],
    "or": ["ଆପଣ କଣ କରିପାରିବେ", "କେଉଁ ସେବା", "ଜନମିତ୍ର କଣ"],
    "gu": ["તમે શું કરી શકો છો", "કઈ સેવાઓ", "જનમિત્ર શું છે"],
    "bn": ["আপনি কী করতে পারেন", "কোন পরিষেবা", "জনমিত্র কী"],
}


# --- TYPE_A: complaint/issue -- "something is wrong" phrasing ---
#
# Split into two tiers -- STATE (an active problem is being described: "not working"/"leaking"/
# टूटा/ভাঙা/...) vs META (a word ABOUT the act of complaining/reporting itself: "report"/
# "complain"/शिकायत/तक्रार/ଅଭିଯୋଗ/ફરિયાદ/অভিযোগ) -- after a real, reported bug: "पानी के रिसाव की
# शिकायत कैसे करें?" ("How do I file a complaint about a water leak?") is a citizen asking about
# the PROCESS, not reporting anything right now, but शिकायत alone matched the old undivided list
# exactly like a genuine complaint would, so combined with the "पानी" category match it silently
# FILED AND ASSIGNED a real complaint (#39) for someone who only wanted to know how. Confirmed
# systemic, not Hindi-specific: "How do I report a water leakage?"/"How can I file a complaint
# about garbage?" hit the identical bug in English via "report"/"complain" -- and every one of
# this file's 6 languages has the same bare complaint-noun in its old list. A genuine STATE verb
# ("How do I fix my leaking pipe") still means TYPE_A unconditionally -- only a bare META word
# combined with explicit how-to framing (see `_HOW_TO_FILE_COMPLAINT_KEYWORDS` below) is
# downgraded, in `classify()`.
_COMPLAINT_STATE_KEYWORDS: dict[str, list[str]] = {
    "en": ["not working", "broken", "not collected", "problem", "issue",
           "leaking", "leak", "overflow", "near my house", "near my home", "near me"],
    "hi": ["काम नहीं कर रहा", "खराब है", "टूटा"],
    "mr": ["काम करत नाही", "बंद आहे"],
    "or": ["କାମ କରୁନାହିଁ", "ଖରାପ"],
    "gu": ["કામ કરતું નથી", "તૂટેલું"],
    "bn": ["কাজ করছে না", "ভাঙা"],
}
_COMPLAINT_META_KEYWORDS: dict[str, list[str]] = {
    "en": ["report", "complain"],
    "hi": ["शिकायत"],
    "mr": ["तक्रार"],
    "or": ["ଅଭିଯୋଗ"],
    "gu": ["ફરિયાદ"],
    "bn": ["অভিযোগ"],
}
# Union of the two tiers -- kept so every EXISTING caller/test that reasons about "did some
# complaint-shaped keyword match at all" (matched_keywords, the out-of-scope/service-info
# interplay below) keeps working unchanged; only `classify()`'s own TYPE_A decision needs the
# tiers kept separate.
_COMPLAINT_VERB_KEYWORDS: dict[str, list[str]] = {
    lang: _COMPLAINT_STATE_KEYWORDS[lang] + _COMPLAINT_META_KEYWORDS[lang] for lang in _COMPLAINT_STATE_KEYWORDS
}

# "How do I report/file a complaint?" -- explicitly asking about Sarthi's OWN process, not
# reporting an issue. Deliberately paired phrases (word for "how" + word for "complaint/report"
# together), never a bare "how"/"कैसे" alone, which would be far too generic and risk swallowing
# unrelated questions (see this file's own established convention of specific multi-word phrases
# over single generic words, e.g. the Hinglish entries above).
_HOW_TO_FILE_COMPLAINT_KEYWORDS: dict[str, list[str]] = {
    "en": ["how do i report", "how do i file", "how can i report", "how can i file",
           "how to report", "how to file", "how do i complain", "how can i complain",
           "how to complain", "how do i lodge", "how to lodge", "how do i raise", "how to raise a complaint"],
    "hi": ["शिकायत कैसे करें", "शिकायत कैसे करूं", "शिकायत कैसे दर्ज करें", "कैसे शिकायत करें",
           "कैसे शिकायत दर्ज करें", "शिकायत कैसे दर्ज करूं"],
    "mr": ["तक्रार कशी करावी", "तक्रार कशी करू", "तक्रार कशी नोंदवावी", "कशी तक्रार करावी"],
    # or/gu/bn: the app's own real suggested-prompt strings (frontend-react/src/lib/i18n.ts's
    # "ask.suggested.waterLeak") use "report"/"inform" wording (ରିପୋର୍ଟ/જાણ/রিপোর্ট), NOT
    # "complaint" (ଅଭିଯୋଗ/ફરિયાদ/অভিযোগ) -- an earlier version of this fix only covered the
    # "complaint"-word phrasing (an unverified guess), missing these entirely: `how_to_file_
    # matches` came back empty for the app's own real "ପାଣି ଲିକେଜ୍ କିପରି ରିପୋର୍ଟ କରିବି?"/"પાણીના
    # લીકેજની જાણ કેવી રીતે કરવી?"/"জলের লিকেজ কীভাবে রিপোর্ট করব?" prompts, so the override never
    # fired and the bare "ପାଣି/પાણી/পানি" (water) category match alone still forced
    # TYPE_A_COMPLAINT -- caught live by testing the app's OWN built-in prompts, not a hypothetical.
    "or": ["ଅଭିଯୋଗ କିପରି କରିବେ", "କିପରି ଅଭିଯୋଗ କରିବେ", "କିପରି ରିପୋର୍ଟ କରିବି", "ରିପୋର୍ଟ କିପରି କରିବି",
           "କିପରି ରିପୋର୍ଟ କରିବେ", "ରିପୋର୍ଟ କିପରି କରିବେ"],
    "gu": ["ફરિયાદ કેવી રીતે કરવી", "કેવી રીતે ફરિયાદ કરવી", "જાણ કેવી રીતે કરવી", "કેવી રીતે જાણ કરવી"],
    "bn": ["অভিযোগ কীভাবে করব", "কীভাবে অভিযোগ করব", "রিপোর্ট কীভাবে করব", "কীভাবে রিপোর্ট করব"],
}

# --- Service category detection (own keyword sets, deliberately NOT reusing
# frontend-react/src/lib/serviceCategories.tsx's looser list -- that list includes bare
# "electric" under STREETLIGHTS, which would make "new ELECTRICITY connection" misclassify as a
# streetlight question. Precision matters more here than in a client-side UI hint.)
#
# Oblique-case stems: both Hindi and Marathi are (partly, for Hindi; fully, for Marathi) fusional
# -- a masculine noun ending in -आ changes shape under a case suffix (की/में/पर/ने/...) instead of
# staying fixed while a separate postposition word attaches, e.g. Marathi पाणी -> पाण्याची, Hindi
# गड्ढा -> गड्ढे की. A citizen saying "गड्ढ्याची तक्रार" ("a complaint about the pothole") is at
# least as natural as, if not more natural than, a bare-nominative sentence -- so a keyword list
# with only the nominative form silently misses it, returning service_category=None and asking
# the citizen to pick a category from a list that already includes the one they named. First
# caught for पाणी/पाण्या (see git history), then confirmed as the same systemic gap across every
# other masculine -आ noun in this list by direct classify() probing with natural oblique-case
# sentences -- each "X, X-oblique" pair below is a real, measured fix, not a guess:
# कचरा/कचऱ्या (mr), कचरा/कचरे + कूड़ा/कूड़े (hi), रस्ता/रस्त्या + खड्डा/खड्ड्या (mr),
# गड्ढा/गड्ढे (hi), दिवा/दिव्या (mr), नाला/नाले (hi). Feminine/consonant-ending nouns (सड़क, बत्ती,
# वीज, ...) and loanword phrases (स्ट्रीट लाइट) don't inflect this way and needed no change --
# confirmed by the same probing, not assumed. Odia not audited the same way (no verified oblique
# forms in hand) -- flagged, not guessed.
_CATEGORY_KEYWORDS: dict[ServiceCategory, dict[str, list[str]]] = {
    ServiceCategory.WASTE_SANITATION: {
        "en": ["garbage", "waste", "trash", "sanitation", "dump", "litter", "rubbish"],
        "hi": ["कचरा", "कचरे", "कूड़ा", "कूड़े"], "mr": ["कचरा", "कचऱ्या"], "or": ["ଆବର୍ଜନା"],
        "gu": ["કચરો", "કચરાની"], "bn": ["আবর্জনা", "ময়লা"],
    },
    ServiceCategory.WATER_DRAINAGE: {
        "en": ["water", "drain", "drainage", "sewage", "sewer", "pipeline", "pipe connection", "flood"],
        "hi": ["पानी", "नाला", "नाले", "पाइप"], "mr": ["पाणी", "पाण्या"], "or": ["ପାଣି"],
        "gu": ["પાણી", "ગટર"], "bn": ["পানি", "জল", "নর্দমা"],
    },
    ServiceCategory.ROADS_POTHOLES: {
        "en": ["road", "pothole", "footpath", "pavement", "civil work"],
        # mr "रस्त्याच" (genitive-only, e.g. रस्त्याची/रस्त्याचा/रस्त्याचे -- "of/about the road"),
        # deliberately narrower than the bare oblique stem "रस्त्या" used for the other nouns in
        # this file: रस्ता's locative form "रस्त्यावर"/"रस्त्यावरचा" ("on the road") is an
        # extremely common way to LOCATE a completely different complaint (a streetlight or a
        # pothole ON the road, garbage ON the road), not a complaint about the road itself. A bare
        # "रस्त्या" match caught during this fix's own regression check: "रस्त्यावरचा दिवा बंद
        # आहे" ("the streetlight on the road is off") flipped from the correct STREETLIGHTS to
        # ROADS_POTHOLES, because ROADS_POTHOLES is checked first in _CATEGORY_KEYWORDS's
        # iteration order and "रस्त्या" is a substring of "रस्त्यावरचा" too. The genitive-only
        # substring still catches the real gap ("रस्त्याची तक्रार") without swallowing every
        # other complaint that merely happens to be located on a road.
        "hi": ["सड़क", "गड्ढा", "गड्ढे"], "mr": ["रस्ता", "रस्त्याच", "खड्डा", "खड्ड्या"], "or": ["ରାସ୍ତା"],
        # gu "રસ્તાન" (genitive-only stem, covers રસ્તાની/રસ્તાનો/રસ્તાનું -- "of the road"),
        # same narrowing as mr "रस्त्याच" above and for the same reason: Gujarati masculine nouns
        # ending in -ો shift to oblique -ા before a postposition (દીકરો -> દીકરાની, "of the son"),
        # so રસ્તો ("road") has the identical bare-nominative-only gap પાણી/रस्ता had -- but its
        # locative form "રસ્તા પર" ("on the road") is just as common a way to locate an unrelated
        # complaint, confirmed by this fix's own regression check ("રસ્તા પર કચરો છે" correctly
        # stayed WASTE_SANITATION, not ROADS_POTHOLES, precisely because "રસ્તાન" does NOT match
        # the locative "રસ્તા પર"/"રસ્તામાં" forms). ખાડાની ("of the pothole") added as a literal
        # rather than a stem, matching કચરાની's precedent above -- ખાડો has no comparable
        # generic-location idiom, so the extra caution wasn't needed there.
        "gu": ["રસ્તો", "રસ્તાન", "ખાડો", "ખાડાની"],
        "bn": ["রাস্তা", "গর্ত"],
    },
    ServiceCategory.STREETLIGHTS: {
        "en": ["streetlight", "street light", "street lamp", "lamp post"],
        "hi": ["स्ट्रीट लाइट", "बत्ती"], "mr": ["स्ट्रीट लाइट", "दिवा", "दिव्या"], "or": ["ଆଲୋକ"],
        "gu": ["સ્ટ્રીટ લાઈટ", "બત્તી"], "bn": ["স্ট্রিট লাইট", "বাতি"],
    },
}

# Known-but-unsupported services -- checked explicitly so "electricity" never gets silently
# absorbed into STREETLIGHTS (they share the word "electric" in casual English) or ignored
# entirely (which would let a generic vector search return an unrelated WATER/ROADS chunk).
_OUT_OF_SCOPE_KEYWORDS: dict[str, list[str]] = {
    "en": ["electricity", "electric connection", "electric meter", "power connection", "power supply"],
    "hi": ["बिजली"], "mr": ["वीज"], "or": ["ବିଦ୍ୟୁତ"],
    "gu": ["વીજળી"],
    # bn: বিদ্যুৎ ("electricity") ends in the letter ৎ (khanda ta), which Bengali sandhi rules
    # regularly change to ত when a vowel-initial suffix follows -- বিদ্যুৎ + এর ("of electricity")
    # surfaces as বিদ্যুতের, not বিদ্যুতেরৎ. Unlike Marathi/Gujarati's vowel-final noun mutation
    # (this file's other oblique-case fixes), Bengali is otherwise agglutinative -- most nouns here
    # (রাস্তা/গর্ত/আবর্জনা) keep their own shape intact under a suffix, confirmed by this fix's own
    # regression check. বিদ্যুৎ is the one specific exception found: without this entry,
    # "বিদ্যুতের নতুন সংযোগ চাই" ("I want a new electricity connection") missed the ELECTRICITY
    # out-of-scope flag entirely and fell to the generic "new connection" label instead -- still
    # correctly kept out of RAG, but with a less specific/honest response than the dedicated
    # "don't have electricity" message this KB is supposed to give.
    "bn": ["বিদ্যুৎ", "বিদ্যুতে"],
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
    "gu": ["નવું જોડાણ"],
    "bn": ["নতুন সংযোগ"],
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
    "gu": ["નવું પાણી જોડાણ"],
    "bn": ["নতুন পানির সংযোগ"],
}


def _any_match(text: str, keyword_lists: dict[str, list[str]]) -> list[str]:
    lowered = text.lower()
    return [kw for kws in keyword_lists.values() for kw in kws if kw.lower() in lowered]


def classify(question: str) -> ClassificationResult:
    """Classifies one question. Never raises. A complaint-verb match or a named service category
    means TYPE_A_COMPLAINT (possibly still missing a category/location, which the caller asks
    for). Failing that, a real "what can you do" question is CAPABILITIES; anything else that
    matched nothing at all is UNCLEAR -- never silently defaulted to TYPE_A_COMPLAINT (see
    QuestionIntent.UNCLEAR's own docstring for the bug this replaced)."""
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
    how_to_file_matches = _any_match(text, _HOW_TO_FILE_COMPLAINT_KEYWORDS)

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

    # "How do I file a complaint?" -- asking about the PROCESS, not reporting anything right now.
    # Deliberately wins UNCONDITIONALLY once a how-to-file phrase matches, even over a `state_
    # matches` hit -- an earlier version of this fix required `not state_matches`, which produced
    # a real, caught-before-shipping inconsistency: "How do I report a water leakage?" kept
    # returning TYPE_A_COMPLAINT (because "leak" is also a state keyword, matched inside
    # "leakage") while its own word-for-word Hindi equivalent, "पानी के रिसाव की शिकायत कैसे
    # करें?", correctly became CAPABILITIES (Hindi's state list has no "leak"-equivalent generic
    # topic-noun to false-positive on). Both phrasings mean exactly the same thing and must behave
    # identically. The `_HOW_TO_FILE_COMPLAINT_KEYWORDS` phrases are all specifically "how [do/
    # can] I [report/file/complain/lodge/raise]" -- a genuine, immediate complaint essentially
    # never uses that interrogative construction ("Street light not working near my house" has no
    # "how do i ..." in it at all, so this branch is never even reached for it); a state keyword
    # co-occurring with an explicit how-to-file phrase is far more often "leak" used as a bare
    # topic noun than a real active-problem report.  Checked before service_info/category so a
    # bare category mention (e.g. "पानी") inside the how-to question can't force TYPE_A_COMPLAINT
    # via the `complaint_matches or category` fallback further below -- exactly the mechanism that
    # produced the real, reported bug this closes. CAPABILITIES already gives an accurate, honest
    # answer to this ("just describe your issue and location, and I'll create the complaint for
    # you") without a RAG lookup that has no "how to use this app" content to find.
    if how_to_file_matches:
        return ClassificationResult(
            intent=QuestionIntent.CAPABILITIES,
            service_category=None,
            out_of_scope_service=None,
            matched_keywords=how_to_file_matches,
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

    # TYPE_A: an explicit complaint-verb match, or a named civic category -- real signal that
    # this is (or is about) a civic complaint, even if the category/location still needs
    # clarifying. Checked before CAPABILITIES/UNCLEAR below so an actual complaint always wins.
    if complaint_matches or category:
        return ClassificationResult(
            intent=QuestionIntent.TYPE_A_COMPLAINT,
            service_category=category,
            out_of_scope_service=None,
            matched_keywords=complaint_matches + category_matches,
            requests_new_connection=requests_new_connection,
        )

    capabilities_matches = _any_match(text, _CAPABILITIES_KEYWORDS)
    if capabilities_matches:
        return ClassificationResult(
            intent=QuestionIntent.CAPABILITIES,
            service_category=None,
            out_of_scope_service=None,
            matched_keywords=capabilities_matches,
            requests_new_connection=requests_new_connection,
        )

    # Genuinely zero signal -- see QuestionIntent.UNCLEAR's own docstring for why this is no
    # longer silently treated as an unspecified complaint.
    return ClassificationResult(
        intent=QuestionIntent.UNCLEAR,
        service_category=None,
        out_of_scope_service=None,
        matched_keywords=[],
        requests_new_connection=requests_new_connection,
    )

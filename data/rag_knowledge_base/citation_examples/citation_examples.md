# RAG Knowledge Base — Worked Citation Examples

These are hand-authored, worked examples of how a future RAG answer should be composed from this
data set's records, showing the target shape: **Answer → Source title → Organization → clickable
URL** (per the schema's design goal, see `backend/schemas/rag_knowledge.py`'s `Chunk` docstring).
Every chunk already carries `source_title`, `source_url`, and `verification_status`, so a
retrieval pipeline can reconstruct this citation block without a join back to the parent document
or knowledge record.

These examples are illustrative of the *data*, not a working chat UI — no retrieval/generation
code exists yet (out of scope for this phase, see the approved plan).

---

## Example 1 — VERIFIED, state-wide source (Odisha)

**User question:** "How many days does it take to get municipal solid waste lifted from my
street in Odisha?"

**Expected answer:**
> Under the Housing & Urban Development Department's Citizen's Charter, the process time limit
> for lifting municipal solid waste from a road or street is **3 days**. You can lodge a
> complaint online through your ULB's grievance portal (or a city-specific one, e.g.
> mycitymypride.org for Bhubaneswar) or in person with the ward Sanitary Inspector, giving your
> locality/ward and a phone number.

**Citation block:**
- **Source title:** Citizen's Charter (Draft) — Housing & Urban Development Department
- **Organization:** Housing & Urban Development Department, Government of Odisha
- **URL:** https://urban.odisha.gov.in/sites/default/files/2021-05/Draft%20Citizen%20Charter_HUD_Final.pdf
- **Verification status:** VERIFIED

**Backing record:** `OD_STATEWIDE_WASTE_SOLID_WASTE_LIFTING`

---

## Example 2 — VERIFIED, city-specific source with a statutory vs. internal SLA distinction (Mohali)

**User question:** "How fast should a water leak be fixed in Mohali, and what's the toll-free
number?"

**Expected answer:**
> Two different figures apply, and a good answer should not conflate them: under the **Punjab
> Right to Service Act 2011** (a statutory right), a water pipeline leak or sewerage
> blockage/overflow must be fixed within **24 hours**. Separately, the Municipal Corporation's own
> Citizen Charter service standard states **3 days** for the same complaint type — the internal
> grievance system's nodal-officer norm also states 3 days. Report it via the toll-free number
> **1800-137-0007**, the MC CRAMAT mobile app, or in person at the Complaint Centre, Sector 68.

**Citation block:**
- **Source title:** Citizen Charter — Municipal Corporation, Sahibzada Ajit Singh Nagar (Mohali) 2016-17
- **Organization:** Municipal Corporation, Sahibzada Ajit Singh Nagar (Mohali), Department of Local Government, Government of Punjab
- **URL:** https://e-nigam.punjab.gov.in/MCData/Mohali/CITIZENCHARTER.pdf
- **Verification status:** VERIFIED

**Backing record:** `PB_MOHALI_WATER_SUPPLY_SEWERAGE`

**Why this example was chosen:** it demonstrates a case where a single real source states
*multiple, genuinely different* figures for the same complaint type (a statutory SLA vs. an
internal service standard) — the correct behavior is to surface both, labeled, not silently pick
one. See that record's `sla` field for how this is represented in the data.

---

## Example 3 — VERIFIED, city-specific source with a documented gap (Patiala)

**User question:** "Is there a legal deadline for pothole repair in Patiala, like there is for
water leaks in Mohali?"

**Expected answer:**
> No — unlike Mohali's charter, Patiala's Right to Service Act table (2018) does not include a
> roads/potholes entry at all, and Patiala's document provides no multi-level escalation ladder
> for this category either. The only figure available is the Citizen Charter's own service
> standard: **7 days** for "Resolution of Complaints & Grievances received from citizens" under
> Civil Works. There is no separate statutory SLA to cite for this specific category in Patiala.

**Citation block:**
- **Source title:** Citizen Charter — Municipal Corporation Patiala
- **Organization:** Municipal Corporation Patiala, Department of Local Government, Government of Punjab
- **URL:** https://enigambackuprestore.blob.core.windows.net/securefilestructure/MC/Patiala/MCSubMenu/pdf/linkpdf_2_20_2025_45_862.CITIZEN%20CHARTER%20MCP.pdf
- **Verification status:** VERIFIED

**Backing record:** `PB_PATIALA_ROADS_CIVIL_WORKS`

**Why this example was chosen:** it demonstrates the correct behavior when a real, verified
source *doesn't* contain a piece of information a user might expect (by analogy to a similar
record from another city) — the answer must say so honestly rather than filling the gap with a
plausible-sounding but unsourced figure.

---

## Example 4 — SYNTHETIC, clearly disclosed (Nagpur)

**User question:** "How long does pothole repair take in Nagpur?"

**Expected answer:**
> I don't have an officially verified figure for Nagpur specifically. Based on patterns seen in
> other cities' verified citizen charters (typically 7-15 days for road/pothole complaints), a
> representative estimate for Nagpur would be in that same range — but this is **not confirmed
> from an official Nagpur government source**, and should be treated as an estimate only.

**Citation block:**
- **Source title:** Synthetic Representative Civic-Service Record
- **Organization:** JanSarthi AI — synthetic representative record (not sourced from an official document)
- **URL:** _(none — synthetic records never carry a URL)_
- **Verification status:** SYNTHETIC

**Backing record:** `SYN_maharashtra_nagpur_ROADS`

**Why this example was chosen:** it is the clearest illustration of the hard rule this entire
data set is built around — a SYNTHETIC record must never be answered as if it were VERIFIED. The
citation block itself makes this unambiguous (no real organization name, no URL), and the
expected answer text explicitly discloses the estimate's synthetic status rather than stating it
as fact.

---

## Example 5 — SYNTHETIC vs. VERIFIED contrast, same service category

**User question:** "Compare street light repair times in Odisha and Jaipur."

**Expected answer:**
> In Odisha, the process time limit for replacing a damaged street light is **10 days** — this
> is a verified figure from the Housing & Urban Development Department's Citizen's Charter. For
> Jaipur, no equivalent verified source was found for this data set; a representative estimate
> (7-10 days, based on patterns from other verified cities) is available but **should not be
> presented with the same confidence** as the Odisha figure, since it has not been individually
> checked against a real Jaipur government source.

**Citation blocks:**
| | Source title | Organization | URL | Verification status |
|---|---|---|---|---|
| Odisha | Citizen's Charter (Draft) — Housing & Urban Development Department | Housing & Urban Development Department, Government of Odisha | https://urban.odisha.gov.in/sites/default/files/2021-05/Draft%20Citizen%20Charter_HUD_Final.pdf | VERIFIED |
| Jaipur | Synthetic Representative Civic-Service Record | JanSarthi AI — synthetic representative record (not sourced from an official document) | _(none)_ | SYNTHETIC |

**Backing records:** `OD_STATEWIDE_STREETLIGHTS_REPLACEMENT`, `SYN_rajasthan_jaipur_STREETLIGHTS`

**Why this example was chosen:** a real user question will often span both tiers in one answer
(the whole reason the hybrid strategy exists). The answer must present each tier with its own,
correctly-labeled confidence level side by side — not silently average them into one number, and
not let the more specific-sounding VERIFIED answer's confidence "rub off" on the SYNTHETIC one.

---

## Example 6 — VERIFIED, escalation-path answer (Mohali, statutory appeal)

**User question:** "My street light complaint in Mohali hasn't been resolved in 3 weeks. What do
I do next?"

**Expected answer:**
> You have two possible escalation routes, per Mohali's Citizen Charter. (1) Statutory: under the
> Punjab Right to Service Act 2011 (Service No. 83), you can appeal to the **SDM of the concerned
> district** if the Executive Officer/CMC has not acted; a further appeal goes to the **Deputy
> Commissioner** of the concerned district. (2) Internal grievance ladder: the complaint should
> move from Junior Engineer (3-day norm) to A.C.E. (2 days) to C.E. (1 day) to the **Commissioner**
> (1 day) if unresolved at each level. Since 3 weeks have passed, escalating directly to the SDM
> or the Commissioner's office is reasonable.

**Citation block:**
- **Source title:** Citizen Charter — Municipal Corporation, Sahibzada Ajit Singh Nagar (Mohali) 2016-17
- **Organization:** Municipal Corporation, Sahibzada Ajit Singh Nagar (Mohali), Department of Local Government, Government of Punjab
- **URL:** https://e-nigam.punjab.gov.in/MCData/Mohali/CITIZENCHARTER.pdf
- **Verification status:** VERIFIED

**Backing record:** `PB_MOHALI_STREETLIGHTS_REPAIR`

**Why this example was chosen:** demonstrates that `escalation_procedure`/`escalation_authority`
are first-class, citable content too — not just the primary SLA — which matters for the app's
existing complaint-tracking/escalation feature (see `backend/services/assignment_service.py`) as
a natural future consumer of this data.

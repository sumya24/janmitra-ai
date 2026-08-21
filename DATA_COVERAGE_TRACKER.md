# JanSarthi AI — Data Coverage Tracker

**What this file is:** one master table, per state/UT, showing exactly what data exists and what's
missing across the full location chain, the four civic services, and Ask Sarthi's three service
types — so a single glance tells you what's usable today, what's missing, and how to go get it.
Checked directly against the live database and the real data files, most recently **2026-08-21**
after the real Ward import (§11) — nothing here is estimated.

**How to keep it updatable:** when new data is added, re-run the checks noted at the bottom of
each section and flip the affected cells from ❌ to ✅ in place. Edit this file directly — it is
not meant to be regenerated from scratch each time.

Lives in the project root (not `docs/`) so it's easy to find.

---

## 1. The location chain — what each column means

```
State/UT → District → Sub-District → ULB (Municipal Corporation) → Zone → Ward → Locality
```

Each level is a real database table, linked to the one above it by a foreign key
(`backend/models.py`: `State`, `District`, `SubDistrict`, `Ulb`, `Zone`, `Ward`, `Locality`).

**As of 2026-08-21: District, ULB, and Ward are all populated with real government data for the 25
states that already have RAG civic-service coverage** (671 real districts, 4,489 real ULBs, 90,172
real wards — see §10 and §11). Deliberately scoped that way, not to all 36 states — a
precisely-named ward in a state Ask Sarthi has no civic-service content for wouldn't actually help
anyone. **Sub-District and Zone still have zero rows anywhere, for any state** — not part of either
import, nothing entered there yet. **Locality still only has the original 6 example rows** (one per
seeded city) — the ward source file has no locality-level breakdown, so a real locality import is a
separate, even-deeper future step. See §11 for the full account of the ward import.

## 2. The four civic services — what each column means

Every complaint (and every knowledge-base article) belongs to exactly one of these four fixed
categories (`backend/schemas/rag_knowledge.py: ServiceCategory`):

| Column | Covers |
|---|---|
| Waste/Sanitation | Garbage collection, sanitation |
| Water/Drainage | Water supply, drainage/sewage |
| Roads/Potholes | Road damage, potholes |
| Streetlights | Non-working/damaged streetlights |

A ✅ here means: Ask Sarthi's knowledge base has at least one real article about that service for
that state.

**What "2V+2S" actually means** (this notation caused confusion, so spelling it out plainly):
each cell is a count of knowledge-base *articles* for that state + that service, split into two
kinds:
- **V = Verified** — an article that was checked against a real, live government/municipal
  source. `2V` means 2 such articles exist.
- **S = Synthetic** — a clearly-labeled example article, written to fill the gap, with **no real
  source behind it** — not something to show a citizen as if it were official. `2S` means 2 such
  placeholder articles exist.

So **"Andhra Pradesh, Waste/Sanitation: 1V+2S"** reads as: *1 real, source-checked article, plus 2
placeholder articles, for garbage/sanitation questions about Andhra Pradesh.* A cell with `0V+2S`
would mean *nothing real yet, only placeholders* — worth knowing even though it still shows ✅.
The CSV version (§7) splits these into separate numeric columns instead of one combined
string, which is easier to sort/filter than reading "V+S" text.

## 3. Ask Sarthi's three service types — what each column means

| Column | What it does | Depends on location data? |
|---|---|---|
| TYPE_A | Files a real complaint through chat | No — works the same everywhere, always ✅ |
| TYPE_B | Answers a civic-service question | **Yes** — only works if that state has knowledge-base data (§2); ❌ otherwise means Ask Sarthi has nothing real to answer with for that state |
| TYPE_C | Checks status of a citizen's own complaint | No — works the same everywhere, always ✅ |

TYPE_B's column below is the one that actually moves per state — it's ✅ exactly when at least one
of the four service columns for that row is ✅.

---

## 4. The master table (all 36 states/UTs)

| State/UT | District | Sub-District | ULB | Zone | Ward | Locality | Waste/Sanitation | Water/Drainage | Roads/Potholes | Streetlights | TYPE_A | TYPE_B | TYPE_C |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Andaman and Nicobar Islands (UT) | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ✅ |
| Andhra Pradesh | ✅ 26 | ❌ | ✅ 119 | ❌ | ✅ 3786 | ❌ | ✅ 2V+2S | ✅ 2V+2S | ✅ 2V+2S | ✅ 2V+2S | ✅ | ✅ | ✅ |
| Arunachal Pradesh | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ✅ |
| Assam | ✅ 35 | ❌ | ✅ 97 | ❌ | ✅ 1014 | ❌ | ✅ 1V+1S | ✅ 1V+1S | ✅ 1V+1S | ✅ 1V+1S | ✅ | ✅ | ✅ |
| Bihar | ✅ 38 | ❌ | ✅ 231 | ❌ | ✅ 5017 | ❌ | ✅ 2V+2S | ✅ 2V+2S | ✅ 2V+2S | ✅ 1V+2S | ✅ | ✅ | ✅ |
| Chandigarh (UT) | ✅ 1 | ❌ | ✅ 1 | ❌ | ✅ 35 | ❌ | ✅ 1V+0S | ✅ 1V+0S | ✅ 1V+0S | ✅ 1V+0S | ✅ | ✅ | ✅ |
| Chhattisgarh | ✅ 33 | ❌ | ✅ 168 | ❌ | ✅ 3251 | ❌ | ✅ 1V+0S | ✅ 1V+0S | ✅ 1V+0S | ❌ | ✅ | ✅ | ✅ |
| Dadra and Nagar Haveli and Daman and Diu (UT) | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ✅ |
| Delhi (UT) | ✅ 11 | ❌ | ✅ 4 | ❌ | ✅ 272 | ❌ | ✅ 3V+1S | ✅ 2V+1S | ✅ 2V+1S | ✅ 1V+1S | ✅ | ✅ | ✅ |
| Goa | ✅ 2 | ❌ | ✅ 14 | ❌ | ✅ 226 | ❌ | ✅ 1V+0S | ✅ 1V+0S | ✅ 1V+0S | ✅ 1V+0S | ✅ | ✅ | ✅ |
| Gujarat | ✅ 33 | ❌ | ✅ 163 | ❌ | ✅ 1367 | ✅ | ✅ 2V+2S | ✅ 2V+2S | ✅ 2V+2S | ✅ 2V+2S | ✅ | ✅ | ✅ |
| Haryana | ✅ 22 | ❌ | ✅ 87 | ❌ | ✅ 1686 | ❌ | ✅ 2V+2S | ✅ 2V+2S | ✅ 2V+2S | ✅ 2V+2S | ✅ | ✅ | ✅ |
| Himachal Pradesh | ✅ 12 | ❌ | ✅ 60 | ❌ | ✅ 553 | ❌ | ✅ 1V+0S | ✅ 1V+0S | ✅ 1V+0S | ✅ 1V+0S | ✅ | ✅ | ✅ |
| Jammu and Kashmir (UT) | ✅ 20 | ❌ | ✅ 78 | ❌ | ✅ 1124 | ❌ | ✅ 1V+0S | ✅ 1V+0S | ✅ 1V+0S | ✅ 1V+0S | ✅ | ✅ | ✅ |
| Jharkhand | ✅ 24 | ❌ | ✅ 46 | ❌ | ✅ 1054 | ❌ | ✅ 1V+0S | ✅ 1V+0S | ✅ 1V+0S | ✅ 1V+0S | ✅ | ✅ | ✅ |
| Karnataka | ✅ 31 | ❌ | ✅ 300 | ❌ | ✅ 7040 | ✅ | ✅ 2V+2S | ✅ 2V+2S | ✅ 1V+2S | ✅ 1V+2S | ✅ | ✅ | ✅ |
| Kerala | ✅ 14 | ❌ | ✅ 93 | ❌ | ✅ 3538 | ❌ | ✅ 2V+2S | ✅ 2V+2S | ✅ 2V+2S | ✅ 2V+2S | ✅ | ✅ | ✅ |
| Ladakh (UT) | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ✅ |
| Lakshadweep (UT) | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ✅ |
| Madhya Pradesh | ✅ 55 | ❌ | ✅ 406 | ❌ | ✅ 7599 | ❌ | ✅ 2V+2S | ✅ 1V+2S | ✅ 1V+2S | ✅ 1V+2S | ✅ | ✅ | ✅ |
| Maharashtra | ✅ 36 | ❌ | ✅ 400 | ❌ | ✅ 6944 | ✅ | ✅ 3V+2S | ✅ 2V+2S | ✅ 2V+2S | ✅ 2V+2S | ✅ | ✅ | ✅ |
| Manipur | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ✅ |
| Meghalaya | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ✅ |
| Mizoram | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ✅ |
| Nagaland | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ✅ |
| Odisha | ✅ 30 | ❌ | ✅ 115 | ❌ | ✅ 2107 | ✅ | ✅ 1V+0S | ✅ 3V+0S | ✅ 2V+0S | ✅ 1V+0S | ✅ | ✅ | ✅ |
| Puducherry (UT) | ✅ 2 | ❌ | ✅ 3 | ❌ | ✅ 92 | ❌ | ✅ 1V+0S | ✅ 1V+0S | ✅ 1V+0S | ✅ 1V+0S | ✅ | ✅ | ✅ |
| Punjab | ✅ 23 | ❌ | ✅ 166 | ❌ | ✅ 3200 | ❌ | ✅ 2V+0S | ✅ 6V+0S | ✅ 2V+0S | ✅ 2V+0S | ✅ | ✅ | ✅ |
| Rajasthan | ✅ 41 | ❌ | ✅ 207 | ❌ | ✅ 7615 | ❌ | ✅ 2V+2S | ✅ 2V+2S | ✅ 2V+2S | ✅ 2V+2S | ✅ | ✅ | ✅ |
| Sikkim | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ✅ |
| Tamil Nadu | ✅ 38 | ❌ | ✅ 647 | ❌ | ✅ 12684 | ❌ | ✅ 2V+2S | ✅ 3V+2S | ✅ 2V+2S | ✅ 2V+2S | ✅ | ✅ | ✅ |
| Telangana | ✅ 33 | ❌ | ✅ 137 | ❌ | ✅ 3451 | ❌ | ✅ 2V+2S | ✅ 3V+2S | ✅ 2V+2S | ✅ 2V+2S | ✅ | ✅ | ✅ |
| Tripura | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ✅ |
| Uttar Pradesh | ✅ 75 | ❌ | ✅ 725 | ❌ | ✅ 12398 | ✅ | ✅ 2V+2S | ✅ 2V+2S | ✅ 2V+2S | ✅ 2V+2S | ✅ | ✅ | ✅ |
| Uttarakhand | ✅ 13 | ❌ | ✅ 99 | ❌ | ✅ 1120 | ❌ | ✅ 1V+0S | ✅ 1V+0S | ✅ 1V+0S | ✅ 1V+0S | ✅ | ✅ | ✅ |
| West Bengal | ✅ 23 | ❌ | ✅ 127 | ❌ | ✅ 2999 | ✅ | ✅ 2V+2S | ✅ 2V+2S | ✅ 3V+2S | ✅ 2V+2S | ✅ | ✅ | ✅ |

*(District/ULB/Ward counts as of 2026-08-21 — real data imported from India's official Local
Government Directory, see §10 for District/ULB and §11 for Ward. The Locality column still
reflects only the original 6 example rows — the ward source file has no locality-level breakdown,
so a real locality import remains a separate future step.)*

**Reading it in one line:** a row that's all ❌ except TYPE_A/TYPE_C means that state can still
*take* a complaint and *track* it, but Ask Sarthi has nothing real to say if someone asks a
civic question about it — 11 of 36 rows are in exactly that state today (down from 19 at the
start of this session — Chandigarh, Goa, Jharkhand, Uttarakhand, Chhattisgarh, Himachal Pradesh,
Puducherry, and Jammu and Kashmir were closed or partially closed, see
`data/rag_knowledge_base/sources/candidate_urls.md` Rounds 14–18).

*(Re-generate this table from live data any time — see the SQL/Python snippets in §8.)*

---

## 5. Drill-down: what the chain actually looks like for one state (Maharashtra)

**Updated 2026-08-21, twice: first after the real District/ULB import (§10) — Maharashtra went
from 1 seeded district/ULB to 36 real districts and 400 real ULBs — then again after the real Ward
import (§11), which took it from 1 example ward to 6,944 real wards.**
The master table in §4 only shows ✅/❌ + a count per level — it doesn't show *what the actual
data is*. Here's Maharashtra, walked one level at a time:

```
State:         Maharashtra                          ✅ (one of the real 36 states)
  ↓
District:      36 real districts (e.g. Pune, Mumbai City, Nagpur, Nashik, Thane, ...)
                                                      ✅ (up from 1 example district)
  ↓
Sub-District:  — nothing stored —                     ❌ (this level is empty for EVERY state,
                                                            not just Maharashtra — see §1)
  ↓
ULB:           400 real ULBs across those districts (e.g. Pune Municipal Corporation,
               Pimpri Chinchwad, Baramati, Daund, Lonavala, ... all real, under Pune district
               alone)                                ✅ (up from 1 example ULB)
  ↓
Zone:          — nothing stored —                     ❌ (this level is empty for EVERY state,
                                                            not just Maharashtra — see §1)
  ↓
Ward:          6,944 real wards across those 400 ULBs (e.g. Pune Municipal Corporation alone has
               43 real wards — Ward 22, Kothrud is one of them; Kolhapur, Nashik, Nagpur, Thane,
               ... each have their own full real ward list too)
                                                      ✅ (up from 1 example ward, see §11)
  ↓
Locality:      Kothrud                                ✅ (still only this ONE example locality —
                                                            the ward source file has no
                                                            locality-level breakdown, see §11)
```

**What this means in practice today:** a citizen in Maharashtra now has their *city* (ULB) chosen
from a real, complete list — all 400 real Maharashtra ULBs — and, within that city, a real,
complete list of *wards* too (Pune Municipal Corporation's real 43 wards, not just one example).
Only the *locality* (neighborhood-within-ward) level still has just the one seeded example per
flagship city — that's the one gap left in this chain, see §11.

### The same drill-down for the 25 states with real district/ULB/ward data (see §4 for the full table)

| State | Real districts | Real ULBs | Real wards |
|---|---:|---:|---:|
| Uttar Pradesh | 75 | 725 | 12,398 |
| Tamil Nadu | 38 | 647 | 12,684 |
| Madhya Pradesh | 55 | 406 | 7,599 |
| Rajasthan | 41 | 207 | 7,615 |
| Karnataka | 31 | 300 | 7,040 |
| Maharashtra | 36 | 400 | 6,944 |
| Bihar | 38 | 231 | 5,017 |
| Andhra Pradesh | 26 | 119 | 3,786 |
| Kerala | 14 | 93 | 3,538 |
| Telangana | 33 | 137 | 3,451 |
| Chhattisgarh | 33 | 168 | 3,251 |
| Punjab | 23 | 166 | 3,200 |
| West Bengal | 23 | 127 | 2,999 |
| Odisha | 30 | 115 | 2,107 |
| Haryana | 22 | 87 | 1,686 |
| Gujarat | 33 | 163 | 1,367 |
| Jammu and Kashmir | 20 | 78 | 1,124 |
| Uttarakhand | 13 | 99 | 1,120 |
| Jharkhand | 24 | 46 | 1,054 |
| Assam | 35 | 97 | 1,014 |
| Himachal Pradesh | 12 | 60 | 553 |
| Delhi | 11 | 4 | 272 |
| Goa | 2 | 14 | 226 |
| Puducherry | 2 | 3 | 92 |
| Chandigarh | 1 | 1 | 35 |

**All other 11 states/UTs:** zero RAG coverage (§4), deliberately excluded from this import — see
§10 for why.

---

## 6. What to actually do about each ❌ — two very different kinds of gap

The location columns (District → Locality) and the service columns (the 4 civic categories) are
**missing for completely different reasons**, so they need different fixes:

### District / Sub-District / ULB / Zone / Ward / Locality — public data, fetch/enter it yourselves
This is factual, publicly published information (which wards exist in which city, which ULB
governs them) — from the **Ministry of Housing and Urban Affairs' ULB directory**, each state's
**Census/Delimitation Commission records**, or a city corporation's own website. No special
"verification" process is needed beyond normal data-entry accuracy — this is a "go get the list
and enter it" task, the same mechanical process already used for the 6 seeded cities
(`scripts/seed_multi_ward_data.py`). **Recommend: fetch/enter directly, no research judgment
calls needed.**

### Waste/Sanitation, Water/Drainage, Roads/Potholes, Streetlights — needs real, verified content
This is not a list of names — it's actual civic-process knowledge ("who do I contact," "what
documents do I need," "what's the SLA for a repair"). Getting this right requires finding and
checking a **real, live government or municipal source** per state per category, the same
process already used for the 129 verified records that exist today
(`data/rag_knowledge_base/sources/`). The project's own data-quality report already documents
real obstacles hit doing this (some government sites block automated access, some have broken
SSL) — **recommend: treat this as ongoing manual research work, state by state, not something to
bulk-generate or scrape.** A synthetic (clearly-labeled, no-real-source) placeholder can fill a
cell short-term, same as the 112 that already exist, but should never be presented to a citizen
as if it were verified.

---

## 7. Filterable CSV versions (open in Excel/Google Sheets)

A markdown table can't be filtered or sorted — these two CSV files (same folder as this file) sit
next to this doc so you can open one in Excel/Google Sheets, turn on its filter/sort dropdowns,
and slice the data however's useful:

### `data_coverage_by_state.csv` — the master table from §4, but spreadsheet-friendly
Same 36 rows, one state/UT per row. The one real difference: every "2V+2S"-style cell from the
markdown table is split into **separate columns** —
`Waste_Sanitation_Verified_Count`, `Waste_Sanitation_Synthetic_Count`,
`Waste_Sanitation_Has_Any_Data` (and the same three columns for the other 3 services) — so you can
sort by "which states have the fewest verified records" or filter to "only states where
Has_Any_Data = No" directly, instead of reading text.

### `location_hierarchy_drilldown.csv` — the actual names from §5, for all 36 states
One row per state, with the real District/Sub-District/ULB/Zone/Ward/Locality names where they
exist (matching §5's table), and `(none)` where nothing's been entered yet. A `Data_Status` column
(`"Example data seeded"` vs `"No location data yet"`) lets you filter straight to the 30 states
that need location data added.

*(Re-generate either file any time from live data with the same Python one-liners used to build
this doc — query `janmitra.db` and `data/rag_knowledge_base/knowledge_records/`, then re-export.)*

---

## 8. How to re-check these numbers later

```sql
-- Location hierarchy row counts
SELECT (SELECT COUNT(*) FROM states), (SELECT COUNT(*) FROM districts),
       (SELECT COUNT(*) FROM sub_districts), (SELECT COUNT(*) FROM ulbs),
       (SELECT COUNT(*) FROM zones), (SELECT COUNT(*) FROM wards),
       (SELECT COUNT(*) FROM localities);
```

```bash
# Knowledge-base record counts, per state and category
python scripts/build_rag_knowledge_base.py --check --stats
# or read the freshly generated:
data/rag_knowledge_base/reports/data_quality_report.md
```

---

## 9. Supporting detail — how the knowledge base is actually built

Checked directly against the files on disk and the live vector database (not documentation):

| Stage | Count | Notes |
|---|---:|---|
| Raw knowledge records | 276 | 164 verified + 112 synthetic (as of 2026-08-21 — see `data/rag_knowledge_base/sources/candidate_urls.md` Rounds 12, 14–18) |
| Built documents | 276 | Records rendered into full articles |
| Retrieval chunks | 971 | Documents split into search-sized pieces |
| Embeddings in ChromaDB | 971 | Matches chunk count exactly — fully built, nothing stale |
| Embedding model | `intfloat/multilingual-e5-small` | Real, pretrained, multilingual |

**Where §4's location columns and §2's service columns already sit next to each other
unconnected:** the knowledge base's `state`/`city` fields are plain text, not linked to the
`states`/`districts`/... tables in §1 — they're two separate datasets today. Checked for
accidental overlap anyway: of the 6 cities that have location-hierarchy data, **Ahmedabad,
Kolkata, and Bengaluru** also already have knowledge-base articles; **Pune, Kanpur, and
Bhubaneswar** don't (Maharashtra's knowledge-base cities are Mumbai/Nagpur, UP's are
Lucknow/Varanasi, and Odisha has no city-level articles, only state-wide ones).

---

## 10. Real District/ULB import (2026-08-21) — what was done and how

**Source:** a community-maintained mirror of India's official Local Government Directory (LGD,
`lgdirectory.gov.in`) — `github.com/ramSeraph/opendata` (districts, current as of Jun 2025) and
`github.com/planemad/india-local-government-directory` (`municipal-directory.csv`, the ULB↔district
mapping, retrieved 11 Mar 2022 per that repo's own README), both under the Government Open Data
License – India. **Not a live fetch from lgdirectory.gov.in itself** — its own bulk-download page
is session/CSRF-protected, and its official API requires a registered key this project doesn't
have (checked: the shared public sample key isn't authorized for this dataset). Files kept in
`data/lgd_import/` for reproducibility. Labeled `source_type="OFFICIAL_LGD_MIRROR_DATASET"` on
every imported row — a distinct tier from this project's other source types, so nothing downstream
mistakes a community mirror for a live-government-site fetch.

**Scope, deliberately not "all of India":** only the 25 states/UTs that already have real RAG
civic-service coverage (§4's Waste/Water/Roads/Streetlights columns) — importing precise districts
and ULBs for a state Ask Sarthi has nothing to say about wouldn't help a citizen there. Run via
`scripts/import_lgd_districts_and_ulbs.py` (idempotent — safe to re-run, skips anything already
present).

**What was imported:** 665 new districts + 4,489 new ULBs across 2 runs (started as 4,491; 2 were
caught as near-duplicates of the existing 6 seeded ULBs — "Ahmadabad" vs. the existing "Ahmedabad
Municipal Corporation", "Bbmp" vs. the existing "Bruhat Bengaluru Mahanagara Palike (BBMP)" — same
real city, different spelling in the source data, removed rather than left as confusing
duplicates). The existing 6 seeded districts/ULBs (Pune, Kanpur Nagar, Khordha, Ahmedabad,
Kolkata, Bengaluru Urban) were matched by name and left untouched, not overwritten.

**A real bug found and fixed mid-pass:** the first run matched states by exact string equality,
which silently dropped **Jammu and Kashmir** entirely (20 districts, 78 ULBs) — the source file
spells it "Jammu **And** Kashmir" (capital "And"), which failed an exact match against our
"Jammu **and** Kashmir" even though both filters nominally checked the same 25-state list.
Caught by checking actual per-state row counts against expectations rather than trusting the
first run's summary numbers at face value; fixed by switching both matching points in
`import_lgd_districts_and_ulbs.py` to case/whitespace-normalized comparison, then re-run
(idempotent, so the first run's already-correct 645+4,411 rows for the other 24 states weren't
touched, only J&K's missing rows were added).

**Honest gaps in this pass:**
- `ULB.type` (Municipal Corporation / Municipality / etc.) is left **null** on every imported row —
  the source data's "Localbody Type Code" field has no publicly documented legend anywhere
  locatable (checked); guessing the mapping risked a wrong label, so it's left unset rather than
  fabricated.
- 328 of the 4,821 matched ULBs (7%) have no district mapping available in the 2022 mapping file
  (likely ULBs created since then) — skipped, not guessed.
- Sub-districts, wards, and localities are **not** part of this pass — wards alone would be
  ~90,000 rows for these same 25 states, deliberately scoped out as a separate next step.

**Verified after:** `PRAGMA integrity_check` → `ok`. Full `test_location_system.py` suite (27
tests) still passes unchanged.

---

## 11. Real Ward import (2026-08-21) — what was done and how

**Why this was the next priority:** a citizen doesn't file a complaint by picking a district or
even a city — they pick their **ward**, the level `assignment_service.py` actually routes work
orders on. District/ULB data (§10) fixed the city picker; this pass fixes the level citizens
actually interact with.

**Source:** the same LGD community mirror as §10 —
`github.com/ramSeraph/opendata`'s `urban_local_body_wards` dataset (current as of 30 Apr 2026),
Government Open Data License – India. Kept at `data/lgd_import/urban_local_body_wards.30Apr2026.csv`.
Labeled `source_type="OFFICIAL_LGD_MIRROR_DATASET"`, same tier as the district/ULB rows. Run via
`scripts/import_lgd_wards.py` (idempotent, matches each ward row to a ULB by LGD code, skips
anything already present).

**What was imported:** 90,166 new real wards, matched against every ULB in the database that has a
known LGD `code` (both the 4,489 §10-imported ULBs and the 6 original hand-seeded ones — see below).
Combined with the 6 original example wards, the database now has 90,172 ward rows total across the
25 covered states.

**A real bug found and fixed mid-pass — 6 duplicate ULB rows:** the 6 original hand-seeded ULBs
(Pune, Kanpur, Bhubaneswar, Ahmedabad, Kolkata, Bengaluru/BBMP) didn't have an LGD `code` on them
originally, since they predate the LGD import entirely. LGD's own dataset independently lists each
of these same 6 real cities too, but under a plainer name — "Pune" vs. our
"Pune Municipal Corporation", "Ahmadabad" vs. our "Ahmedabad Municipal Corporation", "Bbmp" vs. our
"Bruhat Bengaluru Mahanagara Palike (BBMP)", etc. — so the §10 import created 6 *duplicate* ULB
rows for cities that already existed under a different name. The real LGD codes for the 6 seeded
ULBs were looked up and backfilled (Pune `251530`, Kanpur `249286`, Bhubaneswar `250520`, Ahmedabad
`251096`, Kolkata `250299`, BBMP `276600`), which let the ward import match them correctly — but it
initially attached each city's real wards to the *duplicate* ULB row instead of the actual seeded
one that workers are assigned to, so the 6 flagship cities appeared to still have only 1 ward each
even after the import ran. Caught by checking `SELECT code, COUNT(*) FROM ulbs GROUP BY code HAVING
COUNT(*) > 1`, which showed all 6 codes duplicated. Fixed via `scripts/merge_duplicate_seed_ulbs.py`
— re-points any wards on a duplicate ULB onto the correct seed ULB (checked for ward-name
collisions first: found 0), then deletes the now-empty duplicate. Verified per-city ward totals
after the fix: Pune 43, Kanpur 113, Bhubaneswar 68, Ahmedabad 49, Kolkata 145, BBMP 226.

**Honest gaps in this pass:**
- Localities are **not** part of this import — the ward source file has no locality-level
  breakdown at all, so a real locality import (even deeper than wards) remains a separate future
  step. The 6 original example localities are untouched.
- Sub-Districts and Zones remain empty for every state — unrelated to this pass, same as §10.
- Ward `zone_id` is left **null** on every imported row — there's no Zone data to link it to yet
  (see above).

**Verified after:** `PRAGMA integrity_check` → `ok`. Full `test_location_system.py` suite (27
tests) passes unchanged.

---

## 12. Bottom line

Every system here (location tables, the 4-category knowledge base, Ask Sarthi's 3 service types)
is real, working engineering — nothing is a stub. Every ❌ in the master table above is a **data**
gap, not a **code** gap, and the two kinds of data gap need two different kinds of effort: location
data is a fetch-and-enter task; service-knowledge data is a find-and-verify task. Use §4 to decide
where to spend that effort next.

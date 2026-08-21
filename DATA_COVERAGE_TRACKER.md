# JanSarthi AI — Data Coverage Tracker

**What this file is:** one master table, per state/UT, showing exactly what data exists and what's
missing across the full location chain, the four civic services, and Ask Sarthi's three service
types — so a single glance tells you what's usable today, what's missing, and how to go get it.
Checked directly against the live database and the real data files on **2026-08-20** — nothing
here is estimated.

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
**Two of these 7 levels currently have zero rows anywhere in the database, for any state — Sub-District
and Zone.** Nothing has ever been entered at those two levels, which is why every row in the
master table below shows ❌ in those two columns without exception. It's not that this table
forgot to check them — the columns exist and are simply empty everywhere.

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
| Andhra Pradesh | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ 2V+2S | ✅ 2V+2S | ✅ 2V+2S | ✅ 2V+2S | ✅ | ✅ | ✅ |
| Arunachal Pradesh | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ✅ |
| Assam | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ 1V+1S | ✅ 1V+1S | ✅ 1V+1S | ✅ 1V+1S | ✅ | ✅ | ✅ |
| Bihar | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ 2V+2S | ✅ 2V+2S | ✅ 2V+2S | ✅ 1V+2S | ✅ | ✅ | ✅ |
| Chandigarh (UT) | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ 1V+0S | ✅ 1V+0S | ✅ 1V+0S | ✅ 1V+0S | ✅ | ✅ | ✅ |
| Chhattisgarh | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ 1V+0S | ✅ 1V+0S | ✅ 1V+0S | ❌ | ✅ | ✅ | ✅ |
| Dadra and Nagar Haveli and Daman and Diu (UT) | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ✅ |
| Delhi (UT) | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ 3V+1S | ✅ 2V+1S | ✅ 2V+1S | ✅ 1V+1S | ✅ | ✅ | ✅ |
| Goa | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ 1V+0S | ✅ 1V+0S | ✅ 1V+0S | ✅ 1V+0S | ✅ | ✅ | ✅ |
| Gujarat | ✅ | ❌ | ✅ | ❌ | ✅ | ✅ | ✅ 2V+2S | ✅ 2V+2S | ✅ 2V+2S | ✅ 2V+2S | ✅ | ✅ | ✅ |
| Haryana | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ 2V+2S | ✅ 2V+2S | ✅ 2V+2S | ✅ 2V+2S | ✅ | ✅ | ✅ |
| Himachal Pradesh | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ 1V+0S | ✅ 1V+0S | ✅ 1V+0S | ✅ 1V+0S | ✅ | ✅ | ✅ |
| Jammu and Kashmir (UT) | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ 1V+0S | ✅ 1V+0S | ✅ 1V+0S | ✅ 1V+0S | ✅ | ✅ | ✅ |
| Jharkhand | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ 1V+0S | ✅ 1V+0S | ✅ 1V+0S | ✅ 1V+0S | ✅ | ✅ | ✅ |
| Karnataka | ✅ | ❌ | ✅ | ❌ | ✅ | ✅ | ✅ 2V+2S | ✅ 2V+2S | ✅ 1V+2S | ✅ 1V+2S | ✅ | ✅ | ✅ |
| Kerala | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ 2V+2S | ✅ 2V+2S | ✅ 2V+2S | ✅ 2V+2S | ✅ | ✅ | ✅ |
| Ladakh (UT) | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ✅ |
| Lakshadweep (UT) | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ✅ |
| Madhya Pradesh | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ 2V+2S | ✅ 1V+2S | ✅ 1V+2S | ✅ 1V+2S | ✅ | ✅ | ✅ |
| Maharashtra | ✅ | ❌ | ✅ | ❌ | ✅ | ✅ | ✅ 3V+2S | ✅ 2V+2S | ✅ 2V+2S | ✅ 2V+2S | ✅ | ✅ | ✅ |
| Manipur | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ✅ |
| Meghalaya | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ✅ |
| Mizoram | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ✅ |
| Nagaland | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ✅ |
| Odisha | ✅ | ❌ | ✅ | ❌ | ✅ | ✅ | ✅ 1V+0S | ✅ 3V+0S | ✅ 2V+0S | ✅ 1V+0S | ✅ | ✅ | ✅ |
| Puducherry (UT) | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ 1V+0S | ✅ 1V+0S | ✅ 1V+0S | ✅ 1V+0S | ✅ | ✅ | ✅ |
| Punjab | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ 2V+0S | ✅ 6V+0S | ✅ 2V+0S | ✅ 2V+0S | ✅ | ✅ | ✅ |
| Rajasthan | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ 2V+2S | ✅ 2V+2S | ✅ 2V+2S | ✅ 2V+2S | ✅ | ✅ | ✅ |
| Sikkim | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ✅ |
| Tamil Nadu | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ 2V+2S | ✅ 3V+2S | ✅ 2V+2S | ✅ 2V+2S | ✅ | ✅ | ✅ |
| Telangana | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ 2V+2S | ✅ 3V+2S | ✅ 2V+2S | ✅ 2V+2S | ✅ | ✅ | ✅ |
| Tripura | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ✅ |
| Uttar Pradesh | ✅ | ❌ | ✅ | ❌ | ✅ | ✅ | ✅ 2V+2S | ✅ 2V+2S | ✅ 2V+2S | ✅ 2V+2S | ✅ | ✅ | ✅ |
| Uttarakhand | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ 1V+0S | ✅ 1V+0S | ✅ 1V+0S | ✅ 1V+0S | ✅ | ✅ | ✅ |
| West Bengal | ✅ | ❌ | ✅ | ❌ | ✅ | ✅ | ✅ 2V+2S | ✅ 2V+2S | ✅ 3V+2S | ✅ 2V+2S | ✅ | ✅ | ✅ |

**Reading it in one line:** a row that's all ❌ except TYPE_A/TYPE_C means that state can still
*take* a complaint and *track* it, but Ask Sarthi has nothing real to say if someone asks a
civic question about it — 11 of 36 rows are in exactly that state today (down from 19 at the
start of this session — Chandigarh, Goa, Jharkhand, Uttarakhand, Chhattisgarh, Himachal Pradesh,
Puducherry, and Jammu and Kashmir were closed or partially closed, see
`data/rag_knowledge_base/sources/candidate_urls.md` Rounds 14–18).

*(Re-generate this table from live data any time — see the SQL/Python snippets in §8.)*

---

## 5. Drill-down: what the chain actually looks like for one state (Maharashtra)

The master table in §4 only shows ✅/❌ per level — it doesn't show *what the actual data is*.
Here's Maharashtra, walked one level at a time, showing the real stored values:

```
State:         Maharashtra                          ✅ (one of the real 36 states)
  ↓
District:      Pune                                  ✅ (the only district Maharashtra has)
  ↓
Sub-District:  — nothing stored —                     ❌ (this level is empty for EVERY state,
                                                            not just Maharashtra — see §1)
  ↓
ULB:           Pune Municipal Corporation             ✅ (the only ULB under Pune district)
  ↓
Zone:          — nothing stored —                     ❌ (this level is empty for EVERY state,
                                                            not just Maharashtra — see §1)
  ↓
Ward:          Ward 22                                ✅ (only this ONE example ward — Pune
                                                            Municipal Corporation really has ~160
                                                            wards; the app only has this one)
  ↓
Locality:      Kothrud                                ✅ (only this ONE example locality —
                                                            under the real Ward 22, Pune has many)
```

**What this means in practice:** if a citizen in Pune picks a ward when filing a complaint, they
can currently only ever pick "Ward 22" — no other real Pune ward is in the system yet. The chain
is real and correctly linked, but it's a single example thread through the hierarchy, not the
city's actual full ward list.

### The same drill-down for all 6 states that have any location data at all

| State | District | Sub-District | ULB | Zone | Ward | Locality |
|---|---|---|---|---|---|---|
| Maharashtra | Pune | *(none)* | Pune Municipal Corporation | *(none)* | Ward 22 | Kothrud |
| Uttar Pradesh | Kanpur Nagar | *(none)* | Kanpur Municipal Corporation | *(none)* | Ward 8 | Civil Lines |
| Odisha | Khordha | *(none)* | Bhubaneswar Municipal Corporation | *(none)* | Ward 5 | Saheed Nagar |
| Gujarat | Ahmedabad | *(none)* | Ahmedabad Municipal Corporation | *(none)* | Ward 11 | Navrangpura |
| West Bengal | Kolkata | *(none)* | Kolkata Municipal Corporation | *(none)* | Ward 6 | Salt Lake |
| Karnataka | Bengaluru Urban | *(none)* | Bruhat Bengaluru Mahanagara Palike (BBMP) | *(none)* | Ward 3 | Indiranagar |

**All other 30 states/UTs:** every level below "State" is empty — there is no district, ULB,
ward, or locality entered for them at all yet, not even one example.

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

## 10. Bottom line

Every system here (location tables, the 4-category knowledge base, Ask Sarthi's 3 service types)
is real, working engineering — nothing is a stub. Every ❌ in the master table above is a **data**
gap, not a **code** gap, and the two kinds of data gap need two different kinds of effort: location
data is a fetch-and-enter task; service-knowledge data is a find-and-verify task. Use §4 to decide
where to spend that effort next.

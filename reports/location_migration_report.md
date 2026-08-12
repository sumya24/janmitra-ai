# Location Migration Report

Generated: 2026-08-10T01:14:03.356404+00:00

**Finalization pass note (2026-08-10, later same day):** re-verified against the live database
after a full backend+frontend validation cycle. Row counts have grown further since this report
was generated (users/complaints keep growing because the Playwright E2E suite exercises the real
app against this same dev database on every run) -- re-run `python
scripts/migrate_existing_locations.py` any time to regenerate this report against current data;
it remains deterministic and idempotent (verified: re-running twice in a row produces identical
match counts). The 6 real-city matches and the classification below have not changed. See the
"Classification" section further down for the full A-E breakdown requested during finalization.

Maps EXISTING free-text `ward` values (on `users` and `complaints`) onto the structured location hierarchy, wherever an exact, unambiguous match exists against the seeded `wards` table (via LocationResolver.resolve_ward_by_text -- the same logic applied live to new complaints, see routes/complaints.py). No value is ever guessed -- every unmapped row below has an explicit reason, not a silent skip.

## Summary
- Worker rows with a ward set: 67 -- matched: 6, unmapped: 61
- Complaint rows with a ward set: 46 -- matched: 18, unmapped: 28
- Citizens: 0 considered -- `users.ward` is confirmed unused for the citizen role (see docs/location_data_audit.md §2), so there is nothing to migrate for citizens in this pass.
- `home_*_id` (home/registered location -- a different concept from the operational `ward_id` this script populates) is untouched by this script and remains entirely null for every user, worker and citizen alike, until a future opt-in profile-location feature is built.
- No row was deleted, no `ward` text value was changed, and no record was created for a location this project has no basis to assert.
- Re-run twice against the live database during finalization (2026-08-10) to confirm determinism: identical match counts both times (6 users / 18 complaints matched, against a growing total row count as the E2E suite added more test rows in between runs) -- safe to re-run repeatedly.

## Classification of every distinct unresolved/resolved value

**A. Successfully mapped** (6 distinct ward strings, all real cities actually present in
`scripts/seed_location_master_data.py`'s coverage): `Ward 11 — Navrangpura, Ahmedabad`,
`Ward 22 — Kothrud, Pune`, `Ward 3 — Indiranagar, Bengaluru`, `Ward 5 — Saheed Nagar, Bhubaneswar`,
`Ward 6 — Salt Lake, Kolkata`, `Ward 8 — Civil Lines, Kanpur` — 6 worker rows + 18 complaint rows,
each backfilled with a full state→district→ULB→ward chain.

**B. Partially mapped:** none. This migration's match strategy is all-or-nothing by design (see
`resolve_ward_by_text`): a ward string either resolves to one seeded `Ward` row with its complete
chain, or it doesn't resolve at all. There is no case here of "state matched but ULB didn't" --
that would require fuzzy/partial matching, which was deliberately not implemented (fuzzy matching
risks a false-positive match, i.e. fabricated-by-inference location).

**C. Requires manual review** (real-looking ward labels, genuinely ambiguous, resolvable in
principle if a human confirms the city): `Ward 14 — Rukadi Road` (1 canonical + 12
timestamped/duplicate worker rows from repeated E2E runs, + 2 complaint rows), `Ward 15 — Rukadi
Road` (1 complaint row), `Ward 9 — Shivaji Nagar` (1 worker row). "Rukadi Road" and "Shivaji
Nagar" are both real Indian place names that exist in more than one city (e.g. Rukadi Road is
associated with Kolhapur, Maharashtra in general usage, but nothing in this project's own records
confirms that specifically for this ward) -- an admin who knows which city these accounts
actually belong to could confirm it, but this script will never guess it.

**D. Test/synthetic data that cannot legitimately be mapped** (and must NOT be converted into
fake Indian geography): all 24 distinct `Tracking Test Ward <timestamp>` values in `users`, and
all 19 distinct ones in `complaints` -- Playwright E2E test fixtures (see
`frontend-react/e2e/complaint-tracking.spec.ts`'s `uniquePhone()`-style unique-ward generation).
These are not real locations and were correctly excluded before any city-matching was even
attempted (matched on the literal prefix `"Tracking Test Ward"`, not on failing to resolve).

**E. Truly unresolved real data** (real data with no plausible path to resolution even via manual
review): none identified in the current database. Every unmapped, non-test value falls into C
(ambiguous but resolvable by a human who knows the missing city) rather than E (unresolvable in
principle) -- worth re-checking this category as the dataset grows, since it may not stay empty.

## Users (`users.ward` -> operational `ward_id` etc, NOT `home_ward_id`)

67 worker row(s) with a ward set, 45 distinct value(s).

| ward text | rows affected | outcome |
|---|---|---|
| `Tracking Test Ward 1786147139645` | 1 | UNMAPPED -- Playwright E2E test artifact, not real geography |
| `Tracking Test Ward 1786147182877` | 1 | UNMAPPED -- Playwright E2E test artifact, not real geography |
| `Tracking Test Ward 1786147246240` | 2 | UNMAPPED -- Playwright E2E test artifact, not real geography |
| `Tracking Test Ward 1786147306470` | 1 | UNMAPPED -- Playwright E2E test artifact, not real geography |
| `Tracking Test Ward 1786147364594` | 2 | UNMAPPED -- Playwright E2E test artifact, not real geography |
| `Tracking Test Ward 1786147507900` | 2 | UNMAPPED -- Playwright E2E test artifact, not real geography |
| `Tracking Test Ward 1786147552840` | 2 | UNMAPPED -- Playwright E2E test artifact, not real geography |
| `Tracking Test Ward 1786147672737` | 2 | UNMAPPED -- Playwright E2E test artifact, not real geography |
| `Tracking Test Ward 1786147780241` | 2 | UNMAPPED -- Playwright E2E test artifact, not real geography |
| `Tracking Test Ward 1786148736027` | 2 | UNMAPPED -- Playwright E2E test artifact, not real geography |
| `Tracking Test Ward 1786152378229` | 2 | UNMAPPED -- Playwright E2E test artifact, not real geography |
| `Tracking Test Ward 1786155200643` | 2 | UNMAPPED -- Playwright E2E test artifact, not real geography |
| `Tracking Test Ward 1786283312163` | 2 | UNMAPPED -- Playwright E2E test artifact, not real geography |
| `Tracking Test Ward 1786316942332` | 2 | UNMAPPED -- Playwright E2E test artifact, not real geography |
| `Tracking Test Ward 1786317405963` | 2 | UNMAPPED -- Playwright E2E test artifact, not real geography |
| `Tracking Test Ward 1786317511281` | 2 | UNMAPPED -- Playwright E2E test artifact, not real geography |
| `Tracking Test Ward 1786317594194` | 2 | UNMAPPED -- Playwright E2E test artifact, not real geography |
| `Tracking Test Ward 1786317671145` | 2 | UNMAPPED -- Playwright E2E test artifact, not real geography |
| `Tracking Test Ward 1786317840008` | 2 | UNMAPPED -- Playwright E2E test artifact, not real geography |
| `Tracking Test Ward 1786317974434` | 2 | UNMAPPED -- Playwright E2E test artifact, not real geography |
| `Tracking Test Ward 1786318084694` | 2 | UNMAPPED -- Playwright E2E test artifact, not real geography |
| `Tracking Test Ward 1786318216604` | 2 | UNMAPPED -- Playwright E2E test artifact, not real geography |
| `Tracking Test Ward 1786323602217` | 2 | UNMAPPED -- Playwright E2E test artifact, not real geography |
| `Tracking Test Ward 1786323679844` | 2 | UNMAPPED -- Playwright E2E test artifact, not real geography |
| `Tracking Test Ward 1786323750145` | 2 | UNMAPPED -- Playwright E2E test artifact, not real geography |
| `Ward 11 — Navrangpura, Ahmedabad` | 1 | MATCHED -> ward_id=4 (state_id=7, district_id=4, ulb_id=4) |
| `Ward 14 — Rukadi Road` | 1 | UNMAPPED -- no city recorded anywhere in the project for this ward string; not guessed |
| `Ward 14 — Rukadi Road 1786152369422` | 1 | UNMAPPED -- no city recorded anywhere in the project for this ward string; not guessed |
| `Ward 14 — Rukadi Road 1786155190012` | 1 | UNMAPPED -- no city recorded anywhere in the project for this ward string; not guessed |
| `Ward 14 — Rukadi Road 1786283296754` | 1 | UNMAPPED -- no city recorded anywhere in the project for this ward string; not guessed |
| `Ward 14 — Rukadi Road 1786316899875` | 1 | UNMAPPED -- no city recorded anywhere in the project for this ward string; not guessed |
| `Ward 14 — Rukadi Road 1786317394615` | 1 | UNMAPPED -- no city recorded anywhere in the project for this ward string; not guessed |
| `Ward 14 — Rukadi Road 1786317658096` | 1 | UNMAPPED -- no city recorded anywhere in the project for this ward string; not guessed |
| `Ward 14 — Rukadi Road 1786317827870` | 1 | UNMAPPED -- no city recorded anywhere in the project for this ward string; not guessed |
| `Ward 14 — Rukadi Road 1786317959563` | 1 | UNMAPPED -- no city recorded anywhere in the project for this ward string; not guessed |
| `Ward 14 — Rukadi Road 1786318070478` | 1 | UNMAPPED -- no city recorded anywhere in the project for this ward string; not guessed |
| `Ward 14 — Rukadi Road 1786318200215` | 1 | UNMAPPED -- no city recorded anywhere in the project for this ward string; not guessed |
| `Ward 14 — Rukadi Road 1786323587498` | 1 | UNMAPPED -- no city recorded anywhere in the project for this ward string; not guessed |
| `Ward 14 — Rukadi Road 1786323737814` | 1 | UNMAPPED -- no city recorded anywhere in the project for this ward string; not guessed |
| `Ward 22 — Kothrud, Pune` | 1 | MATCHED -> ward_id=1 (state_id=14, district_id=1, ulb_id=1) |
| `Ward 3 — Indiranagar, Bengaluru` | 1 | MATCHED -> ward_id=6 (state_id=11, district_id=6, ulb_id=6) |
| `Ward 5 — Saheed Nagar, Bhubaneswar` | 1 | MATCHED -> ward_id=3 (state_id=19, district_id=3, ulb_id=3) |
| `Ward 6 — Salt Lake, Kolkata` | 1 | MATCHED -> ward_id=5 (state_id=28, district_id=5, ulb_id=5) |
| `Ward 8 — Civil Lines, Kanpur` | 1 | MATCHED -> ward_id=2 (state_id=26, district_id=2, ulb_id=2) |
| `Ward 9 — Shivaji Nagar` | 1 | UNMAPPED -- no city recorded anywhere in the project for this ward string; not guessed |

## Complaints (`complaints.ward` -> structured location columns)

46 complaint row(s) with a ward set, 27 distinct value(s).

| ward text | rows affected | outcome |
|---|---|---|
| `Tracking Test Ward 1786147139645` | 7 | UNMAPPED -- Playwright E2E test artifact, not real geography |
| `Tracking Test Ward 1786147246240` | 1 | UNMAPPED -- Playwright E2E test artifact, not real geography |
| `Tracking Test Ward 1786147364594` | 1 | UNMAPPED -- Playwright E2E test artifact, not real geography |
| `Tracking Test Ward 1786147507900` | 1 | UNMAPPED -- Playwright E2E test artifact, not real geography |
| `Tracking Test Ward 1786147552840` | 1 | UNMAPPED -- Playwright E2E test artifact, not real geography |
| `Tracking Test Ward 1786147672737` | 1 | UNMAPPED -- Playwright E2E test artifact, not real geography |
| `Tracking Test Ward 1786147780241` | 1 | UNMAPPED -- Playwright E2E test artifact, not real geography |
| `Tracking Test Ward 1786148736027` | 1 | UNMAPPED -- Playwright E2E test artifact, not real geography |
| `Tracking Test Ward 1786152378229` | 1 | UNMAPPED -- Playwright E2E test artifact, not real geography |
| `Tracking Test Ward 1786155200643` | 1 | UNMAPPED -- Playwright E2E test artifact, not real geography |
| `Tracking Test Ward 1786317405963` | 1 | UNMAPPED -- Playwright E2E test artifact, not real geography |
| `Tracking Test Ward 1786317511281` | 1 | UNMAPPED -- Playwright E2E test artifact, not real geography |
| `Tracking Test Ward 1786317594194` | 1 | UNMAPPED -- Playwright E2E test artifact, not real geography |
| `Tracking Test Ward 1786317671145` | 1 | UNMAPPED -- Playwright E2E test artifact, not real geography |
| `Tracking Test Ward 1786317840008` | 1 | UNMAPPED -- Playwright E2E test artifact, not real geography |
| `Tracking Test Ward 1786318084694` | 1 | UNMAPPED -- Playwright E2E test artifact, not real geography |
| `Tracking Test Ward 1786318216604` | 1 | UNMAPPED -- Playwright E2E test artifact, not real geography |
| `Tracking Test Ward 1786323679844` | 1 | UNMAPPED -- Playwright E2E test artifact, not real geography |
| `Tracking Test Ward 1786323750145` | 1 | UNMAPPED -- Playwright E2E test artifact, not real geography |
| `Ward 11 — Navrangpura, Ahmedabad` | 3 | MATCHED -> ward_id=4 (state_id=7, district_id=4, ulb_id=4) |
| `Ward 14 — Rukadi Road` | 2 | UNMAPPED -- no city recorded anywhere in the project for this ward string; not guessed |
| `Ward 15 — Rukadi Road` | 1 | UNMAPPED -- no city recorded anywhere in the project for this ward string; not guessed |
| `Ward 22 — Kothrud, Pune` | 3 | MATCHED -> ward_id=1 (state_id=14, district_id=1, ulb_id=1) |
| `Ward 3 — Indiranagar, Bengaluru` | 3 | MATCHED -> ward_id=6 (state_id=11, district_id=6, ulb_id=6) |
| `Ward 5 — Saheed Nagar, Bhubaneswar` | 3 | MATCHED -> ward_id=3 (state_id=19, district_id=3, ulb_id=3) |
| `Ward 6 — Salt Lake, Kolkata` | 3 | MATCHED -> ward_id=5 (state_id=28, district_id=5, ulb_id=5) |
| `Ward 8 — Civil Lines, Kanpur` | 3 | MATCHED -> ward_id=2 (state_id=26, district_id=2, ulb_id=2) |

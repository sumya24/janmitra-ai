# Database Count Integrity — Forensic Report

Generated during the final data/location/RAG audit. Method: (1) code-inspection of every
migration script to prove what it can and cannot have written, (2) a row-by-row diff of every
original backup row against its counterpart in the live database, matched by primary key,
comparing every original column. Not a top-level count comparison — an actual per-row audit.

## A. Pre-migration state (from the backup, ground truth)

| Table | Count |
|---|---|
| users | 209 (of which 59 are workers) |
| complaints | 42 |
| complaint_rejections | 17 |
| complaint_translations | 14 |

Backup: `db_backups/janmitra_pre_location_migration_20260810T060615.db` — schema confirmed to be
the original 4-table schema (no location columns/tables), `PRAGMA integrity_check` = `ok`.

## B. Post-migration state, before any test activity

**Not separately snapshotted** — no backup was taken at that exact moment. Reconstructed instead
by code-inspecting every migration script for any `INSERT`/`db.add(User(...))`/`db.add(Complaint(...))`
call against the `users`/`complaints` tables:

```
grep -n "INSERT\|db.add\|User(\|Complaint(" scripts/migrate_location_schema.py     -> 0 matches
grep -n "User\|Complaint" scripts/seed_location_master_data.py                     -> 0 matches
grep -n "db.add(User\|db.add(Complaint\|User(\|Complaint(" scripts/migrate_existing_locations.py -> 0 matches
```

All three migration scripts only: (1) `ALTER TABLE`/`CREATE TABLE` (schema, zero rows), (2)
insert rows into the 7 new location tables only, (3) `UPDATE` (via ORM `setattr` + `commit`)
pre-existing `users`/`complaints` rows' new FK columns — never `INSERT` a new `users`/`complaints`
row. Therefore the post-migration-before-tests state is logically identical to pre-migration on
row *count*: **209 users, 42 complaints, 59 workers, 17 rejections, 14 translations** — this is a
proven fact from the code, not an assumption from comparing totals.

## C. Rows created by migration itself

**0 users, 0 complaints.** Proven by the code inspection above, not inferred. Migration only ever
modifies existing rows' new columns or inserts into the new location-hierarchy tables.

## D. Rows created later by tests

**93 new users (IDs 286–378), 14 new complaints, 7 new complaint_rejections** — confirmed by
direct inspection: every new row's `id` is above the backup's maximum id (users: 285, complaints:
56), and every sampled new row has a name/pattern unmistakably from the E2E fixtures — `"Tracking
Test Admin"`, `"Track Worker One"`, `"Just A Citizen"`, `"Voice User"`, `"Test User"`, wards
matching `"Tracking Test Ward <timestamp>"` (18 of the 93 new users) or the `"Ward 14 — Rukadi
Road <timestamp>"` duplicate-account pattern already known from earlier in this project.
Timestamps cluster tightly around this session's `npx playwright test` runs (00:59–02:05 UTC).

**Zero** new rows use the `900000xx` phone pattern this audit's own `tests/test_location_system.py`
pytest fixtures use — confirming, independently of the code-inspection above, that `pytest` never
touched this file (it uses an isolated in-memory SQLite database per `tests/conftest.py`, verified
by `grep -rn "janmitra.db" tests/` returning zero matches).

**Conclusion: 100% of the count growth (209→302 users, 42→56 complaints) is Playwright E2E test
activity accumulated across this project's testing sessions — 0% is migration-created.**

## E. Were any original rows deleted or modified?

**No — verified for all 251 original rows individually, not sampled.**

- Every one of the 209 pre-migration `users` rows (id 6–285) still exists in the live database.
- Every one of the 42 pre-migration `complaints` rows (id 13–56) still exists.
- For each, every original column (`phone, password_hash, full_name, role, preferred_language,
  ward, created_at` for users; `citizen_id, original_text, original_language, translated_text,
  summary, photo_path, status, ward, assigned_worker_id, feedback_rating, feedback_comment,
  created_at` for complaints) was compared byte-for-byte against the backup.

**0 missing rows. 0 modified rows.** The only change to any original row was the *addition* of
values in the new nullable FK columns this migration introduced (`ward_id`, `state_id`, etc.) —
which are new columns, not modifications to any original column.

## Summary table

| | users | complaints | workers (subset) | complaint_rejections | complaint_translations |
|---|---|---|---|---|---|
| Pre-migration | 209 | 42 | 59 | 17 | 14 |
| Post-migration, before tests | 209 (proven identical) | 42 (proven identical) | 59 | 17 | 14 |
| Current (after accumulated test runs) | 302 | 56 | 85 | 24 | 14 |
| Created by migration | 0 | 0 | 0 | 0 | 0 |
| Created by tests | 93 | 14 | 26 | 7 | 0 |
| Original rows deleted | 0 | 0 | — | — | — |
| Original rows unexpectedly modified | 0 | 0 | — | — | — |

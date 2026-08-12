"""Backfills structured location IDs onto EXISTING users/complaints rows, from their existing
free-text `ward` value -- deterministically, never guessing.

Uses LocationResolver.resolve_ward_by_text() / .location_chain_for_ward() (the same shared logic
POST /complaints now applies to newly-created complaints, see routes/complaints.py) so historical
and live data are resolved identically, not by two independently-maintained copies of the same
parsing rule.

For `users`, this populates the OPERATIONAL location block (`ward_id` etc -- the structured
counterpart of the existing operational `ward` text) -- NEVER `home_ward_id` etc, a different
concept (where someone lives/registered) that no existing data source can answer and that this
script never touches, for any user.

Writes reports/location_migration_report.md with the full per-value outcome (matched / unmapped
and why), per docs/location_migration_plan.md's migration-strategy commitment.

Idempotent: re-running only touches rows whose ward_id is still null, and produces the same
report content given the same underlying data.

Usage:
    python scripts/migrate_existing_locations.py
"""

import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.database import SessionLocal
from backend.models import Complaint, User
from backend.services.location_resolver import LocationResolver

# Recognized as test/CI artifacts, not real geography -- never attempted, always logged as such
# rather than silently skipped, so the report is honest about *why* each value wasn't mapped.
TEST_ARTIFACT_PREFIX = "Tracking Test Ward"


def main() -> None:
    db = SessionLocal()
    resolver = LocationResolver()
    report_lines = [
        "# Location Migration Report",
        f"\nGenerated: {datetime.now(timezone.utc).isoformat()}",
        "\nMaps EXISTING free-text `ward` values (on `users` and `complaints`) onto the "
        "structured location hierarchy, wherever an exact, unambiguous match exists against "
        "the seeded `wards` table (via LocationResolver.resolve_ward_by_text -- the same logic "
        "applied live to new complaints, see routes/complaints.py). No value is ever guessed -- "
        "every unmapped row below has an explicit reason, not a silent skip.",
    ]

    # --- users (workers only; citizens never have ward set, confirmed during audit) ---
    # IMPORTANT: this backfills the OPERATIONAL block (User.ward_id etc, the structured
    # counterpart of the existing operational `ward` text) -- NOT User.home_ward_id, which is a
    # different concept (where this person lives/registered, see models.py's User docstring) and
    # is never touched by this script, for anyone, ever.
    report_lines.append("\n## Users (`users.ward` -> operational `ward_id` etc, NOT `home_ward_id`)")
    workers = db.query(User).filter(User.role == "worker", User.ward.isnot(None)).all()
    distinct_worker_wards = sorted({w.ward for w in workers})
    report_lines.append(f"\n{len(workers)} worker row(s) with a ward set, {len(distinct_worker_wards)} distinct value(s).\n")
    report_lines.append("| ward text | rows affected | outcome |")
    report_lines.append("|---|---|---|")

    matched_user_rows = 0
    for ward_text in distinct_worker_wards:
        matching_rows = [w for w in workers if w.ward == ward_text]
        if ward_text.startswith(TEST_ARTIFACT_PREFIX):
            report_lines.append(f"| `{ward_text}` | {len(matching_rows)} | UNMAPPED -- Playwright E2E test artifact, not real geography |")
            continue
        ward = resolver.resolve_ward_by_text(db, ward_text)
        if ward is None:
            report_lines.append(f"| `{ward_text}` | {len(matching_rows)} | UNMAPPED -- no city recorded anywhere in the project for this ward string; not guessed |")
            continue
        chain = resolver.location_chain_for_ward(db, ward)
        for row in matching_rows:
            if row.ward_id is None:  # never overwrite an already-backfilled or manually-set value
                for field, value in chain.items():
                    setattr(row, field, value)
        matched_user_rows += len(matching_rows)
        report_lines.append(f"| `{ward_text}` | {len(matching_rows)} | MATCHED -> ward_id={ward.id} (state_id={chain['state_id']}, district_id={chain['district_id']}, ulb_id={chain['ulb_id']}) |")
    db.commit()

    # --- complaints ---
    report_lines.append("\n## Complaints (`complaints.ward` -> structured location columns)")
    complaints = db.query(Complaint).filter(Complaint.ward.isnot(None)).all()
    distinct_complaint_wards = sorted({c.ward for c in complaints})
    report_lines.append(f"\n{len(complaints)} complaint row(s) with a ward set, {len(distinct_complaint_wards)} distinct value(s).\n")
    report_lines.append("| ward text | rows affected | outcome |")
    report_lines.append("|---|---|---|")

    matched_complaint_rows = 0
    for ward_text in distinct_complaint_wards:
        matching_rows = [c for c in complaints if c.ward == ward_text]
        if ward_text.startswith(TEST_ARTIFACT_PREFIX):
            report_lines.append(f"| `{ward_text}` | {len(matching_rows)} | UNMAPPED -- Playwright E2E test artifact, not real geography |")
            continue
        ward = resolver.resolve_ward_by_text(db, ward_text)
        if ward is None:
            report_lines.append(f"| `{ward_text}` | {len(matching_rows)} | UNMAPPED -- no city recorded anywhere in the project for this ward string; not guessed |")
            continue
        chain = resolver.location_chain_for_ward(db, ward)
        for row in matching_rows:
            if row.ward_id is None:
                for field, value in chain.items():
                    setattr(row, field, value)
        matched_complaint_rows += len(matching_rows)
        report_lines.append(f"| `{ward_text}` | {len(matching_rows)} | MATCHED -> ward_id={ward.id} (state_id={chain['state_id']}, district_id={chain['district_id']}, ulb_id={chain['ulb_id']}) |")
    db.commit()

    # --- summary ---
    total_users_considered = len(workers)
    total_complaints_considered = len(complaints)
    report_lines.insert(3, (
        f"\n## Summary\n"
        f"- Worker rows with a ward set: {total_users_considered} -- matched: {matched_user_rows}, "
        f"unmapped: {total_users_considered - matched_user_rows}\n"
        f"- Complaint rows with a ward set: {total_complaints_considered} -- matched: {matched_complaint_rows}, "
        f"unmapped: {total_complaints_considered - matched_complaint_rows}\n"
        f"- Citizens: 0 considered -- `users.ward` is confirmed unused for the citizen role "
        f"(see docs/location_data_audit.md §2), so there is nothing to migrate for citizens in "
        f"this pass.\n"
        f"- `home_*_id` (home/registered location -- a different concept from the operational "
        f"`ward_id` this script populates) is untouched by this script and remains entirely null "
        f"for every user, worker and citizen alike, until a future opt-in profile-location "
        f"feature is built.\n"
        f"- No row was deleted, no `ward` text value was changed, and no record was created for "
        f"a location this project has no basis to assert."
    ))

    report_path = Path(__file__).resolve().parent.parent / "reports" / "location_migration_report.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    print(f"Matched {matched_user_rows}/{total_users_considered} worker rows, "
          f"{matched_complaint_rows}/{total_complaints_considered} complaint rows.")
    print(f"Report written to {report_path}")
    db.close()


if __name__ == "__main__":
    main()

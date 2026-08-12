"""Additive schema migration for the structured location system (see docs/location_migration_plan.md).

This project has no Alembic/migration tooling (see docs/location_data_audit.md) -- schema changes
are applied by hand, the same way `complaints.ward`/`assigned_worker_id` were added previously.
This script follows that exact precedent for the new columns on `users`/`complaints`, and lets
SQLAlchemy's own `Base.metadata.create_all()` handle the 7 brand-new location-hierarchy tables
(safe: create_all only ever creates *missing* tables, never touches existing ones).

Safe to re-run: every ALTER TABLE is guarded by a PRAGMA table_info() check first, so running
this twice is a no-op the second time, not an error.

IMPORTANT: back up the database before running this the first time on a real database --
this script does NOT take its own backup (the operator is expected to, as documented in
docs/location_migration_plan.md and reports/location_migration_report.md, both of which record
the exact backup path used for this project's own migration).

Usage:
    python scripts/migrate_location_schema.py
"""

import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.config import settings
from backend.database import Base, engine

# (table, column, sql_type) -- exactly matches the new nullable columns added to
# backend/models.py's User and Complaint classes. Order doesn't matter for ALTER TABLE ADD COLUMN.
NEW_USER_COLUMNS = [
    # Operational location -- structured counterpart of the existing `ward` text (workers only).
    ("users", "state_id", "INTEGER"),
    ("users", "district_id", "INTEGER"),
    ("users", "sub_district_id", "INTEGER"),
    ("users", "ulb_id", "INTEGER"),
    ("users", "zone_id", "INTEGER"),
    ("users", "ward_id", "INTEGER"),
    ("users", "locality_id", "INTEGER"),
    # Home/registered location -- a different, currently-unpopulated concept (see models.py).
    ("users", "home_state_id", "INTEGER"),
    ("users", "home_district_id", "INTEGER"),
    ("users", "home_sub_district_id", "INTEGER"),
    ("users", "home_ulb_id", "INTEGER"),
    ("users", "home_zone_id", "INTEGER"),
    ("users", "home_ward_id", "INTEGER"),
    ("users", "home_locality_id", "INTEGER"),
]
NEW_COMPLAINT_COLUMNS = [
    ("complaints", "state_id", "INTEGER"),
    ("complaints", "district_id", "INTEGER"),
    ("complaints", "sub_district_id", "INTEGER"),
    ("complaints", "ulb_id", "INTEGER"),
    ("complaints", "zone_id", "INTEGER"),
    ("complaints", "ward_id", "INTEGER"),
    ("complaints", "locality_id", "INTEGER"),
    ("complaints", "latitude", "FLOAT"),
    ("complaints", "longitude", "FLOAT"),
    ("complaints", "gps_accuracy", "FLOAT"),
    ("complaints", "address", "TEXT"),
]


def _existing_columns(cur: sqlite3.Cursor, table: str) -> set[str]:
    cur.execute(f"PRAGMA table_info({table})")
    return {row[1] for row in cur.fetchall()}


def add_missing_columns(cur: sqlite3.Cursor, columns: list[tuple[str, str, str]]) -> list[str]:
    """Adds each (table, column, type) that doesn't already exist. Returns the list actually added."""
    added = []
    by_table: dict[str, set[str]] = {}
    for table, column, sql_type in columns:
        if table not in by_table:
            by_table[table] = _existing_columns(cur, table)
        if column in by_table[table]:
            continue
        cur.execute(f"ALTER TABLE {table} ADD COLUMN {column} {sql_type}")
        added.append(f"{table}.{column}")
    return added


def main() -> None:
    db_path = settings.DATABASE_URL.removeprefix("sqlite:///")
    print(f"Target database: {db_path}")

    print("\nStep 1: creating the 7 new location-hierarchy tables (skips any that already exist)...")
    import backend.models  # noqa: F401 -- registers State/District/.../Complaint/User on Base

    before = set(Base.metadata.tables.keys())
    Base.metadata.create_all(bind=engine)
    print(f"  Tables now known to the ORM: {sorted(before)}")

    print("\nStep 2: adding new nullable columns to 'users' (home_* location references)...")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    added_user_cols = add_missing_columns(cur, NEW_USER_COLUMNS)
    conn.commit()
    if added_user_cols:
        print(f"  Added: {added_user_cols}")
    else:
        print("  Nothing to add -- already present (safe re-run).")

    print("\nStep 3: adding new nullable columns to 'complaints' (incident location + GPS)...")
    added_complaint_cols = add_missing_columns(cur, NEW_COMPLAINT_COLUMNS)
    conn.commit()
    if added_complaint_cols:
        print(f"  Added: {added_complaint_cols}")
    else:
        print("  Nothing to add -- already present (safe re-run).")

    print("\nStep 4: verifying no existing data was touched...")
    cur.execute("SELECT COUNT(*) FROM users")
    user_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM complaints")
    complaint_count = cur.fetchone()[0]
    print(f"  users: {user_count} rows, complaints: {complaint_count} rows (row counts, not content, checked here)")

    conn.close()
    print("\nSchema migration complete. Existing 'ward' text columns are untouched.")


if __name__ == "__main__":
    main()

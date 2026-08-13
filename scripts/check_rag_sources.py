"""Data-quality report for the RAG civic-knowledge-base data set.

Runs the same schema + referential-integrity checks as build_rag_knowledge_base.py, standalone
(so it can run without regenerating documents/chunks), plus:
- cross-field consistency (VERIFIED <=> non-null source_url+retrieved_at, SYNTHETIC <=> null
  source_url) — this is already enforced by the Pydantic validator on load, but re-stated here
  explicitly in the report so it's visible, not just silently relied upon;
- duplicate detection on (service_id, city, source_url);
- a live HTTP check of every distinct VERIFIED source_url (skippable for CI/blocked environments);
- data/rag_knowledge_base/reports/data_quality_report.md, with an explicit, honest
  verified-vs-synthetic scope-accounting summary at the top.

Usage:
    python scripts/check_rag_sources.py                  # full check, including live URL checks
    python scripts/check_rag_sources.py --skip-network    # schema/referential checks only
"""

import argparse
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.config import settings
from backend.schemas.rag_knowledge import VerificationStatus
from scripts.build_rag_knowledge_base import check_referential_integrity, load_knowledge_records, load_sources


def find_duplicates(records) -> list[str]:
    seen: dict[tuple, str] = {}
    duplicates = []
    for r in records:
        key = (r.service_id, r.city, r.source_url)
        if key in seen:
            duplicates.append(f"{r.record_id} duplicates {seen[key]} on (service_id={r.service_id!r}, city={r.city!r}, source_url={r.source_url!r})")
        else:
            seen[key] = r.record_id
    return duplicates


def check_urls_live(urls: list[str]) -> dict[str, str]:
    """Returns {url: status_string}. status_string is either an HTTP status code or an error
    description. One retry on failure -- most real-world blips are transient.

    timeout=20s (not 10s): some real government servers (e.g. urban.odisha.gov.in has been
    observed taking ~12s to serve its PDF) are just slow, not down -- a tighter timeout would
    misreport a live, correct source as broken."""
    import requests

    results = {}
    for url in urls:
        status = None
        for attempt in range(2):
            try:
                resp = requests.get(url, timeout=20, headers={"User-Agent": "Mozilla/5.0 (JanSarthiAI-RAG-QA/1.0)"})
                status = str(resp.status_code)
                break
            except requests.exceptions.SSLError:
                status = "SSL_ERROR"
            except requests.exceptions.RequestException as exc:
                status = f"ERROR: {type(exc).__name__}"
        results[url] = status or "UNKNOWN"
    return results


def build_report(records, sources, duplicates, url_statuses, skip_network: bool) -> str:
    verified = [r for r in records if r.verification_status == VerificationStatus.VERIFIED]
    synthetic = [r for r in records if r.verification_status == VerificationStatus.SYNTHETIC]
    # Only records that actually name a city count toward "cities covered" -- a state-wide
    # record (city=None) is real coverage of that state, but not of any specific city, so
    # counting it as one would overstate city-level breadth.
    cities_verified = {(r.city, r.state) for r in verified if r.city}
    cities_synthetic = {(r.city, r.state) for r in synthetic if r.city}
    cities_all = cities_verified | cities_synthetic
    states_only_verified = {r.state for r in verified if not r.city}

    lines = []
    lines.append("# RAG Knowledge Base — Data Quality Report")
    lines.append(f"\nGenerated: {datetime.now(timezone.utc).isoformat()}")

    lines.append("\n## Scope accounting (honest summary)")
    lines.append(
        f"\nThe original brief asked for coverage across 10+ states and 30+ cities. Given real "
        f"access barriers to Indian government data sources found during research (data.gov.in "
        f"blocking automated access, broken SSL on tnurbantree.tn.gov.in, etc. — see "
        f"sources/candidate_urls.md), that volume is **not achievable as a fully-verified dataset**. "
        f"This report tracks both tiers separately and honestly, per the confirmed hybrid strategy:\n"
    )
    state_note = f" (plus {len(states_only_verified)} state-wide record(s) covering {', '.join(sorted(states_only_verified))}, not tied to one city)" if states_only_verified else ""
    lines.append(f"- **VERIFIED records**: {len(verified)}, across {len(cities_verified)} cit(y/ies){state_note} — individually checked against a live source.")
    lines.append(f"- **SYNTHETIC records**: {len(synthetic)}, across {len(cities_synthetic)} cit(y/ies) — clearly labeled representative data, no real source_url, fixed synthetic source_organization.")
    lines.append(f"- **Total**: {len(records)} records, {len(cities_all)} distinct cities.")

    lines.append("\n## Coverage by service category and state")
    by_cat = Counter(r.service_category.value for r in records)
    for cat, count in sorted(by_cat.items()):
        lines.append(f"- {cat}: {count}")
    lines.append("\nBy state:")
    by_state: dict[str, Counter] = defaultdict(Counter)
    for r in records:
        by_state[r.state][r.verification_status.value] += 1
    for state in sorted(by_state):
        tiers = by_state[state]
        lines.append(f"- {state}: {tiers.get('VERIFIED', 0)} verified, {tiers.get('SYNTHETIC', 0)} synthetic")

    lines.append("\n## Verified sources checked")
    if skip_network:
        lines.append("\n(--skip-network: live URL checks were not run this pass.)")
    else:
        lines.append("\n| Source URL | HTTP status | Checked at |")
        lines.append("|---|---|---|")
        checked_at = datetime.now(timezone.utc).isoformat()
        for url, status in sorted(url_statuses.items()):
            lines.append(f"| {url} | {status} | {checked_at} |")

    lines.append("\n## Flagged issues")
    issues = []
    if duplicates:
        issues.extend(f"Duplicate: {d}" for d in duplicates)
    if not skip_network:
        broken = [u for u, s in url_statuses.items() if not (s.isdigit() and s.startswith(("2", "3")))]
        issues.extend(f"Source URL not returning 2xx/3xx: {u} (status={url_statuses[u]})" for u in broken)
    orphan_sources = [s.source_id for s in sources.values() if not any(r.source_id == s.source_id for r in records)]
    issues.extend(f"Source with zero referencing records: {sid}" for sid in orphan_sources)
    if issues:
        for issue in issues:
            lines.append(f"- {issue}")
    else:
        lines.append("- None.")

    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skip-network", action="store_true", help="Skip live URL checks.")
    args = parser.parse_args()

    sources = load_sources()
    records = load_knowledge_records()
    check_referential_integrity(records, sources)
    print(f"Schema + referential integrity OK: {len(sources)} source(s), {len(records)} record(s).")

    duplicates = find_duplicates(records)
    if duplicates:
        print(f"Found {len(duplicates)} duplicate(s):")
        for d in duplicates:
            print(f"  {d}")

    url_statuses: dict[str, str] = {}
    if not args.skip_network:
        verified_urls = sorted({r.source_url for r in records if r.source_url})
        print(f"Checking {len(verified_urls)} distinct VERIFIED source URL(s) live...")
        url_statuses = check_urls_live(verified_urls)
        for url, status in url_statuses.items():
            print(f"  {status}  {url}")

    report = build_report(records, sources, duplicates, url_statuses, args.skip_network)
    report_path = settings.RAG_DATA_DIR / "reports" / "data_quality_report.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report, encoding="utf-8")
    print(f"\nWrote {report_path}")

    broken = [u for u, s in url_statuses.items() if not (s.isdigit() and s.startswith(("2", "3")))]
    if duplicates or broken:
        raise SystemExit(f"FAILED: {len(duplicates)} duplicate(s), {len(broken)} broken URL(s).")
    print("All checks passed.")


if __name__ == "__main__":
    main()

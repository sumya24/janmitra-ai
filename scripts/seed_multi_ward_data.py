"""One-time helper: seed multiple administrative areas (wards) across different states/languages
with a worker each, plus citizens filing complaints into various wards — so ward-based routing
(a complaint reaching exactly the worker assigned to that area, and no one else) can actually be
tested with more than the single "Ward 14" area used everywhere else in this repo's tests.

This hits the real running backend (not raw SQL) so it exercises the actual signup/admin/complaint
API paths, same as a real user would. Additive: safe to re-run, everything uses a fresh timestamp
suffix so phone numbers never collide with earlier runs.

Usage: python scripts/seed_multi_ward_data.py
(backend must already be running on http://127.0.0.1:8000)
"""

import json
import subprocess
import time

import requests

BASE = "http://127.0.0.1:8000"

# One ward per major region/language this app supports — deliberately spread across real Indian
# states, not just variations on the one "Ward 14 — Rukadi Road" used everywhere else.
AREAS = [
    {"ward": "Ward 22 — Kothrud, Pune",              "lang": "mr", "worker": "Sunita Pawar"},
    {"ward": "Ward 8 — Civil Lines, Kanpur",          "lang": "hi", "worker": "Rajesh Kumar"},
    {"ward": "Ward 5 — Saheed Nagar, Bhubaneswar",    "lang": "or", "worker": "Debasish Nayak"},
    {"ward": "Ward 11 — Navrangpura, Ahmedabad",      "lang": "gu", "worker": "Mitesh Patel"},
    {"ward": "Ward 6 — Salt Lake, Kolkata",           "lang": "bn", "worker": "Sourav Chatterjee"},
    {"ward": "Ward 3 — Indiranagar, Bengaluru",       "lang": "en", "worker": "Arjun Reddy"},
]

# A few sample complaints per area, in that area's own language, to prove the whole
# language + routing pipeline together — not just routing on its own.
COMPLAINT_TEXT = {
    "mr": "रस्त्यावर खूप कचरा साचला आहे.",
    "hi": "यहाँ सड़क पर पानी भर गया है.",
    "or": "ଏଠାରେ ରାସ୍ତା ବାତି ଖରାପ ହୋଇଛି।",
    "gu": "અહીં ડ્રેનેજ ઓવરફ્લો થઈ રહ્યું છે.",
    "bn": "এখানে একটি বড় গাছ রাস্তা আটকে আছে।",
    "en": "There is a large pothole blocking traffic here.",
}


def main() -> None:
    suffix = str(int(time.time()))[-6:]
    admin_phone = f"7{suffix}00"

    print(f"Seeding admin ({admin_phone})...")
    subprocess.run(
        ["python", "scripts/seed_admin.py", "--phone", admin_phone, "--password", "adminpass123", "--name", "Multi-Ward Seed Admin"],
        check=True,
    )
    admin_token = requests.post(f"{BASE}/auth/login", json={"identifier": admin_phone, "password": "adminpass123"}).json()["access_token"]

    created = []
    for i, area in enumerate(AREAS):
        worker_phone = f"7{suffix}{i + 1:02d}"
        r = requests.post(
            f"{BASE}/admin/workers",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "full_name": area["worker"],
                "phone": worker_phone,
                "password": "workerpass123",
                "ward": area["ward"],
                "preferred_language": area["lang"],
            },
        )
        r.raise_for_status()
        print(f"  worker: {area['worker']:<20} phone={worker_phone} ward={area['ward']!r} lang={area['lang']}")

        # A citizen — in this same area's language — files one complaint into this exact ward.
        citizen_phone = f"7{suffix}{i + 51:02d}"
        r = requests.post(f"{BASE}/auth/signup", json={
            "full_name": f"Citizen of {area['ward'].split(chr(8212))[-1].strip()}",
            "phone": citizen_phone, "password": "citizenpass123", "preferred_language": area["lang"],
            "ward": area["ward"],
        })
        r.raise_for_status()
        citizen_token = r.json()["access_token"]

        r = requests.post(
            f"{BASE}/complaints",
            headers={"Authorization": f"Bearer {citizen_token}"},
            data={"text": COMPLAINT_TEXT[area["lang"]], "language": area["lang"], "ward": area["ward"]},
            timeout=60,
        )
        r.raise_for_status()
        complaint = r.json()
        print(f"    complaint #{complaint['id']}: {complaint['summary']!r}")

        created.append({
            "ward": area["ward"], "worker_phone": worker_phone, "worker_password": "workerpass123",
            "worker_lang": area["lang"], "citizen_phone": citizen_phone, "citizen_password": "citizenpass123",
            "complaint_id": complaint["id"],
        })

    with open("scripts/multi_ward_seed_output.json", "w", encoding="utf-8") as f:
        json.dump({"admin_phone": admin_phone, "admin_password": "adminpass123", "areas": created}, f, ensure_ascii=False, indent=2)

    print(f"\nDone — {len(AREAS)} wards, {len(AREAS)} workers, {len(AREAS)} citizens, {len(AREAS)} complaints.")
    print("Details written to scripts/multi_ward_seed_output.json")


if __name__ == "__main__":
    main()

"""Second, larger seed pass: reuses the 6 wards/workers from seed_multi_ward_data.py and adds
2 more citizens + complaints per ward (3 complaints per ward total, across both scripts), plus
marks one complaint per ward "resolved" so each worker's queue shows a realistic open/resolved
mix instead of a single item.

Requires scripts/multi_ward_seed_output.json to already exist (run seed_multi_ward_data.py first).

Usage: python scripts/seed_multi_ward_data_batch2.py
(backend must already be running on http://127.0.0.1:8000)
"""

import json
import time

import requests

BASE = "http://127.0.0.1:8000"

# Two more complaint texts per language, distinct from the first script's, so a worker's queue
# shows varied content, not three copies of the same sentence.
EXTRA_COMPLAINTS = {
    "mr": ["सार्वजनिक शौचालय गलिच्छ आहे.", "पिण्याच्या पाण्याचा पुरवठा अनियमित आहे."],
    "hi": ["सार्वजनिक पार्क में रोशनी नहीं है.", "नाली का ढक्कन टूटा हुआ है."],
    "or": ["ଏଠାରେ ଏକ ନୂଆ ରାସ୍ତା ଆବଶ୍ୟକ।", "ଆବର୍ଜନା ସଂଗ୍ରହ ଅନିୟମିତ ଅଛି।"],
    "gu": ["જાહેર બગીચામાં કચરો ભરેલો છે.", "શેરીની લાઇટ ઘણા દિવસોથી બંધ છે."],
    "bn": ["এই এলাকায় জলাবদ্ধতা একটি বড় সমস্যা।", "রাস্তার পাশের ল্যাম্পপোস্ট ভাঙা।"],
    "en": ["The public toilet here needs urgent cleaning.", "Stray dogs are becoming a safety concern in this area."],
}


def main() -> None:
    with open("scripts/multi_ward_seed_output.json", encoding="utf-8") as f:
        seed = json.load(f)

    suffix = str(int(time.time()))[-6:]
    all_citizens = []

    for i, area in enumerate(seed["areas"]):
        lang = area["worker_lang"]
        # Find the ward name back from the original AREAS list is not stored directly here, but
        # area dict already has "ward".
        ward = area["ward"]
        print(f"Ward: {ward}")

        complaint_ids_this_ward = [area["complaint_id"]]
        for j, text in enumerate(EXTRA_COMPLAINTS[lang]):
            citizen_phone = f"7{suffix}{i}{j}9"
            r = requests.post(f"{BASE}/auth/signup", json={
                "full_name": f"Resident {i}-{j} of {ward.split(chr(8212))[-1].strip()}",
                "phone": citizen_phone, "password": "citizenpass123", "preferred_language": lang,
                "ward": ward,
            })
            r.raise_for_status()
            citizen_token = r.json()["access_token"]

            r = requests.post(
                f"{BASE}/complaints",
                headers={"Authorization": f"Bearer {citizen_token}"},
                data={"text": text, "language": lang, "ward": ward},
                timeout=60,
            )
            r.raise_for_status()
            complaint = r.json()
            complaint_ids_this_ward.append(complaint["id"])
            print(f"  citizen {citizen_phone}: complaint #{complaint['id']}: {complaint['summary']!r}")
            all_citizens.append({
                "ward": ward, "citizen_phone": citizen_phone, "citizen_password": "citizenpass123",
                "citizen_lang": lang, "complaint_id": complaint["id"],
            })

        # Mark the first complaint in this ward (from batch 1) resolved, via the worker account,
        # so the queue shows a realistic open/resolved mix rather than everything open. The
        # complaint-resolution workflow now requires going through accept -> start -> resolve
        # (see backend/routes/complaints.py) rather than a single status PATCH, which this script
        # predates.
        r = requests.post(f"{BASE}/auth/login", json={"phone": area["worker_phone"], "password": area["worker_password"]})
        worker_token = r.json()["access_token"]
        headers = {"Authorization": f"Bearer {worker_token}"}
        complaint_id = area["complaint_id"]

        r = requests.post(f"{BASE}/complaints/{complaint_id}/accept", headers=headers)
        r.raise_for_status()

        r = requests.post(
            f"{BASE}/complaints/{complaint_id}/start",
            headers=headers,
            data={"assessment": "Assessed the issue on site; proceeding with resolution."},
        )
        r.raise_for_status()

        r = requests.post(
            f"{BASE}/complaints/{complaint_id}/resolve",
            headers=headers,
            data={"completion_status": "Issue resolved and verified on site."},
        )
        r.raise_for_status()
        print(f"  marked complaint #{complaint_id} resolved")

    with open("scripts/multi_ward_seed_batch2_output.json", "w", encoding="utf-8") as f:
        json.dump(all_citizens, f, ensure_ascii=False, indent=2)

    print(f"\nDone — {len(all_citizens)} more citizens/complaints added, 1 resolved per ward.")


if __name__ == "__main__":
    main()

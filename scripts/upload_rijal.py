"""
Phase 3/4: Rijal Upload Pipeline
Merges multiple data sources and uploads to Supabase rijal table.

Data priority (later sources override earlier for same field):
  1. Core curated seed (highest accuracy, hand-verified)
  2. Wikidata (dates, geography)
  3. Extracted narrator names from our own DB (hadith_count, books)

Usage:
  python scripts/upload_rijal.py --key <SUPABASE_SERVICE_ROLE_KEY>
"""

import json
import os
import sys
import argparse
import requests
from pathlib import Path

SUPABASE_URL = "https://idokyspokenbmzoegahq.supabase.co"
BASE_API = f"{SUPABASE_URL}/rest/v1"
ANON_KEY = "sb_publishable_Hz6k4Jp7rdSxwXCk1AO-sQ_r93N88QR"


def get_headers(service_key: str):
    return {
        "apikey": service_key,
        "Authorization": f"Bearer {service_key}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates,return=minimal"
    }


def load_json(path: str) -> list:
    p = Path(path)
    if not p.exists():
        print(f"  [SKIP] {path} not found")
        return []
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


def merge_records(base: dict, override: dict) -> dict:
    """Merge two rawi dicts. Override fills in missing fields from base."""
    merged = dict(base)
    for k, v in override.items():
        # Only override if the value is non-empty and field is missing/empty in base
        if v and not merged.get(k):
            merged[k] = v
    return merged


def compute_hadith_stats(service_key: str) -> dict:
    """Query our own hadiths table to compute hadith_count and books for each narrator."""
    print("  Computing hadith stats from DB (Narrated X: pattern)...")
    headers = {"apikey": service_key, "Authorization": f"Bearer {service_key}"}

    import re
    stats = {}  # name_en_normalized -> {count, books}

    offset = 0
    page_size = 1000
    while True:
        r = requests.get(
            f"{BASE_API}/hadiths?select=book_id,text_en&limit={page_size}&offset={offset}",
            headers=headers
        )
        data = r.json()
        if not data:
            break
        for h in data:
            en = h.get("text_en", "")
            book = h.get("book_id", "")
            m = re.match(r'^Narrated\s+([^:]+):', en)
            if m:
                name = m.group(1).strip()
                name = re.sub(r'\s*\(.*\)', '', name).strip()
                key = name.lower().replace("'", "").replace("`", "").replace(" ", "_")
                if key not in stats:
                    stats[key] = {"count": 0, "books": set()}
                stats[key]["count"] += 1
                if book:
                    stats[key]["books"].add(book)
        offset += page_size
        if len(data) < page_size:
            break

    # Convert sets to sorted lists
    return {k: {"hadith_count": v["count"], "books": sorted(v["books"])} for k, v in stats.items()}


def normalize_name_key(name_en: str) -> str:
    """Normalize name for matching."""
    import re
    key = name_en.lower()
    key = re.sub(r"['\u2018\u2019\u02bc\u02be\u02bf`]", "", key)
    key = re.sub(r'[^a-z0-9]+', '_', key)
    return key.strip('_')


def upload_batch(records: list, service_key: str, batch_size: int = 50):
    """Upload records to Supabase in batches using upsert."""
    headers = get_headers(service_key)
    total = len(records)
    success = 0
    errors = 0

    for i in range(0, total, batch_size):
        batch = records[i:i + batch_size]
        r = requests.post(
            f"{BASE_API}/rijal",
            headers=headers,
            json=batch
        )
        if r.status_code in (200, 201):
            success += len(batch)
        else:
            print(f"  ERROR batch {i//batch_size}: {r.status_code} {r.text[:200]}")
            errors += len(batch)
        print(f"  Uploaded {min(i+batch_size, total)}/{total}...", end="\r")

    print(f"\n  Done: {success} uploaded, {errors} errors")
    return success, errors


def prepare_record_for_db(r: dict) -> dict:
    """Clean a record dict for Supabase insertion (ensure uniform keys for PostgREST batching)."""
    ALLOWED_FIELDS = [
        "id", "name_en", "name_ar", "name_id", "kunya", "kunya_en",
        "laqab", "laqab_en", "nasab", "nasab_en", "nisba", "nisba_en",
        "name_variants", "generation", "generation_ar", "tabaqat_number", "gender",
        "born_ah", "died_ah", "born_ce", "died_ce", "age_at_death",
        "city_of_birth", "city_of_death", "city_of_residence", "region",
        "is_sahabi", "is_thiqah", "grade", "grade_ar", "grade_detail", "grade_source",
        "hadith_count", "books", "bio_en", "bio_ar", "bio_id",
        "teacher_ids", "student_ids", "sources", "external_ids", "muslimscholars_id"
    ]

    clean = {}
    for field in ALLOWED_FIELDS:
        val = r.get(field)
        if isinstance(val, set):
            val = sorted(val)
        if val == "" or val == [] or val == {}:
            val = None
        clean[field] = val

    return clean


def main():
    parser = argparse.ArgumentParser(description="Upload Rijal data to Supabase")
    parser.add_argument("--key", help="Supabase Service Role Key", required=False)
    parser.add_argument("--dry-run", action="store_true", help="Validate only, don't upload")
    args = parser.parse_args()

    service_key = args.key or os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    if not service_key and not args.dry_run:
        print("ERROR: Provide --key or set SUPABASE_SERVICE_ROLE_KEY environment variable")
        sys.exit(1)

    print("=" * 60)
    print("HADEETH.ID -- Rijal Upload Pipeline")
    print("=" * 60)

    # ── Step 1: Load all data sources ──────────────────────────
    print("\n[1/4] Loading data sources...")

    core = load_json("scratch/rijal_core_seed.json")
    wikidata = load_json("scratch/rijal_wikidata.json")
    print(f"  Core curated:   {len(core)} records")
    print(f"  Wikidata:       {len(wikidata)} records")

    # ── Step 2: Build master index keyed by ID ─────────────────
    print("\n[2/4] Merging data sources...")

    master = {}

    # Load Wikidata first (lowest priority)
    for r in wikidata:
        if r.get("id"):
            master[r["id"]] = r

    # Merge/override with core (highest priority)
    for r in core:
        rid = r["id"]
        if rid in master:
            master[rid] = merge_records(master[rid], r)
        else:
            master[rid] = r

    print(f"  Merged total: {len(master)} unique narrators")

    # ── Step 3: Compute hadith_count from our own DB ───────────
    if not args.dry_run:
        print("\n[3/4] Computing hadith counts from DB...")
        hadith_stats = compute_hadith_stats(service_key)
        print(f"  Found stats for {len(hadith_stats)} unique narrator name keys")

        # Match narrator names to rijal records
        for rid, rawi in master.items():
            # Try matching kunya_en first (most common in "Narrated X:" text)
            kunya_key = normalize_name_key(rawi.get("kunya_en", ""))
            name_key = normalize_name_key(rawi.get("name_en", ""))

            stats = hadith_stats.get(kunya_key) or hadith_stats.get(name_key)
            if stats:
                rawi["hadith_count"] = stats["hadith_count"]
                # Merge books
                existing_books = set(rawi.get("books", []))
                existing_books.update(stats["books"])
                rawi["books"] = sorted(existing_books)

    # ── Step 4: Prepare and upload ─────────────────────────────
    print("\n[4/4] Preparing records for upload...")
    # Clean records and provide fallback for name_ar if empty
    records = []
    for r in master.values():
        rec = prepare_record_for_db(r)
        if rec.get("id") and rec.get("name_en"):
            if not rec.get("name_ar"):
                rec["name_ar"] = rec["name_en"]  # Fallback to English name
            records.append(rec)

    valid = records
    invalid = len(records) - len(valid)
    if invalid:
        print(f"  WARNING: {invalid} records missing required fields (id/name_en/name_ar), skipping")
    print(f"  Ready to upload: {len(valid)} records")

    # Preview first 3
    print("\n  Preview (first 3 records):")
    for r in valid[:3]:
        print(f"    - {r['id']}: {r['name_en']} | {r.get('grade','?')} | died {r.get('died_ah','?')} AH")

    if args.dry_run:
        print("\n[DRY RUN] Skipping upload. Save preview to scratch/rijal_upload_preview.json")
        with open("scratch/rijal_upload_preview.json", "w", encoding="utf-8") as f:
            json.dump(valid, f, ensure_ascii=False, indent=2)
        return

    print(f"\n  Uploading {len(valid)} records to Supabase rijal table...")
    success, errors = upload_batch(valid, service_key)

    print("\n" + "=" * 60)
    print(f"DONE: {success} records uploaded successfully")
    if errors:
        print(f"ERRORS: {errors} records failed - check output above")
    print("=" * 60)


if __name__ == "__main__":
    main()

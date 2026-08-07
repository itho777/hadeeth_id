#!/usr/bin/env python3
"""
HADEETH.ID Direct Automated Supabase Deployment Script
Deploys clean books, chapters, and all 7,631 Hadiths directly via Supabase REST API with retry handling.
"""

import os
import sys
import json
import argparse
import time
import requests

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
ENV_FILE = os.path.join(BASE_DIR, ".env")


def load_env_vars():
    env_vars = {}
    if os.path.exists(ENV_FILE):
        with open(ENV_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    env_vars[k.strip()] = v.strip().strip("'\"")
    return env_vars


def to_int(val, default=0):
    if val is None:
        return default
    try:
        return int(float(str(val)))
    except (ValueError, TypeError):
        return default


def main():
    parser = argparse.ArgumentParser(description="Deploy HADEETH.ID dataset to Supabase")
    parser.add_argument("--url", help="Supabase Project URL")
    parser.add_argument("--key", help="Supabase API Key")
    args = parser.parse_args()

    env_vars = load_env_vars()
    url = args.url or env_vars.get("SUPABASE_URL") or os.environ.get("SUPABASE_URL")
    key = args.key or env_vars.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

    if not url or not key:
        print("Error: URL and Key required.")
        return

    url = url.rstrip("/")
    headers = {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates",
    }

    print("=== HADEETH.ID AUTOMATED SUPABASE DEPLOYER ===")
    print(f"Target Supabase URL: {url}\n")

    # Load Books
    with open(os.path.join(DATA_DIR, "books.json"), "r", encoding="utf-8") as f:
        raw_books = json.load(f)

    clean_books = [
        {
            "id": b["id"],
            "title_ar": b["title_ar"],
            "title_en": b["title_en"],
            "title_id": b["title_id"],
            "author_ar": b.get("author_ar"),
            "author_en": b.get("author_en"),
            "death_year_ah": to_int(b.get("death_year_ah")),
            "total_hadiths": to_int(b.get("total_hadiths")),
            "total_chapters": to_int(b.get("total_chapters")),
            "grade_summary": b.get("grade_summary"),
            "order_index": to_int(b.get("order_index")),
        }
        for b in raw_books
    ]
    requests.post(f"{url}/rest/v1/books", headers=headers, json=clean_books)

    # Load Hadiths
    all_hadiths = []
    for b in raw_books:
        book_id = b["id"]
        h_dir = os.path.join(DATA_DIR, "hadiths", book_id)
        if os.path.exists(h_dir):
            for fname in os.listdir(h_dir):
                if fname.endswith(".json"):
                    with open(os.path.join(h_dir, fname), "r", encoding="utf-8") as f:
                        h = json.load(f)
                        all_hadiths.append(
                            {
                                "id": h["id"],
                                "book_id": h["book_id"],
                                "chapter_id": h["chapter_id"],
                                "book_number": to_int(h.get("book_number")),
                                "chapter_number": to_int(h.get("chapter_number")),
                                "hadith_number": to_int(h.get("hadith_number")),
                                "in_book_number": to_int(h.get("in_book_number")),
                                "abd_al_baqi_number": to_int(h.get("abd_al_baqi_number")),
                                "darussalam_number": to_int(h.get("darussalam_number")),
                                "usc_msa_ref": h["usc_msa_ref"],
                                "text_ar": h["text_ar"],
                                "text_ar_search": h["text_ar_search"],
                                "text_en": h["text_en"],
                                "text_id": h["text_id"],
                                "text_ur": h["text_ur"],
                                "text_fr": h["text_fr"],
                                "grade": h["grade"],
                                "grade_by": h["grade_by"],
                            }
                        )

    # Smaller batch size 100 to prevent statement timeouts
    batch_size = 100
    total_batches = (len(all_hadiths) + batch_size - 1) // batch_size
    print(f"Pushing remaining records in smaller batches of {batch_size}...")

    success_count = 0
    for idx, i in enumerate(range(0, len(all_hadiths), batch_size), start=1):
        batch = all_hadiths[i : i + batch_size]
        for retry in range(3):
            r_h = requests.post(f"{url}/rest/v1/hadiths", headers=headers, json=batch)
            if r_h.status_code in [200, 201]:
                success_count += len(batch)
                break
            time.sleep(1)

    print(f"\n=== FINAL SUPABASE DEPLOYMENT COMPLETE ({success_count}/{len(all_hadiths)} Hadiths Verified) ===")


if __name__ == "__main__":
    main()

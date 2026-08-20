"""
fix_fawaz_lidwa_links.py
=========================
Rebuilds the Fawazahmed0 -> Lidwa Arabic-text link for all 9 Core books using
TF-IDF cosine similarity (the same technique already proven for
AhmedBaset<->Lidwa in relinker.py / relinker2.py).

WHY THIS SCRIPT EXISTS
-----------------------
1. The live per-book link files (data/links/{book}.ndjson), which
   rebuild_master_link.py and sanad_engine_v3.py actually read, currently
   hold "fawaz_to_lidwa" mappings produced by 3_cross_linker.py using an
   EXACT 40-char prefix/suffix hash match. Any hadith whose Arabic text
   differs even slightly between the two datasets (after normalization)
   fails to match and is silently dropped -> null lidwa_id -> that hadith
   can never get a sanad/narrator link either, since sanad_engine_v3.py
   only processes hadiths that already have a resolved lidwa_id.

2. A better matcher (fawaz_relinker.py) already exists and uses TF-IDF
   cosine similarity, which tolerates minor textual variation. But it:
     a) only covered 7 of the 9 Core books (missing darimi, ahmad)
     b) wrote its results to a SEPARATE file (data/links/fawaz_{book}.ndjson)
        that nothing downstream ever reads -- an orphaned output.
     c) did not persist match scores, so there was no way to distinguish
        confident matches from weak ones.

This script fixes all three: covers all 9 Core books, merges results
directly into the correct key inside the existing data/links/{book}.ndjson
files (preserving any other keys already there, e.g. fawaz_to_ab,
fawaz_to_rawis), and only keeps matches with cosine similarity > 0.5,
leaving weaker candidates as null rather than guessing.

USAGE
-----
    pip install scikit-learn --break-system-packages   # if not already installed
    python scripts/fix_fawaz_lidwa_links.py

Run this BEFORE scripts/rebuild_master_link.py, so master_link.ndjson picks
up the improved links. Then re-run sanad_engine_v3.py to re-attempt sanad
matching against the newly-resolved lidwa_ids.

A summary report (before/after coverage per book) is printed at the end
and also written to data/links/_fawaz_lidwa_relink_report.json.
"""

import json
import os
import re
import sys
import urllib.request

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIDWA_DIR = os.path.join(BASE_DIR, "data", "sources", "lidwa")
EDITIONS_DIR = os.path.join(BASE_DIR, "data", "editions")
LINKS_DIR = os.path.join(BASE_DIR, "data", "links")

# All 9 Core books -- darimi and ahmad were previously missing here.
CORE_9 = [
    "bukhari", "muslim", "abudawud", "tirmidhi",
    "nasai", "ibnmajah", "malik", "darimi", "ahmad",
]

# Only merge matches at or above this cosine-similarity score.
# Weaker candidates are left null rather than guessed, per project decision
# to prioritize precision over coverage on this pass.
CONFIDENCE_THRESHOLD = 0.5

CDN_URL_TEMPLATE = "https://cdn.jsdelivr.net/gh/fawazahmed0/hadith-api@1/editions/ara-{book}.json"


def normalize_arabic(text):
    if not text:
        return ""
    text = re.sub(r'[\u0617-\u061A\u064B-\u0652]', '', text)   # strip tashkeel
    text = re.sub(r'\u0640', '', text)                          # strip tatweel
    text = re.sub(r'[\u0625\u0623\u0622\u0627]', '\u0627', text)  # normalize alef
    text = re.sub(r'[\u064A\u0649]', '\u064A', text)             # normalize yaa
    text = re.sub(r'[\u0629\u0647]', '\u0647', text)             # normalize taa marbuta
    text = re.sub(r'\u0624', '\u0648', text)                     # normalize hamza-waw
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def load_lidwa(book_id):
    path = os.path.join(LIDWA_DIR, f"{book_id}.ndjson")
    if not os.path.exists(path):
        print(f"  [!] Lidwa source not found for {book_id}: {path}")
        return None
    with open(path, 'r', encoding='utf-8') as f:
        data = [json.loads(line) for line in f]
    
    return data


def load_fawaz(book_id):
    """Prefer local data/editions/ara-{book}.json; fall back to CDN download."""
    local_path = os.path.join(EDITIONS_DIR, f"ara-{book_id}.json")
    if os.path.exists(local_path):
        with open(local_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        source = f"local:{local_path}"
    else:
        url = CDN_URL_TEMPLATE.format(book=book_id)
        print(f"  [*] Local edition not found, downloading {url}")
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=30) as response:
                data = json.loads(response.read().decode('utf-8'))
            source = url
        except Exception as e:
            print(f"  [!] Download failed for {book_id}: {e}")
            return None, None

    hadiths = data.get('hadiths', []) if isinstance(data, dict) else data
    return hadiths, source


def relink_book(book_id):
    print(f"\n--- {book_id} ---", flush=True)

    lidwa_data = load_lidwa(book_id)
    if not lidwa_data:
        return None

    lidwa_docs, lidwa_map = [], []
    for h in lidwa_data:
        hnum = h.get('hadith_number')
        if not hnum:
            continue
        norm_ar = normalize_arabic(h.get('text_ar', ''))
        if not norm_ar:
            continue
        lidwa_docs.append(norm_ar)
        lidwa_map.append(str(hnum))

    if not lidwa_docs:
        print("  [!] No usable Lidwa documents, skipping.")
        return None

    fawaz_hadiths, source = load_fawaz(book_id)
    if not fawaz_hadiths:
        print("  [!] No Fawazahmed0 data available, skipping.")
        return None
    print(f"  Source: {source}")

    fawaz_docs, fawaz_map = [], []
    for h in fawaz_hadiths:
        hnum = h.get('hadithnumber', h.get('id'))
        if not hnum:
            continue
        norm_ar = normalize_arabic(h.get('text', ''))
        if not norm_ar:
            continue
        fawaz_docs.append(norm_ar)
        fawaz_map.append(str(hnum))

    if not fawaz_docs:
        print("  [!] No usable Fawazahmed0 documents, skipping.")
        return None

    vectorizer = TfidfVectorizer(analyzer='word', ngram_range=(1, 3), min_df=1)
    lidwa_matrix = vectorizer.fit_transform(lidwa_docs)
    fawaz_matrix = vectorizer.transform(fawaz_docs)
    sims = cosine_similarity(fawaz_matrix, lidwa_matrix)

    fawaz_to_lidwa = {}
    below_threshold = 0
    for i, fawaz_id in enumerate(fawaz_map):
        best_idx = sims[i].argmax()
        score = float(sims[i][best_idx])
        if score >= CONFIDENCE_THRESHOLD:
            fawaz_to_lidwa[fawaz_id] = lidwa_map[best_idx]
        else:
            below_threshold += 1

    total = len(fawaz_map)
    matched = len(fawaz_to_lidwa)
    print(f"  Matched {matched}/{total} ({matched/total:.0%}) at score >= {CONFIDENCE_THRESHOLD}; "
          f"{below_threshold} left unmatched below threshold.")

    # --- Merge into the existing per-book link file, preserving other keys ---
    link_path = os.path.join(LINKS_DIR, f"{book_id}.json")
    existing = {}
    old_count = 0
    if os.path.exists(link_path):
        with open(link_path, 'r', encoding='utf-8') as f:
            existing = json.load(f)
        old_count = len(existing.get('fawaz_to_lidwa', {}))

    existing['fawaz_to_lidwa'] = fawaz_to_lidwa
    with open(link_path, 'w', encoding='utf-8') as f:
        json.dump(existing, f, ensure_ascii=False, indent=2)

    print(f"  Wrote {matched} links to {link_path} (previously {old_count}).")

    return {
        "book": book_id,
        "total_fawaz_hadiths": total,
        "matched_above_threshold": matched,
        "below_threshold": below_threshold,
        "coverage_pct": round(matched / total * 100, 1) if total else 0,
        "previous_link_count": old_count,
    }


def main():
    os.makedirs(LINKS_DIR, exist_ok=True)
    print("[*] Rebuilding Fawaz -> Lidwa links (TF-IDF cosine, threshold "
          f"{CONFIDENCE_THRESHOLD}) for all 9 Core books...")

    report = []
    for book_id in CORE_9:
        result = relink_book(book_id)
        if result:
            report.append(result)

    report_path = os.path.join(LINKS_DIR, "_fawaz_lidwa_relink_report.json")
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for r in report:
        print(f"  {r['book']:12s}  {r['matched_above_threshold']:>5}/{r['total_fawaz_hadiths']:<5} "
              f"({r['coverage_pct']}%)   was: {r['previous_link_count']}")
    print(f"\nFull report written to {report_path}")
    print("\nNext steps:")
    print("  1. Review the report -- any book with unexpectedly low coverage")
    print("     may need its normalize_arabic() rules adjusted.")
    print("  2. Run scripts/rebuild_master_link.py to regenerate master_link.ndjson")
    print("     from these updated per-book link files.")
    print("  3. Re-run scripts/sanad_engine_v3.py so sanad matching can attempt")
    print("     the newly-resolved lidwa_ids.")


if __name__ == "__main__":
    main()

"""
link_lidwa_to_ahmedbaset_9books.py
=============================
Rebuilds the AhmedBaset -> Lidwa Arabic-text link for all 9 Core books using
TF-IDF cosine similarity.

This completely replaces Fawazahmed0 as the anchor for the 9 books.

USAGE
-----
    pip install scikit-learn --break-system-packages
    python scripts/link_lidwa_to_ahmedbaset_9books.py
"""

import json
import os
import re
import sys

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIDWA_DIR = os.path.join(BASE_DIR, "data", "sources", "lidwa")
AHMEDBASET_DIR = os.path.join(BASE_DIR, "data", "sources", "ahmedbaset", "by_book", "the_9_books")
LINKS_DIR = os.path.join(BASE_DIR, "data", "links")
OUT_DIR = os.path.join(LINKS_DIR, "relinked_ab")

os.makedirs(OUT_DIR, exist_ok=True)

CORE_9 = [
    "bukhari", "muslim", "abudawud", "tirmidhi",
    "nasai", "ibnmajah", "malik"
]

CONFIDENCE_THRESHOLD = 0.5


def normalize_arabic(text):
    if not text:
        return ""
    text = re.sub(r'[\u0617-\u061A\u064B-\u0652]', '', text)
    text = re.sub(r'\u0640', '', text)
    text = re.sub(r'[\u0625\u0623\u0622\u0627]', '\u0627', text)
    text = re.sub(r'[\u064A\u0649]', '\u064A', text)
    text = re.sub(r'[\u0629\u0647]', '\u0647', text)
    text = re.sub(r'\u0624', '\u0648', text)
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def load_lidwa(book_id):
    path = os.path.join(LIDWA_DIR, f"{book_id}.json")
    if not os.path.exists(path):
        print(f"  [!] Lidwa source not found for {book_id}: {path}")
        return None
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    if isinstance(data, dict) and 'hadiths' in data:
        data = data['hadiths']
    return data


def load_ahmedbaset(book_id):
    local_path = os.path.join(AHMEDBASET_DIR, f"{book_id}.json")
    if os.path.exists(local_path):
        with open(local_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        print(f"  [!] Ahmedbaset file not found: {local_path}")
        return None
    hadiths = data.get('hadiths', []) if isinstance(data, dict) else data
    return hadiths


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

    ab_hadiths = load_ahmedbaset(book_id)
    if not ab_hadiths:
        print("  [!] No AhmedBaset data available, skipping.")
        return None

    ab_docs, ab_map = [], []
    for h in ab_hadiths:
        hnum = str(h.get('idInBook', h.get('id')))
        if not hnum:
            continue
        norm_ar = normalize_arabic(h.get('arabic', ''))
        if not norm_ar:
            continue
        ab_docs.append(norm_ar)
        ab_map.append(str(hnum))

    if not ab_docs:
        print("  [!] No usable AhmedBaset documents, skipping.")
        return None

    vectorizer = TfidfVectorizer(analyzer='word', ngram_range=(1, 3), min_df=1)
    lidwa_matrix = vectorizer.fit_transform(lidwa_docs)
    ab_matrix = vectorizer.transform(ab_docs)
    sims = cosine_similarity(ab_matrix, lidwa_matrix)

    ab_to_lidwa = {}
    below_threshold = 0
    for i, ab_id in enumerate(ab_map):
        best_idx = sims[i].argmax()
        score = float(sims[i][best_idx])
        if score >= CONFIDENCE_THRESHOLD:
            ab_to_lidwa[ab_id] = {
                "lidwa_id": lidwa_map[best_idx]
            }
        else:
            below_threshold += 1

    total = len(ab_map)
    matched = len(ab_to_lidwa)
    print(f"  Matched {matched}/{total} ({matched/total:.0%}) at score >= {CONFIDENCE_THRESHOLD}; "
          f"{below_threshold} left unmatched below threshold.")

    out_path = os.path.join(OUT_DIR, f"{book_id}.json")
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(ab_to_lidwa, f, ensure_ascii=False, indent=2)

    return {
        "book": book_id,
        "total_ahmedbaset": total,
        "matched": matched,
        "unmatched": below_threshold,
        "match_rate": matched / total if total else 0
    }


def main():
    report = {}
    for book in CORE_9:
        stats = relink_book(book)
        if stats:
            report[book] = stats

    report_path = os.path.join(OUT_DIR, "_report_ab_to_lidwa.json")
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)

    print(f"\nSaved report to {report_path}")

if __name__ == "__main__":
    main()

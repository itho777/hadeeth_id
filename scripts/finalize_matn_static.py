#!/usr/bin/env python3
"""Finalize the four new matn books for the static site and the R2 archive.

Reads the NDJSON emitted by `build_matn_from_syarah.py` (muntaqa) and
`emit_matn_units.py` (umdat, masabih, maani) and:

  1. appends catalog + books_v2 entries for books that are not there yet
  2. verifies every syarah link number resolves against the emitted matn keys
  3. writes a gzip copy of each plain file under export/matn/ with sha256

Idempotent: re-running updates the entry rather than appending a duplicate.
"""
import gzip
import hashlib
import json
import os
import sqlite3

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
API = os.path.join(ROOT, "export_site", "api")
ARCHIVE = os.path.join(ROOT, "export", "matn")
SRC = "H:/Itho/2026/Project/Hadeeth/data source/Syarah From Muse"

BOOKS = {
    "muntaqa": {
        "package": "muntaqa", "count": 3944, "order": 21,
        "title_ar": "منتقى الأخبار", "title_en": "Muntaqa al-Akhbar",
        "title_id": "Muntaqa al-Akhbar",
        "author_en": "Imam Majd al-Din Ibn Taymiyya",
        "author_id": "Imam Majd al-Din Ibn Taymiyya",
        "author_ar": "الإمام مجد الدين ابن تيمية",
        "desc": "Kumpulan hadits pilihan dari Musnad Ahmad, disusun oleh Ibnu Taimiyah.",
    },
    "maani": {
        "package": "maani", "count": 7013, "order": 22,
        "title_ar": "معاني الآثار", "title_en": "Ma'ani al-Athar",
        "title_id": "Ma'ani al-Athar",
        "author_en": "Imam Abu Ja'far al-Tahawi",
        "author_id": "Imam Abu Ja'far al-Tahawi",
        "author_ar": "الإمام الطحاوي",
        "desc": "Kitab hadits Imam ath-Thahawi, edisi tahqiq al-Bahraiji.",
    },
    "masabih": {
        "package": "masabih", "count": 4929, "order": 23,
        "title_ar": "مصابيح السنة", "title_en": "Masabih al-Sunna",
        "title_id": "Masabih al-Sunna",
        "author_en": "Imam Abu Muhammad al-Baghawi",
        "author_id": "Imam Abu Muhammad al-Baghawi",
        "author_ar": "الإمام البغوي",
        "desc": "Kumpulan hadits pilihan karya Imam al-Baghawi, edisi al-Mar'ashli.",
    },
    "umdat": {
        "package": "umdat", "count": 414, "order": 24,
        "title_ar": "عمدة الأحكام", "title_en": "Umdat al-Ahkam",
        "title_id": "Umdat al-Ahkam",
        "author_en": "Imam Ibn Daqiq al-'Id",
        "author_id": "Imam Ibn Daqiq al-Id",
        "author_ar": "الإمام ابن دقيق العيد",
        "desc": "Ringkasan hadits hukum karya Imam Ibn Daqiq al-'Id, edisi al-Qasim.",
    },
}


def index_keys(book):
    for folder in (API, os.path.join(ROOT, "data", "api")):
        p = os.path.join(folder, f"{book}_index.ndjson")
        if os.path.exists(p):
            return {int(json.loads(l)["n"]) for l in open(p, encoding="utf-8") if l.strip()}
    # A clean rebuild has no generated index yet. Read the numbers from the
    # canonical data file instead so the registry is never published with zeros.
    for folder in (os.path.join(ROOT, "data", "api"), API):
        p = os.path.join(folder, f"{book}.ndjson")
        if os.path.exists(p):
            return {int(json.loads(l)["hadith_number"])
                    for l in open(p, encoding="utf-8") if l.strip()}
    return set()


def verify_links(book, keys):
    pkg = BOOKS[book]["package"]
    db = os.path.join(SRC, pkg, f"syarah_{pkg}.db")
    if not os.path.exists(db) or not keys:
        return None
    con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    nums = {r[0] for r in con.execute(
        "SELECT DISTINCT source_native_number FROM syarah_links")
        if r[0] is not None}
    con.close()
    return (len(nums), sum(1 for n in nums if n in keys))


def chapter_count(book):
    for folder in (os.path.join(ROOT, "data", "api"), API):
        p = os.path.join(folder, f"{book}.ndjson")
        if not os.path.exists(p):
            continue
        ids = set()
        for line in open(p, encoding="utf-8"):
            if not line.strip():
                continue
            cid = json.loads(line).get("chapter_id")
            if cid not in (None, ""):
                ids.add(cid)
        return len(ids)
    return 0


def update_catalog():
    p = os.path.join(ROOT, "export_site", "catalog.ndjson")
    rows = [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]
    have = {r["id"] for r in rows}
    for book, m in BOOKS.items():
        keys = index_keys(book)
        if not keys:
            print(f"  catalog: SKIP {book} (no index yet)")
            continue
        row = {
            "id": book, "title_ar": m["title_ar"], "title_en": m["title_en"],
            "title_id": m["title_id"], "author_en": m["author_en"],
            "author_id": m["author_id"], "total_hadiths": len(keys),
            "hadiths_count": len(keys), "total_chapters": chapter_count(book),
            "grade_summary": "", "order_index": m["order"],
        }
        if book in have:
            rows = [row if r["id"] == book else r for r in rows]
        else:
            rows.append(row)
            have.add(book)
    with open(p, "w", encoding="utf-8", newline="\n") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n")
    print(f"  catalog: {len(rows)} books")


def update_books_v2():
    p = os.path.join(ROOT, "data", "books_v2.json")
    rows = json.load(open(p, encoding="utf-8"))
    have = {r["id"] for r in rows}
    for book, m in BOOKS.items():
        keys = index_keys(book)
        if not keys:
            continue
        row = {
            "id": book, "name": m["title_en"], "nameId": m["title_en"],
            "count": len(keys), "description": m["desc"],
            "descriptionId": m["desc"], "icon": "menu_book",
            "total_hadiths": len(keys), "title_en": m["title_en"],
            "title_id": m["title_id"], "title_ar": m["title_ar"],
            "author_en": m["author_en"], "author_id": m["author_id"],
            "author_ar": m["author_ar"], "grade_summary": "",
            "order_index": m["order"], "source": "matn_rebuild",
            "authorId": "", "editions": [], "book_type_ar": "",
            "hadiths_count": len(keys),
            "total_chapters": chapter_count(book),
        }
        if book in have:
            rows = [row if r["id"] == book else r for r in rows]
        else:
            rows.append(row)
            have.add(book)
    with open(p, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(rows, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    print(f"  books_v2: {len(rows)} books")


def archive():
    os.makedirs(ARCHIVE, exist_ok=True)
    manifest = {}
    for book in BOOKS:
        plain = os.path.join(API, f"{book}.ndjson")
        if not os.path.exists(plain):
            continue
        raw = open(plain, "rb").read()
        gz = os.path.join(ARCHIVE, f"{book}.ndjson.gz")
        with gzip.open(gz, "wb", compresslevel=9) as fh:
            fh.write(raw)
        manifest[book] = {
            "plain_bytes": len(raw),
            "gz_bytes": os.path.getsize(gz),
            "sha256_plain": hashlib.sha256(raw).hexdigest(),
        }
        print(f"  archive {book}: {len(raw)/2**20:.2f} -> {os.path.getsize(gz)/2**20:.2f} MiB")
    with open(os.path.join(ARCHIVE, "MANIFEST.json"), "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, ensure_ascii=False, indent=2)


def main():
    print("link resolution:")
    for book in BOOKS:
        keys = index_keys(book)
        v = verify_links(book, keys)
        if v is None:
            print(f"  {book}: NOT BUILT")
        else:
            print(f"  {book}: {v[1]}/{v[0]} syarah numbers resolve, "
                  f"{v[0]-v[1]} dangling, {len(keys)} matn rows")
    print("catalog updates:")
    update_catalog()
    update_books_v2()
    print("archive:")
    archive()


if __name__ == "__main__":
    main()

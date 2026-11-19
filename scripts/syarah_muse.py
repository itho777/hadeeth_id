#!/usr/bin/env python
"""Import the "Syarah From Muse" corpus into the commentary tree.

Each source directory holds one classical sharh as a SQLite DB with three
relevant tables: `syarah_links` (hadith number -> page), `syarah_passages`
(one row per turath page, verbatim text) and `syarah_sources` (the edition's
name, author and licence).

The links carry `source_native_number` in the numbering of whatever hadith
side they were built against. Two cases, both handled without guessing:

  source_dataset = 'fawaz'       the number is a fawaz edition number, which
                                 equals our canonical number for most books
  source_dataset = 'hadeeth_id'  already our own canonical number

A link whose number is absent from that book's canonical index has no row to
attach to and is dropped, not coerced. Editions of matns we do not carry
(maani, muntaqa, masabih, umdat) have no page on the site and are skipped.

Rows are shaped for the existing syarah engine in js/app.js: it renders one
tab per row, labelled by `source_name_en`, and reads `explanation_ar` /
`syarah_ar`. Everything else on the row is provenance.
"""
import json
import os
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = Path(os.environ.get("SYARAH_MUSE_DIR",
                          r"H:/Itho/2026/Project/Hadeeth/data source/Syarah From Muse"))
OUT = ROOT / "export_site"
MAX_PAGES = 1  # inline text is the page the commentary starts on

# Tab-sized names. The full title still ships in `source_title_full`; the UI
# renders `source_name_en` on a button, where the 58-character catalogue title
# does not fit.
SHORT = {
    "bukhari": "Fath al-Bari",
    "bukhari_battal": "Ibn Battal",
    "bukhari_khattabi": "al-Khattabi",
    "muslim": "Sharh al-Nawawi",
    "abudawud": "Awn al-Ma'bud",
    "tirmidhi": "Tuhfat al-Ahwadhi",
    "tirmidhi_sindi": "Hashiyat al-Sindi",
    "nasai": "Hashiyat al-Sindi",
    "nasai_suyuti": "al-Suyuti",
    "ibnmajah": "Hashiyat al-Sindi",
    "ibnmajah_mughultay": "Mughultay",
    "malik": "al-Zurqani",
    "malik_tamhid": "al-Tamhid",
    "mishkat": "Mirqat al-Mafatih",
    "mishkat_tibi": "al-Kashif",
    "bulugh": "Subul al-Salam",
    "riyad": "Dalil al-Falihin",
    "shamail": "Jam' al-Wasa'il",
    "syafii": "al-Shafi",
    "nawawi": "Jami' al-Ulum",
}


def canonical_numbers():
    """hadith number -> set, from the shipped per-book indexes."""
    out = {}
    for path in sorted((OUT / "api").glob("*_index.ndjson")):
        book = path.name[:-len("_index.ndjson")]
        nums = set()
        with path.open(encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                row = json.loads(line)
                if "n" in row:
                    nums.add(str(row["n"]))
        if nums:
            out[book] = nums
    return out


def edition_names(con):
    """(name_ar, name_en) for the sharh itself, ignoring reference/method rows."""
    try:
        rows = list(con.execute(
            "select kind, name, name_ar, url, edition, licence from syarah_sources"))
    except sqlite3.Error:
        return ("Syarah", "Syarah", None, None)
    for kind, name, name_ar, url, edition, licence in rows:
        if kind == "syarah_book":
            return (name_ar or name, name, url, licence)
    return ("Syarah", "Syarah", None, None)


def page_texts(con):
    try:
        return {r[0]: r[1] for r in con.execute(
            "select page_index, text_ar from syarah_passages")}, \
               {r[0]: (r[1], r[2]) for r in con.execute(
            "select page_index, vol, page_printed from syarah_passages")}
    except sqlite3.Error:
        return {}, {}


def import_dir(path, canon):
    """-> ({(book, number): [row, ...]}, stats dict)"""
    dbs = sorted(path.glob("syarah_*.db"))
    if not dbs:
        return {}, {"dir": path.name, "skip": "no db"}
    con = sqlite3.connect(f"file:{dbs[0]}?mode=ro", uri=True)
    tables = {r[0] for r in con.execute(
        "select name from sqlite_master where type='table'")}
    link_table = next((t for t in ("syarah_links", "links") if t in tables), None)
    if not link_table:
        con.close()
        return {}, {"dir": path.name, "skip": "no links table"}

    books = sorted({r[0] for r in con.execute(
        f"select distinct source_book_id from {link_table}")})
    if len(books) != 1 or books[0] not in canon:
        con.close()
        return {}, {"dir": path.name, "skip": f"no site page for {books}"}

    book = books[0]
    name_ar, name_en, url, licence = edition_names(con)
    texts, meta = page_texts(con)
    cols = [c[1] for c in con.execute(f"pragma table_info({link_table})")]
    has_span = "commentary_start_page_index" in cols

    slug = path.name
    rows = {}
    links = dropped = 0
    seen = set()
    for link in con.execute(
            f"select source_native_number, target_page_index"
            + (", commentary_start_page_index, commentary_end_page_index" if has_span else "")
            + (", confidence, method" if "confidence" in cols else "")
            + f" from {link_table}"):
        native, target = link[0], link[1]
        start = end = None
        if has_span and len(link) > 3:
            start, end = link[2], link[3]
        confidence = link[-2] if "confidence" in cols else None
        method = link[-1] if "confidence" in cols else None
        links += 1
        number = str(native)
        if number not in canon[book]:
            dropped += 1
            continue
        page = start if start is not None else target
        if page is None:
            dropped += 1
            continue
        key = (slug, number, page)
        if key in seen:          # several chains can point at one page
            continue
        seen.add(key)
        body = texts.get(page) or ""
        if not body.strip():
            dropped += 1
            continue
        vol, printed = meta.get(page, (None, None))
        row = {
            "book_id": book,
            "anchor_id": str(native),
            "hadith_number": number,
            "source_key": slug,
            "source_name_ar": name_ar,
            "source_name_en": SHORT.get(slug, name_en),
            "source_name_id": SHORT.get(slug, name_en),
            "source_title_full": name_en,
            "explanation_ar": body,
            "syarah_ar": body,
            "langs": "['ar']",
            "origin": "muse",
            "syarah_edition": slug,
            "syarah_vol": vol,
            "syarah_page": printed,
            "syarah_pages_index": (f"{start}-{end}" if start is not None and end not in (None, start)
                                   else (str(start) if start is not None else None)),
            "syarah_url": url,
            "syarah_licence": licence,
            "link_confidence": confidence,
            "link_method": method,
        }
        rows.setdefault((book, number), []).append(row)
    con.close()
    stats = {"dir": path.name, "book": book, "links": links, "kept": links - dropped,
             "dropped": dropped, "hadiths": len(rows),
             "pages": len(texts), "edition": name_en}
    return rows, stats


def build(canon=None):
    if not SRC.is_dir():
        return {}, []
    canon = canon or canonical_numbers()
    merged = {}
    report = []
    for path in sorted(p for p in SRC.iterdir() if p.is_dir()):
        rows, stats = import_dir(path, canon)
        report.append(stats)
        for key, bucket in rows.items():
            merged.setdefault(key, []).extend(bucket)
    return merged, report


def main():
    merged, report = build()
    for s in report:
        if s.get("skip"):
            print(f"  skip {s['dir']:22} {s['skip']}")
            continue
        print(f"  {s['dir']:22} {s['book']:10} links={s['links']:6} kept={s['kept']:6} "
              f"hadiths={s['hadiths']:6} dropped={s['dropped']:6}  {s['edition'][:40]}")
    print(f"total: {sum(len(v) for v in merged.values())} rows on {len(merged)} hadiths")
    return 0


if __name__ == "__main__":
    sys.exit(main())

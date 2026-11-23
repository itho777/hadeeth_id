#!/usr/bin/env python3
"""Emit a matn book as static-site NDJSON from a `*_matn_units.json` build input.

The units files come from the extraction scripts in each Muse package
(`build_matn_umdat.py`, `build_matn_masabih.py`, `segment_matn_maani.py`).
They carry the numbering authority for the sharh that links into them, so the
output rows are keyed by that same number -- the syarah link's
`source_native_number` is the row's `hadith_number`, no crosswalk needed.

Output matches `export_site/api/<book>.ndjson` + `<book>_index.ndjson` exactly,
so `js/api.js` reads it with the same Range decode it uses for the 24 existing
books.

Usage:
    python scripts/emit_matn_units.py umdat
    python scripts/emit_matn_units.py masabih maani muntaqa
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = "H:/Itho/2026/Project/Hadeeth/data source/Syarah From Muse"
OUT_DIR = os.path.join(ROOT, "export_site", "api")

# book -> (units file, extra fields for the catalog)
BOOKS = {
    "umdat":   ("umdat/raw/umdat_matn_units.json",),
    "masabih": ("masabih/raw/masabih_matn_units.json",),
    "maani":   ("maani/data/maani_matn_units.json",),
}


def load_units(book):
    rel = BOOKS[book][0]
    path = os.path.join(SRC, rel)
    if not os.path.exists(path):
        raise SystemExit(f"missing units file: {path}")
    with open(path, encoding="utf-8") as fh:
        blob = json.load(fh)
    units = blob["units"] if isinstance(blob, dict) else blob
    rows = []
    for u in units:
        # masabih uses `slot`; umdat/maani use `native_number`/`n`.
        n = u.get("native_number", u.get("n", u.get("slot")))
        text = (u.get("text_ar") or u.get("text") or "").strip()
        if n is None or not text or u.get("sub_of") is not None:
            continue
        rows.append({
            "id": int(n),
            "book": book,
            "hadith_number": str(n),
            "lidwa_id": [],
            "chapter_id": u.get("chapter_id"),
            "text_ar": text,
            "text_source": f"Syarah From Muse/{rel.split('/')[0]}",
        })
    rows.sort(key=lambda r: r["id"])
    return rows, blob


def write(book, rows, blob):
    os.makedirs(OUT_DIR, exist_ok=True)
    plain = os.path.join(OUT_DIR, f"{book}.ndjson")
    index = os.path.join(OUT_DIR, f"{book}_index.ndjson")
    offset = 0
    with open(plain, "w", encoding="utf-8", newline="\n") as fh, \
         open(index, "w", encoding="utf-8", newline="\n") as ix:
        for i, r in enumerate(rows, 1):
            raw = (json.dumps(r, ensure_ascii=False) + "\n").encode("utf-8")
            fh.write(raw.decode("utf-8"))
            ix.write(json.dumps({"i": i, "id": r["id"], "n": r["hadith_number"],
                                 "s": offset, "e": offset + len(raw) - 1,
                                 "c": r["chapter_id"], "l": []},
                                ensure_ascii=False) + "\n")
            offset += len(raw)
    return plain, index, offset


def main():
    books = sys.argv[1:] or list(BOOKS)
    for book in books:
        rows, blob = load_units(book)
        nums = [r["id"] for r in rows]
        gaps = [n for n in range(1, max(nums) + 1) if n not in set(nums)]
        plain, index, size = write(book, rows, blob)
        print(f"{book}: {len(rows)} rows, keys {min(nums)}..{max(nums)}, "
              f"{len(gaps)} gaps {gaps[:6]}, {size / 2**20:.2f} MiB")
        print(f"  -> {plain}\n  -> {index}")


if __name__ == "__main__":
    main()

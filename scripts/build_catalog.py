#!/usr/bin/env python3
"""
build_catalog.py — Emit export/catalog.json, the one file the site fetches first.

index.json is the full manifest (every file, sha256, bytes) — useful for cache
validation, too heavy for a page load. catalog.json is the bootstrap: which books
exist, which editions each has, how many hadiths, and the base URL for the rest.

Reads:  export/index.json, export/book/<book>/index.json
Writes: export/catalog.json

Usage:
  python scripts/build_catalog.py
"""

import json
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent.parent
WORK = ROOT / "export"

BASE_URL = "https://cdn.hadeeth.id"  # was r2.dev; custom domain is the serving origin

# display order for the site; anything not listed sorts after, alphabetically
CANON = ["bukhari", "muslim", "abudawud", "tirmidhi", "nasai", "ibnmajah",
         "malik", "ahmad", "darimi", "nawawi", "qudsi", "riyad",
         "syafii", "mustadrak", "ibnuhibban", "ibnukhuzaimah",
         "daruquthni", "dehlawi"]

AR_TITLES = {
    "bukhari": "صحيح البخاري", "muslim": "صحيح مسلم",
    "abudawud": "سنن أبي داود", "tirmidhi": "جامع الترمذي",
    "nasai": "سنن النسائي", "ibnmajah": "سنن ابن ماجه",
    "malik": "موطأ مالك", "ahmad": "مسند أحمد", "darimi": "سنن الدارمي",
    "nawawi": "الأربعون النووية", "qudsi": "الأحاديث القدسية",
    "riyad": "رياض الصالحين", "syafii": "مسند الشافعي",
    "mustadrak": "المستدرك", "ibnuhibban": "صحيح ابن حبان",
    "ibnukhuzaimah": "صحيح ابن خزيمة", "daruquthni": "سنن الدارقطني",
    "dehlawi": "الأربعون الدهلوية",
}


def main():
    idx = json.loads((WORK / "index.json").read_text(encoding="utf-8"))
    files = idx["files"]
    bundles = idx.get("bundles", {})

    books = {}
    for rel, meta in files.items():
        parts = rel.split("/")
        if len(parts) != 2 or parts[0] in ("global", "book", "map"):
            continue
        fs_src, fname = parts[0], parts[1].replace(".ndjson.gz", "")
        book = fs_src.split("_", 1)[1]
        b = books.setdefault(book, {"book": book, "editions": {}, "rows": {}})
        ed = b["editions"].setdefault(fs_src, {"source_id": fs_src.replace("_", ":", 1),
                                               "tables": {}})
        ed["tables"][fname] = {"rows": meta["rows"], "bytes_gz": meta["bytes_gz"]}
        b["rows"][fname] = b["rows"].get(fname, 0) + meta["rows"]

    out_books = []
    for book in sorted(books, key=lambda b: (CANON.index(b) if b in CANON else 999, b)):
        b = books[book]
        bdir = WORK / "book" / book
        avail = []
        for t in ("hadiths", "sanad", "hadith_bab"):
            p = bdir / f"{t}.ndjson.gz"
            if p.exists():
                key = f"book/{book}/{t}.ndjson.gz"
                avail.append({"table": t, "path": key,
                              "rows": bundles.get(key, {}).get("rows", b["rows"].get(t, 0)),
                              "bytes_gz": p.stat().st_size})
        out_books.append({
            "book": book,
            "title_ar": AR_TITLES.get(book, book),
            "hadiths": b["rows"].get("hadiths", 0),
            "editions": [{"source_id": e["source_id"],
                          "rows": e["tables"].get("hadiths", {}).get("rows", 0)}
                         for e in b["editions"].values()],
            "tables": avail,
        })

    catalog = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "base_url": BASE_URL,
        "format": "ndjson.gz",
        "books": out_books,
        "global": sorted(p.split("/")[1].replace(".ndjson.gz", "")
                         for p in files if p.startswith("global/")),
        "totals": {
            "books": len(out_books),
            "editions": sum(len(b["editions"]) for b in out_books),
            "hadiths": sum(b["hadiths"] for b in out_books),
            "rows": idx["totals"]["rows"],
            "bytes_gz": idx["totals"]["bytes_gz"]
                        + sum(v["bytes_gz"] for v in bundles.values()),
        },
    }
    p = WORK / "catalog.json"
    p.write_text(json.dumps(catalog, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"catalog: {p}  ({p.stat().st_size:,} B)")
    print(f"books  : {len(out_books)}")
    print(f"hadiths: {catalog['totals']['hadiths']:,}")
    for b in out_books[:6]:
        tables = ",".join(t["table"] for t in b["tables"])
        print(f"  {b['book']:14s} {b['hadiths']:>7,}  editions={len(b['editions'])}  [{tables}]")


if __name__ == "__main__":
    main()

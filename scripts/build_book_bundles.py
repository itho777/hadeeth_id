#!/usr/bin/env python3
"""
build_book_bundles.py — Merge per-source NDJSON.gz into per-book bundles.

Pure local work: no D1 calls. The export keeps provenance in src/<source>/…;
the static site wants one file per book per table so a book view is a single
fetch instead of one per edition.

Reads:  export/index.json + export/<source>/*.ndjson.gz
Writes: export/book/<book>/<table>.ndjson.gz
        export/book/<book>/index.json      (editions, counts, tables)

A merged row keeps its original `source_id`, so the client can group by edition
without another lookup.

Usage:
  python scripts/build_book_bundles.py [--force]
"""

import sys, json, gzip, hashlib
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent.parent
WORK = ROOT / "export"
MANIFEST = WORK / "index.json"

PARTITIONED = ["hadiths", "sanad", "hadith_bab"]


def src_to_book(fs_src: str) -> str:
    return fs_src.split("_", 1)[1]


def gz_sha(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    force = "--force" in sys.argv
    if not MANIFEST.exists():
        sys.exit("export/index.json missing — run the export first")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    files = manifest.get("files", {})

    # group per-source files by book
    books = {}
    for rel in files:
        parts = rel.split("/")
        if len(parts) != 2 or parts[0] in ("global", "book", "map"):
            continue
        fs_src, fname = parts[0], parts[1]
        books.setdefault(src_to_book(fs_src), {}).setdefault(fname, []).append(fs_src)

    print(f"=== per-book bundles ===  books: {len(books)}")
    bundle_meta = {}
    for book, tables in sorted(books.items()):
        bdir = WORK / "book" / book
        bdir.mkdir(parents=True, exist_ok=True)
        editions = sorted({s for v in tables.values() for s in v})

        for fname, srcs in sorted(tables.items()):
            out = bdir / fname
            if out.exists() and not force:
                meta = manifest.get("bundles", {}).get(f"book/{book}/{fname}")
                if meta and meta.get("rows"):
                    print(f" = book/{book}/{fname}: cached")
                    bundle_meta[f"book/{book}/{fname}"] = meta
                    continue
            rows = 0
            with gzip.open(out, "wt", encoding="utf-8", compresslevel=9) as w:
                for fs_src in sorted(srcs):
                    src_path = WORK / fs_src / fname
                    if not src_path.exists():
                        continue
                    with gzip.open(src_path, "rt", encoding="utf-8") as r:
                        for line in r:
                            if not line.strip():
                                continue
                            w.write(line if line.endswith("\n") else line + "\n")
                            rows += 1
            if rows == 0:
                out.unlink(missing_ok=True)
                continue
            meta = {"rows": rows, "bytes_gz": out.stat().st_size,
                    "sha256_gz": gz_sha(out), "editions": sorted(srcs)}
            bundle_meta[f"book/{book}/{fname}"] = meta
            print(f"   ok book/{book}/{fname}: {rows:,} rows "
                  f"from {len(srcs)} edition(s)", flush=True)

        # small per-book index: editions + row counts, cheap to fetch in the UI
        bindex = {
            "book": book,
            "editions": editions,
            "tables": {},
            "rows": {},
        }
        for fname, srcs in tables.items():
            key = f"book/{book}/{fname}"
            if key in bundle_meta:
                bindex["tables"][fname.replace(".ndjson.gz", "")] = srcs
                bindex["rows"][fname.replace(".ndjson.gz", "")] = bundle_meta[key]["rows"]
            else:
                key2 = f"{srcs[0]}/{fname}"
                if key2 in files:
                    bindex["tables"].setdefault(fname.replace(".ndjson.gz", ""), srcs)
                    bindex["rows"][fname.replace(".ndjson.gz", "")] = files[key2]["rows"]
        (bdir / "index.json").write_text(
            json.dumps(bindex, ensure_ascii=False, indent=2), encoding="utf-8")

    manifest["bundles"] = bundle_meta
    manifest["bundles_generated_at"] = datetime.now(timezone.utc).isoformat()
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2),
                        encoding="utf-8")

    print(f"\nbundles: {len(bundle_meta)}  "
          f"rows: {sum(v['rows'] for v in bundle_meta.values()):,}  "
          f"size: {sum(v['bytes_gz'] for v in bundle_meta.values()) / 1e6:.2f} MB")


if __name__ == "__main__":
    main()

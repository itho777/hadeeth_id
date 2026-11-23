#!/usr/bin/env python3
"""Emit the four rebuilt matn books in `hadiths` column shape for a later D1 load.

This is staging, not an import. `source_id` uses the provisional form
`mutun:<book>` because no D1 source id has been assigned to these books yet;
the manifest records that so the loader and the report can show it.
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "export", "d1", "hadeeth-id-v2")
BOOKS = ("maani", "masabih", "muntaqa", "umdat")


def main():
    os.makedirs(OUT, exist_ok=True)
    manifest = {"note": "provisional source_id = mutun:<book>; target table hadiths",
                "books": {}}
    all_rows = 0
    all_bytes = 0
    path = os.path.join(OUT, "matn_staging.ndjson")
    with open(path, "w", encoding="utf-8", newline="\n") as dst:
        for book in BOOKS:
            src = os.path.join(ROOT, "data", "api", f"{book}.ndjson")
            rows = 0
            for line in open(src, encoding="utf-8"):
                if not line.strip():
                    continue
                r = json.loads(line)
                out = {
                    "source_id": f"mutun:{book}",
                    "book_id": book,
                    "hadith_number": int(r["hadith_number"]),
                    "text_ar": r.get("text_ar") or "",
                }
                dst.write(json.dumps(out, ensure_ascii=False,
                                     separators=(",", ":")) + "\n")
                rows += 1
            manifest["books"][book] = {"path": f"data/api/{book}.ndjson", "rows": rows}
            all_rows += rows
            print(f"  {book:10} {rows:6} rows")
    all_bytes = os.path.getsize(path)
    manifest.update({"path": "export/d1/hadeeth-id-v2/matn_staging.ndjson",
                     "rows": all_rows, "bytes": all_bytes,
                     "columns": ["source_id", "book_id", "hadith_number", "text_ar"]})
    p = os.path.join(ROOT, "export", "d1", "MANIFEST.json")
    d = json.load(open(p, encoding="utf-8"))
    d["v2"]["matn_staging"] = manifest
    with open(p, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(d, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    print(f"TOTAL {all_rows:,} rows / {all_bytes/2**20:.2f} MiB -> {path}")


if __name__ == "__main__":
    main()

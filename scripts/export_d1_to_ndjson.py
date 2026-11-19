#!/usr/bin/env python3
"""
export_d1_to_ndjson.py — Build the R2 NDJSON tree from the local D1 SQL dump.

Why not read D1 over the REST API: every row read there counts against the free
tier's daily row-read limit, and a full export is ~357k rows walked repeatedly.
The D1 export endpoint hands back one .sql dump at no row-read cost, so the
pipeline is: dump -> local SQLite (scripts/load_d1_dump.py) -> NDJSON here.

Output:
  export/<source>/<table>.ndjson.gz     one file per edition per table
  export/global/<table>.ndjson.gz       tables without source_id
  export/index.json                     manifest: rows, bytes_gz, sha256_gz

Usage:
  python scripts/export_d1_to_ndjson.py [--db PATH] [--out DIR]
"""

import sys, json, gzip, hashlib, sqlite3, argparse
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DB = ROOT / ".dump" / "hadeeth.sqlite"

PARTITIONED = ["hadiths", "sanad", "hadith_bab"]
GLOBAL      = ["narrators", "kitab", "imam_bio", "grades", "chapters",
               "fawaid", "audio", "syarah_links", "text_link"]


class Sink:
    """A gzip NDJSON file, opened lazily and closed with a sha256 of its bytes."""

    def __init__(self, path: Path, compresslevel=6):
        self.path = path
        path.parent.mkdir(parents=True, exist_ok=True)
        self.fh = gzip.open(path, "wt", encoding="utf-8", compresslevel=compresslevel)
        self.rows = 0

    def write(self, rec: dict):
        self.fh.write(json.dumps(rec, ensure_ascii=False))
        self.fh.write("\n")
        self.rows += 1

    def close(self):
        self.fh.close()
        h = hashlib.sha256()
        with open(self.path, "rb") as f:
            for chunk in iter(lambda: f.read(1 << 20), b""):
                h.update(chunk)
        return {"rows": self.rows, "bytes_gz": self.path.stat().st_size,
                "sha256_gz": h.hexdigest()}


def table_names(con):
    return [r[0] for r in con.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]


def columns(con, table):
    return [r[1] for r in con.execute(f'PRAGMA table_info("{table}")')]


def pk_columns(con, table):
    """Primary-key columns in declaration order — the ordering key for the export.

    Needed because a WITHOUT ROWID table has no rowid to ORDER BY, and a plain
    ORDER BY on a non-indexed column would sort the whole table in memory.
    """
    rows = con.execute(f'PRAGMA table_info("{table}")').fetchall()
    pk = sorted([r for r in rows if r[5]], key=lambda r: r[5])
    return [r[1] for r in pk]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default=str(DEFAULT_DB))
    ap.add_argument("--out", default=str(ROOT / "export"))
    ap.add_argument("--level", type=int, default=6, help="gzip level (6 balances size/time)")
    args = ap.parse_args()

    db = Path(args.db)
    work = Path(args.out)
    if not db.exists():
        sys.exit(f"missing {db} — run scripts/load_d1_dump.py first")
    work.mkdir(parents=True, exist_ok=True)

    con = sqlite3.connect(db)
    con.text_factory = str
    present = set(table_names(con))

    print("=== SQLite dump -> NDJSON ===")
    print(f"db   : {db}  ({db.stat().st_size / 1e6:.0f} MB)")
    print(f"out  : {work}")

    manifest = {"generated_at": None, "d1_database": "154c5a69-39af-477d-938a-c0a2cedeb2f7",
                "provenance": "d1 sql export -> local sqlite -> ndjson.gz",
                "files": {}, "books": {}}

    def dump_table(table, partitioned):
        cols = columns(con, table)
        sel = ", ".join(f'"{c}"' for c in cols)
        sinks = {}

        def sink_for(rel):
            if rel not in sinks:
                sinks[rel] = Sink(work / rel, args.level)
            return sinks[rel]

        n = 0
        order = ", ".join(f'"{c}"' for c in pk_columns(con, table)) or "rowid"
        sql = f'SELECT {sel} FROM "{table}" ORDER BY {order}'
        cur = con.execute(sql)
        while True:
            batch = cur.fetchmany(5000)
            if not batch:
                break
            for row in batch:
                rec = dict(zip(cols, row))
                if partitioned:
                    sid = rec.get("source_id")
                    if not sid:
                        continue
                    rel = f"{sid.replace(':', '_', 1)}/{table}.ndjson.gz"
                else:
                    rel = f"global/{table}.ndjson.gz"
                sink_for(rel).write(rec)
                n += 1

        out = {}
        for rel, s in sinks.items():
            meta = s.close()
            if meta["rows"] == 0:
                s.path.unlink(missing_ok=True)
                continue
            out[rel] = meta
        print(f"   {table:14s} {n:>8,} rows -> {len(out):>2} file(s)", flush=True)
        return out

    for t in PARTITIONED + GLOBAL:
        if t not in present:
            print(f"   {t:14s} absent, skipped")
            continue
        print(f"-> {t}", flush=True)
        manifest["files"].update(dump_table(t, t in PARTITIONED))

    books = {}
    for rel, m in manifest["files"].items():
        parts = rel.split("/")
        if parts[0] in ("global", "book", "map"):
            continue
        book = parts[0].split("_", 1)[1]
        b = books.setdefault(book, {"sources": [], "tables": {}, "rows": 0})
        if parts[0] not in b["sources"]:
            b["sources"].append(parts[0])
        b["tables"].setdefault(parts[0], {})[parts[1].replace(".ndjson.gz", "")] = m["rows"]
        b["rows"] += m["rows"]
    manifest["books"] = books
    manifest["totals"] = {"files": len(manifest["files"]),
                          "rows": sum(v["rows"] for v in manifest["files"].values()),
                          "bytes_gz": sum(v["bytes_gz"] for v in manifest["files"].values())}
    manifest["generated_at"] = datetime.now(timezone.utc).isoformat()
    (work / "index.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    t = manifest["totals"]
    print(f"\n=== SUMMARY ===")
    print(f"files      : {t['files']}")
    print(f"rows       : {t['rows']:,}")
    print(f"compressed : {t['bytes_gz'] / 1e6:.2f} MB")
    print(f"manifest   : {work / 'index.json'}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Build the offline D1 import set from the already-transformed R2 archive.

No network calls. Source of truth is `export/syarah/` (gzip NDJSON, one folder per
syarah package), produced by scripts/export_syarah_ndjson.py from the importer's
own prep_book()+COLS. This script only re-encodes it into one NDJSON file per D1
table, in foreign-key-safe order, plus the schema and a checksum manifest.

    python scripts/build_d1_offline.py

Output:
    export/d1/hadeeth-meta/<table>.ndjson     plain, one row per line
    export/d1/hadeeth-meta/schema.sql          DDL + indexes from the importer
    export/d1/hadeeth-id-v2/hadith_map.ndjson  cross-dataset map, already offline
    export/d1/MANIFEST.json                    counts, bytes, sha256, import order
"""
import gzip
import hashlib
import json
import os
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARCHIVE = os.path.join(ROOT, "export", "syarah")
OUT = os.path.join(ROOT, "export", "d1")
META = os.path.join(OUT, "hadeeth-meta")
V2 = os.path.join(OUT, "hadeeth-id-v2")
IMPORTER = r"G:/PortableHermes/data/AppData/Local/hermes/scripts"

# INSERT OR IGNORE semantics: first row wins for a duplicate primary key.
ORDER = [
    ("syarah_sources", "source_id"),
    ("syarah_chapters", "chapter_id"),
    ("syarah_passages", "passage_id"),
    ("syarah_links", "link_id"),
    ("syarah_entries", "entry_no"),
    ("syarah_editions", "source_id"),
]


def load_importer():
    sys.path.insert(0, IMPORTER)
    import hadeeth_v2_syarah_import as imp  # noqa: E402
    return imp


def package_dirs():
    return sorted(p for p in os.listdir(ARCHIVE)
                  if os.path.isdir(os.path.join(ARCHIVE, p)))


def source_files(table):
    """Package-local gz first; editions live once at the archive root."""
    if table == "syarah_editions":
        p = os.path.join(ARCHIVE, "syarah_editions.ndjson.gz")
        return [(os.path.basename(p), p)] if os.path.exists(p) else []
    out = []
    for pkg in package_dirs():
        p = os.path.join(ARCHIVE, pkg, f"{table}.ndjson.gz")
        if os.path.exists(p):
            out.append((pkg, p))
    return out


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def build_table(table, pk, imp):
    dst = os.path.join(META, f"{table}.ndjson")
    seen = set()
    rows = 0
    per_package = {}
    cols = imp.COLS[table]
    with open(dst, "w", encoding="utf-8", newline="\n") as fh:
        for pkg, path in source_files(table):
            n = 0
            with gzip.open(path, "rt", encoding="utf-8") as gz:
                for line in gz:
                    if not line.strip():
                        continue
                    row = json.loads(line)
                    key = row.get(pk)
                    if key in seen:
                        continue
                    seen.add(key)
                    # Same coercion the live importer applies before binding.
                    row = {c: imp._coerce(c, row.get(c)) for c in cols}
                    fh.write(json.dumps(row, ensure_ascii=False,
                                        separators=(",", ":")) + "\n")
                    rows += 1
                    n += 1
            per_package[pkg] = n
    return {
        "rows": rows,
        "bytes": os.path.getsize(dst),
        "sha256": sha256(dst),
        "columns": cols,
        "primary_key": pk,
        "per_package": per_package,
        "path": os.path.relpath(dst, ROOT).replace("\\", "/"),
    }


def write_schema(imp):
    p = os.path.join(META, "schema.sql")
    with open(p, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("-- hadeeth-meta / D1. Generated from hadeeth_v2_syarah_import.py.\n")
        fh.write("-- Apply in order, before any NDJSON rows.\n\n")
        for stmt in imp.DDL:
            fh.write(stmt + ";\n\n")
        for name, table, cols in imp.INDEXES:
            fh.write(f"CREATE INDEX IF NOT EXISTS {name} ON {table} ({cols});\n")
    return {"path": os.path.relpath(p, ROOT).replace("\\", "/"),
            "bytes": os.path.getsize(p), "sha256": sha256(p)}


def copy_map():
    src = os.path.join(ROOT, "data", "hadith_map.ndjson")
    if not os.path.exists(src):
        return None
    dst = os.path.join(V2, "hadith_map.ndjson")
    shutil.copy2(src, dst)
    with open(dst, "rb") as fh:
        n = sum(1 for l in fh if l.strip())
    return {"path": os.path.relpath(dst, ROOT).replace("\\", "/"),
            "rows": n, "bytes": os.path.getsize(dst), "sha256": sha256(dst)}


def night_plan(tables, budget):
    """Split the load into nights of at most `budget` row writes.

    Tables stay in dependency order; a table larger than one night is split
    into row ranges so the loader can resume with (table, offset, limit).
    """
    plan, night, used = [], 1, 0
    for table, meta in tables.items():
        left = meta["rows"]
        offset = 0
        while left:
            room = budget - used
            if room <= 0:
                night += 1
                used = 0
                room = budget
            take = min(room, left)
            if not plan or plan[-1]["night"] != night:
                plan.append({"night": night, "rows": 0, "parts": []})
            plan[-1]["parts"].append({"table": table, "offset": offset, "limit": take})
            plan[-1]["rows"] += take
            used += take
            offset += take
            left -= take
    return plan


def main():
    imp = load_importer()
    os.makedirs(META, exist_ok=True)
    os.makedirs(V2, exist_ok=True)
    manifest = {
        "generated_from": "export/syarah/ (gzip archive of importer prep_book output)",
        "targets": {
            "hadeeth-meta": imp.META_DB,
            "hadeeth-id-v2": "154c5a69-39af-477d-938a-c0a2cedeb2f7",
        },
        "import_order": [t for t, _ in ORDER],
        "tables": {},
        "schema": write_schema(imp),
        "v2": {"hadith_map": copy_map()},
    }
    for table, pk in ORDER:
        m = build_table(table, pk, imp)
        manifest["tables"][table] = m
        print(f"  {table:20} {m['rows']:7} rows  {m['bytes']/2**20:7.2f} MiB")
    total = sum(m["rows"] for m in manifest["tables"].values())
    manifest["total_rows"] = total
    manifest["write_budget_per_day"] = 100000
    manifest["night_plan"] = night_plan(manifest["tables"], 100000)
    p = os.path.join(OUT, "MANIFEST.json")
    with open(p, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(manifest, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    print(f"TOTAL {total:,} rows -> {p}")


if __name__ == "__main__":
    main()

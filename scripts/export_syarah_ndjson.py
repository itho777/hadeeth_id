"""
export_syarah_ndjson.py — the syarah layer as per-package NDJSON, for R2.

Layout is per package, not per book and not one big file:

    export/syarah/<package_id>/syarah_links.ndjson.gz
    export/syarah/<package_id>/syarah_passages.ndjson.gz
    ...
    export/syarah/syarah_editions.ndjson.gz      (20 rows, the version picker)
    export/syarah/index.json                     (book -> packages -> files, with sha256)

Bukhari carries three sharhs and its biggest one alone is ~72 MB of text; a single 54 MiB
`passages` blob would force a reader to fetch every book to show one hadith. The package is
the unit a reader actually asks for: pick the book, pick the version, fetch that package.
The index tells a client which packages exist for a book without downloading any of them.

Parity with the importer is the whole point, so the transforms are not reimplemented here:
the importer module is loaded and its own prep_book()/COLS are used. If the import rules
change, the export changes with them — there is one definition of a row, not two.

Rows carry target column names, None where a package does not supply a field. Order is
deterministic: the order the package itself stored the rows.

Usage:
  python scripts/export_syarah_ndjson.py            # write export/syarah/**
  python scripts/export_syarah_ndjson.py --plain    # also keep uncompressed copies
"""
import gzip
import hashlib
import importlib.util
import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMPORTER = r"G:/PortableHermes/data/AppData/Local/hermes/scripts/hadeeth_v2_syarah_import.py"
EDITIONS = os.path.join(ROOT, "data", "syarah_editions.ndjson")
OUTDIR = os.path.join(ROOT, "export", "syarah")
PACKAGE_TABLES = ["syarah_sources", "syarah_chapters", "syarah_passages",
                  "syarah_links", "syarah_entries"]
PLAIN = "--plain" in sys.argv


def load_importer():
    """The importer module, so export and import agree on every row."""
    spec = importlib.util.spec_from_file_location("syarah_importer", IMPORTER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def ndjson(path):
    if not os.path.exists(path):
        return
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                yield json.loads(line)


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def roundtrip(path, expected):
    """Every file must parse, and the count must match what was written."""
    n, last = 0, None
    with gzip.open(path, "rt", encoding="utf-8") as fh:
        for line in fh:
            last = json.loads(line)
            n += 1
    return {"rows": n, "matches_counter": n == expected,
            "last_line_parsed": last is not None}


def derived_ahmad_links(mod):
    """The sharh package ships no links by design; our text-derived set is offline."""
    p = os.path.join(ROOT, "data", "syarah_ahmad_links.ndjson")
    if not os.path.exists(p):
        return None
    return [{c: r.get(c) for c in mod.COLS["syarah_links"]} for r in ndjson(p)]


def write_package(mod, package, pkgdir):
    """One package -> one gzipped file per non-empty table."""
    rows, notes = mod.prep_book(package)
    if package.get("package_id") == "ahmad":
        derived = derived_ahmad_links(mod)
        if derived is not None:
            rows["syarah_links"] = derived
            note = (f"derived ahmad links: {len(derived)} rows from "
                    "data/syarah_ahmad_links.ndjson (sharh numbering is not hadith numbering)")
            if isinstance(notes, dict):
                notes["derived_ahmad_links"] = note
            else:
                notes.append(note)
    files, counts = {}, {}
    for table in PACKAGE_TABLES:
        data = rows.get(table) or []
        counts[table] = len(data)
        if not data:
            continue
        os.makedirs(pkgdir, exist_ok=True)
        path = os.path.join(pkgdir, f"{table}.ndjson.gz")
        cols = mod.COLS[table]
        with gzip.open(path, "wt", encoding="utf-8", newline="\n", compresslevel=9) as fh:
            for row in data:
                fh.write(json.dumps({c: row.get(c) for c in cols},
                                    ensure_ascii=False) + "\n")
        files[table] = {
            "path": f"{os.path.basename(pkgdir)}/{os.path.basename(path)}",
            "rows": len(data),
            "gz_bytes": os.path.getsize(path),
            "sha256": sha256_file(path),
            "roundtrip": roundtrip(path, len(data)),
        }
        if PLAIN:
            plain = path[:-3]
            with gzip.open(path, "rt", encoding="utf-8") as src, \
                    open(plain, "w", encoding="utf-8", newline="\n") as dst:
                for line in src:
                    dst.write(line)
    return files, counts, notes


def main():
    mod = load_importer()
    os.makedirs(OUTDIR, exist_ok=True)
    started = time.time()

    packages = mod.discover_packages()
    print(f"{len(packages)} packages -> {OUTDIR}/<package_id>/")

    index = {"generated_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
             "source_root": mod.SYARAH_ROOT,
             "layout": "export/syarah/<package_id>/<table>.ndjson.gz",
             "books": {}, "packages": {}}
    total_rows = total_bytes = 0
    bad = []

    for package in packages:
        pid = package["package_id"]
        pkgdir = os.path.join(OUTDIR, pid)
        files, counts, notes = write_package(mod, package, pkgdir)
        n = sum(counts.values())
        b = sum(f["gz_bytes"] for f in files.values())
        total_rows += n
        total_bytes += b
        bad += [f["path"] for f in files.values()
                if not f["roundtrip"]["matches_counter"] or not f["roundtrip"]["last_line_parsed"]]
        index["packages"][pid] = {
            "book_id": package["book_id"], "source_id": package["source_id"],
            "turath_id": package["turath_id"], "rows": counts,
            "total_rows": n, "gz_bytes": b, "files": files, "transforms": notes,
        }
        print(f"  {pid:22s} {package['book_id']:<10} {n:6d} rows  {b/2**20:6.2f} MiB")

    # editions: one global file, they describe the packages themselves
    ed_rows = list(ndjson(EDITIONS))
    epath = os.path.join(OUTDIR, "syarah_editions.ndjson.gz")
    with gzip.open(epath, "wt", encoding="utf-8", newline="\n", compresslevel=9) as fh:
        for row in ed_rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    ebytes = os.path.getsize(epath)
    total_bytes += ebytes
    total_rows += len(ed_rows)
    if not roundtrip(epath, len(ed_rows))["matches_counter"]:
        bad.append("syarah_editions.ndjson.gz")
    index["editions"] = {"path": "syarah_editions.ndjson.gz", "rows": len(ed_rows),
                         "gz_bytes": ebytes, "sha256": sha256_file(epath)}

    # book -> packages, ordered by default_rank so a client can take [0] as the default
    for row in ed_rows:
        entry = index["books"].setdefault(row["book_id"], {"packages": []})
        entry["packages"].append({"package_id": row["package_id"],
                                  "source_id": row["source_id"],
                                  "default_rank": row["default_rank"],
                                  "variant": row["variant"],
                                  "lang": row["lang"],
                                  "title_ar": row["title_ar"],
                                  "author_ar": row["author_ar"]})
    for book in index["books"].values():
        book["packages"].sort(key=lambda p: p["default_rank"])

    index["total_rows"] = total_rows
    index["total_gz_bytes"] = total_bytes
    index["seconds"] = round(time.time() - started, 1)
    mpath = os.path.join(OUTDIR, "index.json")
    with open(mpath, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(index, fh, ensure_ascii=False, indent=1)

    print(f"\n{'':22s} {'rows':>9s} {'gz MiB':>8s}")
    print(f"{'TOTAL':22s} {total_rows:9d} {total_bytes/2**20:8.2f}")
    print(f"books: {len(index['books'])}  packages: {len(index['packages'])}")
    print("round-trip:", "all files parse" if not bad else f"FAILED {bad}")
    print(f"index -> {mpath}")


if __name__ == "__main__":
    main()

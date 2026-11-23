"""
build_syarah_static.py — turn the R2 archive export into the static site's data scheme.

The site at G:/hadeeth_id/js/api.js does NOT download whole NDJSON files. It fetches
`<file>_index.ndjson` (one row per record: `id`, `n`, `s`, `e` = byte offsets) and then uses
HTTP Range requests against the plain, UNCOMPRESSED `<file>.ndjson`. That is why the gzipped
archive is not usable as the serving copy: a byte range into a gzip stream cannot be
decoded on its own.

This script writes the serving copy beside the static data tree:

    export_site/syarah/<package_id>/syarah_links.ndjson
    export_site/syarah/<package_id>/syarah_links_index.ndjson
    export_site/syarah/<package_id>/syarah_passages.ndjson
    ...
    export_site/syarah/books.ndjson
    export_site/syarah/editions.ndjson

Each index row is {"id": <primary key>, "n": <native number, when the table has one>,
"s": <byte offset of first byte>, "e": <byte offset of last byte>} — the same i/n/s/e
contract the site already uses for api/<book>_index.ndjson. `coalesceRuns()` in api.js
merges neighbouring entries into one Range request.

Reads the gzipped archive made by export_syarah_ndjson.py; no package files are needed.

Usage:
  python scripts/build_syarah_static.py
"""
import gzip
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "export", "syarah")
OUT = os.path.join(ROOT, "export_site", "syarah")
TABLES = ["syarah_sources", "syarah_chapters", "syarah_passages",
          "syarah_links", "syarah_entries"]

# (primary-key field, native-number field or None) per target table
KEYS = {
    "syarah_sources": ("source_id", None),
    "syarah_chapters": ("chapter_id", None),
    "syarah_passages": ("passage_id", None),
    "syarah_links": ("link_id", "source_native_number"),
    "syarah_entries": ("entry_no", None),
}


def gz_lines(path):
    with gzip.open(path, "rt", encoding="utf-8") as fh:
        for line in fh:
            line = line.rstrip("\n")
            if line:
                yield line


def text_lines(path):
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.rstrip("\n")
            if line:
                yield line


def build_table(src_gz, out_dir, table):
    """Write the plain NDJSON and its byte-offset index; verify a sampled row."""
    os.makedirs(out_dir, exist_ok=True)
    plain = os.path.join(out_dir, f"{table}.ndjson")
    index = os.path.join(out_dir, f"{table}_index.ndjson")
    id_field, num_field = KEYS[table]
    rows = []
    offset = 0
    with open(plain, "w", encoding="utf-8", newline="\n") as fh:
        for line in gz_lines(src_gz):
            raw = (line + "\n").encode("utf-8")
            r = json.loads(line)
            rows.append({"id": r.get(id_field),
                         "n": r.get(num_field) if num_field else None,
                         "s": offset, "e": offset + len(raw) - 1})
            fh.write(raw.decode("utf-8"))
            offset += len(raw)

    with open(index, "w", encoding="utf-8", newline="\n") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")

    # critical check: a byte range taken from the index must decode to that exact row
    checks = [0, len(rows) // 2, len(rows) - 1] if rows else []
    verified = True
    with open(plain, "rb") as fh:
        for pos in checks:
            want_id = rows[pos]["id"]
            fh.seek(rows[pos]["s"])
            chunk = fh.read(rows[pos]["e"] - rows[pos]["s"] + 1)
            got = json.loads(chunk.decode("utf-8"))
            if got.get(id_field) != want_id:
                verified = False
    return len(rows), offset, verified


def main():
    idx = json.load(open(os.path.join(SRC, "index.json"), encoding="utf-8"))
    os.makedirs(OUT, exist_ok=True)
    print(f"{len(idx['packages'])} packages -> {OUT}")

    books, total_rows, total_bytes, bad = [], 0, 0, []
    for pid, meta in sorted(idx["packages"].items()):
        pkgdir = os.path.join(OUT, pid)
        counts, size = {}, 0
        for table in TABLES:
            rel = meta["files"].get(table, {}).get("path")
            if not rel:
                continue
            n, b, ok = build_table(os.path.join(SRC, rel.replace("/", os.sep)),
                                   pkgdir, table)
            counts[table] = n
            size += b
            total_rows += n
            total_bytes += b
            if not ok:
                bad.append(f"{pid}/{table}")
        print(f"  {pid:22s} {sum(counts.values()):6d} rows  {size/2**20:6.2f} MiB")

    # book -> packages, default first, for the version dropdown
    for book, entry in sorted(idx["books"].items()):
        books.append({
            "book_id": book,
            "packages": [
                {"package_id": p["package_id"], "source_id": p["source_id"],
                 "default_rank": p["default_rank"], "variant": p["variant"],
                 "lang": p["lang"], "title_ar": p["title_ar"],
                 "author_ar": p["author_ar"]}
                for p in sorted(entry["packages"], key=lambda x: x["default_rank"])
            ],
        })
    with open(os.path.join(OUT, "books.ndjson"), "w", encoding="utf-8", newline="\n") as fh:
        for b in books:
            fh.write(json.dumps(b, ensure_ascii=False) + "\n")

    # The archive's editions gzip was removed with the old monolithic export;
    # rebuild it deterministically (mtime=0) and refresh its hash in index.json.
    ed_src = os.path.join(ROOT, "data", "syarah_editions.ndjson")
    ed_lines = list(text_lines(ed_src))
    ed_n = len(ed_lines)
    with open(os.path.join(OUT, "editions.ndjson"), "w", encoding="utf-8", newline="\n") as fh:
        for line in ed_lines:
            fh.write(line + "\n")

    ed_gz = os.path.join(SRC, "syarah_editions.ndjson.gz")
    with open(ed_gz, "wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw,
                           compresslevel=9, mtime=0) as gz:
            for line in ed_lines:
                gz.write((line + "\n").encode("utf-8"))
    import hashlib
    h = hashlib.sha256()
    with open(ed_gz, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    idx["editions"]["gz_bytes"] = os.path.getsize(ed_gz)
    idx["editions"]["sha256"] = h.hexdigest()
    with open(os.path.join(SRC, "index.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(idx, fh, ensure_ascii=False, indent=1)

    print(f"\nTOTAL {total_rows + ed_n:,} rows  {total_bytes/2**20:.2f} MiB plain")
    print(f"books: {len(books)}  indexes: {sum(len(m['files']) for m in idx['packages'].values())}")
    print("range check:", "all sampled byte offsets decode to the right row" if not bad
          else f"FAILED {bad}")


if __name__ == "__main__":
    main()

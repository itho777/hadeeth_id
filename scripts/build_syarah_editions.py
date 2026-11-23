"""
build_syarah_editions.py — one row per syarah package, for the UI's version picker.

The UI shows ONE sharh by default and the rest behind a pull-down ("versions", next to
"languages"). That only works if every package declares, in the database, which book it
belongs to, what its title and author are, and which one is the default. The per-package
MANIFEST.json has all of it, but it lives on disk in 18 folders, so this script collapses
them into one table-shaped file.

Deliberate choices:
  * `package_id` is the folder name, always. Two packages can share a `book_id`
    (bukhari: fath + battal), so the folder is the only stable identity.
  * `source_id` is `turath_<turath_id>`, which is what the packages themselves use in
    `syarah_sources` and in every `passage_id`. When the package's .db is on disk the
    value is checked against its own `syarah_sources` instead of being assumed.
  * `default_rank` 1 = shown by default for that book. The package whose folder is the
    bare book name is the default; a second sharh on the same book is rank 2. Nothing
    else is invented: the column is editable, and re-running this script does not
    overwrite a rank a human has already set in the .ndjson.

Reads only the local packages. No D1 calls, no writes.

Usage:
  python scripts/build_syarah_editions.py            # writes data/syarah_editions.ndjson
  python scripts/build_syarah_editions.py --check    # print, write nothing
"""
import glob
import json
import os
import sqlite3
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SYARAH_ROOT = r"H:/Itho/2026/Project/Hadeeth/data source/Syarah From Muse"
OUT = os.path.join(ROOT, "data", "syarah_editions.ndjson")
COLS = ["source_id", "package_id", "book_id", "variant", "title_ar", "author_ar",
        "turath_id", "lang", "default_rank", "links", "passages", "chapters",
        "payload_mb", "retrieved_at", "package_sha256", "package_dir"]

CHECK_ONLY = "--check" in sys.argv
DERIVED_AHMAD = os.path.join(ROOT, "data", "syarah_ahmad_links.ndjson")


def link_count(package_id, declared):
    """Ahmad's MANIFEST honestly says 0; our derived links live outside the package."""
    if package_id != "ahmad" or not os.path.exists(DERIVED_AHMAD):
        return declared
    with open(DERIVED_AHMAD, encoding="utf-8") as fh:
        return sum(1 for line in fh if line.strip())


def source_id_from_db(pkg_dir, dbname):
    """The package's own syarah_sources row, when its .db is on disk."""
    path = os.path.join(pkg_dir, dbname)
    if not os.path.exists(path):
        return None
    try:
        con = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
        rows = con.execute(
            "SELECT source_id FROM syarah_sources WHERE kind = 'syarah_book'").fetchall()
        con.close()
    except sqlite3.Error:
        return None
    return rows[0][0] if len(rows) == 1 else None


def existing_ranks():
    """Keep any default_rank a human already set, so a rerun is not a reset."""
    out = {}
    if not os.path.exists(OUT):
        return out
    with open(OUT, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            if r.get("package_id") and r.get("default_rank"):
                out[r["package_id"]] = int(r["default_rank"])
    return out


def main():
    keep = existing_ranks()
    rows = []
    for mf in sorted(glob.glob(os.path.join(SYARAH_ROOT, "*", "MANIFEST.json"))):
        pkg_dir = os.path.dirname(mf)
        package_id = os.path.basename(pkg_dir)
        with open(mf, encoding="utf-8") as fh:
            m = json.load(fh)

        book_id = m.get("book_id")
        turath_id = m.get("turath_id")
        if not book_id or not turath_id:
            print(f"  SKIP {package_id}: manifest has no book_id/turath_id")
            continue

        dbs = [p for p in os.listdir(pkg_dir) if p.endswith(".db")]
        from_db = source_id_from_db(pkg_dir, dbs[0]) if dbs else None
        source_id = from_db or f"turath_{turath_id}"
        if from_db and from_db != f"turath_{turath_id}":
            print(f"  NOTE {package_id}: db says {from_db}, manifest turath_id {turath_id}")

        variant = m.get("syarah_variant") or ("primary" if package_id == book_id else package_id)
        rows.append({
            "source_id": source_id,
            "package_id": package_id,
            "book_id": book_id,
            "variant": variant,
            "title_ar": m.get("syarah_title_ar"),
            "author_ar": m.get("author_ar"),
            "turath_id": int(turath_id),
            "lang": "ar",
            "default_rank": None,          # filled below
            "links": link_count(package_id, m.get("links")),
            "passages": m.get("passages"),
            "chapters": m.get("chapters"),
            "payload_mb": m.get("payload_mb"),
            "retrieved_at": m.get("retrieved_at"),
            "package_sha256": m.get("sha256"),
            "package_dir": os.path.relpath(pkg_dir, SYARAH_ROOT).replace("\\", "/"),
        })

    # default_rank: the bare-book-name package is 1, the rest of that book follows,
    # ordered by turath_id so a rerun produces the same file.
    by_book = {}
    for r in rows:
        by_book.setdefault(r["book_id"], []).append(r)
    for book, group in by_book.items():
        group.sort(key=lambda r: (r["package_id"] != book, r["turath_id"]))
        for i, r in enumerate(group, 1):
            r["default_rank"] = keep.get(r["package_id"], i)

    rows.sort(key=lambda r: (r["book_id"], r["default_rank"], r["turath_id"]))
    payload = sum(float(r["payload_mb"] or 0) for r in rows)
    multi = {b: len(g) for b, g in by_book.items() if len(g) > 1}

    print(f"{len(rows)} packages, {len(by_book)} books, payload {payload:.2f} MB")
    print("multi-sharh books: " + (", ".join(f"{b}={n}" for b, n in sorted(multi.items())) or "none"))
    for r in rows:
        print(f"  {r['default_rank']}  {r['book_id']:<10} {r['package_id']:<16} "
              f"{r['source_id']:<13} {str(r['title_ar'])[:44]}")

    if CHECK_ONLY:
        print("[check] not written")
        return

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        for r in rows:
            fh.write(json.dumps({c: r[c] for c in COLS}, ensure_ascii=False) + "\n")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()

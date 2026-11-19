#!/usr/bin/env python3
"""
syarah_build.py — collapse data/commentaries/*.json into per-book NDJSON.

30,080 single-hadith JSON files cannot be reached by a Range lookup and cannot
be uploaded one object at a time. Three source shapes exist on disk and are
normalised to the keys the reader already expects (explanation_*, syarah_*,
benefits_*, source_name_*):

    dorar   book_id, anchor_id, source, syarah_ar, rawi, muhaddith, hadith_ar
    expl    book_id, hadith_number, explanation_{ar,en,id}, benefits_*, ...
    en      book_id, hadith_num, hadith_en, syarah_en

Two trees are written, because the commentary corpus and the hadith page do not
share a key:

    commentaries/<book>.ndjson           full corpus, keyed by Dorar anchor_id,
                                         grouped by anchor so one Range returns
                                         every source for that anchor
    commentaries/<book>_index.ndjson     anchor -> byte range
    commentaries/matched/<book>.ndjson   only the confident text matches
                                         (scripts/syarah_match.py), keyed by the
                                         shipped hadith number: one Range per page
    commentaries/matched/<book>_index.ndjson
    commentaries/_catalog.ndjson         per-book availability
    commentaries/editions.ndjson         syarah package descriptors

Nothing is dropped except placeholders ("Not Available", "None", "غير متوفر"),
which are not text and only make the UI open an empty panel. An explanation that
could not be matched still ships in the anchor-keyed tree.
"""

import ast
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "commentaries"
NAME = re.compile(r"^([a-z_]+?)_(\d+)(?:[._](\d+))?\.json$")
PLACEHOLDER = {"", "not available", "none", "null", "n/a", "غير متوفر", "غير متاح", "-"}


def clean(value):
    """Return a real string, or '' when the value is a placeholder."""
    if value is None:
        return ""
    if isinstance(value, (list, tuple)):
        items = [clean(v) for v in value]
        return [i for i in items if i] if items else ""
    text = str(value).strip()
    return "" if text.lower() in PLACEHOLDER else text


def as_list(value):
    if isinstance(value, list):
        return [clean(v) for v in value if clean(v)]
    text = clean(value)
    if not text:
        return []
    # The benefits fields arrive as a Python list repr ("['a', \"it's b\"]"),
    # which quote-swapping corrupts: literal_eval reads it as written.
    try:
        parsed = ast.literal_eval(text)
        if isinstance(parsed, (list, tuple)):
            return [clean(v) for v in parsed if clean(v)]
    except (ValueError, SyntaxError):
        pass
    return [text]


def parse_name(path):
    m = NAME.match(path.name)
    return (m.group(1), m.group(2), m.group(3) or "1") if m else None


def norm_row(doc, book, anchor, alt, origin):
    row = {"book_id": book, "anchor_id": anchor, "source_key": alt}
    texts = {}

    # dorar shape
    if "anchor_id" in doc or "syarah_ar" in doc:
        row["source_name_ar"] = clean(doc.get("source")) or "الدرر السنية"
        row["source_name_en"] = "Dorar (al-Durar al-Saniyyah)"
        row["source_name_id"] = "Dorar (ad-Durar as-Saniyyah)"
        row["explanation_ar"] = clean(doc.get("syarah_ar"))
        for key in ("hadith_ar", "rawi", "muhaddith", "masdar", "grade", "takhrij"):
            val = clean(doc.get(key))
            if val:
                row[key] = val
        row["hadith_id"] = f"{book}_{clean(doc.get('anchor_id')) or anchor}"
        texts["ar"] = row["explanation_ar"]

    # explanation shape (ar / en / id, sometimes benefits)
    if "explanation_ar" in doc or "explanation_en" in doc or "explanation_id" in doc:
        for lang in ("ar", "en", "id"):
            val = clean(doc.get(f"explanation_{lang}"))
            if val:
                row[f"explanation_{lang}"] = val
                texts[lang] = val
        for lang in ("en", "id"):
            benefits = as_list(doc.get(f"benefits_{lang}"))
            if benefits:
                row[f"benefits_{lang}"] = benefits
        for lang in ("ar", "en", "id"):
            val = clean(doc.get(f"source_name_{lang}"))
            if val:
                row[f"source_name_{lang}"] = val
        if doc.get("hadith_id"):
            row["hadith_id"] = clean(doc.get("hadith_id"))

    # en/ shape
    if "syarah_en" in doc and "explanation_en" not in row:
        row["explanation_en"] = clean(doc.get("syarah_en"))
        row.setdefault("source_name_en", "English commentary")
        row.setdefault("source_name_id", "Syarah bahasa Inggris")
        row.setdefault("source_name_ar", "شرح بالإنجليزية")
        if clean(doc.get("hadith_en")):
            row["hadith_en"] = clean(doc.get("hadith_en"))
        texts["en"] = row["explanation_en"]

    # mirror explanation_* into syarah_* so both reader paths agree
    for lang in ("ar", "en", "id"):
        val = row.get(f"explanation_{lang}")
        if val:
            row[f"syarah_{lang}"] = val
    row["langs"] = sorted(texts)
    row["origin"] = origin
    return row


def dedupe_key(row):
    """Identity of an explanation: same source AND same text is the same panel.

    Dorar's index lists a hadith once per chain, so one hadith can arrive with
    hundreds of identical explanations; showing them all is not more information.
    """
    text = (row.get("explanation_ar") or row.get("explanation_en")
            or row.get("explanation_id") or "")
    return (row.get("source_name_en") or "", text[:400], len(text))


def has_text(row):
    return any(row.get(f"explanation_{l}") for l in ("ar", "en", "id"))


def load_links():
    """Dorar anchor -> shipped hadith number, from syarah_match.py."""
    path = ROOT / "data" / "links" / "syarah_match.json"
    if not path.exists():
        raise SystemExit("run scripts/syarah_match.py first: no anchor->number map")
    raw = json.loads(path.read_text(encoding="utf-8"))
    return {book: {anchor: int(hit[0]) for anchor, hit in links.items()}
            for book, links in raw.items()}


def collect():
    """anchor -> list of rows (full corpus), plus count of placeholders skipped."""
    by_anchor = {}
    dropped = scanned = 0

    def ingest(path, origin):
        nonlocal dropped, scanned
        parsed = parse_name(path)
        if not parsed:
            return None
        scanned += 1
        book, anchor, alt = parsed
        doc = json.loads(path.read_text(encoding="utf-8"))
        row = norm_row(doc, book, anchor, alt, origin)
        if not has_text(row):
            dropped += 1
            return None
        return book, anchor, row

    for path in SRC.glob("*.json"):
        got = ingest(path, "root")
        if got:
            book, anchor, row = got
            by_anchor.setdefault((book, anchor), []).append(row)

    en_dir = SRC / "en"
    if en_dir.is_dir():
        for path in en_dir.glob("*.json"):
            got = ingest(path, "en")
            if not got:
                continue
            book, anchor, row = got
            bucket = by_anchor.setdefault((book, anchor), [])
            merged = False
            for existing in bucket:
                if not existing.get("explanation_en") and row.get("explanation_en"):
                    existing["explanation_en"] = row["explanation_en"]
                    existing["syarah_en"] = row["explanation_en"]
                    existing.setdefault("source_name_en", row.get("source_name_en"))
                    existing["langs"] = sorted({l for l in ("ar", "en", "id")
                                                if existing.get(f"explanation_{l}")})
                    if row.get("hadith_en"):
                        existing.setdefault("hadith_en", row["hadith_en"])
                    merged = True
                    break
            if not merged:
                bucket.append(row)
    return by_anchor, scanned, dropped


def write_tree(prefix, groups, out_dir, key_name, ship=True):
    """Write <prefix>/<book>.ndjson + _index.ndjson for one grouping.

    ship=False writes the files but keeps them out of the manifest: an
    anchor-keyed tree has no reader route (a page knows its hadith number, not
    Dorar's anchor), so it stays on disk for the next matching pass instead of
    adding 258 MB to the bucket.
    """
    folder = out_dir / prefix
    folder.mkdir(parents=True, exist_ok=True)
    by_book = {}
    for (book, key), rows in groups.items():
        by_book.setdefault(book, []).append((int(key), key, rows))

    manifest, report = [], []
    for book in sorted(by_book):
        entries = sorted(by_book[book], key=lambda x: x[0])
        ndjson = folder / f"{book}.ndjson"
        index = folder / f"{book}_index.ndjson"
        pos = 0
        with ndjson.open("w", encoding="utf-8", newline="\n") as out, \
                index.open("w", encoding="utf-8", newline="\n") as idx:
            for ordinal, (_, key, rows) in enumerate(entries, 1):
                start = pos
                for row in rows:
                    blob = json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n"
                    out.write(blob)
                    pos += len(blob.encode("utf-8"))
                idx.write(json.dumps({"n": key, "s": start, "e": pos - 1,
                                      "k": len(rows), "i": ordinal},
                                     ensure_ascii=False, separators=(",", ":")) + "\n")
        if ship:
            manifest.append({"path": ndjson.as_posix(),
                             "key": f"{prefix}/{book}.ndjson",
                             "bytes": ndjson.stat().st_size, "ct": "application/x-ndjson"})
            manifest.append({"path": index.as_posix(),
                             "key": f"{prefix}/{book}_index.ndjson",
                             "bytes": index.stat().st_size, "ct": "application/x-ndjson"})
        report.append((f"{prefix}/{book}.ndjson",
                       sum(len(r) for _, _, r in entries),
                       f"{len(entries)} {key_name}"))
    return manifest, report


def build(out_dir):
    out_dir = Path(out_dir)
    by_anchor, scanned, dropped = collect()
    links = load_links()

    # anchor-keyed tree stays local (no reader route); only the matched tree ships
    _, anchor_report = write_tree("commentaries", by_anchor, out_dir, "anchors", ship=False)
    manifest, report = [], list(anchor_report)

    matched = {}
    matched_rows = 0
    duplicates = 0
    for (book, anchor), rows in by_anchor.items():
        number = links.get(book, {}).get(anchor)
        if number is None:
            continue
        bucket = matched.setdefault((book, number), [])
        seen = {dedupe_key(r) for r in bucket}
        for row in rows:
            key = dedupe_key(row)
            if key in seen:
                duplicates += 1
                continue
            seen.add(key)
            target = dict(row)
            target["hadith_number"] = str(number)
            bucket.append(target)
            matched_rows += 1

    # Classical sharh from the Muse corpus: links already carry a number, so
    # these attach without text matching. Merged into the same buckets so one
    # Range still returns every source for a hadith, one tab per edition.
    muse_rows = 0
    muse_report = []
    try:
        import syarah_muse
        muse, muse_report = syarah_muse.build()
    except Exception as exc:                       # never lose the Dorar tree
        muse = {}
        print(f"  ! muse import skipped: {exc}")
    for (book, number), rows in muse.items():
        bucket = matched.setdefault((book, number), [])
        seen = {dedupe_key(r) for r in bucket}
        for row in rows:
            key = dedupe_key(row)
            if key in seen:
                duplicates += 1
                continue
            seen.add(key)
            bucket.append(row)
            matched_rows += 1
            muse_rows += 1

    m_manifest, m_report = write_tree("commentaries/matched", matched, out_dir, "hadiths")
    manifest += m_manifest
    report += m_report

    catalog = []
    books = sorted({b for (b, _) in matched} | {b for b, _ in by_anchor})
    for book in books:
        shipped = [r for (b, _), bucket in matched.items() if b == book for r in bucket]
        anchors = [r for (b, _), bucket in by_anchor.items() if b == book for r in bucket]
        langs = {l: sum(1 for r in anchors if r.get(f"explanation_{l}")) for l in ("ar", "en", "id")}
        editions = {}
        for r in shipped:
            name = r.get("source_name_en") or "Commentary"
            editions[name] = editions.get(name, 0) + 1
        catalog.append({"book_id": book,
                        "anchors": len({a for (b, a) in by_anchor if b == book}),
                        "rows": len(anchors), "langs": langs,
                        "matched": len({n for (b, n) in matched if b == book}),
                        "commentaries": len(shipped),
                        "editions": [{"name": n, "rows": c} for n, c in
                                     sorted(editions.items(), key=lambda kv: -kv[1])]})
    cat_path = out_dir / "commentaries" / "_catalog.ndjson"
    with cat_path.open("w", encoding="utf-8", newline="\n") as f:
        for row in catalog:
            f.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
    manifest.append({"path": cat_path.as_posix(), "key": "commentaries/_catalog.ndjson",
                     "bytes": cat_path.stat().st_size, "ct": "application/x-ndjson"})
    report.append(("commentaries/_catalog.ndjson", len(catalog), "books"))

    registry = ROOT / "data" / "syarah_editions.ndjson"
    if registry.exists():
        dst = out_dir / "commentaries" / "editions.ndjson"
        dst.write_bytes(registry.read_bytes())
        manifest.append({"path": dst.as_posix(), "key": "commentaries/editions.ndjson",
                         "bytes": dst.stat().st_size, "ct": "application/x-ndjson"})
        report.append(("commentaries/editions.ndjson",
                       sum(1 for _ in registry.open("rb")), "editions"))

    print(f"syarah: scanned {scanned} files, {dropped} placeholders skipped, "
          f"{len(by_anchor)} anchors, {matched_rows} rows matched "
          f"({duplicates} duplicate explanations collapsed)")
    return manifest, report


if __name__ == "__main__":
    m, r = build(ROOT / "export_site")
    for key, count, note in r:
        print(f"  {key:46} rows={count:7} {note}")

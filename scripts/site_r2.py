#!/usr/bin/env python3
"""
site_r2.py — build the NDJSON serving tree, upload it, verify it.

Everything the site reads becomes NDJSON. Master hadith files are already
NDJSON and are uploaded byte-identical (they are read with HTTP Range, so they
must NOT be gzipped). Every JSON sidecar is converted: one row per line.

    python scripts/site_r2.py build
    python scripts/site_r2.py upload
    python scripts/site_r2.py verify
"""

import argparse
import ast
import glob
import hashlib
import json
import os
import sqlite3
import sys
import time
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cf_env import ACCOUNT, BUCKET, token  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OUT = ROOT / "export_site"
MANIFEST = OUT / "_manifest.ndjson"
API = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT}/r2/buckets/{BUCKET}/objects"
PUBLIC = "https://pub-075ac3f4a31e4e85a876c26c815ae93d.r2.dev"
CT = "application/x-ndjson"


# ---------------------------------------------------------------- conversion

def rows(obj, key_name):
    """Turn a loaded JSON document into a flat list of rows."""
    if isinstance(obj, list):
        return obj
    if isinstance(obj, dict):
        vals = list(obj.values())
        if vals and all(isinstance(v, (dict, list)) for v in vals):
            out = []
            for k, v in obj.items():
                if isinstance(v, dict):
                    row = dict(v)
                    row.setdefault(key_name, k)
                else:
                    row = {key_name: k, "value": v}
                out.append(row)
            return out
        return [obj]
    return [{"value": obj}]


def write_ndjson(path, rows_iter):
    path.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    with path.open("w", encoding="utf-8", newline="\n") as f:
        for row in rows_iter:
            f.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")))
            f.write("\n")
            n += 1
    return n


def convert(src, dst, key_name):
    doc = json.loads(Path(src).read_text(encoding="utf-8"))
    return write_ndjson(Path(dst), rows(doc, key_name))


def build_index_map(src, dst):
    """One row per hadith: {"i","id","n","s","e"} plus optional "c","l".

    The pair lists that shipped before carried position only, so any lookup by
    hadith number, lidwa id or chapter meant scanning the whole file — no
    advantage over plain JSON. This map is content-keyed, and being NDJSON it can
    itself be fetched with Range.
    """
    dst.parent.mkdir(parents=True, exist_ok=True)
    n = pos = 0
    with Path(src).open("rb") as f, dst.open("w", encoding="utf-8", newline="\n") as out:
        for line in f:
            if not line.strip():
                continue
            length = len(line)              # raw bytes, newline included
            row = json.loads(line)
            entry = {
                "i": n + 1,                 # 1-based row ordinal
                "id": row.get("id", n + 1),
                "n": row.get("hadith_number"),
                "s": pos,
                "e": pos + length - 1,      # inclusive, newline included
            }
            if row.get("chapter_id") is not None:
                entry["c"] = row["chapter_id"]
            if row.get("lidwa_id"):
                entry["l"] = row["lidwa_id"]
            out.write(json.dumps(entry, ensure_ascii=False, separators=(",", ":")) + "\n")
            pos += length
            n += 1
    return n


def normalize_tabarani(src, dst):
    """Rebuild tabarani from the complete fawaz edition into the site row shape.

    The file currently served is a 13,555-row Shamela extract using
    `hadithnumber` / `text_ara`. The registry declares 21,850, and
    `data/editions/ara-tabarani.ndjson` has exactly that many rows.
    Returns (row_count, [[start,len], ...]) so the byte index matches the bytes
    actually written.
    """
    dst.parent.mkdir(parents=True, exist_ok=True)
    idx, n, pos = [], 0, 0
    with Path(src).open(encoding="utf-8") as f, dst.open("wb") as out:
        for line in f:
            if not line.strip():
                continue
            r = json.loads(line)
            num = r.get("hadithnumber", r.get("arabicnumber"))
            grades = r.get("grades")
            if isinstance(grades, str):
                try:
                    grades = json.loads(grades)
                except ValueError:
                    grades = []
            ref = r.get("reference")
            if isinstance(ref, str):
                try:
                    ref = ast.literal_eval(ref)
                except (ValueError, SyntaxError):
                    ref = None
            text = r.get("text") or ""
            row = {
                "id": n + 1,
                "book": "tabarani",
                "hadith_number": None if num is None else str(num),
                "arabic_number": None if num is None else str(num),
                "text_ar": text,
                "grades": grades or [],
                "reference": ref,
                "translations": {"ar": [{"source": "fawaz", "text": text}]},
            }
            blob = (json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n").encode("utf-8")
            out.write(blob)
            idx.append([pos, len(blob)])
            pos += len(blob)
            n += 1
    return n, idx


CORE9 = ["bukhari", "muslim", "abudawud", "tirmidhi", "nasai",
         "ibnmajah", "malik", "ahmad", "darimi"]


def lidwa_master(book, old_path, num_map, dst):
    """Canonical default rows built from the lidwa source itself.

    Every field that defines numbering and chapter comes from this file or from
    the D1 map keyed by the same lidwa number. No international numbering is
    involved. Existing master rows are used only for richer metadata (grade,
    sanad, etc.) matched on the identical number.
    """
    src = DATA / "sources" / "lidwa" / f"{book}.ndjson"
    if not src.exists():
        return None
    old = {}
    if Path(old_path).exists():
        with open(old_path, encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                r = json.loads(line)
                try:
                    old[str(int(r["hadith_number"]))] = r
                except (KeyError, TypeError, ValueError):
                    pass
    dst.parent.mkdir(parents=True, exist_ok=True)
    stats = {}
    n = 0
    with open(src, encoding="utf-8") as f, dst.open("w", encoding="utf-8", newline="\n") as out:
        for line in f:
            if not line.strip():
                continue
            r = json.loads(line)
            try:
                num = int(str(r.get("hadith_number", "")).strip())
            except (TypeError, ValueError):
                continue
            prior = old.get(str(num), {})
            rawis = r.get("rawis") or []
            if isinstance(rawis, str):
                try:
                    rawis = ast.literal_eval(rawis)
                except (ValueError, SyntaxError):
                    rawis = []
            text_ar = r.get("text_ar") or prior.get("text_ar") or ""
            text_id = r.get("text_id") or prior.get("text_id") or ""
            text_en = r.get("text_en") or prior.get("text_en") or ""
            row = {
                "id": num,
                "book": book,
                "hadith_number": str(num),
                "lidwa_id": [str(num)],
                "text_ar": text_ar,
                "text_id": text_id,
                "text_en": text_en,
                "rawis": rawis,
                "translations": {"ar": [{"source": "lidwa", "text": text_ar}],
                                 "id": [{"source": "lidwa", "text": text_id}]},
            }
            if text_en:
                row["translations"]["en"] = [{"source": "fawaz", "text": text_en}]
            for key in ("grade", "grade_id", "gradings", "status", "elevation", "source"):
                if key in prior:
                    row[key] = prior[key]
            kitab = num_map.get(num)
            if kitab is not None:
                row["chapter_id"] = str(kitab)
                st = stats.setdefault(str(kitab), [None, None, 0])
                st[0] = num if st[0] is None else min(st[0], num)
                st[1] = num if st[1] is None else max(st[1], num)
                st[2] += 1
            out.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
            n += 1
    return n, stats


def edition_reference_map(book):
    """hadith number -> kitab/book number from the international edition."""
    p = DATA / "editions" / f"ara-{book}.ndjson"
    edition_rows = None
    if p.exists():
        edition_rows = (json.loads(line) for line in open(p, encoding="utf-8") if line.strip())
    else:
        p = DATA / "editions" / f"ara-{book}.json"
        if p.exists():
            doc = json.loads(p.read_text(encoding="utf-8"))
            edition_rows = doc.get("hadiths", []) if isinstance(doc, dict) else doc
    refs = {}
    for r in (edition_rows or []):
        num = r.get("hadithnumber", r.get("hadith_number"))
        if num is None:
            continue
        ref = r.get("reference")
        if isinstance(ref, str):
            try:
                ref = ast.literal_eval(ref)
            except (ValueError, SyntaxError):
                ref = None
        if isinstance(ref, dict) and ref.get("book") is not None:
            refs[str(num)] = str(ref["book"])
    return refs


def international_master(book, src, dst):
    """Second dataset: existing international rows, chapter from its own edition."""
    refs = edition_reference_map(book)
    dst.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    with open(src, encoding="utf-8") as f, dst.open("w", encoding="utf-8", newline="\n") as out:
        for line in f:
            if not line.strip():
                continue
            r = json.loads(line)
            r.pop("chapter_id", None)
            num = str(r.get("hadith_number", "")).strip()
            if num in refs:
                r["chapter_id"] = refs[num]
            out.write(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n")
            n += 1
    return n, refs


DB = ROOT / ".dump" / "hadeeth.sqlite"


def load_bab_maps():
    """book -> {lidwa hadith number: kitab number}, book -> {kitab: name}.

    The shipped rows carry ``lidwa_id`` and nothing chapter-shaped. D1's
    ``hadith_bab`` is the only real chapter mapping in the project; the
    ``data/chapters/*.json`` files were generated wrong (every entry claimed
    hadith_start 2 / hadith_end 97), so ranges are recomputed from the rows.
    """
    if not DB.exists():
        return {}, {}
    conn = sqlite3.connect(str(DB))
    num_map, names = {}, {}
    for book, num, kitab in conn.execute(
            "select book_id, hadith_number, kitab_number from hadith_bab"):
        num_map.setdefault(book, {})[int(num)] = int(kitab)
    for book, kitab, name in conn.execute(
            "select book_id, kitab_number, kitab_name from kitab"):
        names.setdefault(book, {})[int(kitab)] = name
    conn.close()
    return num_map, names


def add_chapter_ids(src, dst, num_map):
    """Rewrite a master file with chapter_id set, and return per-chapter stats."""
    dst.parent.mkdir(parents=True, exist_ok=True)
    stats = {}
    n = 0
    with open(src, encoding="utf-8") as f, dst.open("wb") as out:
        for line in f:
            if not line.strip():
                continue
            r = json.loads(line)
            lid = r.get("lidwa_id")
            ids = lid if isinstance(lid, list) else ([lid] if lid not in (None, "") else [])
            kitab = None
            for i in ids:
                s = str(i).strip()
                if s.lstrip("-").isdigit() and int(s) in num_map:
                    kitab = num_map[int(s)]
                    break
            if kitab is None:
                try:
                    kitab = num_map.get(int(str(r.get("hadith_number", "")).strip()))
                except (TypeError, ValueError):
                    kitab = None
            if kitab is not None:
                r["chapter_id"] = str(kitab)
                try:
                    num = int(r.get("hadith_number"))
                except (TypeError, ValueError):
                    num = None
                st = stats.setdefault(kitab, [None, None, 0])
                if num is not None:
                    st[0] = num if st[0] is None else min(st[0], num)
                    st[1] = num if st[1] is None else max(st[1], num)
                st[2] += 1
            out.write((json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n").encode("utf-8"))
            n += 1
    return n, stats


def convert_chapter_ranges(src, dst):
    """Convert a chapter table, accepting first_hadith/last_hadith as well as
    hadith_start/hadith_end, and deriving the count from the range."""
    doc = json.loads(Path(src).read_text(encoding="utf-8"))
    meta = {k: v for k, v in doc.items() if k != "chapters"} if isinstance(doc, dict) and "chapters" in doc else {}
    out = []
    for i, c in enumerate(rows(doc, "chapter_number"), 1):
        if not isinstance(c, dict):
            continue
        row = dict(c)
        try:
            lo = int(str(row.get("hadith_start", row.get("first_hadith"))).strip())
            hi = int(str(row.get("hadith_end", row.get("last_hadith"))).strip())
        except (TypeError, ValueError):
            lo = hi = None
        if lo is not None:
            row.setdefault("book_id", meta.get("book_id"))
            row["hadith_start"] = lo
            row["hadith_end"] = hi
            row.setdefault("hadith_count", max(0, hi - lo + 1))
            if row.get("chapter_number") is None:
                row["chapter_number"] = row.get("id", i)
            row.setdefault("title_en", row.get("title") or "")
            row.setdefault("title_id", row.get("title") or "")
        for k in ("first_hadith", "last_hadith", "title"):
            if k in row and k not in ("title_en", "title_id"):
                row.pop(k, None)
        out.append(row)
    write_ndjson(dst, out)
    return len(out)


def scan_row_chapters(src):
    """Chapter stats from the rows themselves, for books whose source file has
    no kitab table: {chapter_id: [min_number, max_number, count]}."""
    stats = {}
    if not Path(src).exists():
        return stats
    with open(src, encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            r = json.loads(line)
            cid = r.get("chapter_id")
            if cid is None or str(cid).strip() == "":
                continue
            try:
                num = int(str(r.get("hadith_number", "")).strip())
            except (TypeError, ValueError):
                num = None
            st = stats.setdefault(str(cid), [None, None, 0])
            if num is not None:
                st[0] = num if st[0] is None else min(st[0], num)
                st[1] = num if st[1] is None else max(st[1], num)
            st[2] += 1
    return stats


def build_chapters(book, stats, names, existing, dst):
    """One row per kitab, with ranges and counts taken from the shipped rows."""
    old = {}
    if existing.exists():
        for e in rows(json.loads(existing.read_text(encoding="utf-8")), "chapter_number"):
            try:
                old[int(e.get("chapter_number"))] = e
            except (TypeError, ValueError):
                pass
    out = []
    stats = {k: v for k, v in stats.items() if v[2] > 0}
    single = len(stats) == 1
    for kitab in sorted(stats, key=lambda k: int(k) if str(k).lstrip("-").isdigit() else 0):
        start, end, count = stats[kitab]
        key = int(kitab) if str(kitab).lstrip("-").isdigit() else kitab
        prev = old.get(key, {})
        fallback_id = "Semua Hadits" if single else f"Kitab {kitab}"
        fallback_en = "All Hadiths" if single else f"Chapter {kitab}"
        out.append({
            "book_id": book,
            "id": f"{book}_c{kitab}",
            "chapter_number": key,
            "title_id": names.get(key) or prev.get("title_id") or fallback_id,
            "title_en": prev.get("title_en") or ("All Hadiths" if single else ""),
            "title_ar": prev.get("title_ar") or "",
            "hadith_start": start,
            "hadith_end": end,
            "hadith_count": count,
        })
    write_ndjson(dst, out)
    return len(out)


def build():
    if OUT.exists():
        for p in OUT.rglob("*"):
            if p.is_file():
                p.unlink()
    OUT.mkdir(parents=True, exist_ok=True)

    manifest = []

    def add(path, key):
        manifest.append({
            "path": Path(path).relative_to(ROOT).as_posix(),
            "key": key,
            "bytes": os.path.getsize(path),
            "ct": CT,
        })

    report = []

    # 1. master hadith NDJSON. Books with a D1 chapter map get chapter_id
    #    injected (rewritten); the rest stay byte-identical.
    num_map, kitab_names = load_bab_maps()
    counts = {}
    chap_stats = {}
    for p in sorted(glob.glob(str(DATA / "api" / "*.ndjson"))):
        name = Path(p).name
        book = name[: -len(".ndjson")]
        if book == "tabarani" or book.startswith("topics"):
            continue
        if book in CORE9:
            built = lidwa_master(book, p, num_map.get(book, {}), OUT / "api" / name)
            if built:
                counts[book], chap_stats[book] = built
                add(OUT / "api" / name, f"api/{name}")
                report.append((f"api/{name}", counts[book], f"lidwa, chapters {len(chap_stats[book])}"))
                fz_dst = OUT / "api" / "fawaz" / name
                fz_n, fz_refs = international_master(book, p, fz_dst)
                add(fz_dst, f"api/fawaz/{name}")
                report.append((f"api/fawaz/{name}", fz_n, f"international, refs {len(fz_refs)}"))
                continue
        if book in num_map and num_map[book]:
            dst = OUT / "api" / name
            n, stats = add_chapter_ids(p, dst, num_map[book])
            chap_stats[book] = stats
            add(dst, f"api/{name}")
            counts[book] = n
            report.append((f"api/{name}", n, f"chapters {len(stats)}"))
        else:
            add(p, f"api/{name}")
            counts[book] = sum(1 for _ in open(p, "rb"))
            report.append((f"api/{name}", "-", counts[book]))

    # 1b. tabarani rebuilt from the complete fawaz edition (21,850 rows).
    #     Its chapter table is expressed as first_hadith/last_hadith, so the
    #     number->chapter map is built from those ranges and injected here.
    dst = OUT / "api" / "tabarani.ndjson"
    n_tab, _ = normalize_tabarani(DATA / "editions" / "ara-tabarani.ndjson", dst)
    tab_ranges = {}
    tab_src = DATA / "chapters" / "tabarani.json"
    if tab_src.exists():
        tdoc = json.loads(tab_src.read_text(encoding="utf-8"))
        for c in rows(tdoc, "chapter_number"):
            if not isinstance(c, dict):
                continue
            try:
                cid = str(c.get("chapter_number", c.get("id")))
                lo = int(str(c.get("first_hadith", c.get("hadith_start"))).strip())
                hi = int(str(c.get("last_hadith", c.get("hadith_end"))).strip())
            except (TypeError, ValueError):
                continue
            for nn in range(lo, hi + 1):
                tab_ranges[nn] = cid
    if tab_ranges:
        rewritten = []
        with open(dst, encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                r = json.loads(line)
                try:
                    cid = tab_ranges.get(int(str(r.get("hadith_number", "")).strip()))
                except (TypeError, ValueError):
                    cid = None
                if cid is not None:
                    r["chapter_id"] = cid
                rewritten.append(r)
        with open(dst, "w", encoding="utf-8", newline="\n") as out:
            for r in rewritten:
                out.write(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n")
    add(dst, "api/tabarani.ndjson")
    counts["tabarani"] = n_tab
    report.append(("api/tabarani.ndjson", n_tab, f"chapters {len(set(tab_ranges.values())) if tab_ranges else 0}"))

    # 2. content-keyed map, one row per hadith: ordinal, id, number, byte range.
    #    Replaces the bare [start,len] pair lists, which were position-only and
    #    satisfied none of the lookup paths (number, lidwa id, chapter).
    for local, key in [(m["path"], m["key"]) for m in manifest
                       if m["key"].startswith("api/") and m["key"].endswith(".ndjson")
                       and not m["key"].endswith("_index.ndjson")]:
        book = Path(key).stem
        folder = key.rsplit("/", 1)[0] if key.count("/") > 1 else "api"
        dst = OUT / folder / f"{book}_index.ndjson"
        n = build_index_map(ROOT / local, dst)
        add(dst, f"{folder}/{book}_index.ndjson")
        report.append((f"{folder}/{book}_index.ndjson", n, "-"))

    # 3. book registry — both counts are set from the rows actually shipped, so
    #    the registry can never advertise a number the file does not contain
    books = json.loads((DATA / "books_v2.json").read_text(encoding="utf-8"))
    for b in books:
        actual = counts.get(b.get("id"))
        if actual is not None:
            b["hadiths_count"] = actual
            b["total_hadiths"] = actual
    dst = OUT / "books.ndjson"
    write_ndjson(dst, books)
    add(dst, "books.ndjson")
    report.append(("books.ndjson", len(books), "-"))

    # small bootstrap: same rows minus the verbose fields
    boot = [{k: b[k] for k in ("id", "title_ar", "title_en", "title_id", "author_en",
                               "author_id", "total_hadiths", "hadiths_count",
                               "total_chapters", "grade_summary", "order_index")
            if k in b} for b in books]
    dst = OUT / "catalog.ndjson"
    write_ndjson(dst, boot)
    add(dst, "catalog.ndjson")
    report.append(("catalog.ndjson", len(boot), "-"))

    # 4. chapters — rebuilt from the shipped rows so ranges and counts can never
    #    disagree with the file they point at. Priority: D1 kitab map (canonical),
    #    then the book's own chapter_id column, then the legacy source file, then
    #    a single "all hadiths" chapter for books that carry no chapter data.
    def shipped_path(book):
        rewritten = OUT / "api" / f"{book}.ndjson"
        return rewritten if rewritten.exists() else DATA / "api" / f"{book}.ndjson"

    def number_span(src):
        lo = hi = None
        count = 0
        if not Path(src).exists():
            return None
        with open(src, encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                r = json.loads(line)
                count += 1
                try:
                    num = int(str(r.get("hadith_number", "")).strip())
                except (TypeError, ValueError):
                    continue
                lo = num if lo is None else min(lo, num)
                hi = num if hi is None else max(hi, num)
        return [lo, hi, count]

    for book in sorted(counts):
        src_chapters = DATA / "chapters" / f"{book}.json"
        dst = OUT / "chapters" / f"{book}.ndjson"
        row_stats = scan_row_chapters(shipped_path(book))
        if book in chap_stats and chap_stats[book]:
            n = build_chapters(book, chap_stats[book], kitab_names.get(book, {}), src_chapters, dst)
        elif row_stats:
            n = build_chapters(book, row_stats, kitab_names.get(book, {}), src_chapters, dst)
        elif src_chapters.exists():
            n = convert_chapter_ranges(src_chapters, dst)
        else:
            span = number_span(shipped_path(book)) or [None, None, 0]
            n = build_chapters(book, {"1": span}, {}, src_chapters, dst)
        add(dst, f"chapters/{book}.ndjson")
        report.append((f"chapters/{book}.ndjson", n, "-"))
        if book in CORE9:
            fz_src = OUT / "api" / "fawaz" / f"{book}.ndjson"
            if fz_src.exists():
                fz_stats = scan_row_chapters(fz_src)
                if not fz_stats:
                    span = number_span(fz_src) or [None, None, 0]
                    fz_stats = {"1": span}
                fz_dst = OUT / "chapters" / "fawaz" / f"{book}.ndjson"
                n_fz = build_chapters(book, fz_stats, kitab_names.get(book, {}), src_chapters, fz_dst)
                add(fz_dst, f"chapters/fawaz/{book}.ndjson")
                report.append((f"chapters/fawaz/{book}.ndjson", n_fz, "-"))

    # 5. lidwa chapters
    for p in sorted(glob.glob(str(DATA / "lidwa-chapters" / "*.json"))):
        book = Path(p).stem
        doc = json.loads(Path(p).read_text(encoding="utf-8"))
        inner = doc.get("chapters", doc) if isinstance(doc, dict) else doc
        meta = {k: v for k, v in doc.items() if k != "chapters"} if isinstance(doc, dict) else {}
        dst = OUT / "lidwa-chapters" / f"{book}.ndjson"
        write_ndjson(dst, ({**meta, **r} if meta else r for r in rows(inner, "chapter_number")))
        n = sum(1 for _ in dst.open("rb"))
        add(dst, f"lidwa-chapters/{book}.ndjson")
        report.append((f"lidwa-chapters/{book}.ndjson", n, "-"))

    # 6. narrators — the outer key of the source dict IS the narrator id; the
    #    inner "id" field is usually an empty string, so carry the key explicitly
    src = DATA / "rawis" / "active_rawis.min.json"
    dst = OUT / "rawis" / "rawis.ndjson"
    doc = json.loads(src.read_text(encoding="utf-8"))
    dst.parent.mkdir(parents=True, exist_ok=True)
    with dst.open("w", encoding="utf-8", newline="\n") as out:
        n = 0
        for k, v in doc.items():
            row = {"rawi_id": k}
            if isinstance(v, dict):
                row.update(v)
            else:
                row["value"] = v
            out.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
            n += 1
    add(dst, "rawis/rawis.ndjson")
    report.append(("rawis/rawis.ndjson", n, "-"))

    # 7. link graph -> edge list
    doc = json.loads((DATA / "link_graph.json").read_text(encoding="utf-8"))
    edges = doc.get("fawaz_to_lidwa", doc)
    dst = OUT / "link_graph.ndjson"
    write_ndjson(dst, ({"fawaz_id": k, "lidwa_id": v} for k, v in edges.items()))
    n = sum(1 for _ in dst.open("rb"))
    add(dst, "link_graph.ndjson")
    report.append(("link_graph.ndjson", n, "-"))

    # 8. misc singletons
    for name in ("mapping-stats.json", "hotd.json"):
        p = DATA / name
        if not p.exists():
            continue
        doc = json.loads(p.read_text(encoding="utf-8"))
        key = name.replace("-", "_").replace(".json", "") + ".ndjson"
        dst = OUT / key
        write_ndjson(dst, rows(doc, "section"))
        n = sum(1 for _ in dst.open("rb"))
        add(dst, key)
        report.append((key, n, "-"))

    # 9. topics (already NDJSON)
    p = DATA / "api" / "topics_metadata.ndjson"
    if p.exists():
        dst = OUT / "topics.ndjson"
        dst.write_bytes(p.read_bytes())
        add(dst, "topics.ndjson")
        report.append(("topics.ndjson", sum(1 for _ in open(p, "rb")), "-"))

    # 10. topic index — one row per (topic, book), so a topic page reads one
    #     small object instead of the whole 790 KB tree
    tsrc = DATA / "api" / "topics_index.json"
    if tsrc.exists():
        doc = json.loads(tsrc.read_text(encoding="utf-8"))
        out_rows = []
        for tid, t in (doc.get("topics") or {}).items():
            for book, nums in (t.get("books") or {}).items():
                out_rows.append({"t": int(tid), "b": book, "n": nums})
        dst = OUT / "topics_index.ndjson"
        write_ndjson(dst, out_rows)
        add(dst, "topics_index.ndjson")
        report.append(("topics_index.ndjson", len(out_rows), "-"))

    # 11. syarah — commentary corpus keyed by Dorar anchor, plus the subset
    #     that a confident text match ties to a shipped hadith number
    import syarah_build
    s_manifest, s_report = syarah_build.build(OUT)
    manifest += s_manifest
    report += s_report

    # 12. links + edition metadata — the detail page reads these to resolve a
    #     record across editions. Small enough to ship whole, one object each.
    links_dir = DATA / "links"
    if links_dir.is_dir():
        for path in sorted(links_dir.glob("*.json")):
            doc = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(doc, dict):
                out = [{"k": k, "v": v} for k, v in doc.items()]
            elif isinstance(doc, list):
                out = doc
            else:
                continue
            dst = OUT / "links" / f"{path.stem}.ndjson"
            dst.parent.mkdir(parents=True, exist_ok=True)
            write_ndjson(dst, out)
            add(dst, f"links/{path.stem}.ndjson")
            report.append((f"links/{path.stem}.ndjson", len(out), "-"))

    meta_src = DATA / "meta" / "fawaz_editions.json"
    if meta_src.exists():
        doc = json.loads(meta_src.read_text(encoding="utf-8"))
        if isinstance(doc, list):
            out = doc
        else:
            # keyed by book, each holding a `collection` of editions: flatten so
            # one NDJSON row is one edition, which is what the reader iterates
            out = [dict(e, book_id=book) for book, payload in doc.items()
                   for e in (payload.get("collection") or [])]
        dst = OUT / "meta" / "fawaz_editions.ndjson"
        dst.parent.mkdir(parents=True, exist_ok=True)
        write_ndjson(dst, out)
        add(dst, "meta/fawaz_editions.ndjson")
        report.append(("meta/fawaz_editions.ndjson", len(out), "-"))

    write_ndjson(MANIFEST, manifest)
    total = sum(m["bytes"] for m in manifest)
    print(f"build: {len(manifest)} objects, {total/1e6:.2f} MB -> export_site/")
    for k, n, extra in report:
        print(f"  {k:44s} rows={n}{(' lines=' + str(extra)) if extra != '-' else ''}")
    return manifest


# ------------------------------------------------------------------- upload

def load_manifest():
    if not MANIFEST.exists():
        raise SystemExit("no manifest — run: python scripts/site_r2.py build")
    return [json.loads(l) for l in MANIFEST.read_text(encoding="utf-8").splitlines() if l]


def put(item, auth):
    path = ROOT / item["path"]
    size = item["bytes"]
    h = {"Authorization": auth, "Content-Type": item["ct"]}
    last = None
    for attempt in range(1, 6):
        try:
            with path.open("rb") as fh:
                r = requests.put(f"{API}/{item['key']}", headers=h, data=fh, timeout=1800)
            if r.status_code in (200, 201):
                got = r.json().get("result", {}).get("size")
                if got is not None and int(got) != size:
                    raise RuntimeError(f"size mismatch local={size} r2={got}")
                return
            if 500 <= r.status_code < 600:
                last = f"HTTP {r.status_code}"
            else:
                raise RuntimeError(f"HTTP {r.status_code}: {r.text[:250]}")
        except requests.RequestException as exc:
            last = str(exc)[:180]
        time.sleep(2 ** attempt)
        print(f"    retry {attempt}/5 {item['key']} ({last})", flush=True)
    raise RuntimeError(f"failed {item['key']}: {last}")


def remote_map():
    """key -> (size, etag) for everything currently in the bucket."""
    auth = {"Authorization": f"Bearer {token()}"}
    base = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT}/r2/buckets/{BUCKET}/objects"
    out, cur = {}, None
    while True:
        p = {"per_page": 1000}
        if cur:
            p["cursor"] = cur
        r = requests.get(base, headers=auth, params=p, timeout=120).json()
        for o in r.get("result", []):
            out[o["key"]] = (int(o["size"]), (o.get("etag") or "").strip('"'))
        cur = (r.get("result_info") or {}).get("cursor")
        if not cur:
            break
    return out


def md5_of(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def upload():
    items = load_manifest()
    items.sort(key=lambda m: (m["bytes"] > 5_000_000, m["key"]))  # small files first
    remote = remote_map()
    auth = f"Bearer {token()}"
    ok = bad = skip = 0
    sent = 0
    t0 = time.time()
    for i, item in enumerate(items, 1):
        rmt = remote.get(item["key"])
        if rmt and rmt[0] == item["bytes"] and rmt[1] == md5_of(ROOT / item["path"]):
            skip += 1
            continue
        try:
            put(item, auth)
            ok += 1
            sent += item["bytes"]
        except Exception as exc:
            bad += 1
            print(f"  FAIL {item['key']}: {exc}", flush=True)
        if i % 15 == 0 or i == len(items):
            el = time.time() - t0
            print(f"  [{i}/{len(items)}] {sent/1e6:.1f} MB  {sent/el/1e6:.1f} MB/s  "
                  f"{ok} ok  {bad} failed", flush=True)
    print(f"upload: {ok}/{len(items)} uploaded, {skip} unchanged/skipped, "
          f"{sent/1e6:.2f} MB, {time.time()-t0:.1f}s, {bad} failed")
    if bad:
        raise SystemExit(1)

    # prune: anything in the bucket that the manifest no longer produces
    wanted = {i["key"] for i in items}
    stale = sorted(set(remote) - wanted)
    if stale:
        base = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT}/r2/buckets/{BUCKET}/objects"
        killed = 0
        for key in stale:
            r = requests.delete(f"{base}/{key}", headers={"Authorization": auth}, timeout=120)
            if r.status_code in (200, 204):
                killed += 1
            else:
                print(f"  prune FAIL {key}: HTTP {r.status_code}")
        print(f"prune: {killed}/{len(stale)} stale objects deleted")
        for key in stale:
            print(f"  removed {key}")


# ------------------------------------------------------------------- verify

def list_keys():
    auth = {"Authorization": f"Bearer {token()}"}
    base = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT}/r2/buckets/{BUCKET}/objects"
    out, cur = {}, None
    while True:
        p = {"per_page": 1000}
        if cur:
            p["cursor"] = cur
        r = requests.get(base, headers=auth, params=p, timeout=120).json()
        for o in r.get("result", []):
            out[o["key"]] = int(o["size"])
        cur = (r.get("result_info") or {}).get("cursor")
        if not cur:
            break
    return out


def verify():
    items = load_manifest()
    remote = list_keys()
    missing = [m["key"] for m in items if m["key"] not in remote]
    wrong = [(m["key"], m["bytes"], remote[m["key"]])
             for m in items if m["key"] in remote and remote[m["key"]] != m["bytes"]]
    print(f"objects in batch: {len(items)}   present in R2: {len(items)-len(missing)}")
    print(f"missing: {len(missing)}   size-mismatch: {len(wrong)}")
    for k in missing[:10]:
        print("  MISSING", k)
    for k, a, b in wrong[:10]:
        print(f"  SIZE {k} local={a} r2={b}")

    # byte-identical content check on one converted file + one small sidecar
    print("\ncontent checks:")
    for key in ("catalog.ndjson", "books.ndjson"):
        local = (OUT / key).read_bytes()
        r = requests.get(f"{PUBLIC}/{key}", timeout=120)
        same = r.status_code == 200 and r.content == local
        print(f"  {key:26s} HTTP {r.status_code}  sha256 match={same}")

    # THE load-bearing check: HTTP Range on a master NDJSON
    print("\nrange check (api/bukhari.ndjson):")
    src = OUT / "api" / "bukhari.ndjson"
    with src.open("rb") as f:
        head = f.read(401)
    r = requests.get(f"{PUBLIC}/api/bukhari.ndjson",
                     headers={"Range": "bytes=0-400"}, timeout=120)
    print(f"  status={r.status_code}  bytes={len(r.content)}  identical={r.content == head}")
    ok_range = r.status_code == 206 and r.content == head

    # index alignment: three map entries must reconstruct their records
    print("\nindex alignment (api/bukhari_index.ndjson):")
    lines = (OUT / "api" / "bukhari_index.ndjson").read_text().splitlines()
    picks = [json.loads(lines[0]), json.loads(lines[len(lines) // 2]), json.loads(lines[-1])]
    ok_idx = True
    for e in picks:
        start, end = e["s"], e["e"]
        r = requests.get(f"{PUBLIC}/api/bukhari.ndjson",
                         headers={"Range": f"bytes={start}-{end}"}, timeout=120)
        rec = json.loads(r.content)
        same = rec.get("hadith_number") == e["n"] and str(rec.get("id")) == str(e["id"])
        ok_idx = ok_idx and r.status_code == 206 and same
        print(f"  n={e['n']:<6} id={e['id']:<6} [{start},{end}] status={r.status_code} record matches={same}")

    print("\nRESULT:", "PASS" if not missing and not wrong and ok_range and ok_idx else "FAIL")
    return not missing and not wrong and ok_range and ok_idx


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("step", choices=["build", "upload", "verify"])
    a = ap.parse_args()
    {"build": build, "upload": upload, "verify": verify}[a.step]()


if __name__ == "__main__":
    main()

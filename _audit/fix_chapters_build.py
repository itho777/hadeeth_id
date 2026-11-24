#!/usr/bin/env python3
"""Move the chapter-sidecar repairs into the builder so `build()` reproduces them.

The 2026-11-20 fix lived only in export_site/chapters/*.ndjson, which
`site_r2.py build` deletes and regenerates: muntaqa lost its 1,109 Arabic
titles, tabarani regained 294 count/range conflicts, and the four
pseudo-chapter books lost the Arabic book title.

Every replacement is asserted; a partial match aborts without writing.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "scripts" / "site_r2.py"

raw = TARGET.read_bytes().decode("utf-8")
CRLF = "\r\n" in raw
text = raw.replace("\r\n", "\n")


def sub(old, new, expect=1):
    global text
    n = text.count(old)
    if n != expect:
        raise SystemExit(f"expected {expect} occurrence(s), found {n}:\n{old[:200]}")
    text = text.replace(old, new)


# ---------------------------------------------------------------- scan_row_chapters
sub(
    '''def scan_row_chapters(src):
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
''',
    '''def scan_row_chapters(src):
    """Chapter stats from the rows themselves, for books whose source file has
    no kitab table: {chapter_id: [min_number, max_number, row_count, distinct]}.

    `distinct` counts different hadith numbers, which is what a chapter holds;
    `row_count` counts shipped rows, which can repeat a number across editions.
    Reporting the row count as the chapter size is the defect this guards.
    """
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
            st = stats.setdefault(str(cid), [None, None, 0, set()])
            if num is not None:
                st[0] = num if st[0] is None else min(st[0], num)
                st[1] = num if st[1] is None else max(st[1], num)
                st[3].add(num)
            st[2] += 1
    for st in stats.values():
        st[3] = len(st[3])
    return stats
''',
)

# ---------------------------------------------------------------- build_chapters
sub(
    '''def build_chapters(book, stats, names, existing, dst):
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
''',
    '''def build_chapters(book, stats, names, existing, dst, book_title_ar=""):
    """One row per kitab, with ranges and counts taken from the shipped rows.

    `old` is keyed by the raw chapter number as a string: id-keyed books carry
    ids like ``turath:1218:heading:0073`` and an int() cast silently dropped
    every title they had. `hadith_count` is the number of distinct hadith the
    chapter contains; the shipped row count rides alongside as `row_count`.
    """
    old = {}
    if existing.exists():
        for e in rows(json.loads(existing.read_text(encoding="utf-8")), "chapter_number"):
            cid = e.get("chapter_number")
            if cid is None:
                continue
            old[str(cid)] = e
    out = []
    stats = {k: v for k, v in stats.items() if v[2] > 0}
    single = len(stats) == 1

    def sort_key(k):
        prev = old.get(str(k), {})
        d = prev.get("display_number")
        if isinstance(d, (int, float)) or str(d).isdigit():
            return (0, float(d))
        return (1, int(k) if str(k).lstrip("-").isdigit() else 0)

    for kitab in sorted(stats, key=sort_key):
        st = stats[kitab]
        start, end, count = st[0], st[1], st[2]
        distinct = st[3] if len(st) > 3 else count
        key = int(kitab) if str(kitab).lstrip("-").isdigit() else kitab
        prev = old.get(str(kitab), {})
        title_ar = prev.get("title_ar") or (book_title_ar if single else "")
        # Never fall back to the raw id when an Arabic title exists: that is how
        # "Kitab turath:1218:heading:0073" reached the chapter cards.
        fallback_id = "Semua Hadits" if single else ("" if title_ar else f"Kitab {kitab}")
        row = {
            "book_id": book,
            "id": f"{book}_c{kitab}",
            "chapter_number": key,
            "title_id": names.get(key) or prev.get("title_id") or fallback_id,
            "title_en": prev.get("title_en") or ("All Hadiths" if single else ""),
            "title_ar": title_ar,
            "hadith_start": start,
            "hadith_end": end,
            "hadith_count": distinct,
        }
        if count != distinct:
            row["row_count"] = count
        if "display_number" in prev:
            row["display_number"] = prev["display_number"]
        elif single:
            row["display_number"] = "M"
        if book == "shah" and single:
            row["title_id"] = "Empat Puluh Hadits"
            row["title_en"] = "Forty Hadiths"
        out.append(row)
    write_ndjson(dst, out)
    return len(out)


def build_from_source(book, stats, source_path, dst):
    """Chapter sidecar where the source file owns the titles and the shipped
    rows own the ranges, for books whose chapter ids are strings.

    Source shape: ``{chapter_id: {"title_ar": ..., "display_number": ...}}``.
    A chapter in the source with no shipped row is skipped rather than shipped
    as an empty card.
    """
    doc = json.loads(Path(source_path).read_text(encoding="utf-8"))
    if not isinstance(doc, dict):
        raise SystemExit(f"{source_path}: expected an id-keyed object")
    out = []
    for cid, meta in doc.items():
        st = stats.get(str(cid))
        if not st or not st[2]:
            continue
        meta = meta if isinstance(meta, dict) else {}
        out.append({
            "book_id": book,
            "id": f"{book}_c{cid}",
            "chapter_number": cid,
            "title_id": "",
            "title_en": "",
            "title_ar": meta.get("title_ar") or "",
            "hadith_start": st[0],
            "hadith_end": st[1],
            "hadith_count": st[3] if len(st) > 3 else st[2],
            "row_count": st[2],
            "_display": meta.get("display_number"),
        })
    numeric = all(str(r["chapter_number"]).lstrip("-").isdigit() for r in out)
    if numeric:
        out.sort(key=lambda r: int(r["chapter_number"]))
        for i, r in enumerate(out, 1):
            r["display_number"] = i
    else:
        out.sort(key=lambda r: (0, r["_display"]) if isinstance(r["_display"], (int, float))
                 else (1, 10 ** 9))
        for i, r in enumerate(out, 1):
            r["display_number"] = r["_display"] if isinstance(r["_display"], (int, float)) else i
    for r in out:
        r.pop("_display", None)
    write_ndjson(dst, out)
    return len(out)
''',
)

# ---------------------------------------------------------------- build() loop
sub(
    '''    for book in sorted(counts):
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
''',
    '''    titles_ar = {b.get("id"): (b.get("title_ar") or "") for b in books}
    # These two carry string chapter ids and a title table of their own; the
    # id-keyed builder would drop the titles, so their source file drives.
    ID_KEYED = ("tabarani", "muntaqa")
    for book in sorted(counts):
        src_chapters = DATA / "chapters" / f"{book}.json"
        dst = OUT / "chapters" / f"{book}.ndjson"
        row_stats = scan_row_chapters(shipped_path(book))
        if book in ID_KEYED and src_chapters.exists() and row_stats:
            n = build_from_source(book, row_stats, src_chapters, dst)
        elif book in chap_stats and chap_stats[book]:
            n = build_chapters(book, chap_stats[book], kitab_names.get(book, {}), src_chapters, dst,
                               titles_ar.get(book, ""))
        elif row_stats:
            n = build_chapters(book, row_stats, kitab_names.get(book, {}), src_chapters, dst,
                               titles_ar.get(book, ""))
        elif src_chapters.exists():
            n = convert_chapter_ranges(src_chapters, dst)
        else:
            span = number_span(shipped_path(book)) or [None, None, 0]
            n = build_chapters(book, {"1": span}, {}, src_chapters, dst, titles_ar.get(book, ""))
''',
)

sub(
    '''                n_fz = build_chapters(book, fz_stats, kitab_names.get(book, {}), src_chapters, fz_dst)
''',
    '''                n_fz = build_chapters(book, fz_stats, kitab_names.get(book, {}), src_chapters, fz_dst,
                                      titles_ar.get(book, ""))
''',
)

out_bytes = text.replace("\n", "\r\n") if CRLF else text
TARGET.write_bytes(out_bytes.encode("utf-8"))
print(f"patched {TARGET} ({'CRLF' if CRLF else 'LF'})")

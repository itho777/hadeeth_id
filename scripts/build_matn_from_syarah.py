"""
build_matn_from_syarah.py — rebuild a matn book that a sharh prints inline.

Some sharhs quote the matn they comment on, with the matn's own printed number in the
margin: `N/ M - ( ... )`. When no edition of the matn exists anywhere else (no fawaz
book, no site rows), the sharh IS the source of the matn — this script reads it back out.

Scope today: `muntaqa` (Muntaqa al-Akbar as printed inside Nayl al-Awtar, Hallaq ed.,
turath 1218), 3,944 units, dense 1..3944.

Output matches the static site's matn format exactly, so the site needs no new code:

    data/matn/muntaqa.ndjson          one row per unit: id, book, hadith_number, text_ar, chapter_id
    data/matn/muntaqa_index.ndjson    {i,id,n,s,e,c} byte offsets into the above

`n` is a STRING in the site's index format (api/bukhari_index.ndjson uses "1", not 1),
because hadith numbers like 270.2 exist elsewhere in the corpus.

Usage:
  python scripts/build_matn_from_syarah.py --book muntaqa [--check]
"""
import argparse
import json
import os
import re
import sqlite3

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = "H:/Itho/2026/Project/Hadeeth/data source/Syarah From Muse"
OUT_DIR = os.path.join(ROOT, "export_site", "api")

AR_DIGITS = "٠١٢٣٤٥٦٧٨٩"


def ar_to_int(s):
    return int("".join(str(AR_DIGITS.index(ch)) for ch in s))


def int_to_ar(n):
    return "".join(AR_DIGITS[int(ch)] for ch in str(n))


GRADING = re.compile(r"\[(?:صحيح|حسن|ضعيف|صحيح لغيره|حسن لغيره|صحيح الإسناد|حسن صحيح)[^\]]*\]")


def clean_matn(t):
    """Trim a quoted matn to the matn itself.

    The page carries three tails that the bracket scan can swallow: the footnote
    rule (`_________`), the grading tag (`[صحيح]`), and the line commentary
    (`قوله: (...)`). Cut at the first of them; keep the tag, drop the rest.
    """
    t = t.split("_________")[0]
    m = GRADING.search(t)
    if m:
        t = t[:m.end()]
    else:
        m = re.search(r"\n\s*قوله\s*:", t)
        if m:
            t = t[:m.start()]
    return t.strip().strip("\u200f\u200e ")


def next_marker_re():
    return re.compile(r"[%s]+\s*/\s*[%s]+\s*-\s*" % (AR_DIGITS, AR_DIGITS))


def segment_quote(text, start, limit=8000):
    """Last resort: from the marker to the next marker, trimmed to the citation tag.

    Covers the three shapes the paren scanner misses: the matn in double quotes,
    the matn closed only by its grading tag (`[صحيح].`), and the matn whose closing
    bracket sits beyond the page window.
    """
    nxt = next_marker_re().search(text, start)
    seg = text[start:nxt.start() if nxt else min(len(text), start + limit)]
    seg = seg.split("_________")[0]
    tag = re.search(r"\[(?:صحيح|حسن|ضعيف|صحيح لغيره|حسن لغيره)[^\]]*\]", seg)
    if tag:
        seg = seg[:tag.end()]
    seg = seg.strip().strip("\u200f\u200e ")
    # a trailing commentary clause is what follows the closing quotation mark
    return seg


def best_quote(text, start):
    """Try the strict bracket cut first, then the segment cut; keep the longer sane one."""
    q = cut_quote(text, start)
    s = segment_quote(text, start)
    if q and len(q) >= 40 and (not s or len(s) > len(q) * 3):
        return q
    if s and len(s) >= 40:
        return s
    return q if q and len(q) >= 40 else None

def cut_quote(text, start, limit=8000):
    """Cut the quotation beginning at `start` at its closing ")".

    Footnote markers like `(^١)` are skipped rather than treated as the closing
    bracket: a 16-character "matn" in an earlier run was exactly that mistake.
    """
    i, depth, stop = start, 0, min(len(text), start + limit)
    while i < stop:
        ch = text[i]
        if ch == "(":
            if re.match(r"\^[%s]+" % AR_DIGITS, text[i + 1:i + 8]):
                close = text.find(")", i + 1, stop)
                if close >= 0:
                    i = close + 1
                    continue
            depth += 1
        elif ch == ")":
            if depth == 0:
                return text[start:i].strip()
            depth -= 1
        i += 1
    return None


def load_pages(db_path):
    """page_index -> text_ar, in page order."""
    con = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    rows = list(con.execute(
        "SELECT page_index, text_ar FROM syarah_passages ORDER BY page_index"))
    con.close()
    return rows


def load_links(db_path):
    con = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    rows = list(con.execute(
        "SELECT source_native_number, target_page_index, source_chapter_id"
        " FROM syarah_links ORDER BY source_native_number"))
    con.close()
    return rows


def load_chapters(db_path):
    con = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    rows = list(con.execute(
        "SELECT chapter_id, page_index, title_native FROM syarah_chapters"
        " ORDER BY page_index, sequence_no"))
    con.close()
    return rows


def extract(pages):
    """Walk the concatenated page text; return {M: (matn_text, page_index, offset)}.

    The marker is `N/ M - (` with Arabic-Indic digits. The matn is inside the
    parentheses, which may themselves nest, so close on the matching bracket, not
    on the first `)`.
    """
    # one big string, with an index of where each page starts
    starts, parts, pos = [], [], 0
    for page_index, text in pages:
        starts.append((pos, page_index))
        chunk = text or ""
        parts.append(chunk)
        pos += len(chunk) + 1          # +1 for the "\n" we join with
    blob = "\n".join(parts)

    def page_of(offset):
        lo, hi = 0, len(starts) - 1
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if starts[mid][0] <= offset:
                lo = mid
            else:
                hi = mid - 1
        return starts[lo][1]

    marker = re.compile(r"([%s]+)\s*/\s*([%s]+)\s*-\s*\(" % (AR_DIGITS, AR_DIGITS))
    out, seen_dup = {}, []
    LIMIT = 8000                        # a matn quote is never longer than this
    for m in marker.finditer(blob):
        num = ar_to_int(m.group(2))
        depth, i, stop = 1, m.end(), min(len(blob), m.end() + LIMIT)
        while i < stop and depth:
            ch = blob[i]
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
            i += 1
        if depth:                       # unbalanced quote: fall back to the first ")"
            close = blob.find(")", m.end(), stop)
            if close < 0:
                continue
            i = close + 1
        text = blob[m.end():i - 1].strip()
        if not text:
            continue
        if num in out:
            seen_dup.append(num)
            continue
        out[num] = (text, page_of(m.start()), m.start())
    return out, seen_dup, blob


def chapter_for(page_index, chapters):
    """Last chapter at or before this page — that is the bab the unit sits in."""
    best = None
    for cid, cpage, _title in chapters:
        if cpage is None or cpage > page_index:
            break
        best = cid
    return best


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--book", default="muntaqa")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--package", default=None, help="package folder name if not --book")
    args = ap.parse_args()

    pkg = args.package or args.book
    pkgdir = os.path.join(SRC, pkg)
    db = os.path.join(pkgdir, f"syarah_{pkg}.db")
    if not os.path.exists(db):
        raise SystemExit(f"no package db at {db}")

    pages = load_pages(db)
    links = load_links(db)
    chapters = load_chapters(db)
    got, dups, blob = extract(pages)

    want = [n for n, _, _ in links]
    missing = [n for n in want if n not in got]

    print(f"{pkg}: {len(pages)} pages, {len(links)} links, {len(got)} matn quoted")
    print(f"  numbers covered: {len([n for n in want if n in got])}/{len(want)}")
    if dups:
        print(f"  duplicate markers ignored: {len(dups)} -> {dups[:10]}")
    if missing:
        print(f"  MISSING: {len(missing)} -> {missing[:20]}")

    # fall back: units not caught by the strict marker are read from their linked page.
    # Two shapes survive there: markers printed mid-line without an opening paren, and
    # markers whose quote is cut by the page break.
    recovered = 0
    ptext = dict(pages)
    pagemap = {num: p for num, p, _ in links}
    for n in missing:
        page = pagemap.get(n)
        text = ptext.get(page, "") or ""
        # (a) "N/ M - " with no opening paren: cut at the real closing ")"
        mark = re.search(r"[%s]+\s*/\s*%s\s*-\s*" % (AR_DIGITS, int_to_ar(n)), text)
        quote = best_quote(text, mark.end()) if mark else None
        # (b) the quote opens on this page and closes on the next
        if quote is None or len(quote) < 20:
            # the quote may close two or three pages later
            joined = "\n".join([text] + [ptext.get(page + k, "") or "" for k in (1, 2, 3)])
            mark = re.search(r"[%s]+\s*/\s*%s\s*-\s*" % (AR_DIGITS, int_to_ar(n)), joined)
            quote = best_quote(joined, mark.end()) if mark else None
        if quote and len(quote) >= 20:
            got[n] = (quote.strip(), page, -1)
            recovered += 1
    if recovered:
        print(f"  recovered from linked page (loose marker): {recovered}")

    # a strict match can still be junk: an early unbalanced ")" ends it after a few
    # words ("عَنْ [سُليم] (^١"). Re-cut those with the footnote-aware scanner.
    regrown = 0
    for n in list(got):
        text, page, _off = got[n]
        if len(text) >= 40:
            continue
        src = "\n".join([ptext.get(page + k, "") or "" for k in (0, 1, 2, 3)])
        mark = re.search(r"[%s]+\s*/\s*%s\s*-\s*" % (AR_DIGITS, int_to_ar(n)), src)
        q = best_quote(src, mark.end()) if mark else None
        if q and len(q) > len(text):
            got[n] = (q, page, _off)
            regrown += 1
    if regrown:
        print(f"  re-cut short quotes: {regrown}")

    rows = []
    for n in sorted(want):
        if n not in got:
            continue
        text, page, _off = got[n]
        text = clean_matn(text)
        if len(text) < 40:
            continue
        rows.append({
            "id": n,
            "book": args.book,
            "hadith_number": str(n),
            "lidwa_id": [],
            "chapter_id": chapter_for(page, chapters),
            "text_ar": text,
            "text_source": f"Syarah From Muse/{pkg}",
        })

    lens = sorted(len(r["text_ar"]) for r in rows)
    print(f"  rows built: {len(rows)}")
    if lens:
        print(f"  text length median {lens[len(lens)//2]}  min {lens[0]}  max {lens[-1]}")

    if args.check:
        print("check only, nothing written")
        return

    os.makedirs(OUT_DIR, exist_ok=True)
    plain = os.path.join(OUT_DIR, f"{args.book}.ndjson")
    index = os.path.join(OUT_DIR, f"{args.book}_index.ndjson")
    offset = 0
    with open(plain, "w", encoding="utf-8", newline="\n") as fh, \
         open(index, "w", encoding="utf-8", newline="\n") as ix:
        for i, r in enumerate(rows, 1):
            raw = (json.dumps(r, ensure_ascii=False) + "\n").encode("utf-8")
            fh.write(raw.decode("utf-8"))
            ix.write(json.dumps({"i": i, "id": r["id"], "n": r["hadith_number"],
                                 "s": offset, "e": offset + len(raw) - 1,
                                 "c": r["chapter_id"], "l": []},
                                ensure_ascii=False) + "\n")
            offset += len(raw)
    print(f"wrote {plain} ({offset/2**20:.2f} MiB) and {index}")


if __name__ == "__main__":
    main()

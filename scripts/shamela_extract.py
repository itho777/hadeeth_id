#!/usr/bin/env python3
"""Shamela page rows -> hadith units, with chain-based region bounding.

Ordering is file order (`sequence_num`). `page_num` is provenance only: it goes
backwards 423 times in adab and resets per volume in tabarani, so it can never
be an ordering key.

Numbering is assigned by a monotone chain: walk the units in file order keeping
an expected counter; a unit is assigned `k` when `k == expected`; a jump forward
is recorded as declared gaps; a number below `expected` is a duplicate and is
skipped. This is what separates the editorial apparatus from the hadith region,
because the apparatus re-uses the same numbers — in mustadrak 24 separate units
are numbered `1`, and exactly one of them is hadith 1 (verified against
mjna:mustadrak at token Jaccard 1.00).

Usage:
    python scripts/shamela_extract.py                    # report all books
    python scripts/shamela_extract.py mustadrak --write
    python scripts/shamela_extract.py --limit 800
"""
import json
import os
import re
import sys
from collections import Counter

PROBE = "G:/hadeeth_id/_probe"
OUT = "G:/hadeeth_id/data/sources/shamela"
SNAPSHOT = "shamela4_full_extraction_pg_2026_04_26"

AR2EN = str.maketrans("\u0660\u0661\u0662\u0663\u0664\u0665\u0666\u0667\u0668\u0669", "0123456789")
SPAN = re.compile(r"<span[^>]*data-type=['\"]title['\"][^>]*>(.*?)</span>", re.S)
MARK = re.compile(r"(?m)^[^\w\n]{0,6}([\u0660-\u0669]{1,6}|[0-9]{1,6})\s*[-\u2013\u2014][ \t]?")
SERVICE = re.compile(r"\u2997[^\u2998]{0,12}\u2998|\(\s*\u00ac\s*[\u0660-\u0669\u0030-\u0039]+\s*\)")
TAG = re.compile(r"<[^>]+>")
WS = re.compile(r"[ \t]+")
BAB = re.compile(r"\[\[BAB:.*?\]\]", re.S)

# key -> (probe dir, book_id, parts, edition, last expected number, mode)
# mode "strict": a number below the running expectation is dropped (editorial
#   apparatus re-uses the numbering — mustadrak has 24 units numbered `1` and
#   exactly one of them is hadith 1, verified against mjna at Jaccard 1.00).
# mode "keep": every unit is kept and colliding print numbers get a `#2` suffix
#   (adab: 21 repeated numbers with different texts; daruquthni: 10 places where
#   the print numbering rolls backwards and re-ascends, 4,846 units vs max 4,836).
BOOKS = {
    "adab":       ("adab",          4750, None,         "t. Abd al-Baqi",                1322, "keep"),
    "mustadrak":  ("mustadrak1268", 1268, None,         "t. al-Risala 1439H",            9018, "strict"),
    "daruquthni": ("daruquthni",    3510, None,         "Shamela 9771",                  4836, "keep"),
    "tabarani":   ("tabarani",      1484, range(1, 13), "t. Hamdi al-Salafi, vols 1-12", 13654, "strict"),
}


def clean(t):
    t = TAG.sub(" ", t)
    t = SERVICE.sub(" ", t)
    t = WS.sub(" ", t)
    return re.sub(r"\n{2,}", "\n", t).strip()


def build_stream(rows, parts=None):
    """One string, with (start, end, page_num, part, sequence_num) per source row."""
    chunks, marks, pos = [], [], 0
    for r in rows:
        p = int(r["part"]) if r.get("part") not in (None, "") else None
        if parts is not None and p is not None and p not in parts:
            continue
        body = re.sub(r"\r\n?", "\n", r["body"] or "")
        m_title = SPAN.search(body)
        if m_title and len(SPAN.sub("", body).strip()) < 40:
            body = "\n[[BAB:" + clean(m_title.group(1)) + "]]\n"
        else:
            body = SPAN.sub(lambda m: "\n[[BAB:" + clean(m.group(1)) + "]]\n", body)
        marks.append((pos, pos + len(body), r["page_num"], p, r["sequence_num"]))
        chunks.append(body)
        pos += len(body) + 1
    return "\n".join(chunks), marks


def unit_text(raw):
    """A bab heading inside a unit starts editorial matter, so the hadith ends there.

    Measured on mustadrak 12: the real hadith ends with `غير الصلاة (¬٣).`, then
    `[[BAB:ج - الظروف العلمية:]]` opens three pages of editor's prose. Keeping
    that prose dropped the twin-similarity against mjna from ~0.9 to 0.04.
    """
    m = BAB.search(raw, 20)
    if m:
        raw = raw[:m.start()]
    return clean(BAB.sub(" ", raw))


def units_from(stream, marks):
    """Split on line-start markers; carry page/part provenance onto each unit."""
    def where(off):
        lo, hi = 0, len(marks) - 1
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if marks[mid][0] <= off:
                lo = mid
            else:
                hi = mid - 1
        return marks[lo]

    units, prev, prev_num = [], 0, None
    for m in MARK.finditer(stream):
        if prev_num is not None:
            r0, r1 = where(prev), where(max(prev, m.start() - 1))
            units.append({"n": prev_num, "text": unit_text(stream[prev:m.start()]),
                          "page_from": r0[2], "page_to": r1[2], "part": r0[3],
                          "seq_from": r0[4], "seq_to": r1[4]})
        prev, prev_num = m.end(), m.group(1).translate(AR2EN)
    if prev_num is not None:
        r0, r1 = where(prev), where(len(stream) - 1)
        units.append({"n": prev_num, "text": unit_text(stream[prev:]),
                      "page_from": r0[2], "page_to": r1[2], "part": r0[3],
                      "seq_from": r0[4], "seq_to": r1[4]})
    return units


ISNAD_OPEN = re.compile(r"^(?:حدثنا|حدثني|حدثناه|أخبرنا|اخبرنا|أخبرني|أخبرناه|أنبأنا|انبانا|أنبأني|نبأنا|قال\s)")


def body_start(units):
    """Index of the first real hadith: the first `1 -` whose text opens on a chain.

    Reading order is `shamela_page_id`, and every front matter of these editions is
    numbered too, so `1 -` alone is ambiguous — the muqaddima's own first item is
    also `1 -`. The body's first hadith is the first `1 -` that opens with a
    transmission verb; everything before it is editorial apparatus.
    """
    for i, u in enumerate(units):
        if u["n"] == "1" and ISNAD_OPEN.match(BAB.sub("", u["text"]).strip()):
            return i
    for i, u in enumerate(units):
        if u["n"] == "1":
            return i
    return 0


def chain_assign(units, last):
    """Monotone chain assignment. Returns (assigned, gaps, duplicates, shortfall)."""
    assigned, gaps, dups = [], [], []
    expected = 1
    for u in units:
        k = int(u["n"])
        if k == expected:
            assigned.append(u)
            expected += 1
        elif k > expected:
            gaps.extend(range(expected, k))
            assigned.append(u)
            expected = k + 1
        else:
            dups.append(u)
    return assigned, gaps, dups, last - (expected - 1)


def report(key, limit=None, write=False):
    d, book_id, parts, edition, last, mode = BOOKS[key]
    rows = [json.loads(l) for l in open(os.path.join(PROBE, d, "pages.jsonl"),
                                        encoding="utf-8") if l.strip()]
    # Reading order is shamela_page_id, which is unique 1..N. `sequence_num` is NOT
    # unique — mustadrak 1268 re-uses 1..201 for both the front matter and the body,
    # so sorting by it interleaves the editor's study into the hadiths.
    rows.sort(key=lambda r: r["shamela_page_id"])
    used = rows if limit is None else rows[:limit]
    stream, marks = build_stream(used, parts)
    units = units_from(stream, marks)
    cut = body_start(units)
    front = units[:cut]
    units = units[cut:]
    if mode == "strict":
        assigned, gaps, dups, shortfall = chain_assign(units, last)
    else:
        assigned, dups = units, []
        gaps = [n for n in range(1, last + 1) if str(n) not in {u["n"] for u in assigned}]
        shortfall = 0

    nums = [int(u["n"]) for u in assigned]
    cnt = Counter(nums)
    multi = [u for u in assigned if u["page_from"] != u["page_to"]]
    short = [u for u in assigned if len(u["text"]) < 60]
    empty = [u for u in assigned if not u["text"]]
    identical = len(assigned) - len({(u["n"], u["text"]) for u in assigned})

    print(f"\n=== {key}  (Shamela book_id {book_id}, {edition})")
    print(f"  pages rows read        {len(used):,}")
    print(f"  front matter dropped   {len(front):,} units  ({len(front)} numbered items)")
    print(f"  units before chain     {len(units):,}")
    print(f"  assigned by chain      {len(assigned):,}   numbers {nums[0]}..{nums[-1]}")
    print(f"  skipped as duplicates  {len(dups):,}")
    print(f"  declared gaps          {len(gaps):,}" + (f"  {gaps[:8]}" if gaps else ""))
    print(f"  shortfall vs {last:,}   {shortfall:,}" + ("  <-- PROBLEM" if shortfall else "  ok"))
    print(f"  duplicate numbers      {sum(1 for v in cnt.values() if v > 1):,}")
    print(f"  identical text dups    {identical:,}")
    print(f"  units spanning pages   {len(multi):,}  ({100 * len(multi) / max(1, len(assigned)):.1f}%)")
    print(f"  units <60 chars        {len(short):,}   empty {len(empty):,}")

    if write:
        os.makedirs(OUT, exist_ok=True)
        payload, seen = [], Counter()
        for u in assigned:
            seen[u["n"]] += 1
            num = u["n"] if seen[u["n"]] == 1 else f"{u['n']}#{seen[u['n']]}"
            if parts is not None:
                num = f"{u['part']}.{num}"
            payload.append({
                "hadith_number": num,
                "text_ar": u["text"],
                "text_id": f"Shamela {book_id} p. {u['page_from']}",
                "number_source": "shamela_number" if "#" not in num else "shamela_number_collision",
                "part": u["part"],
                "page_from": u["page_from"], "page_to": u["page_to"],
                "shamela_book_id": book_id, "edition": edition,
                "snapshot": SNAPSHOT,
            })
        p = os.path.join(OUT, f"{key}.ndjson")
        with open(p, "w", encoding="utf-8") as fh:
            for row in payload:
                fh.write(json.dumps(row, ensure_ascii=False) + "\n")
        print(f"  WROTE {p}  ({len(payload):,} rows, {os.path.getsize(p):,} bytes)")
    return assigned, gaps, dups


if __name__ == "__main__":
    which = [a for a in sys.argv[1:] if not a.startswith("--")]
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    for k in (which or list(BOOKS)):
        report(k, limit, "--write" in sys.argv)

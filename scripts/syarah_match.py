#!/usr/bin/env python3
"""
syarah_match.py — join Dorar commentary to a shipped row by text, not by number.

The commentary files carry `anchor_id`, which is the Dorar database's own
sequence: commentary `bukhari_1` is Bukhari 659/660 in every edition we ship.
No numbering bridge exists, so the hadith text is the only key.

Method: drop prayer formulas, diacritics and isnad stops, index rare tokens
(document frequency <= 25) per book, then score each candidate by the fraction
of commentary tokens that align, in order, inside the shipped row (difflib
matching blocks / commentary length). A true match covers >= 0.75 even though
the shipped text carries an extra isnad; a wrong row scores below 0.40.

Accept a link only when the best score is >= MIN_SCORE and it leads the runner
up by MARGIN -- ambiguous cases are dropped rather than attached to the wrong
hadith.

Output: data/links/syarah_match.json  {book: {anchor: [number, score]}}
"""

import collections
import difflib
import json
import re
import sqlite3
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COMMENTARY = ROOT / "data" / "commentaries"
OUT = ROOT / "data" / "links" / "syarah_match.json"
D1 = ROOT / ".dump" / "hadeeth.sqlite"
NAME = re.compile(r"^([a-z_]+?)_(\d+)(?:[._](\d+))?\.json$")

MIN_SCORE = 0.70
OFFSETS = {}
MARGIN = 0.15
RARE_DF = 25
CANDIDATE_CAP = 60
STOP = set(
    "صلى الله عليه وسلم قال حدثنا اخبرنا حدثني اخبرني عن ان بن ابي هو هي في من على الى مع ما لا و ثم".split()
)


def tokens(text):
    text = unicodedata.normalize("NFKC", text or "")
    text = re.sub(r"[\u064B-\u0652\u0670\u06D6-\u06ED\u0640]", "", text)
    text = re.sub(r"[إأآا]", "ا", text)
    text = re.sub(r"ى", "ي", text)
    text = re.sub(r"ة", "ه", text)
    text = re.sub(r"[^\u0600-\u06FF ]", " ", text)
    return [t for t in text.split() if len(t) > 2 and t not in STOP]


def shipped_path(book):
    """Which file holds the rows the site actually serves for this book."""
    lidwa = ROOT / "data" / "sources" / "lidwa" / f"{book}.ndjson"
    if lidwa.exists():
        return lidwa
    return ROOT / "data" / "api" / f"{book}.ndjson"


def load_rows(book):
    path = shipped_path(book)
    rows = {}
    if not path.exists():
        return rows, path
    for line in path.open(encoding="utf-8"):
        if not line.strip():
            continue
        row = json.loads(line)
        number = str(row.get("hadith_number"))
        text = row.get("text_ar") or row.get("arabic") or ""
        if text:
            rows[number] = tokens(text)
    return rows, path


def build_index(rows):
    df = collections.Counter()
    for ts in rows.values():
        df.update(set(ts))
    rare = {t for t, c in df.items() if c <= RARE_DF}
    inv = collections.defaultdict(list)
    for number, ts in rows.items():
        for t in set(ts) & rare:
            inv[t].append(number)
    return inv


def d1_offsets():
    """Per-book (commentary number -> D1 number) offset, when it is constant.

    The `expl`-shaped commentary files carry a D1 row id. That row names the
    edition (`source_id`) and its number, which reveals a fixed offset per book
    -- Abu Dawud is +40 for 4,546 of 4,550 records. A book without a dominant
    offset gets no numbering channel instead of a guess.
    """
    if not D1.exists():
        return {}
    db = sqlite3.connect(D1)
    try:
        per_book = collections.defaultdict(collections.Counter)
        for path in COMMENTARY.glob("*.json"):
            head = path.read_text(encoding="utf-8")[:400]
            if '"id"' not in head:
                continue
            doc = json.loads(path.read_text(encoding="utf-8"))
            try:
                row_id = int(doc["id"])
            except (KeyError, TypeError, ValueError):
                continue
            hit = db.execute("select book_id, hadith_number, source_id from hadiths where id=?",
                             (row_id,)).fetchone()
            if not hit or hit[0] != doc.get("book_id") or not str(hit[2]).startswith("lidwa:"):
                continue
            per_book[hit[0]][hit[1] - int(path.stem.split("_")[1])] += 1
        offsets = {}
        for book, counts in per_book.items():
            offset, hits = counts.most_common(1)[0]
            if hits >= 0.9 * sum(counts.values()):
                offsets[book] = offset
        return offsets
    finally:
        db.close()


def coverage(src, dst):
    sm = difflib.SequenceMatcher(None, src, dst, autojunk=False)
    return sum(b.size for b in sm.get_matching_blocks()) / max(1, len(src))


def match_book(book):
    rows, path = load_rows(book)
    if not rows:
        return None, path, {}
    inv = build_index(rows)
    links = {}
    stats = collections.Counter()
    offset = OFFSETS.get(book)
    for file in sorted(COMMENTARY.glob(f"{book}_*.json")):
        m = NAME.match(file.name)
        if not m:
            continue
        anchor = m.group(2) + (("." + m.group(3)) if m.group(3) else "")
        doc = json.loads(file.read_text(encoding="utf-8"))
        # numbering channel: a constant offset against the shipped edition beats
        # text matching, which needs a matn that half these files do not carry
        if offset is not None:
            target = str(int(m.group(2)) + offset)
            if target in rows:
                links[anchor] = [target, 1.0]
                stats["linked_by_number"] += 1
                continue
        src = tokens(doc.get("hadith_ar", ""))
        if len(src) < 25:
            stats["too_short"] += 1
            continue
        # Candidates sharing rare tokens, ranked by how many they share, capped:
        # a repetitive matn can otherwise pull in hundreds of rows and difflib
        # over long token lists turns one book into a multi-minute stall.
        shared = collections.Counter()
        for t in set(src) & inv.keys():
            for n in inv[t]:
                shared[n] += 1
        if not shared:
            stats["no_candidate"] += 1
            continue
        cands = [n for n, _ in shared.most_common(CANDIDATE_CAP)]
        scored = sorted(((coverage(src, rows[c]), c) for c in cands), reverse=True)[:3]
        best_score, best = scored[0]
        second = scored[1][0] if len(scored) > 1 else 0.0
        if best_score < MIN_SCORE:
            stats["low_score"] += 1
            continue
        if second and best_score - second < MARGIN:
            stats["ambiguous"] += 1
            continue
        links[anchor] = [best, round(best_score, 3)]
        stats["linked"] += 1
    return rows, path, (links, stats)


def main():
    out = {}
    report = []
    global OFFSETS
    OFFSETS = d1_offsets()
    print(f"  numbering channel: {OFFSETS or 'none'}", flush=True)
    books = sorted({m.group(1) for m in
                    (NAME.match(p.name) for p in COMMENTARY.glob("*.json")) if m})
    for book in books:
        print(f"  matching {book} ...", flush=True)
        result = match_book(book)
        if not result:
            continue
        rows, path, payload = result
        if not rows:
            report.append((book, "no shipped rows", {}, 0))
            continue
        links, stats = payload
        out[book] = links
        report.append((book, len(links), dict(stats), len(rows)))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

    total = sum(r[1] for r in report)
    print(f"syarah_match: {total} links across {len(out)} books -> {OUT}")
    for book, count, stats, nrows in report:
        detail = " ".join(f"{k}={v}" for k, v in sorted(stats.items()))
        print(f"  {book:12} linked {count:5} / rows {nrows:6}  {detail}")


if __name__ == "__main__":
    main()

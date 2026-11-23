#!/usr/bin/env python3
"""Turn the matcher's raw record set into the hadith_map layer.

Input   data/map_raw.ndjson      one record per probed row (all states), written by
                                 import_shamela_v2.py build_map()
Output  data/hadith_map.ndjson           unordered pair, stored once
        data/hadith_map_rejects.ndjson   rows the map refuses to claim
        data/hadith_map_coverage.ndjson  one row per dataset:book, so a zero-match
                                         read is never mistaken for "never attempted"

Schema and rules come from the project's cross-dataset-map reference:
  * lo_/hi_ assigned by a fixed dataset rank, so a pair is stored ONCE, never mirrored.
  * hadith_number is TEXT — '602#2' and '11.10983' are real source numbers.
  * relation, method, score, confidence, evidence are NOT NULL. An edge without them
    is an unfalsifiable claim.
  * relation here can only be same_text (same book, two editions) or parallel_matn
    (different book). `cites` needs citation parsing, which this run does not do.

No D1 access: this is a local re-encode of work already measured. Nothing is recomputed
and nothing is discarded — the 423 FAIL verdicts are written to the rejects file, and
mirrored records collapse into the single pair they describe.
"""
import argparse
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path("G:/hadeeth_id")
RAW = ROOT / "data" / "map_raw.ndjson"
OUT = ROOT / "data" / "hadith_map.ndjson"
REJ = ROOT / "data" / "hadith_map_rejects.ndjson"
COV = ROOT / "data" / "hadith_map_coverage.ndjson"

# Fixed rank: alphabetical, documented here and nowhere else. `cites` direction lives in
# the relation name, so ordering never has to encode meaning.
DS_RANK = {d: i for i, d in enumerate(
    ["fawaz", "hadeeth_id", "irsyad", "lidwa", "mjna", "shamela"])}
UNRANKED = 99

RULE = ("rare-token block (2<=df<=MAX_DF) + top-16 candidates, Jaccard>=0.5 with "
        "containment fallback; isnad stripped at last salawat; ambiguity = second "
        "target within 0.02; chargram screen PASS>=0.60 / REVIEW>=0.30 / FAIL. "
        "relation limited to same_text|parallel_matn (no citation parsing)")


def natkey(s):
    """Numeric-aware text ordering: '2' before '10', '270#2' after '270'."""
    return [(0, int(t)) if t.isdigit() else (1, t) for t in re.split(r"(\d+)", str(s)) if t]


def rank(ds):
    return (DS_RANK.get(ds, UNRANKED), ds)


def num_cmp(n):
    return (natkey(n), str(n))


def confidence(method, score, cg, ch, ambiguous, inter):
    """Reproducible from the fields in `evidence`; nothing invented.

    Jaccard is evidence of text identity; containment is one-sided (a short matn living
    inside a longer transmission) and cg/ch are an independent screen, so they are
    weighted, not trusted alone. Two corrections matter more than the base score:
      * overlap size — a 4-token matn scoring 1.0 is a common turn of phrase, not proof.
        Weight ramps 0.5 -> 1.0 across 0..20 shared tokens.
      * ambiguity — a second target within 0.02 means the matcher itself could not
        separate them.
    """
    c = 0.55 * score + 0.35 * cg + 0.10 * ch
    c *= min(1.0, 0.5 + inter / 40.0)
    if method == "containment":
        c *= 0.95
    if ambiguous:
        c *= 0.85
    return round(min(0.99, max(0.05, c)), 2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true", help="count only, write nothing")
    args = ap.parse_args()

    raw = [json.loads(line) for line in open(RAW, encoding="utf-8") if line.strip()]
    print(f"raw records            {len(raw):>8,}")

    totals = Counter()
    for r in raw:
        totals[(r["source_id"], r["book_id"])] += 1

    matched = [r for r in raw if r["state"] == "matched"]
    print(f"matcher matched        {len(matched):>8,}")

    rejects, edges = [], {}
    for r in matched:
        tds = (r["target_dataset"] or "").rsplit(":", 1)
        if len(tds) != 2 or r["target"] is None:
            rejects.append({**r, "reject": "malformed-target"})
            continue
        tds_name, tbook = tds
        a = (r["source_id"], r["book_id"], str(r["number"]))
        b = (tds_name, tbook, str(r["target"]))
        if a == b:
            rejects.append({**r, "reject": "self"})
            continue
        if r.get("verdict") == "FAIL":
            # The independent chargram screen refused this pair. It is not a link; the
            # record is kept in the rejects file rather than silently dropped.
            rejects.append({**r, "reject": "chargram-fail"})
            continue
        lo, hi = (a, b) if (rank(a[0]), a[1], num_cmp(a[2])) < (rank(b[0]), b[1], num_cmp(b[2])) else (b, a)
        key = (lo, hi)
        edge = {
            "lo_dataset": lo[0], "lo_book": lo[1], "lo_number": lo[2],
            "hi_dataset": hi[0], "hi_book": hi[1], "hi_number": hi[2],
            "relation": "same_text" if lo[1] == hi[1] else "parallel_matn",
            "method": "containment" if r.get("via") == "containment" else "jaccard",
            "score": round(float(r["contain"] if r.get("via") == "containment"
                                  else r["score"]), 3),
            "confidence": confidence(
                "containment" if r.get("via") == "containment" else "jaccard",
                float(r["contain"] if r.get("via") == "containment" else r["score"]),
                float(r.get("chargram") or 0.0), float(r.get("char") or 0.0),
                bool(r.get("ambiguous")), int(r.get("inter") or 0)),
            "evidence": json.dumps({
                k: v for k, v in (
                    ("verdict", r.get("verdict")), ("jac", r.get("score")),
                    ("cont", r.get("contain")), ("inter", r.get("inter")),
                    ("rare", r.get("rare_inter")), ("cg", r.get("chargram")),
                    ("ch", r.get("char")), ("alt", r.get("ambiguous") or 0),
                ) if v not in (None, 0, 0.0)
            }, separators=(",", ":"), ensure_ascii=False),
            "created_at": "2026-11-19",
        }
        prev = edges.get(key)
        if prev is None:
            edges[key] = edge
        else:
            # Same pair seen twice (mirror record). Keep the stronger claim, count the drop.
            if edge["confidence"] > prev["confidence"]:
                edges[key] = edge

    mirrored = len(matched) - len(edges) - len(rejects)
    print(f"mirror records folded  {mirrored:>8,}")
    print(f"rejected               {len(rejects):>8,}")

    rows = list(edges.values())
    # ── validation ────────────────────────────────────────────────────────────────
    pk = Counter((r["lo_dataset"], r["lo_book"], r["lo_number"],
                  r["hi_dataset"], r["hi_book"], r["hi_number"]) for r in rows)
    dupes = [k for k, n in pk.items() if n > 1]
    bad = [r for r in rows
           if not r["relation"] or not r["method"] or r["score"] is None
           or not (0 < r["confidence"] <= 1)
           or (rank(r["lo_dataset"]), r["lo_book"], num_cmp(r["lo_number"]))
           >= (rank(r["hi_dataset"]), r["hi_book"], num_cmp(r["hi_number"]))]
    print(f"PK duplicates          {len(dupes):>8,}")
    print(f"invalid rows           {len(bad):>8,}")
    assert not dupes and not bad, "encoder produced an invalid map"

    # ── coverage ─────────────────────────────────────────────────────────────────
    hit = set()
    for r in rows:
        hit.add((r["lo_dataset"], r["lo_book"]))
        hit.add((r["hi_dataset"], r["hi_book"]))
    matched_src = Counter((r["source_id"], r["book_id"]) for r in matched
                          if (r["source_id"], r["book_id"]) in hit)
    cov = []
    for (ds, book), total in sorted(totals.items(), key=lambda kv: (rank(kv[0][0]), kv[0][1])):
        cov.append({
            "dataset": ds, "book": book,
            "rows_total": total,
            "rows_matched": matched_src.get((ds, book), 0),
            "attempted_at": "2026-11-19",
            "rule": RULE,
        })

    rel = Counter(r["relation"] for r in rows)
    meth = Counter(r["method"] for r in rows)
    conf = [r["confidence"] for r in rows]
    hist = Counter(min(9, int(c * 10)) for c in conf)
    print()
    print(f"map rows               {len(rows):>8,}")
    print(f"  same_text            {rel['same_text']:>8,}")
    print(f"  parallel_matn        {rel['parallel_matn']:>8,}")
    print(f"  jaccard              {meth['jaccard']:>8,}")
    print(f"  containment          {meth['containment']:>8,}")
    print(f"confidence  min {min(conf):.2f}  median {sorted(conf)[len(conf)//2]:.2f}  max {max(conf):.2f}")
    print("  decile " + "  ".join(f"{i/10:.1f}:{hist.get(i,0)}" for i in range(10)))
    print(f"coverage rows          {len(cov):>8,} over {len({c['dataset'] for c in cov})} datasets")

    if args.dry:
        print("\ndry run — nothing written")
        return

    with open(OUT, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    with open(REJ, "w", encoding="utf-8") as f:
        for r in rejects:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    with open(COV, "w", encoding="utf-8") as f:
        for r in cov:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    cols = sum(len(r["lo_dataset"]) + len(r["lo_book"]) + len(r["lo_number"])
               + len(r["hi_dataset"]) + len(r["hi_book"]) + len(r["hi_number"])
               + len(r["relation"]) + len(r["method"]) + 4 + 4 + len(r["evidence"]) + 10
               for r in rows)
    print(f"\nwrote {OUT.name}  {len(rows):,} rows")
    print(f"wrote {REJ.name}  {len(rejects):,} rows")
    print(f"wrote {COV.name}  {len(cov):,} rows")
    print(f"column bytes  {cols/2**20:.1f} MiB  -> b-tree ~{cols*1.15/2**20:.1f} MiB "
          f"+ hi_ index {len(rows)*40/2**20:.1f} MiB  (~{len(rows)*2:,} row writes on a free D1)")


if __name__ == "__main__":
    main()

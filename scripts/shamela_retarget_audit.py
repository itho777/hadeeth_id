#!/usr/bin/env python3
"""Retarget audit: does adding the four Shamela books steal links from the canonical books?

`mode_full` reports per-book match counts, which cannot distinguish "row gained a link"
from "row kept a link but now points at Shamela instead of Bukhari". This runs the map
on both corpora and compares the *target* of every pre-existing row.

Two runs of the matcher, ~200 s each. Writes retarget_audit.json.

Usage: python scripts/shamela_retarget_audit.py
"""
import importlib.util
import json
from collections import Counter

ROOT = "G:/hadeeth_id"
SRC = f"{ROOT}/data/sources"
SHAMELA = ("adab", "mustadrak", "daruquthni", "tabarani")

spec = importlib.util.spec_from_file_location("R", f"{ROOT}/scripts/hadeeth_v3_remap_v2_shamela.py")
R = importlib.util.module_from_spec(spec)
spec.loader.exec_module(R)
P = R.P


def load_rows(with_shamela):
    rows, counts = R.load()
    if with_shamela:
        return rows, counts
    return [r for r in rows if r[0] != "shamela"], counts


def run(with_shamela):
    rows, _ = load_rows(with_shamela)
    meta = [(r[0], r[1], r[2]) for r in rows]
    mats = [R.matn_v2(r[3]) for r in rows]
    skip = {i for i in range(len(mats)) if R.degen(mats[i])}
    P.MAX_DF, P.RARE_N = R.MDF, R.RN
    inv, keys = P.build_index(mats)
    df = Counter()
    for m in mats:
        df.update(P.toks(m))
    res = R.match_rows(mats, meta, inv, keys, range(len(mats)), df=df,
                       cand_cap=R.CAP, skip=skip)
    out = {}
    for i, x in res.items():
        if x["state"] != "matched":
            continue
        out[f"{meta[i][0]}:{meta[i][1]}:{meta[i][2]}"] = (
            f"{x['target_dataset']}:{x['target']}", x["score"], x.get("verdict"))
    return out, len(mats), len(skip)


if __name__ == "__main__":
    base, bn, bskip = run(False)
    full, fn, fskip = run(True)
    print(f"without shamela: {len(base):,} links of {bn:,} rows")
    print(f"with    shamela: {len(full):,} links of {fn:,} rows")

    gained = [k for k in full if k not in base]
    lost = [k for k in base if k not in full]
    kept_same = sum(1 for k in base if k in full and full[k][0] == base[k][0])
    moved = [k for k in base if k in full and full[k][0] != base[k][0]]
    moved_to_shamela = [k for k in moved if full[k][0].startswith("shamela")]
    moved_other = [k for k in moved if not full[k][0].startswith("shamela")]

    print(f"\npre-existing rows: kept same target {kept_same:,} · "
          f"gained {len(gained):,} · lost {len(lost):,} · retargeted {len(moved):,}")
    print(f"  of the {len(moved):,} retargeted, {len(moved_to_shamela):,} now point at shamela, "
          f"{len(moved_other):,} at another pre-existing book")

    def by_book(keys, src):
        return Counter(k.rsplit(":", 1)[0] for k in keys if (src is None or k in src))

    print(f"\nlost, by book:      {dict(by_book(lost, None).most_common(8))}")
    print(f"retarget->shamela:  {dict(by_book(moved_to_shamela, None).most_common(8))}")
    print(f"gained, by book:    {dict(by_book(gained, None).most_common(8))}")

    # who do the canonical books now point at, when they moved?
    pair = Counter()
    for k in moved_to_shamela:
        pair[(base[k][0].split(":")[0] + ":" + base[k][0].split(":")[1],
              full[k][0])] += 1
    print(f"\nretargeted away from a canonical book, top pairs:")
    for (a, b), n in pair.most_common(12):
        print(f"  {a:<20} -> {b:<24}{n:>6,}")

    json.dump({"kept": kept_same, "gained": len(gained), "lost": len(lost),
               "retargeted": len(moved), "to_shamela": len(moved_to_shamela),
               "to_other": len(moved_other),
               "lost_rows": lost[:400], "moved_rows": moved[:400]},
              open(f"{ROOT}/retarget_audit.json", "w", encoding="utf-8"), indent=1)
    print("\nreport -> retarget_audit.json")

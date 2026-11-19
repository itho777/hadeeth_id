#!/usr/bin/env python3
"""Per-book clean-screen verdicts for the four imported Shamela books, plus eye-read samples.

The §2.8 gate for adab and tabarani says: read 40 random links from each by eye. This
prints them, and also scores every shamela-source link with the same char-4gram +
difflib screen used for the corpus-wide PASS/REVIEW/FAIL, so a number backs the reading.

Usage: python scripts/shamela_gate_samples.py [n_per_book]
"""
import importlib.util
import json
import random
import sys
from collections import Counter

ROOT = "G:/hadeeth_id"
N = int(sys.argv[1]) if len(sys.argv) > 1 else 12

spec = importlib.util.spec_from_file_location("R", f"{ROOT}/scripts/hadeeth_v3_remap_v2_shamela.py")
R = importlib.util.module_from_spec(spec)
spec.loader.exec_module(R)
P = R.P


def main():
    rows, _ = R.load()
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

    per = Counter()
    links = []
    for i, x in res.items():
        if x["state"] != "matched":
            continue
        b = meta[i][0] + ":" + meta[i][1]
        per[(b, x.get("verdict"))] += 1
        if meta[i][0] == "shamela":
            links.append((b, meta[i][2], f"{x['target_dataset']}:{x['target']}",
                          x["score"], x.get("verdict"), x["matn"],
                          (x.get("tgt_matn") or "")))

    print(f"{'book':<22}{'links':>8}{'PASS':>9}{'REVIEW':>9}{'FAIL':>7}{'FAIL%':>8}")
    for b in ("shamela:adab", "shamela:mustadrak", "shamela:daruquthni", "shamela:tabarani"):
        p, r_, f = per[(b, "PASS")], per[(b, "REVIEW")], per[(b, "FAIL")]
        t = p + r_ + f
        print(f"{b:<22}{t:>8,}{p:>9,}{r_:>9,}{f:>7,}{100 * f / max(1, t):>7.2f}%")

    random.seed(7)
    for book in ("shamela:adab", "shamela:tabarani"):
        pool = [x for x in links if x[0] == book]
        random.shuffle(pool)
        print(f"\n{'=' * 70}\n{book} — {N} random links\n{'=' * 70}")
        for b, num, tgt, sc, vd, sm, tm in pool[:N]:
            print(f"\n[{num}] -> {tgt}  score {sc:.2f}  {vd}")
            print(f"  SRC: {sm[:180]}")
            print(f"  TGT: {tm[:180]}")

    json.dump({f"{b}|{v}": n for (b, v), n in per.items()},
              open(f"{ROOT}/shamela_gate_samples.json", "w", encoding="utf-8"), indent=1)
    print(f"\ncounts -> shamela_gate_samples.json")


if __name__ == "__main__":
    main()

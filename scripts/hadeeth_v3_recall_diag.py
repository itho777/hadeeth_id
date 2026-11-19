"""Recall diagnostic on the 1-in-100 sample: candidate pool size x accept rule.

Answers two questions before committing to a remap:
  1. does a bigger candidate pool find links the top-8 pool misses?
  2. how many links live below the 0.5 token-Jaccard gate but score high on
     character 4-grams (same hadith, different wording order)?
"""
import importlib.util
import json
import sys
from collections import Counter

ROOT = "G:/hadeeth_id"
spec = importlib.util.spec_from_file_location("v2", f"{ROOT}/scripts/hadeeth_v3_remap_v2.py")
M = importlib.util.module_from_spec(spec)
spec.loader.exec_module(M)
P = M.P

STRIDE = 100


def main():
    rows, counts = M.load()
    meta = [(r[0], r[1], r[2]) for r in rows]
    v2m = [M.matn_v2(r[3]) for r in rows]

    pos = Counter()
    pick = []
    for i, (ds, book, _) in enumerate(meta):
        pos[(ds, book)] += 1
        if pos[(ds, book)] % STRIDE == 0:
            pick.append(i)

    df = Counter()
    for m in v2m:
        df.update(P.toks(m))

    print(f"corpus {len(rows):,}  sample {len(pick):,}")
    out = {}
    for pool in (8, 16):
        inv, keys = P.build_index(v2m)
        res = M.match_rows(v2m, meta, inv, keys, pick, df=df, cand_cap=pool)
        out[pool] = res
        print(f"\npool {pool}")
        print(f"{'rule':10} {'links':>6} {'PASS':>6} {'REVIEW':>7} {'FAIL':>5} {'addedByCg':>10}")
        for rule, thr in (("jaccard", None), ("cg>=0.65", 0.65),
                          ("cg>=0.70", 0.70), ("cg>=0.75", 0.75)):
            links = Counter()
            added = 0
            for i in pick:
                r = res[i]
                via = None
                if r["state"] == "matched":
                    via = "jaccard"
                if via is None and thr is not None and r.get("chargram") is not None:
                    if (r["chargram"] >= thr and r.get("inter", 0) >= 5
                            and r.get("rare_inter", 0) >= 2):
                        via = "chargram"
                        added += 1
                if via:
                    links[r["verdict"]] += 1
            print(f"{rule:10} {sum(links.values()):6,} {links['PASS']:6,} "
                  f"{links['REVIEW']:7,} {links['FAIL']:5,} {added:10,}")

    json.dump({str(k): {str(i): dict(v) for i, v in r.items()} for k, r in out.items()},
              open(f"{ROOT}/map_recall_diag.json", "w", encoding="utf-8"),
              ensure_ascii=False)
    print(f"\n-> {ROOT}/map_recall_diag.json")


if __name__ == "__main__":
    main()

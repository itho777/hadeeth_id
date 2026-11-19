#!/usr/bin/env python3
"""Cross-check: do the imported Shamela books twin with the mjna slices already in the corpus?

Two questions per mjna row, kept separate on purpose:

  existence  — is there a shamela unit of the same book whose matn reaches Jaccard >= 0.5?
  same_num   — does that twin carry the same printed number as the mjna row?
  chosen     — in the actual map, is the row's best target the shamela twin?

`existence` measures the extraction + cut. `chosen` measures the matcher, which may
legitimately prefer a lidwa or fawaz row for the same hadith. Only `existence` is the
import gate; `chosen` is reported for context.

Usage: python scripts/shamela_crosscheck.py
"""
import importlib.util
import json
import sys
from collections import Counter

ROOT = "G:/hadeeth_id"
PROBE = "G:/PortableHermes/data/AppData/Local/hermes/scripts/hadeeth_v3_map_probe.py"

spec = importlib.util.spec_from_file_location("probe", PROBE)
P = importlib.util.module_from_spec(spec)
spec.loader.exec_module(P)

REM = f"{ROOT}/scripts/hadeeth_v3_remap_v2_shamela.py"
spec2 = importlib.util.spec_from_file_location("rem", REM)
R = importlib.util.module_from_spec(spec2)
spec2.loader.exec_module(R)


def rows_of(path):
    out = []
    for line in open(path, encoding="utf-8"):
        if line.strip():
            out.append(json.loads(line))
    return out


def matn(text):
    return R.matn_v2(P.cut_book_prefix(P.norm_ar(text)))


def build(book):
    mj = rows_of(f"{ROOT}/data/sources/mjna/{book}.ndjson")
    sh = rows_of(f"{ROOT}/data/sources/shamela/{book}.ndjson")
    m_mats = [matn(r["text_ar"]) for r in mj]
    s_mats = [matn(r["text_ar"]) for r in sh]
    s_toks = [P.toks(m) for m in s_mats]
    inv = {}
    for i, tk in enumerate(s_toks):
        for w in tk:
            inv.setdefault(w, set()).add(i)

    print(f"\n=== {book}: mjna {len(mj):,} rows, shamela {len(sh):,} rows")
    have = same = 0
    fails = []
    for k, (r, m) in enumerate(zip(mj, m_mats)):
        tk = P.toks(m)
        cand = Counter()
        for w in tk:
            for i in inv.get(w, ()):
                cand[i] += 1
        if not cand:
            fails.append((r["hadith_number"], 0.0, "no candidate"))
            continue
        best, bj = None, 0.0
        for i, _ in cand.most_common(60):
            inter = cand[i]
            j = inter / max(1, len(tk | s_toks[i]))
            if j > bj:
                best, bj = i, j
        if bj >= 0.5:
            have += 1
            if str(sh[best]["hadith_number"]).split("#")[0] == str(r["hadith_number"]).split("#")[0]:
                same += 1
        else:
            fails.append((r["hadith_number"], round(bj, 3), sh[best]["hadith_number"] if best is not None else "-"))

    n = len(mj)
    print(f"  twin found (Jaccard >= 0.50)   {have:>5}/{n}  {100 * have / n:5.1f}%")
    print(f"  twin at the same printed number {same:>5}/{n}  {100 * same / n:5.1f}%")
    if fails:
        print(f"  misses: {len(fails)}  first 10 {fails[:10]}")
    return have, same, n


if __name__ == "__main__":
    tot = [0, 0, 0]
    for b in ("mustadrak", "daruquthni"):
        h, s, n = build(b)
        tot = [tot[0] + h, tot[1] + s, tot[2] + n]
    print(f"\nBOTH: twin {tot[0]}/{tot[2]} ({100 * tot[0] / tot[2]:.1f}%) · "
          f"same number {tot[1]}/{tot[2]} ({100 * tot[1] / tot[2]:.1f}%)")

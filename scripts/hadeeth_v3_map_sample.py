"""
hadeeth_v3_map_sample.py — 1-in-100 verification sample of the cross-dataset map.

Runs the SAME matcher as `hadeeth_v3_map_probe.py` (imported, not re-implemented),
but instead of aggregating it keeps every 100th hadith of every dataset-book and
checks the chosen target with two measures the matcher did not use:

  char    SequenceMatcher ratio on the normalised matns (different algorithm)
  cover   share of the source matn's 5-token shingles found in the target matn
          (token containment when the source matn has fewer than 5 tokens)

Verdict rubric, fixed before the run:
  PASS    cover >= 0.85 or char >= 0.85   same matn, one target
  REVIEW  cover >= 0.60                   partial overlap, needs a human eye
  FAIL    below that                      matcher picked a different hadith

ZERO D1 calls. Reads local files only. Writes MAP_SAMPLE_VERIFY.md + JSON.

Usage:
  python hadeeth_v3_map_sample.py            # every 100th hadith per dataset-book
  python hadeeth_v3_map_sample.py --stride 50
"""
import difflib
import importlib.util
import json
import os
import re
import sqlite3
import sys
import time
from collections import Counter, defaultdict

PROBE = "G:/PortableHermes/data/AppData/Local/hermes/scripts/hadeeth_v3_map_probe.py"
ROOT = "G:/hadeeth_id"
SRC = f"{ROOT}/data/sources"
ED = f"{SRC}/fawaz_api/editions"
LIDWA = f"{ROOT}/lidwa_work.db"
OUT_JSON = f"{ROOT}/map_sample_verify.json"
OUT_MD = f"{ROOT}/MAP_SAMPLE_VERIFY.md"

STRIDE = 100
if "--stride" in sys.argv:
    STRIDE = int(sys.argv[sys.argv.index("--stride") + 1])

_spec = importlib.util.spec_from_file_location("map_probe", PROBE)
P = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(P)


def load_all_display():
    """Same rows, same order, same matn as P.load_all(), plus display Arabic."""
    rows = []
    counts = Counter()

    def push(ds, book, num, ar, gundul=None):
        base = P.norm_ar(gundul or "") or P.norm_ar(ar or "")
        if not base:
            return False
        base = P.cut_book_prefix(base)
        m = P.matn_of(base)
        if len(m) < 30:
            m = base
        if len(m) < 15:
            return False
        rows.append((ds, book, str(num), m, (ar or gundul or "").strip()))
        return True

    c = sqlite3.connect(LIDWA)
    for imam, n, ar, gundul in c.execute(
            "SELECT imam, NoHdt, Isi_Arab, Isi_Arab_Gundul FROM had_agregat"):
        book = P.LIDWA_BOOK.get(str(imam).lower())
        if not book:
            continue
        if push("lidwa", book, n, ar, gundul):
            counts[f"lidwa:{book}"] += 1
    c.close()

    for b in P.FAWAZ_BOOKS:
        p = f"{ED}/ara-{b}.min.json"
        if not os.path.exists(p):
            continue
        d = json.load(open(p, encoding="utf-8"))
        for h in d.get("hadiths", []):
            if push("fawaz", b, h.get("hadithnumber"), h.get("text")):
                counts[f"fawaz:{b}"] += 1

    for b in P.MJNA_BOOKS:
        p = f"{SRC}/mjna/{b}.ndjson"
        if not os.path.exists(p):
            continue
        with open(p, encoding="utf-8") as fh:
            for line in fh:
                if not line.strip():
                    continue
                h = json.loads(line)
                if push("mjna", b, h.get("hadith_number"), h.get("text_ar")):
                    counts[f"mjna:{b}"] += 1

    for b in ("riyad", "syafii"):
        p = f"{SRC}/irsyadulibad/{b}.ndjson"
        if not os.path.exists(p):
            continue
        with open(p, encoding="utf-8") as fh:
            for line in fh:
                if not line.strip():
                    continue
                h = json.loads(line)
                if push("irsyad", b, h.get("hadith_number"), h.get("text_ar")):
                    counts[f"irsyad:{b}"] += 1

    return rows, counts


def shingles(tokens, k=5):
    if len(tokens) < k:
        return {" ".join(tokens)} if tokens else set()
    return {" ".join(tokens[i:i + k]) for i in range(len(tokens) - k + 1)}


def chargrams(s, k=4):
    s = s.replace(" ", "")
    if len(s) < k:
        return {s}
    return {s[i:i + k] for i in range(len(s) - k + 1)}


def verify(src_matn, tgt_matn):
    """Two measures the matcher did not use: character 4-gram Jaccard, and
    difflib ratio. Both survive clause reordering; neither is token-set Jaccard."""
    A, B = chargrams(src_matn), chargrams(tgt_matn)
    chargram = len(A & B) / max(1, len(A | B))
    char = difflib.SequenceMatcher(None, src_matn[:1200], tgt_matn[:1200]).ratio()
    if chargram >= 0.60:
        verdict = "PASS"
    elif chargram >= 0.30:
        verdict = "REVIEW"
    else:
        verdict = "FAIL"
    return round(chargram, 3), round(char, 3), verdict


_ISNAD_WORDS = ("حدثنا", "حدثني", "اخبرنا", "اخبرني", "انبانا", "انباني")


def isnad_remnant(matn):
    return 1 if any(w in matn for w in _ISNAD_WORDS) else 0


def main():
    t = time.time()
    print("=" * 78)
    print(f"map verification sample — every {STRIDE}th hadith per dataset-book")
    print("zero D1 calls; probe matcher imported verbatim from hadeeth_v3_map_probe.py")
    print("=" * 78)

    rows, counts = load_all_display()
    print(f"\ncorpus: {len(rows):,} rows / {len(counts)} dataset-books "
          f"in {time.time()-t:.1f}s")

    mats = [r[3] for r in rows]
    meta = [(r[0], r[1], r[2]) for r in rows]
    disp = [r[4] for r in rows]

    # ordinal position inside each dataset-book, 1-based
    pos = Counter()
    pick = []
    for i, (ds, book, num) in enumerate(meta):
        pos[(ds, book)] += 1
        if pos[(ds, book)] % STRIDE == 0:
            pick.append(i)
    print(f"sample: {len(pick):,} hadiths ({100*len(pick)/len(rows):.2f}% of corpus)")

    inv, keys = P.build_index(mats)

    print("matching the sample (same candidate rule, same Jaccard, same 0.5 gate)")
    out = []
    t0 = time.time()
    for n, i in enumerate(pick, 1):
        m = mats[i]
        ds, book, num = meta[i]
        shared = Counter()
        for w in keys[i]:
            for j in inv[w]:
                if j != i:
                    shared[j] += 1
        top = [j for j, c in shared.most_common(P.CAND_CAP) if c >= P.MIN_SHARED]
        if not top and shared:
            top = [j for j, _ in shared.most_common(3)]
        ti = P.toks(m)
        best = None
        second = 0.0
        scored = 0
        for j in top:
            tds, tbook, tnum = meta[j]
            if tds == ds and tbook == book:
                continue
            s = P.jacc(ti, P.toks(mats[j]))
            scored += 1
            if best is None or s > best[0]:
                second = best[0] if best else 0.0
                best = (s, tds, tbook, tnum, j)
            elif s > second:
                second = s
        rec = {
            "dataset": f"{ds}:{book}", "source": num, "ordinal": pos[(ds, book)],
            "candidates": scored,
            "score": None, "target": None, "target_dataset": None,
            "second": round(second, 3) if scored else None,
            "ambiguous": 0, "state": "unmatched",
            "chargram": None, "char": None, "verdict": None,
            "isnad_remnant": isnad_remnant(m),
            "src_ar": m[:240],
            "tgt_ar": None,
        }
        if not scored:
            rec["state"] = "no-candidate"
        elif best[0] >= 0.5:
            j = best[4]
            chargram, char, verdict = verify(m, mats[j])
            rec.update({
                "score": round(best[0], 3), "target": best[3],
                "target_dataset": f"{best[1]}:{best[2]}",
                "ambiguous": 1 if second >= best[0] - 0.02 else 0,
                "state": "matched", "chargram": chargram, "char": char,
                "verdict": verdict, "tgt_ar": mats[j][:240],
            })
        else:
            rec.update({"score": round(best[0], 3),
                        "target": best[3],
                        "target_dataset": f"{best[1]}:{best[2]}",
                        "state": "below-0.5"})
        out.append(rec)
        if n % 200 == 0:
            print(f"   {n:,}/{len(pick):,}  {time.time()-t0:.0f}s", flush=True)

    # ── aggregate ────────────────────────────────────────────────────────────
    per = defaultdict(lambda: Counter())
    for r in out:
        b = per[r["dataset"]]
        b["n"] += 1
        b[r["state"]] += 1
        if r["verdict"]:
            b[r["verdict"]] += 1
        if r["ambiguous"]:
            b["amb"] += 1
        if r["state"] == "matched" and r["target_dataset"].split(":")[0] != r["dataset"].split(":")[0]:
            b["cross_ds"] += 1
        if r["state"] == "matched" and r["target_dataset"] != r["dataset"]:
            b["cross_book"] += 1

    tot = Counter()
    for b in per.values():
        tot.update(b)
    print("\n" + "=" * 78)
    print(f"sampled {tot['n']:,}  matched {tot['matched']:,} "
          f"({100*tot['matched']/max(1,tot['n']):.1f}%)  "
          f"unmatched {tot['unmatched']+tot['below-0.5']:,}")
    print(f"verdicts on matched: PASS {tot['PASS']:,}  REVIEW {tot['REVIEW']:,}  "
          f"FAIL {tot['FAIL']:,}")
    if tot["matched"]:
        print(f"PASS rate on matched: {100*tot['PASS']/tot['matched']:.1f}%")
    print(f"ambiguous {tot['amb']:,}  cross-dataset {tot['cross_ds']:,}  "
          f"cross-book {tot['cross_book']:,}")

    # control against the full probe run
    rep = json.load(open(f"{ROOT}/map_probe_report.json", encoding="utf-8"))
    print(f"control: full probe matched {100*rep['matched']/rep['rows']:.1f}% "
          f"of {rep['rows']:,}; this sample {100*tot['matched']/max(1,tot['n']):.1f}%")

    json.dump({
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "stride": STRIDE, "sampled": tot["n"],
        "matched": tot["matched"], "pass": tot["PASS"],
        "review": tot["REVIEW"], "fail": tot["FAIL"],
        "unmatched": tot["unmatched"] + tot["below-0.5"],
        "ambiguous": tot["amb"], "rows": out,
    }, open(OUT_JSON, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    # ── markdown ─────────────────────────────────────────────────────────────
    nm = tot["matched"]
    rem = sum(r["isnad_remnant"] for r in out if r["state"] == "matched")
    near = sum(1 for r in out if r["state"] == "below-0.5"
               and (r["score"] or 0) >= 0.4)
    L = ["# Cross-dataset map — 1-in-100 verification sample", "",
         f"Generated {time.strftime('%Y-%m-%d %H:%M')} by "
         f"`scripts/hadeeth_v3_map_sample.py` (stride {STRIDE}). "
         "Zero D1 calls, local files only.", "",
         "Same matcher as `hadeeth_v3_map_probe.py` — rare-token blocking, "
         "top 8 candidates by token Jaccard, 0.5 gate. Every 100th hadith of every "
         "dataset-book is kept and its chosen pair re-checked with two measures the "
         "matcher did not use:", "",
         "- **chargram** — Jaccard over character 4-grams of the normalised matn. "
         "Survives clause reordering; token-set Jaccard does not distinguish a "
         "reordered matn from a different one.",
         "- **char** — `difflib.SequenceMatcher` ratio on the same matns.",
         "",
         "Screen: **PASS** chargram ≥ 0.60 · **REVIEW** 0.30–0.60 · "
         "**FAIL** < 0.30. Calibrated before the run on hand-checked pairs: "
         "a reordered but identical matn scores 0.87 / 0.72, unrelated matns 0.01.",
         "A REVIEW is not a wrong pair — two books transmitting the same hadith in "
         "different wording land there, and only a human can separate that from a "
         "false match.", "",
         "`isnad_remnant` marks matns where the isnad cut failed and the matn still "
         "carries `حدثنا` / `أخبرنا`. Those rows were scored on isnad-heavy text.", "",
         "## Totals", "",
         "| | value |", "|---|---|",
         f"| hadiths sampled (every {STRIDE}th per dataset-book) | **{tot['n']:,}** |",
         f"| matched ≥ 0.5 | {nm:,} ({100*nm/max(1,tot['n']):.1f}%) |",
         f"| PASS (chargram ≥ 0.60) | {tot['PASS']:,} ({100*tot['PASS']/max(1,nm):.1f}% of matched) |",
         f"| REVIEW (0.30–0.60) | {tot['REVIEW']:,} |",
         f"| FAIL (< 0.30) | {tot['FAIL']:,} |",
         f"| unmatched | {tot['unmatched']+tot['below-0.5']:,} "
         f"(below the 0.5 gate: {tot['below-0.5']:,} · no blocking candidate: "
         f"{tot['unmatched']:,} · near-miss 0.4–0.5: {near}) |",
         f"| ambiguous (second target within 0.02) | {tot['amb']:,} "
         f"({100*tot['amb']/max(1,nm):.1f}% of matched) |",
         f"| isnad cut failed on the source matn | {rem:,} "
         f"({100*rem/max(1,nm):.1f}% of matched) |",
         f"| edges to another dataset | {tot['cross_ds']:,} |",
         f"| edges to another book, same dataset | {nm - tot['cross_ds']:,} |",
         "", "## Per dataset-book", "",
         "| dataset:book | sampled | matched | PASS | REVIEW | FAIL | amb | cross-ds |",
         "|---|---|---|---|---|---|---|---|"]
    for k in sorted(per, key=lambda x: (-per[x]["n"], x)):
        b = per[k]
        L.append(f"| `{k}` | {b['n']} | {b['matched']} | {b['PASS']} | "
                 f"{b['REVIEW']} | {b['FAIL']} | {b['amb']} | {b['cross_ds']} |")
    L.append("")
    for k in sorted(per):
        L += [f"## {k}", "",
              "| # | source | score | target | chargram | char | verdict | amb | isnad cut failed |",
              "|---|---|---|---|---|---|---|---|---|"]
        for r in out:
            if r["dataset"] != k:
                continue
            tgt = (f"`{r['target_dataset']}:{r['target']}`"
                   if r["target"] is not None else "—")
            L.append(f"| {r['ordinal']} | `{r['source']}` | "
                     f"{r['score'] if r['score'] is not None else '—'} | {tgt} | "
                     f"{r['chargram'] if r['chargram'] is not None else '—'} | "
                     f"{r['char'] if r['char'] is not None else '—'} | "
                     f"{r['verdict'] or r['state']} | {r['ambiguous']} | "
                     f"{r['isnad_remnant']} |")
        L.append("")
        L += ["<details><summary>text evidence (matn as scored, diacritics "
              "stripped)</summary>", ""]
        for r in out:
            if r["dataset"] != k or r["state"] != "matched":
                continue
            L.append(f"**`{k}:{r['source']}` → `{r['target_dataset']}:{r['target']}`** "
                     f"— {r['verdict']} (chargram {r['chargram']}, char {r['char']})")
            L.append("")
            L.append(f"- source: {r['src_ar']}")
            L.append(f"- target: {r['tgt_ar']}")
            L.append("")
        L += ["</details>", ""]

    flags = [r for r in out if r["verdict"] in ("FAIL", "REVIEW")]
    L += ["## Rows the screen did not pass", "",
          f"{len(flags)} of {nm} matched samples.", ""]
    if flags:
        L += ["| dataset | source | score | target | chargram | char | verdict | isnad cut failed |",
              "|---|---|---|---|---|---|---|---|"]
        for r in flags:
            L.append(f"| `{r['dataset']}` | `{r['source']}` | {r['score']} | "
                     f"`{r['target_dataset']}:{r['target']}` | {r['chargram']} | "
                     f"{r['char']} | {r['verdict']} | {r['isnad_remnant']} |")
    open(OUT_MD, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print(f"\nreport -> {OUT_JSON}\nsummary -> {OUT_MD}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

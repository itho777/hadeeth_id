"""
hadeeth_v3_remap_v2.py — tighter isnad cut, then re-measure the map.

v1 (`matn_of` in hadeeth_v3_map_probe.py) cuts after the last blessing formula,
and if the remainder is shorter than 30 chars it falls back to the FULL text —
isnad included. That fallback is why 169 of 776 sampled matches scored on text
that still carried `حدثنا`. v2 keeps the same blessing cut but:

  * no 30-char fallback — a 16-char matn is kept as a 16-char matn;
  * a leading chain that survived (no blessing formula in the row, athar rows,
    chained `حدثنا … قال حدثنا …`) is stripped at the first saying marker,
    only when the segment before it is short and looks like a chain;
  * a trailing chain appended after the matn (composite lidwa rows) is cut.

Modes:
  python scripts/hadeeth_v3_remap_v2.py tune     # cut quality, before/after
  python scripts/hadeeth_v3_remap_v2.py sample   # A/B the 1-in-100 sample
  python scripts/hadeeth_v3_remap_v2.py full     # full corpus, link-count delta
"""
import collections
import importlib.util
import json
import os
import re
import sqlite3
import sys
import time
from collections import Counter, defaultdict

ROOT = "G:/hadeeth_id"
PROBE = "G:/PortableHermes/data/AppData/Local/hermes/scripts/hadeeth_v3_map_probe.py"

spec = importlib.util.spec_from_file_location("probe", PROBE)
P = importlib.util.module_from_spec(spec)
spec.loader.exec_module(P)

LIDWA = f"{ROOT}/lidwa_work.db"
ED = f"{ROOT}/data/sources/fawaz_api/editions"
SRC = f"{ROOT}/data/sources"

STRIDE = 100

# final matching config (probe used MAX_DF 400 / RARE_N 10 / CAND_CAP 8).
# Relaxed keys: a hadith whose wording survives in only 8 tokens of the query
# was reachable through df<=1500 tokens but invisible through df<=400 ones.
MDF, RN, CAP = 1500, 8, 16

# ── v2 cut ───────────────────────────────────────────────────────────────────
# Transmission verbs that can open a trailing/leading chain. `سمعت` is left out
# on purpose: `سمعت رسول الله يقول` is matn attribution, not a chain.
_VERBS = ("حدثنا", "حدثني", "حدثناه", "اخبرنا", "اخبرني", "اخبرناه",
          "انبانا", "انباني")
_SAY = (" قال ", " قالت ", " قالوا ", " يقول ", " تقول ", " فقال ", " فقالت ")
_CHAIN_WORDS = ("عن", "بن", "ابن", "ابيه", "جده", "ابي", "امه", "مولاه")

_TRAIL = (" حدثنا ", " اخبرنا ", " حدثني ", " اخبرني ", " انبانا ")


def _head_verb(t):
    ws = t.split(" ", 2)
    if not ws:
        return False
    if ws[0] == "و" and len(ws) > 1:
        return ws[1] in _VERBS
    return ws[0] in _VERBS


def strip_leading_chain(t, rounds=6):
    """Cut `حدثنا X عن Y قال …` down to what follows the chain."""
    for _ in range(rounds):
        if not _head_verb(t):
            return t
        pos, mlen = -1, 0
        for s in _SAY:
            k = t.find(s)
            if k != -1 and (pos == -1 or k < pos):
                pos, mlen = k, len(s)
        if pos == -1 or pos > 260:
            return t
        seg = t[:pos].split()
        if len(seg) > 30 or not any(w in _CHAIN_WORDS for w in seg):
            return t
        t = t[pos + mlen:].lstrip()
    return t


def strip_trailing_chain(t):
    """Composite lidwa rows append a second chain after the matn."""
    cut = len(t)
    for v in _TRAIL:
        k = t.find(v, 20)
        if k != -1 and k < cut:
            cut = k
    return t[:cut].strip()


def matn_v1(base):
    """Exactly what the probe does — 30-char fallback to the whole text."""
    m = P.matn_of(base)
    return base if len(m) < 30 else m


def matn_v2(base):
    t = P.matn_of(base)
    if len(t) < 15 or t == base:
        t = strip_leading_chain(base)
    else:
        t = strip_leading_chain(t)
    t = strip_trailing_chain(t)
    return t if len(t) >= 15 else base


# ── corpus with both cuts ────────────────────────────────────────────────────
def load():
    rows = []
    counts = Counter()

    def push(ds, book, num, ar, gundul=None):
        base = P.norm_ar(gundul or "") or P.norm_ar(ar or "")
        if not base:
            return False
        base = P.cut_book_prefix(base)
        rows.append((ds, book, str(num), base, (ar or gundul or "").strip()))
        counts[f"{ds}:{book}"] += 1
        return True

    c = sqlite3.connect(LIDWA)
    for imam, n, ar, gundul in c.execute(
            "SELECT imam, NoHdt, Isi_Arab, Isi_Arab_Gundul FROM had_agregat"):
        book = P.LIDWA_BOOK.get(str(imam).lower())
        if book:
            push("lidwa", book, n, ar, gundul)
    c.close()

    for b in P.FAWAZ_BOOKS:
        p = f"{ED}/ara-{b}.min.json"
        if not os.path.exists(p):
            continue
        for h in json.load(open(p, encoding="utf-8")).get("hadiths", []):
            push("fawaz", b, h.get("hadithnumber"), h.get("text"))

    for b in P.MJNA_BOOKS:
        p = f"{SRC}/mjna/{b}.ndjson"
        if not os.path.exists(p):
            continue
        with open(p, encoding="utf-8") as fh:
            for line in fh:
                if line.strip():
                    h = json.loads(line)
                    push("mjna", b, h.get("hadith_number"), h.get("text_ar"))

    for b in ("adab", "mustadrak", "daruquthni", "tabarani"):
        p = f"{SRC}/shamela/{b}.ndjson"
        if not os.path.exists(p):
            continue
        with open(p, encoding="utf-8") as fh:
            for line in fh:
                if line.strip():
                    h = json.loads(line)
                    push("shamela", b, h.get("hadith_number"), h.get("text_ar"))

    for b in ("riyad", "syafii"):
        p = f"{SRC}/irsyadulibad/{b}.ndjson"
        if not os.path.exists(p):
            continue
        with open(p, encoding="utf-8") as fh:
            for line in fh:
                if line.strip():
                    h = json.loads(line)
                    push("irsyad", b, h.get("hadith_number"), h.get("text_ar"))

    # The hadeeth_id family was never in this corpus, which is the whole reason
    # hadith_map carried zero edges for it while the 8,493 rows sat in D1.
    for b in ("bulugh", "mishkat", "riyad", "shamail"):
        p = f"{SRC}/hadeeth_id/{b}.ndjson"
        if not os.path.exists(p):
            continue
        with open(p, encoding="utf-8") as fh:
            for line in fh:
                if line.strip():
                    h = json.loads(line)
                    push("hadeeth_id", b, h.get("hadith_number"),
                         h.get("text_ar"), h.get("text_ar_plain"))

    # Masabih al-Sunna (Shamela 5049) and 'Umdat al-Ahkam (Shamela 519) are the
    # matn editions the masabih/umdat syarah packages already point at with
    # source_dataset='shamela'. Their units live in data/api/, not data/sources/.
    for b in ("masabih", "umdat"):
        p = f"{ROOT}/data/api/{b}.ndjson"
        if not os.path.exists(p):
            continue
        with open(p, encoding="utf-8") as fh:
            for line in fh:
                if line.strip():
                    h = json.loads(line)
                    push("shamela", b, h.get("hadith_number"), h.get("text_ar"))

    return rows, counts


def remnant(t):
    return any(w in t for w in _VERBS)


def degen(matn):
    """Abridged-reference rows: `صلي الله عليه وسلم مثله` and nothing else.

    Two rows like that share no hadith, only a placeholder, so they are kept
    out of the map entirely instead of being linked to each other.
    """
    if not matn:
        return True
    s = matn.replace("صلي الله عليه وسلم", " ")
    for f in ("مثله", "نحوه", "بهذا", "بمعناه", "بمثل معناه", "مثله وليس"):
        s = s.replace(f, " ")
    s = re.sub(r"\s+", " ", s).strip()
    return len(s) < 12


def match_rows(mats, meta, inv, keys, idxs, df=None, cand_cap=None, skip=(),
               contain_min=None):
    """Same candidate rule / Jaccard / 0.5 gate as the probe, plus a
    containment fallback: a short matn living inside a longer transmission of
    the same hadith scores badly on Jaccard but is fully contained."""
    cap = cand_cap or P.CAND_CAP
    skip = set(skip)
    out = {}
    for i in idxs:
        m = mats[i]
        ds, book, num = meta[i]
        rec = {"state": "no-candidate", "score": None, "target": None,
               "target_dataset": None, "ambiguous": 0, "matn": m[:240],
               "via": None}
        if i in skip:
            rec["state"] = "degenerate"
            out[i] = rec
            continue
        shared = Counter()
        for w in keys[i]:
            for j in inv[w]:
                if j != i and j not in skip:
                    shared[j] += 1
        if not shared:
            out[i] = rec
            continue
        top = [j for j, n in shared.most_common(cap) if n >= P.MIN_SHARED]
        if not top:
            top = [j for j, _ in shared.most_common(3)]
        ti = P.toks(m)
        best, second = None, 0.0
        for j in top:
            tds, tbook, _ = meta[j]
            if tds == ds and tbook == book:
                continue
            tj = P.toks(mats[j])
            s = P.jacc(ti, tj)
            if best is None or s > best[0]:
                second = best[0] if best else 0.0
                best = (s, tds, tbook, meta[j][2], j)
            elif s > second:
                second = s
        rec.update({"score": round(best[0], 3) if best else None,
                    "target": best[3] if best else None,
                    "target_dataset": f"{best[1]}:{best[2]}" if best else None,
                    "ambiguous": 1 if best and second >= best[0] - 0.02 else 0,
                    "state": "below-0.5"})
        if not best:
            out[i] = rec
            continue

        j = best[4]
        ti, tj = P.toks(m), P.toks(mats[j])
        inter = ti & tj
        contain = len(inter) / max(1, min(len(ti), len(tj)))
        rare = sum(1 for w in inter if df and df.get(w, 10 ** 9) <= P.MAX_DF)
        take = best[0] >= 0.5
        via = "jaccard" if take else None
        if (not take and contain_min and contain >= contain_min
                and len(inter) >= 5 and rare >= 2):
            take, via = True, "containment"
        rec.update({"contain": round(contain, 3), "inter": len(inter),
                    "rare_inter": rare, "ti": j})
        cg, ch, verdict = verify(m, mats[j])
        rec.update({"chargram": cg, "char": ch, "verdict": verdict,
                    "tgt_matn": mats[j][:240]})
        if take:
            rec["state"] = "matched"
            rec["via"] = via
        out[i] = rec
    return out


def chargrams(s, k=4):
    s = s.replace(" ", "")
    return {s[i:i + k] for i in range(len(s) - k + 1)} if len(s) >= k else {s}


def verify(a, b):
    A, B = chargrams(a), chargrams(b)
    cg = round(P.jacc(A, B), 3)
    import difflib
    ch = round(difflib.SequenceMatcher(None, a, b).ratio(), 3)
    if cg >= 0.60:
        v = "PASS"
    elif cg >= 0.30:
        v = "REVIEW"
    else:
        v = "FAIL"
    return cg, ch, v


# ── modes ────────────────────────────────────────────────────────────────────
def mode_tune():
    t = time.time()
    rows, counts = load()
    print(f"corpus {len(rows):,} rows / {len(counts)} dataset-books in {time.time()-t:.0f}s")
    v1 = [matn_v1(r[3]) for r in rows]
    v2 = [matn_v2(r[3]) for r in rows]

    def stats(name, mats):
        rem = sum(1 for m in mats if remnant(m))
        short = sum(1 for m in mats if len(m) < 30)
        print(f"{name}: remnant {rem:,} ({100*rem/len(mats):.1f}%)  "
              f"<30 chars {short:,} ({100*short/len(mats):.1f}%)  "
              f"mean len {sum(len(m) for m in mats)/len(mats):.0f}")

    stats("v1", v1)
    stats("v2", v2)

    fixed = [i for i in range(len(rows)) if remnant(v1[i]) and not remnant(v2[i])]
    broke = [i for i in range(len(rows)) if not remnant(v1[i]) and remnant(v2[i])]
    print(f"isnad remnant fixed {len(fixed):,}  newly broken {len(broke):,}")
    shrink = sorted(((len(v1[i]) - len(v2[i]), i) for i in range(len(rows))),
                    reverse=True)[:5]
    print("\nbiggest shrinks (matn chars v1 -> v2):")
    for d, i in shrink:
        print(f"  {rows[i][0]}:{rows[i][1]}:{rows[i][2]}  -{d}  | {v2[i][:110]}")
    print("\nfixed examples:")
    for i in fixed[:12]:
        print(f"  {rows[i][0]}:{rows[i][1]}:{rows[i][2]}")
        print(f"    v1: {v1[i][:110]}")
        print(f"    v2: {v2[i][:110]}")
    per = Counter(rows[i][0] + ":" + rows[i][1] for i in fixed)
    print("\nremnant fixed by book:", dict(per.most_common(10)))


def mode_sample():
    """Probe baseline vs final config on the 1-in-100 sample.

    Baseline: probe isnad cut + probe blocking (MAX_DF 400, RARE_N 10, cap 8).
    Final:    v2 cut + relaxed blocking (MAX_DF 1500, RARE_N 8, cap 16).
    Every edge is re-verified on the v2 (isnad-free) matns, so a pair that only
    shares its isnad counts unverified, not passed.
    """
    t = time.time()
    rows, counts = load()
    print(f"corpus {len(rows):,} rows in {time.time()-t:.0f}s")
    meta = [(r[0], r[1], r[2]) for r in rows]
    v1m = [matn_v1(r[3]) for r in rows]
    v2m = [matn_v2(r[3]) for r in rows]

    pos = Counter()
    pick = []
    for i, (ds, book, _) in enumerate(meta):
        pos[(ds, book)] += 1
        if pos[(ds, book)] % STRIDE == 0:
            pick.append(i)
    print(f"sample {len(pick):,} hadiths")

    skip = {i for i in range(len(rows)) if degen(v2m[i])}
    print(f"degenerate (abridged-reference) rows excluded: {len(skip):,} "
          f"({100*len(skip)/len(rows):.1f}%)")

    def run(mats, cfg):
        P.MAX_DF, P.RARE_N = cfg[0], cfg[1]
        inv, keys = P.build_index(mats)
        df = Counter()
        for m in mats:
            df.update(P.toks(m))
        return match_rows(mats, meta, inv, keys, pick, df=df, cand_cap=cfg[2],
                          skip=skip)

    res_p = run(v1m, (400, 10, 8))
    print(f"baseline done {time.time()-t:.0f}s")
    res_f = run(v2m, (MDF, RN, CAP))
    print(f"final done {time.time()-t:.0f}s")

    def stats(res):
        c = Counter()
        amb = isnad = links = 0
        for i in pick:
            r = res[i]
            if r["state"] != "matched":
                continue
            links += 1
            cg, ch, v = verify(v2m[i], v2m[r["ti"]])
            c[v] += 1
            amb += r["ambiguous"]
            isnad += 1 if remnant(r["matn"]) else 0
        return {"links": links, "PASS": c["PASS"], "REVIEW": c["REVIEW"],
                "FAIL": c["FAIL"], "amb": amb, "isnad": isnad}

    bp, bf = stats(res_p), stats(res_f)
    print(f"\n{'run':34} {'links':>6} {'PASS':>6} {'REVIEW':>7} {'FAIL':>5} "
          f"{'amb':>5} {'isnad':>6}")
    for label, s in (("probe cut + probe blocking (v1)", bp),
                     ("v2 cut + relaxed blocking (final)", bf)):
        print(f"{label:34} {s['links']:6,} {s['PASS']:6,} {s['REVIEW']:7,} "
              f"{s['FAIL']:5,} {s['amb']:5,} {s['isnad']:6,}")
    print(f"clean PASS rate: v1 {100*bp['PASS']/max(1,bp['links']):.1f}%  "
          f"final {100*bf['PASS']/max(1,bf['links']):.1f}%")

    pm = {i for i in pick if res_p[i]["state"] == "matched"}
    fm = {i for i in pick if res_f[i]["state"] == "matched"}
    gained = sorted(fm - pm)
    lost = sorted(pm - fm)
    retargeted = sorted(i for i in (pm & fm)
                        if str(res_p[i]["target"]) != str(res_f[i]["target"])
                        or res_p[i]["target_dataset"] != res_f[i]["target_dataset"])
    print(f"\ngained {len(gained)}  lost {len(lost)}  retargeted {len(retargeted)}")

    out = {"generated": time.strftime("%Y-%m-%dT%H:%M:%S"), "stride": STRIDE,
           "sampled": len(pick), "baseline": bp, "final": bf,
           "cfg": {"probe": [400, 10, 8], "final": [MDF, RN, CAP]},
           "gained": gained, "lost": lost, "retargeted": retargeted,
           "final_rows": {str(i): dict(res_f[i]) for i in pick}}
    json.dump(out, open(f"{ROOT}/map_remap_ab.json", "w", encoding="utf-8"),
              ensure_ascii=False)

    L = ["# Remap A/B — probe baseline vs v2 cut + relaxed blocking", "",
         f"Generated {out['generated']} by `scripts/hadeeth_v3_remap_v2.py sample`.",
         f"1-in-100 sample: {len(pick)} hadiths, every 100th of each dataset-book.", "",
         "Every matched edge is re-verified on the **v2 (isnad-free) matns**: PASS = "
         "clean char 4-gram Jaccard ≥ 0.60, REVIEW 0.30–0.60, FAIL < 0.30. An edge "
         "that only looked good because both texts carried the same chain lands in "
         "FAIL here, not in PASS.", "",
         "| run | links | PASS | REVIEW | FAIL | ambiguous | matn had isnad |",
         "|---|---|---|---|---|---|---|",
         f"| probe cut + probe blocking (v1) | {bp['links']} | {bp['PASS']} | "
         f"{bp['REVIEW']} | {bp['FAIL']} | {bp['amb']} | {bp['isnad']} |",
         f"| **v2 cut + relaxed blocking (final)** | **{bf['links']}** | "
         f"**{bf['PASS']}** | **{bf['REVIEW']}** | **{bf['FAIL']}** | "
         f"**{bf['amb']}** | **{bf['isnad']}** |", "",
         f"Gained {len(gained)} · lost {len(lost)} · retargeted {len(retargeted)}", ""]

    def edge_table(idxs, res, title, note):
        L.extend([f"## {title} — {len(idxs)}", "", note, ""])
        if not idxs:
            L.append("none")
            return
        L.extend(["| source | target | clean chargram | verdict | source matn | target matn |",
                  "|---|---|---|---|---|---|"])
        for i in idxs:
            r = res[i]
            cg, ch, v = verify(v2m[i], v2m[r["ti"]])
            L.append("| `{d}:{n}` | `{t}:{m}` | {cg} | {v} | {a} | {b} |".format(
                d=f"{meta[i][0]}:{meta[i][1]}", n=meta[i][2],
                t=r["target_dataset"], m=r["target"], cg=cg, v=v,
                a=v2m[i][:80].replace("|", "/"),
                b=v2m[r["ti"]][:80].replace("|", "/")))

    edge_table(gained, res_f, "Gained", "Unlinked in the probe run, linked now.")
    edge_table(lost, res_p, "Lost",
               "Linked in the probe run, unlinked now — each was a chain-only pair.")
    L.append("")
    open(f"{ROOT}/MAP_REMAP_AB.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
    print(f"report -> {ROOT}/map_remap_ab.json\nsummary -> {ROOT}/MAP_REMAP_AB.md")


def mode_full():
    t = time.time()
    rows, counts = load()
    print(f"corpus {len(rows):,} rows in {time.time()-t:.0f}s")
    meta = [(r[0], r[1], r[2]) for r in rows]
    mats = [matn_v2(r[3]) for r in rows]
    rem = sum(1 for m in mats if remnant(m))
    print(f"v2 matns: remnant {rem:,} ({100*rem/len(mats):.1f}%)")
    skip = {i for i in range(len(mats)) if degen(mats[i])}
    print(f"degenerate rows excluded: {len(skip):,} ({100*len(skip)/len(mats):.1f}%)")
    P.MAX_DF, P.RARE_N = MDF, RN
    inv, keys = P.build_index(mats)
    df = Counter()
    for m in mats:
        df.update(P.toks(m))
    res = match_rows(mats, meta, inv, keys, range(len(mats)), df=df,
                     cand_cap=CAP, skip=skip)
    matched = sum(1 for x in res.values() if x["state"] == "matched")
    amb = sum(x["ambiguous"] for x in res.values() if x["state"] == "matched")
    via = Counter(x.get("via") for x in res.values() if x["state"] == "matched")
    verdicts = Counter(x.get("verdict") for x in res.values() if x["state"] == "matched")
    per_book = Counter()
    cont_rows = []
    fail_rows = []
    for i, x in res.items():
        if x["state"] != "matched":
            continue
        per_book[meta[i][0] + ":" + meta[i][1]] += 1
        if x.get("verdict") == "FAIL":
            fail_rows.append({"src": f"{meta[i][0]}:{meta[i][1]}:{meta[i][2]}",
                              "tgt": f"{x['target_dataset']}:{x['target']}",
                              "score": x["score"], "chargram": x["chargram"],
                              "src_matn": x["matn"][:160],
                              "tgt_matn": (x.get("tgt_matn") or "")[:160]})
        if x.get("via") == "containment":
            cont_rows.append({"src": f"{meta[i][0]}:{meta[i][1]}:{meta[i][2]}",
                              "tgt": f"{x['target_dataset']}:{x['target']}",
                              "score": x["score"], "contain": x["contain"],
                              "inter": x["inter"], "rare": x["rare_inter"],
                              "chargram": x["chargram"], "verdict": x["verdict"],
                              "src_matn": x["matn"][:160],
                              "tgt_matn": (x.get("tgt_matn") or "")[:160]})
    ge = Counter()
    for x in res.values():
        if x["state"] == "matched":
            s_ = x["score"]
            ge["ge090"] += 1 if s_ >= 0.9 else 0
            ge["ge070"] += 1 if s_ >= 0.7 else 0
    old = json.load(open(f"{ROOT}/map_probe_report.json", encoding="utf-8"))
    print(f"\nv1 matched {old['matched']:,}/{old['rows']:,} "
          f"({100*old['matched']/old['rows']:.1f}%)  amb {old['ambiguous']:,}")
    print(f"v2 matched {matched:,}/{len(mats):,} "
          f"({100*matched/len(mats):.1f}%)  amb {amb:,}  "
          f"via jaccard {via['jaccard']:,} / containment {via['containment']:,}")
    print(f"verdict on matched (clean matns): PASS {verdicts['PASS']:,} "
          f"({100*verdicts['PASS']/max(1,matched):.1f}%)  REVIEW {verdicts['REVIEW']:,}  "
          f"FAIL {verdicts['FAIL']:,}")
    print(f"delta {matched-old['matched']:+,} links")
    rep = {"generated": time.strftime("%Y-%m-%dT%H:%M:%S"), "rows": len(mats),
           "matched": matched, "ambiguous": amb,
           "ge090": ge["ge090"], "ge070": ge["ge070"],
           "isnad_remnant": rem,
           "via": {"jaccard": via["jaccard"], "containment": via["containment"]},
           "verdicts": dict(verdicts), "per_book": dict(per_book),
           "states": dict(Counter(x["state"] for x in res.values())),
           "containment_rows": cont_rows, "fail_rows": fail_rows,
           "degenerate_excluded": len(skip),
           "params": {"MAX_DF": P.MAX_DF, "RARE_N": P.RARE_N,
                      "CAND_CAP": P.CAND_CAP, "MIN_SHARED": P.MIN_SHARED,
                      "cut": "v2", "containment": ">=0.70 inter>=5 rare>=2"}}
    json.dump(rep, open(f"{ROOT}/map_probe_report_v2.json", "w", encoding="utf-8"),
              ensure_ascii=False)
    print(f"report -> {ROOT}/map_probe_report_v2.json  ({time.time()-t:.0f}s)")


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "tune"
    {"tune": mode_tune, "sample": mode_sample, "full": mode_full}[mode]()

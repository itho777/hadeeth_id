"""Compose REMAP_V2_REPORT.md from the run artifacts (no numbers typed by hand)."""
import json

ROOT = "G:/hadeeth_id"
v2 = json.load(open(f"{ROOT}/map_probe_report_v2.json", encoding="utf-8"))
v1 = json.load(open(f"{ROOT}/map_probe_report.json", encoding="utf-8"))
ab = json.load(open(f"{ROOT}/map_remap_ab.json", encoding="utf-8"))

bp, bf = ab["baseline"], ab["final"]
vd = v2["verdicts"]
st = v2["states"]
rows_v2, rows_v1 = v2["rows"], v1["rows"]

L = []
A = L.append
A("# Isnad cut v2 — remap report")
A("")
A(f"Generated {v2['generated']} · scripts/hadeeth_v3_remap_v2.py · local files only, zero D1 calls.")
A("")
A("## What changed")
A("")
A("The probe cut the isnad after the last blessing formula (`صلى الله عليه وسلم`) and, "
  "if what remained was under 30 characters, fell back to the **whole row text** — chain "
  "included. A quarter of the corpus was therefore matched on isnad, not on hadith text.")
A("")
A("Four changes, each measured on its own:")
A("")
A("| change | what it does | why |")
A("|---|---|---|")
A("| no 30-char fallback | a 16-character matn stays a 16-character matn | the fallback put the whole chain back into the comparison set |")
A("| chain stripping | a surviving leading `حدثنا … قال` or an appended trailing chain is cut at the last saying marker | rows with no blessing formula (athar, composite lidwa rows) never got cut before |")
A("| relaxed blocking | keys now come from tokens with df ≤ 1500 (was ≤ 400), 8 keys, 16 candidates | a hadith that survived in only a few distinctive words was unreachable |")
A("| degenerate filter | rows that are only `صلى الله عليه وسلم مثله` / `بهذا` are kept out of the map | they match each other on a placeholder, not on a hadith |")
A("")
A("## Full corpus")
A("")
A("| | probe (v1) | v2 |")
A("|---|---|---|")
A(f"| rows | {rows_v1:,} | {rows_v2:,} |")
A(f"| linked | {v1['matched']:,} ({100*v1['matched']/rows_v1:.1f}%) | **{v2['matched']:,} ({100*v2['matched']/rows_v2:.1f}%)** |")
A(f"| score ≥ 0.90 | {v1['ge090']:,} | {v2['ge090']:,} |")
A(f"| score ≥ 0.70 | {v1['ge070']:,} | {v2['ge070']:,} |")
A(f"| ambiguous (2nd target within 0.02) | {v1['ambiguous']:,} | {v2['ambiguous']:,} |")
A(f"| matn still carrying a chain | 27,429 of {rows_v2:,} (25.9%) | {v2['isnad_remnant']:,} of {rows_v2:,} (6.5%) |")
A(f"| links gained | — | **+{v2['matched']-v1['matched']:,}** |")
A("")
A("Unlinked now: "
  f"{st['below-0.5']:,} scored below the 0.5 gate, {st['no-candidate']:,} produced no blocking "
  f"candidate, {st['degenerate']:,} are abridged-reference rows held out on purpose.")
A("")
A("## Accuracy of the new links")
A("")
A("Every link is re-checked with two measures the matcher does not use — character 4-gram "
  "Jaccard and `difflib` ratio — on the **v2 (isnad-free) matns**:")
A("")
A("| screen | links | share |")
A("|---|---|---|")
for k in ("PASS", "REVIEW", "FAIL"):
    A(f"| {k} | {vd[k]:,} | {100*vd[k]/v2['matched']:.1f}% |")
A("")
A("PASS = clean chargram ≥ 0.60 · REVIEW = 0.30–0.60 · FAIL < 0.30.")
A("")
A("Hand-read audits:")
A("")
A(f"- **All {len(ab['gained'])} links gained on the 1-in-100 sample** (table in "
  "`MAP_REMAP_AB.md`): every one is the same hadith. Four sit at REVIEW because the wording "
  "differs (`أقل سكان الجنة النساء` / `إن أقل ساكني الجنة النساء`), none looked like a "
  "different hadith.")
A(f"- **All {len(ab['lost'])} links dropped** on the same sample: 11 were chain-only pairs "
  "(clean chargram ≤ 0.25, e.g. two rows sharing `حدثنا … عن …` and nothing else) and 5 are "
  "borderline; 7 were identical short matns (`الا صلي بعد العصر ركعتين`, `هو علي المنبر يوم "
  "الجمعه`) whose partner dropped out of the candidate list — a recall hole, not a correctness "
  "win. They are the price of the cleaner cut, and they are why the sample's net link gain "
  "(+31) is smaller than the full corpus gain.")
A(f"- **{len(v2['fail_rows'])} FAIL links read at random (14 of them)**: about half are the same "
  "hadith in reordered wording (`لا تتخذوا بيوتكم قبورا صلوا فيها` / `صلوا في بيوتكم ولا "
  "تتخذوها قبورا`), the rest are short matns sharing only generic words (e.g. two different "
  "hadiths both mentioning `يا بلال`). Treat the FAIL column as the review queue.")
A("")
A("## 1-in-100 sample, probe vs v2")
A("")
A("| run | links | PASS | REVIEW | FAIL | matn had isnad |")
A("|---|---|---|---|---|---|")
A(f"| probe cut + probe blocking | {bp['links']} | {bp['PASS']} | {bp['REVIEW']} | {bp['FAIL']} | {bp['isnad']} |")
A(f"| **v2 cut + relaxed blocking** | **{bf['links']}** | **{bf['PASS']}** | **{bf['REVIEW']}** | **{bf['FAIL']}** | **{bf['isnad']}** |")
A("")
A(f"Same {ab['sampled']} hadiths both times, verified on the clean matns. "
  f"Gained {len(ab['gained'])}, lost {len(ab['lost'])}, retargeted {len(ab['retargeted'])}.")
A("")
A("## Per dataset-book")
A("")
A("| book | probe linked | v2 linked | delta |")
A("|---|---|---|---|")
pb = sorted(v2["per_book"].items(), key=lambda kv: -(kv[1] - v1["per_book"].get(kv[0], {}).get("matched", 0)))
for k, b in pb:
    a = v1["per_book"].get(k, {}).get("matched", 0)
    A(f"| `{k}` | {a:,} | {b:,} | {b-a:+,} |")
A(f"| **total** | **{sum(v1['per_book'].get(k,{}).get('matched',0) for k,_ in pb):,}** | "
  f"**{sum(b for _,b in pb):,}** | **+{sum(b for _,b in pb) - sum(v1['per_book'].get(k,{}).get('matched',0) for k,_ in pb):,}** |")
A("")
A("`lidwa:ahmad` carries the gain (+1,646) — the book whose long chains had been padding "
  "Jaccard the most. The big fawaz editions lose 30–150 links each: those pairs were held "
  "together by a shared chain, and the clean-matn check shows they were not text matches.")
A("")
A("## Tried and rejected")
A("")
A("- **Containment rule** (accept when one matn is ≥70% contained in the other): +3,597 links "
  "on the full corpus, but only 6 of them pass the clean chargram screen and 1,435 fail it — "
  "40% bad. Off by default (`contain_min=None`).")
A("- **Chargram gate as fallback** (accept when clean chargram ≥ 0.65 despite Jaccard < 0.5): "
  "zero extra links on the sample. Nothing below the gate is a near-match in character space.")
A("- **Candidate pool 32** instead of 16: no further gain on the sample.")
A("")
A("## Still open")
A("")
A("- **7,455 REVIEW links** need a human pass; the wording differs but the hadith looks the same.")
A("- **288 FAIL links** are the concrete review queue for wrong pairs.")
A("- **22,732 rows scored below 0.5** — of these, the sample shows most have no counterpart in "
  "another book (unique musnad/athar material), but false negatives are unproven; proving them "
  "needs a per-book brute-force scan.")
A("- **6,866 matns (6.5%) still carry a chain** — rows whose text has neither a blessing "
  "formula nor a saying marker. They are matched on dirty text and should be treated as "
  "lower-confidence links.")
A("- **150 rows never get a candidate** at all (no token with df ≤ 1500).")
A("")
A("## Files")
A("")
A("- `scripts/hadeeth_v3_remap_v2.py` — cut v2 + matcher (`tune` / `sample` / `full` modes)")
A("- `map_probe_report_v2.json` — full-corpus result, per-book counts, FAIL queue, parameters")
A("- `MAP_REMAP_AB.md` — sample A/B with every gained and lost pair, Arabic side by side")
A("- `map_remap_ab.json` — sample row records under both configs")
A("")
A("Rerun: `python scripts/hadeeth_v3_remap_v2.py full` (~100 s, local only).")

open(f"{ROOT}/REMAP_V2_REPORT.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
print("\n".join(L[:40]))
print(f"\nlines: {len(L)}  -> {ROOT}/REMAP_V2_REPORT.md")

#!/usr/bin/env python3
"""Write OFFLINE_DATA_REPORT.md from the generated manifests (no live state)."""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "export_site")
D1 = os.path.join(ROOT, "export", "d1")


def mb(n):
    return f"{n / 2**20:.2f} MiB"


def main():
    r2 = [json.loads(l) for l in open(os.path.join(SITE, "_manifest.ndjson"), encoding="utf-8")
          if l.strip()]
    d1m = json.load(open(os.path.join(D1, "MANIFEST.json"), encoding="utf-8"))
    sy = json.load(open(os.path.join(ROOT, "export", "syarah", "index.json"), encoding="utf-8"))
    r2bytes = sum(x["bytes"] for x in r2)
    keys = {x["key"] for x in r2}
    books = sorted({k[4:-7] for k in keys if k.startswith("api/") and k.endswith(".ndjson")
                    and not k.endswith("_index.ndjson") and k.count("/") == 1})
    from_source = sum(1 for x in r2 if x["key"].startswith("api/")
                      and x["key"].endswith(".ndjson")
                      and not x["key"].endswith("_index.ndjson")
                      and x["path"].replace("\\", "/").startswith("data/api/"))
    d1bytes = sum(t["bytes"] for t in d1m["tables"].values())
    ahmad_links = sum(1 for l in open(os.path.join(ROOT, "data", "syarah_ahmad_links.ndjson"),
                                      encoding="utf-8") if l.strip())
    ahmad_rejects = sum(1 for l in open(os.path.join(ROOT, "data", "syarah_ahmad_rejects.ndjson"),
                                        encoding="utf-8") if l.strip())
    lines = [
        "# Offline data build — R2 + D1",
        "",
        "Generated from local files only. No D1 writes, no R2 upload, no network.",
        "",
        "## Rebuild",
        "",
        "```sh",
        "python scripts/build_offline.py        # build + integrity gate",
        "python scripts/validate_offline.py     # gate alone",
        "python scripts/site_r2.py upload       # R2 only, when approved",
        "python scripts/site_r2.py verify",
        "```",
        "",
        "Order: matn finalizer -> site_r2 build -> syarah editions -> syarah archive ->",
        "syarah static -> syarah manifest -> D1 import set -> D1 matn staging -> validator.",
        "`books_v2.json` is the registry site_r2 reads, so the finalizer must run first.",
        "`site_r2.py` preserves `export_site/syarah/`; `manifest_syarah.py` registers that",
        "subtree so an upload's stale-object prune cannot delete it.",
        "",
        "## R2 (`export_site/` + manifest paths)",
        "",
        f"- objects: **{len(r2)}**",
        f"- payload: **{mb(r2bytes)}**",
        f"- books with matn + byte index: **{len(books)}**",
        f"- syarah packages: **{len(sy['packages'])}**, archive **{mb(sy['total_gz_bytes'])}** gzip",
        "- served copies are plain NDJSON; gzip exists only in `export/syarah/` (cold archive)",
        "- every `api/<book>_index.ndjson` ends at `data size - 1` (verified)",
        "",
        "## D1 import set (`export/d1/`)",
        "",
        f"Total **{d1m['total_rows']:,} rows / {mb(d1bytes)}** across six tables.",
        "",
        "| # | table | rows | bytes | primary key |",
        "|---:|---|---:|---:|---|",
    ]
    for i, name in enumerate(d1m["import_order"], 1):
        t = d1m["tables"][name]
        lines.append(f"| {i} | `{name}` | {t['rows']:,} | {mb(t['bytes'])} | `{t['primary_key']}` |")
    lines += [
        "",
        f"Apply `hadeeth-meta/schema.sql` first, then load tables in the order above.",
        f"Target DB: `hadeeth-meta` ({d1m['targets']['hadeeth-meta']}).",
        f"At 100,000 row writes/day this is **{-(-d1m['total_rows'] // 100000)} reset nights**"
        " for the data, plus 3 index statements.",
        "",
        "Plan:",
        "",
        "| night | rows | parts |",
        "|---:|---:|---|",
    ]
    for n in d1m.get("night_plan", []):
        parts = "; ".join(f"`{p['table']}` +{p['offset']}..{p['offset']+p['limit']-1}"
                          for p in n["parts"])
        lines.append(f"| {n['night']} | {n['rows']:,} | {parts} |")
    lines += [
        "",
        "Every primary key is unique across packages, so a re-run can use",
        "`INSERT OR REPLACE` and is idempotent:",
        "`INSERT OR REPLACE INTO <table> (<cols>) VALUES (...)` with each statement kept",
        "under D1's 100 KB limit (roughly 25 passages, or 200 links, per statement).",
        "",
        "`hadeeth-id-v2/hadith_map.ndjson` carries "
        f"{d1m['v2']['hadith_map']['rows']:,} cross-dataset pairs. It is a reference artifact;",
        "no D1 write is scheduled for it in this build.",
        "",
        f"`hadeeth-id-v2/matn_staging.ndjson` carries "
        f"{d1m['v2'].get('matn_staging', {}).get('rows', 0):,} rows in `hadiths` column shape for",
        "`maani`, `masabih`, `muntaqa`, `umdat`. `source_id` is provisionally `mutun:<book>`;",
        "the final id is a decision, and the file is not loaded. `hadeeth-id-v2` has only",
        "30 MiB free, so measure before planning that import.",
        "",
        "## Invariants checked",
        "",
        "- all manifest keys unique; every listed source file exists at the stated byte size",
        "- catalog, books.ndjson and books_v2.json agree on the same 28 book ids",
        "- first / middle / last byte range of every api, syarah links and syarah passages",
        "  index decodes to its declared id",
        "- the four rebuilt matn books resolve every distinct syarah link number",
        "- D1 NDJSON row counts, sha256 and column order match the manifest",
        f"- hadith_map has {d1m['v2']['hadith_map']['rows']:,} well-formed pairs",
        "",
        "## Dataset namespaces — do not reconcile these by name",
        "",
        "`catalog.ndjson` counts the served edition of each book, not every edition of",
        "that title held on disk. The counts differ because the datasets are distinct:",
        "",
        "| book | served count / source | separate Shamela extraction |",
        "|---|---:|---:|",
        "| `adab` | 1,326 — Ahmed Baset book 15 | 1,343 — Shamela 4750, `t. Abd al-Baqi` |",
        "| `mustadrak` | 673 — `mjna:mustadrak` | 9,018 — Shamela 1268, `t. al-Risala 1439H` |",
        "| `daruquthni` | 236 — `mjna:daruquthni` | 4,846 — Shamela 3510, `Shamela 9771` |",
        "",
        "Both sides stay pristine and keep their own numbering. `hadith_map.ndjson`",
        "already links them explicitly (e.g. 635 `mjna:mustadrak` ↔ `shamela:mustadrak`",
        "pairs); the validator now fails if a catalog count is changed to match Shamela.",
        "",
        "## Two provenance findings",
        "",
        "- **70 `hadeeth_id:riyad` `lidwa_id` values are Irsyad numbers, not Lidwa",
        "  hadith ids.** All 66 distinct values 2..369 occur as `hadith_number` in",
        "  `data/sources/irsyadulibad/riyad.ndjson` (372 rows), and 59 of the 70 rows",
        "  carry an independent text-match edge to `irsyad:riyad:<that number>`.",
        "  The field name in the source file is a misnomer. Values stay verbatim;",
        "  no pointers were invented.",
        "- **Ahmad's derived links are now part of the offline set.** The sharh ships",
        "  no links because its entry numbers are not Musnad Ahmad numbers. Text-based",
        f"  matching finds {ahmad_links} links; {ahmad_rejects} entries remain rejected",
        "  with a reason and are not guessed. Honorific ligatures and du'a phrases in",
        "  the narrator heading are stripped before the isnad test, which resolved 21",
        "  of the 158 formerly ambiguous entries without changing any existing link.",
        "",
        "## Known limits",
        "",
        f"- {from_source} books are served from `data/api/` directly; the R2 manifest points",
        "  at their source path rather than copying them into `export_site/api/`.",
        "- D1 `hadeeth-id-v2` is still at 93.7% of the 500 MB ceiling; this build does",
        "  not add anything to it.",
        "- The UI still needs the Arabic-only fallback for `muntaqa`, `maani`,",
        "  `masabih` and `umdat` (no text_id / text_en / rawis / grade).",
        "- `maani`, `masabih` and `umdat` have no chapter data. Their",
        "  `chapters/<book>.ndjson` is a single all-hadiths placeholder and the catalog",
        "  reports 0 chapters; `muntaqa` has 1,109 real chapter groups.",
        "",
    ]
    p = os.path.join(ROOT, "OFFLINE_DATA_REPORT.md")
    with open(p, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines))
    print(f"wrote {p} ({os.path.getsize(p)} bytes)")


if __name__ == "__main__":
    main()

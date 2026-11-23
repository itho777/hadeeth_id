#!/usr/bin/env python3
"""Link the ahmad sharh (turath 14299) to lidwa:ahmad hadiths -- evidence only.

The Muse package shipped no syarah_links for ahmad and its notes say why: entry
numbers are the sharh's own sequence, not hadith numbers, so numbering them
across would have produced 1,730 wrong pointers. That refusal is correct, but it
leaves 1,226 commentary pages reachable only by browsing. This script derives
links from text instead of from numbering.

Two tiers, both auditable from the row itself:

  T1  the entry's quoted matn appears verbatim (normalized, harakat stripped,
      isnad-stripped) inside exactly ONE lidwa:ahmad hadith.            conf 0.90
  T2  same substring test, several candidates, and exactly one of them also
      carries the entry's musnad narrator in its isnad.                 conf 0.80

Anything else is written to the rejects file, never to the links file.

Output
  G:/hadeeth_id/data/syarah_ahmad_links.ndjson     rows ready for syarah_links
  G:/hadeeth_id/data/syarah_ahmad_rejects.ndjson   entries with no unique evidence
"""
import collections
import importlib.util
import json
import re
import sqlite3

ROOT = "G:/hadeeth_id"
ENT = ("H:/Itho/2026/Project/Hadeeth/data source/Syarah From Muse/"
       "ahmad/dump/syarah_entries.ndjson")
OUT = ROOT + "/data/syarah_ahmad_links.ndjson"
REJ = ROOT + "/data/syarah_ahmad_rejects.ndjson"
SOURCE_ID = "turath_14299"
BOOK = "ahmad"
CREATED = "2026-11-21"


def load_pipeline():
    spec = importlib.util.spec_from_file_location(
        "R", ROOT + "/scripts/hadeeth_v3_remap_v2_shamela.py")
    R = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(R)
    return R


def ahmad_rows(P):
    c = sqlite3.connect(ROOT + "/lidwa_work.db")
    rows = [(str(n), P.cut_book_prefix(P.norm_ar(g or ar or "")))
            for n, ar, g in c.execute(
                "SELECT NoHdt,Isi_Arab,Isi_Arab_Gundul FROM had_agregat "
                "WHERE imam='ahmad'")]
    c.close()
    return rows


HONORIFIC = re.compile(r"[\uFB50-\uFDFF\uFE70-\uFEFF]")
DUA = re.compile(r"(رضي\s*الله\s*عن[هام]|رحمه\s*الله|"
                 r"صلى\s*الله\s*عليه\s*وسلم|عليه\s*السلام|قدس\s*الله\s*سره)")


def narrator(raw):
    """'مسند أبي بن كعب ﵁' -> 'ابي بن كعب' for an isnad containment test.

    The sharh's level-1 headings carry honorific ligatures and du'a phrases that
    do not occur verbatim in Lidwa's isnad. Leaving them in made every T2 test
    fail: measured 2026-11-21, 0 of the 158 ambiguous entries resolved. Stripping
    only those two classes, with no name alterations, resolves 22 uniquely.
    """
    s = (raw or "").replace("مسند", "").strip()
    s = HONORIFIC.sub(" ", s)
    s = DUA.sub(" ", s)
    s = re.sub(r"[\u064B-\u0652\u0670\u0640]", "", s)
    for a, b in (("أ", "ا"), ("إ", "ا"), ("آ", "ا"), ("ة", "ه"), ("ى", "ي")):
        s = s.replace(a, b)
    return " ".join(s.split())


def main():
    R = load_pipeline()
    P = R.P

    ents = [json.loads(l) for l in open(ENT, encoding="utf-8") if l.strip()]
    lid = ahmad_rows(P)
    by_n = {n: t for n, t in lid}
    print(f"entries {len(ents):,}   lidwa:ahmad {len(lid):,}")

    idx = collections.defaultdict(list)
    for n, t in lid:
        for w in set(re.findall(r"[\u0600-\u06FF]+", t)):
            idx[w].append(n)

    stats = collections.Counter()
    links, rejects = [], []

    for e in ents:
        q = P.cut_book_prefix(P.norm_ar(e.get("matn_quoted_ar") or ""))
        qt = re.findall(r"[\u0600-\u06FF]+", q)
        if len(qt) < 4:
            stats["short"] += 1
            rejects.append({**e, "reject": "quote-too-short"})
            continue
        rare = sorted(set(qt), key=lambda w: len(idx.get(w, [])))[:3]
        pool = set()
        for w in rare:
            pool.update(idx.get(w, []))
        hits = [n for n in pool if q in by_n[n]]

        tier = None
        hit = None
        if len(hits) == 1:
            tier, hit = "T1", hits[0]
        elif len(hits) > 1:
            nar = narrator(e.get("musnad_narrator_ar"))
            narrowed = [n for n in hits if nar and nar in by_n[n]] if nar else []
            if len(narrowed) == 1:
                tier, hit = "T2", narrowed[0]
            else:
                stats["ambiguous"] += 1
                rejects.append({**e, "reject": "ambiguous",
                                "candidates": hits[:8]})
                continue
        else:
            stats["no-quote-in-lidwa"] += 1
            rejects.append({**e, "reject": "no-quote-in-lidwa"})
            continue

        stats[tier] += 1
        page = int(e["page_index"])
        links.append({
            "link_id": f"ahmad_{SOURCE_ID.split('_')[1]}:{e['entry_no']}",
            "source_book_id": BOOK,
            "source_dataset": "lidwa",
            "source_native_number": int(hit),
            "source_chapter_id": None,
            "target_passage_id": f"turath:14299:page:{page}",
            "target_book_id": BOOK,
            "target_page_index": page,
            "commentary_start_page_index": page,
            "commentary_end_page_index": page,
            "relation": "has_commentary_in",
            "confidence": 0.90 if tier == "T1" else 0.80,
            "method": "exact_substring" if tier == "T1" else "substring+narrator",
            "method_detail": f"{tier}: {len(qt)}-token normalized quote, "
                             f"rare-token block, {len(hits)} substring hit(s)",
            "bab_title": e.get("heading_text_ar"),
            "provenance": ("matn_quoted_ar appears verbatim (harakat stripped, "
                           "isnad removed) in lidwa:ahmad"),
            "created_at": CREATED,
        })

    with open(OUT, "w", encoding="utf-8") as f:
        for r in links:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    with open(REJ, "w", encoding="utf-8") as f:
        for r in rejects:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    print("stats:", dict(stats))
    print(f"links {len(links):,} -> {OUT}")
    print(f"rejects {len(rejects):,} -> {REJ}")
    uniq = len({(r["source_native_number"], r["target_passage_id"]) for r in links})
    print(f"distinct (hadith, page) pairs: {uniq:,}"
          f"   {'OK' if uniq == len(links) else 'DUPLICATES PRESENT'}")


if __name__ == "__main__":
    main()

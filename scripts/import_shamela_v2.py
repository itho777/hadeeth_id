#!/usr/bin/env python3
"""Import the four Shamela books and the cross-book link map into hadeeth-id-v2.

Target DB is `hadeeth-id-v2` (154c5a69), not the legacy `hadeeth-id` (d9558c6d) that
worker/wrangler.toml still binds. v2 is the one holding the real schema (narrators,
sanad, grades, fawaid, text_link) and the 114,833 current rows; the legacy DB only has
books/chapters/hadiths.

Phases
  hadiths  four books -> hadiths          (28,804 rows)
  links    matcher    -> text_link        (92,865 rows)
  verify   read-only counts on the target

hadith_number encoding (column is INTEGER, UNIQUE(source_id, hadith_number))
  adab / mustadrak / daruquthni   '270' -> 270 ; '270#2' -> 270.2
      The fractional form is this project's existing convention for a second row
      carrying the same printed number (77 such rows already in fawaz:bukhari).
  tabarani                        '12.13654' -> 12*100000 + 13654 = 1213654
      Parts 1-12 run continuously 1..13654, but parts 13/17-20/22-25 each restart at 1,
      so a bare number is not unique. reference carries {"part":P,"number":N} for display.

Quota: D1 free tier allows 100,000 rows written per day per database. hadiths (28.8k)
plus links (92.9k) is 121.7k, so `links` is resumable and stops at --link-cap.
State lives in scripts/import_shamela_v2_state.json.
"""
import argparse
import importlib.util
import json
import os
import sys
from pathlib import Path

ROOT = Path("G:/hadeeth_id")
# Layer-per-database on the Workers Free plan: 500 MB per database, 5 GB per account,
# 10 databases per account. hadeeth-id-v2 is at 468.5 MB of its 500 MB wall, so the
# 28,804 Shamela rows and their 92,865 links get their own database instead of
# shovelling the last 31 MB of headroom full. Syarah already targets hadeeth-meta
# (15 MB used) via scripts/hadeeth_v2_syarah_import.py.
SHAMELA_ID = "5e820019-76f3-4f6e-a95b-93287e2aef15"
MAIN_ID = "154c5a69-39af-477d-938a-c0a2cedeb2f7"
BOOKS = ("adab", "mustadrak", "daruquthni", "tabarani")
PART_BOOKS = {"tabarani"}
STATE = ROOT / "scripts" / "import_shamela_v2_state.json"
MAP_OUT = ROOT / "data" / "shamela_map.ndjson"
# Full matcher record per probed row: carries via (jaccard|containment), ambiguity,
# contain/inter/rare_inter and the chargram verdict. hadith_map needs those fields to
# fill method/score/confidence/evidence honestly; the narrow MAP_OUT above keeps only
# what text_link was able to hold.
RAW_OUT = ROOT / "data" / "map_raw.ndjson"


def load_etl(db_id=SHAMELA_ID):
    """Reuse the existing ETL's d1()/flush()/sq()/si() helpers, re-pointed at `db_id`."""
    spec = importlib.util.spec_from_file_location("etl", ROOT / "etl_all_sources.py")
    etl = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(etl)
    etl.CF_TOKEN = os.environ.get("CF_TOKEN", "")
    etl.DB_ID = db_id
    etl.HEADERS = {"Authorization": f"Bearer {etl.CF_TOKEN}", "Content-Type": "application/json"}
    etl.D1_URL = etl.d1_url()
    return etl


def enc_number(book, raw):
    """Printed number string -> (numeric key, reference json, alt, alt_source)."""
    raw = str(raw).strip()
    if book in PART_BOOKS:
        part, _, n = raw.partition(".")
        key = int(part) * 100000 + int(n)
        ref = json.dumps({"part": int(part), "number": int(n)})
        return key, ref, int(n), f"shamela_part_{int(part)}"
    base, _, suffix = raw.partition("#")
    if suffix:
        return int(base) + int(suffix) / 10.0, json.dumps({"number": int(base), "variant": int(suffix)}), None, "shamela_number_collision"
    if "." in base:
        # Already-disambiguated number carried by the fawaz pipeline (e.g. '1390.2',
        # '3604.03'). 77 such rows exist in fawaz:bukhari; keep the value as-is.
        return float(base), json.dumps({"number": base}), None, "fractional"
    return int(base), json.dumps({"number": int(base)}), None, "shamela_number"


def num_sql(v):
    """Render an int/float literally; str() would give '270.2' quoted wrongly for REAL."""
    if isinstance(v, float):
        return repr(v)
    return str(int(v))


def read_book(book):
    p = ROOT / "data" / "sources" / "shamela" / f"{book}.ndjson"
    with open(p, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def phase_hadiths(etl, dry=False):
    stmts = []
    per_book = {}
    seen = set()
    for book in BOOKS:
        rows = read_book(book)
        per_book[book] = len(rows)
        for r in rows:
            num, ref, alt, alt_src = enc_number(book, r["hadith_number"])
            sid = f"shamela:{book}"
            key = (sid, num)
            if key in seen:
                raise SystemExit(f"duplicate key {key} in {book} {r['hadith_number']}")
            seen.add(key)
            stmts.append(
                "INSERT OR IGNORE INTO hadiths "
                "(source_id,book_id,hadith_number,hadith_number_alt,hadith_number_alt_source,"
                "text_ar,reference) VALUES ("
                f"{etl.sq(sid)},{etl.sq(book)},{num_sql(num)},"
                f"{etl.si(alt)},{etl.sq(alt_src)},{etl.sq(r['text_ar'])},{etl.sq(ref)})"
            )
    print("rows to insert:", {k: f"{v:,}" for k, v in per_book.items()}, "total", f"{len(stmts):,}")
    if dry:
        print("dry run — first statement:\n", stmts[0][:400])
        return 0
    etl.flush(stmts, "shamela hadiths")
    return len(stmts)


def build_map():
    """Run the matcher over the full corpus exactly as mode_full does, dump links as ndjson."""
    from collections import Counter
    spec = importlib.util.spec_from_file_location("R", ROOT / "scripts" / "hadeeth_v3_remap_v2_shamela.py")
    R = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(R)
    rows, _counts = R.load()
    meta = [(r[0], r[1], r[2]) for r in rows]
    mats = [R.matn_v2(r[3]) for r in rows]
    skip = {i for i in range(len(mats)) if R.degen(mats[i])}
    R.P.MAX_DF, R.P.RARE_N = R.MDF, R.RN
    inv, keys = R.P.build_index(mats)
    df = Counter()
    for m in mats:
        df.update(R.P.toks(m))
    res = R.match_rows(mats, meta, inv, keys, range(len(mats)), df=df,
                       cand_cap=R.CAP, skip=skip)
    n = 0
    with open(MAP_OUT, "w", encoding="utf-8") as f, open(RAW_OUT, "w", encoding="utf-8") as raw:
        for i, x in res.items():
            ds, book, num = meta[i]
            raw.write(json.dumps({
                "source_id": ds, "book_id": book, "number": str(num),
                "state": x["state"], "via": x.get("via"),
                "score": x.get("score"), "contain": x.get("contain"),
                "inter": x.get("inter"), "rare_inter": x.get("rare_inter"),
                "ambiguous": x.get("ambiguous"), "verdict": x.get("verdict"),
                "chargram": x.get("chargram"),
                "target_dataset": x.get("target_dataset"),
                "target": None if x.get("target") is None else str(x.get("target")),
            }, ensure_ascii=False) + "\n")
            if x["state"] != "matched":
                continue
            tgt_ds, tgt_book = x["target_dataset"].rsplit(":", 1)
            f.write(json.dumps({
                "source_id": ds, "book_id": book, "number": str(num),
                "link_source_id": tgt_ds, "link_book_id": tgt_book,
                "link_number": str(x["target"]),
                "sim": x["score"], "basis": x.get("verdict"),
            }, ensure_ascii=False) + "\n")
            n += 1
    print(f"map written: {MAP_OUT} {n:,} links, skipped {len(skip):,} degenerate")
    return n


def phase_links(etl, cap=None, dry=False):
    rows = [json.loads(line) for line in open(MAP_OUT, encoding="utf-8") if line.strip()]
    st = json.loads(STATE.read_text(encoding="utf-8")) if STATE.exists() else {}
    done = int(st.get("links_done", 0))
    todo = rows[done:]
    if cap is not None:
        todo = todo[: max(0, cap - done)] if cap > done else []
    print(f"links total {len(rows):,} | already done {done:,} | this run {len(todo):,}")
    if dry:
        print("dry run — first statement:\n", "see encoding")
        for r in todo[:1]:
            print(r)
        return 0
    stmts = []
    for r in todo:
        # The map carries dataset and book separately ('fawaz' + 'bukhari'); D1 keys
        # source_id as 'dataset:book'. Composed, the (source_id, hadith_number) PK is
        # collision-free across all 92,865 links; uncomposed it collides 56,067 times.
        src_id = f"{r['source_id']}:{r['book_id']}"
        link_id = f"{r['link_source_id']}:{r['link_book_id']}"
        num, _ref, _alt, _src = enc_number(r["book_id"], r["number"])
        tnum, _tref, _talt, _tsrc = enc_number(r["link_book_id"], r["link_number"])
        stmts.append(
            "INSERT OR IGNORE INTO text_link "
            "(source_id,hadith_number,link_source_id,link_hadith_number,basis,sim) VALUES ("
            f"{etl.sq(src_id)},{num_sql(num)},{etl.sq(link_id)},"
            f"{num_sql(tnum)},{etl.sq(r['basis'])},{'NULL' if r['sim'] is None else repr(float(r['sim']))})"
        )
    etl.flush(stmts, "text_link")
    st["links_done"] = done + len(stmts)
    STATE.write_text(json.dumps(st, indent=2), encoding="utf-8")
    print(f"state: links_done={st['links_done']:,} of {len(rows):,}")
    return len(stmts)


SCHEMA = [
    """CREATE TABLE IF NOT EXISTS hadiths (
        id               INTEGER PRIMARY KEY AUTOINCREMENT,
        source_id        TEXT NOT NULL,
        book_id          TEXT NOT NULL,
        hadith_number    INTEGER NOT NULL,
        hadith_number_alt         INTEGER,
        hadith_number_alt_source  TEXT,
        text_ar          TEXT,
        reference        TEXT,
        UNIQUE(source_id, hadith_number)
    )""",
    "CREATE INDEX IF NOT EXISTS idx_hadiths_source ON hadiths(source_id)",
    """CREATE TABLE IF NOT EXISTS text_link (
        source_id          TEXT    NOT NULL,
        hadith_number      INTEGER NOT NULL,
        link_source_id     TEXT    NOT NULL,
        link_hadith_number INTEGER NOT NULL,
        basis              TEXT,
        sim                REAL,
        PRIMARY KEY (source_id, hadith_number)
    ) WITHOUT ROWID""",
]


def phase_schema(etl):
    for ddl in SCHEMA:
        etl.d1(ddl)
    print(f"schema ready on {etl.DB_ID}: hadiths, text_link")


def phase_verify(etl):
    def q(sql):
        return etl.d1(sql)["result"][0]["results"]

    main = load_etl(MAIN_ID)

    def qm(sql):
        return main.d1(sql)["result"][0]["results"]

    print("== hadiths in the shamela DB ==")
    for r in q("SELECT source_id, COUNT(*) n, MIN(hadith_number) mn, MAX(hadith_number) mx "
               "FROM hadiths GROUP BY 1 ORDER BY 1"):
        print(f"  {r['source_id']:<20}{r['n']:>8,}  {r['mn']}..{r['mx']}")
    print("  total", q("SELECT COUNT(*) n FROM hadiths")[0]["n"])
    print("== text_link ==")
    for r in q("SELECT basis, COUNT(*) n FROM text_link GROUP BY 1 ORDER BY n DESC"):
        print(f"  {str(r['basis']):<10}{r['n']:>8,}")
    print("  total", q("SELECT COUNT(*) n FROM text_link")[0]["n"])
    print("== source-side orphans (link whose own row is missing) ==")
    print(" ", q("SELECT COUNT(*) n FROM text_link t WHERE NOT EXISTS ("
                 "SELECT 1 FROM hadiths h WHERE h.source_id=t.source_id "
                 "AND h.hadith_number=t.hadith_number)")[0]["n"])
    # D1 cannot join across databases, so target validation is a range check: every
    # link target must fall inside the number span that source actually occupies in v2.
    print("== target-side range check against hadeeth-id-v2 ==")
    ranges = {(r["source_id"], r["book_id"]): (r["mn"], r["mx"])
              for r in qm("SELECT source_id, book_id, MIN(hadith_number) mn, MAX(hadith_number) mx "
                          "FROM hadiths GROUP BY 1,2")}
    for sid in ("fawaz", "lidwa", "mjna", "irsyad"):
        rows = q("SELECT link_source_id, MIN(link_hadith_number) mn, MAX(link_hadith_number) mx, "
                 f"COUNT(*) n FROM text_link WHERE link_source_id LIKE '{sid}:%' GROUP BY 1")
        for r in rows:
            src, book = r["link_source_id"].rsplit(":", 1)
            lo, hi = ranges.get((src, book), (None, None))
            if lo is None:
                print(f"  {r['link_source_id']:<22} NO SUCH SOURCE IN V2 ({r['n']:,} links)")
            elif r["mn"] < lo or r["mx"] > hi:
                print(f"  {r['link_source_id']:<22} OUT OF RANGE: links {r['mn']}..{r['mx']} "
                      f"vs v2 {lo}..{hi}")
            else:
                print(f"  {r['link_source_id']:<22} ok  {r['n']:,} links inside {lo}..{hi}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("phase", choices=["schema", "hadiths", "map", "links", "verify", "all"])
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--link-cap", type=int, default=None)
    a = ap.parse_args()
    etl = load_etl()
    if a.phase in ("schema", "all"):
        if a.dry:
            print("dry run — DDL:", *SCHEMA, sep="\n")
        else:
            phase_schema(etl)
    if a.phase in ("hadiths", "all"):
        phase_hadiths(etl, a.dry)
    if a.phase == "map":
        build_map()
    if a.phase in ("links", "all"):
        if a.phase == "all" and not MAP_OUT.exists():
            build_map()
        phase_links(etl, a.link_cap, a.dry)
    if a.phase in ("verify", "all"):
        phase_verify(etl)


if __name__ == "__main__":
    main()

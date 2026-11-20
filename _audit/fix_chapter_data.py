#!/usr/bin/env python3
"""Regenerate the chapter sidecars that the 2026-11-20 audit found wrong.

Sources are never invented:
  * tabarani ranges/titles come from data/chapters/tabarani.json
  * muntaqa titles come from the syarah_muntaqa.db `syarah_chapters` table
  * pseudo-chapter Arabic titles come from the shipped books.ndjson

Run with --upload to write to R2. Without it the script only prints a diff.
"""
import argparse
import json
import sqlite3
import sys
from collections import defaultdict
from pathlib import Path

import requests

ROOT = Path(r"G:/hadeeth_id")
sys.path.insert(0, str(ROOT / "scripts"))
from cf_env import ACCOUNT, BUCKET, token  # noqa: E402
from site_r2 import API, put  # noqa: E402

R2 = "https://pub-075ac3f4a31e4e85a876c26c815ae93d.r2.dev"
H = {"User-Agent": "Mozilla/5.0"}
S = requests.Session()
S.headers.update(H)


def nd(url):
    r = S.get(url, timeout=180)
    r.raise_for_status()
    return [json.loads(line) for line in r.text.splitlines() if line.strip()]


def dump(rows):
    return "\n".join(json.dumps(r, ensure_ascii=False, separators=(",", ":")) for r in rows) + "\n"


def numbers_in(rows, start, end):
    nums = set()
    count = 0
    for r in rows:
        try:
            n = int(r.get("hadith_number") or r.get("hadithnumber") or r.get("n") or 0)
        except (TypeError, ValueError):
            continue
        if start <= n <= end:
            nums.add(n)
            count += 1
    return len(nums), count


books = {b["id"]: b for b in nd(f"{R2}/books.ndjson")}
out = {}

# ---------------------------------------------------------------- tabarani
src = json.loads((ROOT / "data/chapters/tabarani.json").read_text(encoding="utf-8"))
api_rows = nd(f"{R2}/api/tabarani.ndjson")
ordered = sorted(src.items(), key=lambda kv: int(kv[1].get("first_hadith") or 0))
rows = []
for order, (key, v) in enumerate(ordered, 1):
    start = int(v["first_hadith"])
    end = int(v["last_hadith"])
    distinct, row_count = numbers_in(api_rows, start, end)
    rows.append({
        "book_id": "tabarani",
        "id": f"tabarani_c{key}",
        "chapter_number": int(key) if str(key).isdigit() else key,
        "title_id": "",
        "title_en": "",
        "title_ar": v.get("title_ar") or v.get("title") or "",
        "hadith_start": start,
        "hadith_end": end,
        "hadith_count": distinct,
        "row_count": row_count,
        "display_number": order,
    })
out["chapters/tabarani.ndjson"] = rows

# ---------------------------------------------------------------- muntaqa
api_rows = nd(f"{R2}/api/muntaqa.ndjson")
by_ch = defaultdict(list)
for r in api_rows:
    if r.get("chapter_id"):
        by_ch[str(r["chapter_id"])].append(r)
db = ROOT.parent / "Itho/2026/Project/Hadeeth/data source/Syarah From Muse/muntaqa/syarah_muntaqa.db"
db = Path(r"H:/Itho/2026/Project/Hadeeth/data source/Syarah From Muse/muntaqa/syarah_muntaqa.db")
con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
titles = dict(con.execute("SELECT chapter_id, title_native FROM syarah_chapters"))
order = {cid: i for i, (cid, _p, _t) in enumerate(con.execute(
    "SELECT chapter_id, page_index, title_native FROM syarah_chapters ORDER BY page_index, sequence_no"), 1)}
con.close()
rows = []
for cid, group in sorted(by_ch.items(), key=lambda kv: order.get(kv[0], 10**9)):
    nums = sorted(int(r.get("hadith_number") or r.get("n") or 0) for r in group)
    nums = [n for n in nums if n > 0]
    if not nums:
        continue
    rows.append({
        "book_id": "muntaqa",
        "id": f"muntaqa_c{cid}",
        "chapter_number": cid,
        "title_id": "",
        "title_en": "",
        "title_ar": titles.get(cid, ""),
        "hadith_start": nums[0],
        "hadith_end": nums[-1],
        "hadith_count": len(set(nums)),
        "row_count": len(group),
        "display_number": order.get(cid, 0),
    })
out["chapters/muntaqa.ndjson"] = rows

# ---------------------------------------------- pseudo-chapters with Arabic book title
for book, chapter_number in [("maani", 1), ("masabih", 1), ("umdat", 1), ("shah", 0)]:
    path = f"chapters/{book}.ndjson"
    current = nd(f"{R2}/{path}")
    if len(current) != 1:
        print(f"SKIP {book}: expected one pseudo chapter, got {len(current)}")
        continue
    r = dict(current[0])
    r["title_ar"] = books[book].get("title_ar") or r.get("title_ar", "")
    if book == "shah":
        r["title_id"] = "Empat Puluh Hadits"
        r["title_en"] = "Forty Hadiths"
    r["display_number"] = "M"
    out[path] = [r]

# ---------------------------------------------------------------- report / upload
ap = argparse.ArgumentParser()
ap.add_argument("--upload", action="store_true")
args = ap.parse_args()

for key, rows in out.items():
    old = nd(f"{R2}/{key}")
    bad_old = 0
    if key.endswith("tabarani.ndjson"):
        bad_old = sum(1 for r in old if r.get("hadith_count", 0) > r.get("hadith_end", 0) - r.get("hadith_start", 0) + 1)
    if key.endswith("muntaqa.ndjson"):
        bad_old = sum(1 for r in old if str(r.get("chapter_number", "")).startswith("turath:") and not r.get("title_ar"))
    print(f"{key}: rows {len(old)} -> {len(rows)}; old defects {bad_old}; bytes {len(dump(rows).encode('utf-8'))}")

if not args.upload:
    print("dry run; pass --upload to publish")
    raise SystemExit(0)

auth = f"Bearer {token()}"
manifest_path = ROOT / "export_site/_manifest.ndjson"
manifest = [json.loads(line) for line in manifest_path.read_text(encoding="utf-8").splitlines() if line.strip()]
for key, rows in out.items():
    rel = f"export_site/{key}"
    target = ROOT / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(dump(rows).encode("utf-8"))
    item = {"key": key, "path": rel, "bytes": target.stat().st_size, "ct": "application/x-ndjson"}
    put(item, auth)
    for m in manifest:
        if m.get("key") == key:
            m["bytes"] = item["bytes"]
    got = S.get(f"{R2}/{key}", timeout=180).content
    print(f"uploaded+verified {key}: {len(got)} bytes, match={got == target.read_bytes()}")
manifest_path.write_text("\n".join(json.dumps(m, ensure_ascii=False, separators=(",", ":")) for m in manifest) + "\n", encoding="utf-8")
print("updated export_site/_manifest.ndjson")

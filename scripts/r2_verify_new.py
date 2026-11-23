#!/usr/bin/env python3
"""Read-only live check for the four newly published matn books and syarah registry.

Run after `site_r2.py upload`. Uses the public R2 URL only; no credentials.
"""
import importlib.util
import json
import os

import requests

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location("site_r2", os.path.join(ROOT, "scripts", "site_r2.py"))
site = importlib.util.module_from_spec(spec)
spec.loader.exec_module(site)
BASE = site.PUBLIC.rstrip("/")
BOOKS = ("maani", "masabih", "muntaqa", "umdat")


def main():
    bad = 0
    for key in ("catalog.ndjson", "books.ndjson", "syarah/books.ndjson",
                "syarah/editions.ndjson"):
        r = requests.get(f"{BASE}/{key}", timeout=120)
        local = os.path.join(ROOT, "export_site", key)
        same = r.status_code == 200 and os.path.exists(local) and r.content == open(local, "rb").read()
        print(f"{key:28s} HTTP {r.status_code}  bytes={len(r.content):8}  identical={same}")
        bad += 0 if same else 1

    for book in BOOKS:
        idx_url = f"{BASE}/api/{book}_index.ndjson"
        data_url = f"{BASE}/api/{book}.ndjson"
        ri = requests.get(idx_url, timeout=120)
        if ri.status_code != 200:
            print(f"{book}: index HTTP {ri.status_code}")
            bad += 1
            continue
        entries = [json.loads(l) for l in ri.text.splitlines() if l.strip()]
        picks = [entries[0], entries[len(entries) // 2], entries[-1]]
        ok = True
        for e in picks:
            r = requests.get(data_url, headers={"Range": f"bytes={e['s']}-{e['e']}"},
                             timeout=120)
            good = r.status_code == 206
            if good:
                try:
                    rec = json.loads(r.content)
                    good = int(rec["hadith_number"]) == int(e["n"])
                except Exception:
                    good = False
            ok = ok and good
            print(f"  {book:9s} n={e['n']:<6} [{e['s']},{e['e']}] "
                  f"HTTP {r.status_code} match={good}")
        print(f"{book:10s} index rows={len(entries):6}  range check={'PASS' if ok else 'FAIL'}")
        bad += 0 if ok else 1
    print("RESULT:", "PASS" if bad == 0 else f"FAIL ({bad})")
    return bad == 0


if __name__ == "__main__":
    main()

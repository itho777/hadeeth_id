#!/usr/bin/env python3
"""Parallel turath page fetch with a larger worker pool.

Uses Muse's `turath_fetch._fetch_page` so the normalized record shape is
identical to the package's own fetcher; only the degree of concurrency differs.

Usage:
    python scripts/fetch_turath_fast.py <book_id> <out.json> [workers]
"""
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

MUSE = "H:/Itho/2026/Project/Hadeeth/data source/Syarah From Muse/maani/scripts"
sys.path.insert(0, MUSE)
import turath_fetch as tf  # noqa: E402


def main():
    book_id = int(sys.argv[1])
    out = sys.argv[2]
    workers = int(sys.argv[3]) if len(sys.argv) > 3 else 24
    total = 4166 if book_id == 1547 else 5000
    have = {}
    if os.path.exists(out):
        try:
            have = {p["page_id"]: p for p in json.load(open(out, encoding="utf-8"))
                    if isinstance(p.get("page_id"), int)}
        except Exception:
            have = {}
    missing = [p for p in range(1, total + 1) if p not in have]
    print(f"book {book_id}: {len(have)} on disk, {len(missing)} to fetch, {workers} workers",
          flush=True)
    t0 = time.time()
    done = 0
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(tf._fetch_page, book_id, p): p for p in missing}
        for fut in as_completed(futures):
            pid = futures[fut]
            try:
                rec = fut.result()
            except Exception as e:
                print(f"  page {pid}: {e}", flush=True)
                continue
            if rec is not None:
                have[pid] = rec
            done += 1
            if done % 400 == 0:
                pages = [have[k] for k in sorted(have)]
                tmp = out + ".tmp"
                with open(tmp, "w", encoding="utf-8") as fh:
                    json.dump(pages, fh, ensure_ascii=False)
                os.replace(tmp, out)
                print(f"  {done}/{len(missing)} in {time.time()-t0:.0f}s "
                      f"({len(have)} pages on disk)", flush=True)
    pages = [have[k] for k in sorted(have)]
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(pages, fh, ensure_ascii=False)
    print(f"wrote {len(pages)} pages to {out} in {time.time()-t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()

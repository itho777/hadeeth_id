#!/usr/bin/env python3
"""
load_d1_dump.py — Ask D1 for a full SQL export and load it into local SQLite.

The D1 export endpoint returns a signed URL to one .sql file of the whole
database. Downloading that costs no row-read quota, unlike paging the query API
(which bills every row it touches against the daily free-tier limit).

The export must be polled with `current_bookmark` until status is `complete`;
Cloudflare cancels an export that is not polled.

Reads:  Cloudflare D1 REST API
Writes: .dump/<uuid>-<bookmark>.sql
        .dump/hadeeth.sqlite

Usage:
  python scripts/load_d1_dump.py [--keep-sql]
"""

import os, sys, time, sqlite3, argparse
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cf_env import ACCOUNT, DB_UUID, headers as cf_headers

BASE = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT}/d1/database/{DB_UUID}"
H = cf_headers()

ROOT = Path(__file__).resolve().parent.parent
DUMP = ROOT / ".dump"


def start_export():
    r = requests.post(f"{BASE}/export", headers=H,
                      json={"output_format": "polling"}, timeout=60).json()
    if not r.get("success"):
        sys.exit(f"export start failed: {r.get('errors')}")
    return r["result"]["at_bookmark"]


def poll_export(bookmark, timeout_s=1800):
    t0 = time.time()
    while time.time() - t0 < timeout_s:
        r = requests.post(f"{BASE}/export", headers=H,
                          json={"output_format": "polling",
                                "current_bookmark": bookmark}, timeout=180).json()
        res = r.get("result") or {}
        status = res.get("status")
        if status == "complete":
            return res["result"]          # {filename, signed_url}
        if status == "error":
            sys.exit(f"export failed: {res.get('error')}")
        time.sleep(5)
    sys.exit("export timed out")


def download(url, dest: Path):
    with requests.get(url, stream=True, timeout=900) as r:
        r.raise_for_status()
        n = 0
        with open(dest, "wb") as f:
            for chunk in r.iter_content(1 << 20):
                f.write(chunk)
                n += len(chunk)
    return n


def load_sql(sql_path: Path, db_path: Path):
    if db_path.exists():
        db_path.unlink()
    con = sqlite3.connect(db_path)
    con.execute("PRAGMA journal_mode=OFF")
    con.execute("PRAGMA synchronous=OFF")
    con.execute("PRAGMA cache_size=-400000")
    sql = sql_path.read_text(encoding="utf-8", errors="replace")
    con.executescript(sql)
    con.commit()
    counts = {}
    for (name,) in con.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"):
        counts[name] = con.execute(f'SELECT COUNT(*) FROM "{name}"').fetchone()[0]
    con.close()
    return counts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--keep-sql", action="store_true",
                    help="keep the downloaded .sql after loading it")
    args = ap.parse_args()

    DUMP.mkdir(exist_ok=True)
    db_path = DUMP / "hadeeth.sqlite"

    print("=== D1 export -> local SQLite ===")
    print(f"db    : {DB_UUID}")
    bm = start_export()
    print(f"start : {bm}")
    res = poll_export(bm)
    sql_path = DUMP / res["filename"]
    print(f"url   : ready")

    if sql_path.exists() and sql_path.stat().st_size > 0:
        print(f"cache : {sql_path.name} already downloaded")
    else:
        n = download(res["signed_url"], sql_path)
        print(f"down  : {n / 1e6:.1f} MB -> {sql_path.name}")

    t0 = time.time()
    counts = load_sql(sql_path, db_path)
    print(f"load  : {time.time() - t0:.0f}s -> {db_path.name} "
          f"({db_path.stat().st_size / 1e6:.0f} MB)")
    for k, v in counts.items():
        print(f"  {k:16s} {v:>8,}")

    if not args.keep_sql:
        sql_path.unlink(missing_ok=True)
        print(f"clean : removed {sql_path.name}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Publish the repaired riyad/syafii payloads and their byte indexes to R2.

Only the four keys whose bytes changed are written, each remote object is saved
first, and every write is verified by re-fetching the public URL.

    python _audit/publish_rn_fix.py            # dry run
    python _audit/publish_rn_fix.py --write    # back up, upload, verify
"""
import argparse
import hashlib
import sys
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from cf_env import ACCOUNT, BUCKET, token  # noqa: E402

API = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT}/r2/buckets/{BUCKET}/objects"
PUBLIC = "https://cdn.hadeeth.id"
CT = "application/x-ndjson"
BACKUP = ROOT / "_audit/backup_2026-11-26"
IDX = ROOT / "_audit/index_2026-11-26"

PAIRS = [
    ("data/api/riyad.ndjson", "api/riyad.ndjson"),
    ("data/api/syafii.ndjson", "api/syafii.ndjson"),
    (str(IDX / "riyad_index.ndjson"), "api/riyad_index.ndjson"),
    (str(IDX / "syafii_index.ndjson"), "api/syafii_index.ndjson"),
]

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/131.0 Safari/537.36"}


def md5(b):
    return hashlib.md5(b).hexdigest()


def fetch(key):
    r = requests.get(f"{PUBLIC}/{key}", headers=UA, timeout=300)
    return r.content if r.status_code == 200 else None


def main(write):
    auth = f"Bearer {token()}"
    todo = []
    for local_path, key in PAIRS:
        path = Path(local_path) if Path(local_path).is_absolute() else ROOT / local_path
        local = path.read_bytes()
        remote = fetch(key)
        same = remote is not None and md5(remote) == md5(local)
        todo.append((key, path, local, remote, same))
        print(f"{'same' if same else 'CHANGED':8} {key:28} local={len(local):>9} "
              f"remote={len(remote) if remote is not None else 'absent':>9}")

    changed = [t for t in todo if not t[4]]
    print(f"\n{len(changed)} of {len(todo)} keys would change")
    if not write or not changed:
        return

    BACKUP.mkdir(parents=True, exist_ok=True)
    for key, _path, _local, remote, _same in changed:
        if remote is not None:
            dst = BACKUP / key
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_bytes(remote)
    print(f"backed up {sum(1 for t in changed if t[3] is not None)} objects to {BACKUP}")

    for key, _path, local, _remote, _same in changed:
        r = requests.put(f"{API}/{key}", headers={"Authorization": auth, "Content-Type": CT},
                         data=local, timeout=1800)
        if r.status_code not in (200, 201):
            raise SystemExit(f"PUT {key} -> HTTP {r.status_code}: {r.text[:300]}")
        after = fetch(key)
        ok = after is not None and md5(after) == md5(local)
        print(f"{'PUT ok' if ok else 'PUT MISMATCH'}  {key}  bytes={len(local)}")
        if not ok:
            raise SystemExit(f"verification failed for {key}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    main(ap.parse_args().write)

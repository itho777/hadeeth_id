#!/usr/bin/env python3
"""
upload_to_r2.py — Push the export tree to the R2 bucket.

Streams each file from disk (no full read into memory) via the CF REST object API,
verifies the returned size, and re-uploads index.json last so the manifest never
advertises a file that is not there yet.

Layout matches export/:
  <source>/<table>.ndjson.gz      per-edition rows
  book/<book>/<table>.ndjson.gz   merged per-book bundles
  global/<table>.ndjson.gz
  index.json                      manifest
  book/<book>/index.json

Usage:
  python scripts/upload_to_r2.py                # everything
  python scripts/upload_to_r2.py --dry-run      # list only
  python scripts/upload_to_r2.py --only book    # one subtree
"""

import sys, json, time
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cf_env import ACCOUNT, BUCKET, headers as cf_headers

BASE = (f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT}"
        f"/r2/buckets/{BUCKET}/objects")

ROOT = Path(__file__).resolve().parent.parent
WORK = ROOT / "export"

CTYPES = {".gz": "application/gzip", ".json": "application/json"}


def put(local: Path, key: str, tries=4):
    ctype = CTYPES.get(local.suffix, "application/octet-stream")
    size = local.stat().st_size
    for attempt in range(tries):
        try:
            with open(local, "rb") as fh:
                r = requests.put(f"{BASE}/{key}",
                                 headers={**cf_headers(False), "Content-Type": ctype},
                                 data=fh, timeout=300)
            res = r.json()
            if res.get("success"):
                got = res.get("result", {}).get("size")
                if got is not None and int(got) != size:
                    raise RuntimeError(f"size mismatch: sent {size} got {got}")
                return size
            errs = res.get("errors")
            # a 5xx or transient auth blip is worth another go; a 4xx is not
            if r.status_code < 500 and errs:
                raise RuntimeError(f"{r.status_code} {errs}")
            print(f"  retry {attempt + 1}: {r.status_code} {errs}")
        except RuntimeError:
            raise
        except Exception as e:
            print(f"  retry {attempt + 1}: {e}")
        time.sleep(2 ** attempt)
    raise RuntimeError(f"upload failed: {key}")


def main():
    dry = "--dry-run" in sys.argv
    only = None
    if "--only" in sys.argv:
        only = sys.argv[sys.argv.index("--only") + 1]

    if not WORK.exists():
        sys.exit("export/ missing — run the export first")

    files = sorted(p for p in WORK.rglob("*") if p.is_file())
    if only:
        files = [p for p in files if p.relative_to(WORK).parts[0] == only]

    # manifests last, so nothing is advertised before it lands
    files.sort(key=lambda p: (p.name == "index.json", str(p)))

    print(f"=== upload -> r2://{BUCKET} ===")
    print(f"files: {len(files)}  bytes: {sum(p.stat().st_size for p in files) / 1e6:.2f} MB")

    if dry:
        for p in files[:40]:
            print("  ", p.relative_to(WORK).as_posix(), p.stat().st_size)
        if len(files) > 40:
            print(f"   … {len(files) - 40} more")
        return

    done = failed = 0
    total = 0
    for i, p in enumerate(files, 1):
        key = p.relative_to(WORK).as_posix()
        try:
            total += put(p, key)
            done += 1
            if done % 20 == 0 or done == len(files):
                print(f"  {done}/{len(files)}  ({total / 1e6:.1f} MB)", flush=True)
        except Exception as e:
            failed += 1
            print(f"  FAILED {key}: {e}", flush=True)

    print(f"\n=== SUMMARY ===")
    print(f"uploaded: {done}/{len(files)}  {total / 1e6:.2f} MB")
    if failed:
        print(f"failed: {failed}")
        sys.exit(1)

    # verify a sample over the public URL
    r = requests.get("https://cdn.hadeeth.id/index.json",
                     timeout=30)
    print(f"public index.json: HTTP {r.status_code}, "
          f"{len(r.content)} bytes, usable={r.ok}")


if __name__ == "__main__":
    main()

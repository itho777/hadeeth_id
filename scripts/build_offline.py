#!/usr/bin/env python3
"""One-command offline rebuild of the R2 export tree and the D1 import set.

Everything runs from files on disk. No D1 writes, no R2 upload, no network.

    python scripts/build_offline.py            # rebuild + validate
    python scripts/build_offline.py --no-check # rebuild only

Order matters. books_v2.json is the registry site_r2 reads, so the matn
finalizer runs first. site_r2 regenerates export_site but now preserves the
syarah subtree; the syarah builders then refresh that subtree from the archive.
"""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STEPS = [
    ("matn finalize", "scripts/finalize_matn_static.py"),
    ("R2 site build", "scripts/site_r2.py build"),
    ("syarah editions", "scripts/build_syarah_editions.py"),
    ("syarah archive", "scripts/export_syarah_ndjson.py"),
    ("syarah static", "scripts/build_syarah_static.py"),
    ("R2 manifest: syarah", "scripts/manifest_syarah.py"),
    ("R2 manifest: map", "scripts/export_map_ndjson.py"),
    # search/ is built by its own script, which also merges its shards into the
    # manifest. Leaving it out of the chain drops 37 keys (391 MiB) from the
    # manifest, and the next upload prunes them from the bucket.
    ("search pre-index", "scripts/build_preindex.py"),
    ("D1 import set", "scripts/build_d1_offline.py"),
    ("D1 matn staging", "scripts/build_d1_matn_staging.py"),
]


def main():
    no_check = "--no-check" in sys.argv
    for label, cmd in STEPS:
        parts = cmd.split()
        argv = [sys.executable, os.path.join(ROOT, parts[0])] + parts[1:]
        print(f"\n=== {label}: {' '.join(parts)}", flush=True)
        r = subprocess.run(argv, cwd=ROOT)
        if r.returncode:
            print(f"FAILED {label}: exit {r.returncode}", file=sys.stderr)
            return r.returncode
    if not no_check:
        print("\n=== integrity gate", flush=True)
        r = subprocess.run([sys.executable, os.path.join(ROOT, "scripts", "validate_offline.py")],
                           cwd=ROOT)
        return r.returncode
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Add the generated syarah subtree to the R2 upload manifest.

`site_r2.py upload` prunes every remote key that is not in `_manifest.ndjson`.
The syarah tree is produced by `build_syarah_static.py`, not by site_r2, so it
must be registered here or an upload would delete it from the bucket.
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "export_site")
MANIFEST = os.path.join(SITE, "_manifest.ndjson")
SKIP = {".DS_Store", "Thumbs.db"}


def main():
    items = [json.loads(l) for l in open(MANIFEST, encoding="utf-8") if l.strip()]
    have = {m["key"] for m in items}
    added = 0
    for dirpath, _dirs, files in os.walk(os.path.join(SITE, "syarah")):
        for name in sorted(files):
            if name in SKIP:
                continue
            p = os.path.join(dirpath, name)
            rel = os.path.relpath(p, SITE).replace("\\", "/")
            if rel in have:
                continue
            items.append({"path": f"export_site/{rel}", "key": rel,
                          "bytes": os.path.getsize(p), "ct": "application/x-ndjson"})
            have.add(rel)
            added += 1
    items.sort(key=lambda m: m["key"])
    keys = [m["key"] for m in items]
    if len(keys) != len(set(keys)):
        raise SystemExit("manifest: duplicate keys after syarah merge")
    with open(MANIFEST, "w", encoding="utf-8", newline="\n") as fh:
        for m in items:
            fh.write(json.dumps(m, ensure_ascii=False, separators=(",", ":")) + "\n")
    total = sum(m["bytes"] for m in items)
    print(f"manifest: {len(items)} objects, {total/2**20:.2f} MiB, {added} syarah added")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Finish the R2-only migration: upload missing objects, then update manifest."""
import json, sys
from pathlib import Path
import requests

ROOT = Path(r"G:/hadeeth_id")
OUT = ROOT / "export_site"
sys.path.insert(0, str(ROOT / "scripts"))
from cf_env import token  # noqa
from site_r2 import put  # noqa

R2 = "https://pub-075ac3f4a31e4e85a876c26c815ae93d.r2.dev"
H = {"User-Agent": "Mozilla/5.0"}

paths = [OUT / "rawis/profiles.ndjson", OUT / "rawis/profiles_index.ndjson"]
paths += sorted((OUT / "links").glob("*.ndjson"))
for f in ["api/glossary.ndjson", "meta/fawaz_editions.ndjson", "api/topics_counts.ndjson"]:
    paths.append(OUT / f)
for sub in ("by_book", "by_chapter"):
    paths += sorted((OUT / "sources/ahmedbaset" / sub).rglob("*.json"))
paths = [p for p in paths if p.exists()]
print("expected objects", len(paths), flush=True)

missing = []
for p in paths:
    key = p.relative_to(OUT).as_posix()
    try:
        r = requests.head(f"{R2}/{key}", headers=H, timeout=60)
        if r.status_code != 200 or int(r.headers.get("Content-Length", -1)) != p.stat().st_size:
            missing.append((key, p))
    except Exception:
        missing.append((key, p))
print("missing or size mismatch", len(missing), flush=True)

auth = f"Bearer {token()}"
for i, (key, p) in enumerate(missing, 1):
    ct = "application/x-ndjson" if key.endswith(".ndjson") else "application/json"
    put({"key": key, "path": f"export_site/{key}", "bytes": p.stat().st_size, "ct": ct}, auth)
    if i % 50 == 0:
        print("uploaded", i, "/", len(missing), flush=True)
print("upload complete", flush=True)

manifest_path = OUT / "_manifest.ndjson"
manifest = [json.loads(line) for line in manifest_path.read_text(encoding="utf-8").splitlines() if line.strip()]
by_key = {m.get("key"): m for m in manifest}
for p in paths:
    key = p.relative_to(OUT).as_posix()
    ct = "application/x-ndjson" if key.endswith(".ndjson") else "application/json"
    e = by_key.get(key)
    if e:
        e["bytes"] = p.stat().st_size
        e["ct"] = ct
    else:
        e = {"path": f"export_site/{key}", "key": key, "bytes": p.stat().st_size, "ct": ct}
        manifest.append(e)
        by_key[key] = e
manifest_path.write_text("\n".join(json.dumps(m, ensure_ascii=False, separators=(",", ":")) for m in manifest) + "\n", encoding="utf-8")
print("manifest entries", len(manifest), flush=True)

for key in ["rawis/profiles.ndjson", "rawis/profiles_index.ndjson", "links/bukhari.ndjson",
            "api/glossary.ndjson", "meta/fawaz_editions.ndjson", "api/topics_counts.ndjson",
            "sources/ahmedbaset/by_chapter/the_9_books/bukhari/1.json"]:
    r = requests.get(f"{R2}/{key}", headers=H, timeout=120)
    local = OUT / key
    print("verify", key, r.status_code, len(r.content), "match", r.content == local.read_bytes() if local.exists() else "n/a", flush=True)

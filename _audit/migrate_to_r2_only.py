#!/usr/bin/env python3
"""Re-encode CDN JSON into R2-native files and publish them.

Row sets become NDJSON (+ byte offset index where a single row is fetched).
Envelope-shaped AhmedBaset JSON is copied byte-identical to R2: it has
metadata/chapters/hadiths in one object and is not a row set.

Nothing local is deleted. Run without --upload to build + report only.
"""
import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(r"G:/hadeeth_id")
DATA = ROOT / "data"
OUT = ROOT / "export_site"
sys.path.insert(0, str(ROOT / "scripts"))
from cf_env import token  # noqa: E402
from site_r2 import put  # noqa: E402

R2 = "https://pub-075ac3f4a31e4e85a876c26c815ae93d.r2.dev"

outputs = {}  # key -> bytes


def ndjson(rows):
    return ("\n".join(json.dumps(r, ensure_ascii=False, separators=(",", ":")) for r in rows) + "\n").encode("utf-8")


def add(key, data):
    if key in outputs:
        raise RuntimeError(f"duplicate key {key}")
    outputs[key] = data


def rows_from_json(path):
    obj = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(obj, list):
        return obj
    if isinstance(obj, dict):
        rows = []
        for k, v in obj.items():
            if isinstance(v, dict):
                row = {"id": k}
                row.update(v)
                rows.append(row)
            else:
                rows.append({"id": k, "value": v})
        return rows
    return [{"value": obj}]


# ---------------------------------------------------------------- rawi profiles
profiles = sorted((DATA / "rawis/profiles").glob("*.json"))
rows, index, pos = [], [], 0
for p in profiles:
    obj = json.loads(p.read_text(encoding="utf-8"))
    line = json.dumps({"_key": p.stem, "data": obj}, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    index.append({"id": p.stem, "s": pos, "e": pos + len(line) - 1})
    pos += len(line) + 1  # trailing newline
    rows.append(line)
blob = b"\n".join(rows) + b"\n"
add("rawis/profiles.ndjson", blob)
add("rawis/profiles_index.ndjson", ndjson(index))
print(f"profiles: {len(profiles)} files -> {len(blob):,} bytes + index {len(outputs['rawis/profiles_index.ndjson']):,} bytes")

# ---------------------------------------------------------------- links
link_files = sorted((DATA / "links").glob("*.json"))
for p in link_files:
    add(f"links/{p.stem}.ndjson", ndjson(rows_from_json(p)))
print(f"links: {len(link_files)} JSON maps -> {len(link_files)} NDJSON files, "
      f"{sum(outputs[f'links/{p.stem}.ndjson'] and len(outputs[f'links/{p.stem}.ndjson']) for p in link_files):,} bytes")

# ---------------------------------------------------------------- small maps / arrays
for src, key in [
    ("api/glossary.json", "api/glossary.ndjson"),
    ("meta/fawaz_editions.json", "meta/fawaz_editions.ndjson"),
    ("api/topics_counts.json", "api/topics_counts.ndjson"),
]:
    add(key, ndjson(rows_from_json(DATA / src)))
    print(f"{src} -> {key}: {len(outputs[key]):,} bytes")

# ---------------------------------------------------------------- AhmedBaset envelopes
ab = 0
for sub in ("by_book", "by_chapter"):
    for p in sorted((DATA / "sources/ahmedbaset" / sub).rglob("*.json")):
        rel = p.relative_to(DATA).as_posix()
        add(rel, p.read_bytes())
        ab += 1
print(f"AhmedBaset envelopes copied byte-identical: {ab} files, "
      f"{sum(len(v) for k, v in outputs.items() if k.startswith('sources/ahmedbaset/')):,} bytes")

print(f"TOTAL new R2 objects: {len(outputs)}, bytes {sum(len(v) for v in outputs.values()):,}")

ap = argparse.ArgumentParser()
ap.add_argument("--upload", action="store_true")
args = ap.parse_args()
if not args.upload:
    print("dry run; pass --upload to publish")
    raise SystemExit(0)

manifest_path = OUT / "_manifest.ndjson"
manifest = [json.loads(line) for line in manifest_path.read_text(encoding="utf-8").splitlines() if line.strip()]
by_key = {m.get("key"): m for m in manifest}

auth = f"Bearer {token()}"
for key, payload in outputs.items():
    rel = OUT / key
    rel.parent.mkdir(parents=True, exist_ok=True)
    rel.write_bytes(payload)
    item = {"key": key, "path": f"export_site/{key}", "bytes": len(payload), "ct": "application/x-ndjson" if key.endswith(".ndjson") else "application/json"}
    put(item, auth)
    m = by_key.get(key)
    if m:
        m["bytes"] = len(payload)
        m["ct"] = item["ct"]
    else:
        entry = {"path": f"export_site/{key}", "key": key, "bytes": len(payload), "ct": item["ct"]}
        manifest.append(entry)
        by_key[key] = entry

manifest_path.write_text("\n".join(json.dumps(m, ensure_ascii=False, separators=(",", ":")) for m in manifest) + "\n", encoding="utf-8")
print(f"uploaded {len(outputs)} objects; manifest now {len(manifest)} entries")

import requests
H = {"User-Agent": "Mozilla/5.0"}
for key in ["rawis/profiles_index.ndjson", "links/bukhari.ndjson", "api/glossary.ndjson",
            "sources/ahmedbaset/by_book/the_9_books/bukhari.json"]:
    got = requests.get(f"{R2}/{key}", headers=H, timeout=180).content
    print(f"verify {key}: {len(got)} bytes, match={got == outputs[key]}")

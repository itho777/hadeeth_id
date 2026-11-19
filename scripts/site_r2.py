#!/usr/bin/env python3
"""
site_r2.py — build the NDJSON serving tree, upload it, verify it.

Everything the site reads becomes NDJSON. Master hadith files are already
NDJSON and are uploaded byte-identical (they are read with HTTP Range, so they
must NOT be gzipped). Every JSON sidecar is converted: one row per line.

    python scripts/site_r2.py build
    python scripts/site_r2.py upload
    python scripts/site_r2.py verify
"""

import argparse
import ast
import glob
import hashlib
import json
import os
import sys
import time
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cf_env import ACCOUNT, BUCKET, token  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OUT = ROOT / "export_site"
MANIFEST = OUT / "_manifest.ndjson"
API = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT}/r2/buckets/{BUCKET}/objects"
PUBLIC = "https://pub-075ac3f4a31e4e85a876c26c815ae93d.r2.dev"
CT = "application/x-ndjson"


# ---------------------------------------------------------------- conversion

def rows(obj, key_name):
    """Turn a loaded JSON document into a flat list of rows."""
    if isinstance(obj, list):
        return obj
    if isinstance(obj, dict):
        vals = list(obj.values())
        if vals and all(isinstance(v, (dict, list)) for v in vals):
            out = []
            for k, v in obj.items():
                if isinstance(v, dict):
                    row = dict(v)
                    row.setdefault(key_name, k)
                else:
                    row = {key_name: k, "value": v}
                out.append(row)
            return out
        return [obj]
    return [{"value": obj}]


def write_ndjson(path, rows_iter):
    path.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    with path.open("w", encoding="utf-8", newline="\n") as f:
        for row in rows_iter:
            f.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")))
            f.write("\n")
            n += 1
    return n


def convert(src, dst, key_name):
    doc = json.loads(Path(src).read_text(encoding="utf-8"))
    return write_ndjson(Path(dst), rows(doc, key_name))


def build_index_map(src, dst):
    """One row per hadith: {"i","id","n","s","e"} plus optional "c","l".

    The pair lists that shipped before carried position only, so any lookup by
    hadith number, lidwa id or chapter meant scanning the whole file — no
    advantage over plain JSON. This map is content-keyed, and being NDJSON it can
    itself be fetched with Range.
    """
    dst.parent.mkdir(parents=True, exist_ok=True)
    n = pos = 0
    with Path(src).open("rb") as f, dst.open("w", encoding="utf-8", newline="\n") as out:
        for line in f:
            if not line.strip():
                continue
            length = len(line)              # raw bytes, newline included
            row = json.loads(line)
            entry = {
                "i": n + 1,                 # 1-based row ordinal
                "id": row.get("id", n + 1),
                "n": row.get("hadith_number"),
                "s": pos,
                "e": pos + length - 1,      # inclusive, newline included
            }
            if row.get("chapter_id") is not None:
                entry["c"] = row["chapter_id"]
            if row.get("lidwa_id"):
                entry["l"] = row["lidwa_id"]
            out.write(json.dumps(entry, ensure_ascii=False, separators=(",", ":")) + "\n")
            pos += length
            n += 1
    return n


def normalize_tabarani(src, dst):
    """Rebuild tabarani from the complete fawaz edition into the site row shape.

    The file currently served is a 13,555-row Shamela extract using
    `hadithnumber` / `text_ara`. The registry declares 21,850, and
    `data/editions/ara-tabarani.ndjson` has exactly that many rows.
    Returns (row_count, [[start,len], ...]) so the byte index matches the bytes
    actually written.
    """
    dst.parent.mkdir(parents=True, exist_ok=True)
    idx, n, pos = [], 0, 0
    with Path(src).open(encoding="utf-8") as f, dst.open("wb") as out:
        for line in f:
            if not line.strip():
                continue
            r = json.loads(line)
            num = r.get("hadithnumber", r.get("arabicnumber"))
            grades = r.get("grades")
            if isinstance(grades, str):
                try:
                    grades = json.loads(grades)
                except ValueError:
                    grades = []
            ref = r.get("reference")
            if isinstance(ref, str):
                try:
                    ref = ast.literal_eval(ref)
                except (ValueError, SyntaxError):
                    ref = None
            text = r.get("text") or ""
            row = {
                "id": n + 1,
                "book": "tabarani",
                "hadith_number": None if num is None else str(num),
                "arabic_number": None if num is None else str(num),
                "text_ar": text,
                "grades": grades or [],
                "reference": ref,
                "translations": {"ar": [{"source": "fawaz", "text": text}]},
            }
            blob = (json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n").encode("utf-8")
            out.write(blob)
            idx.append([pos, len(blob)])
            pos += len(blob)
            n += 1
    return n, idx


def build():
    if OUT.exists():
        for p in OUT.rglob("*"):
            if p.is_file():
                p.unlink()
    OUT.mkdir(parents=True, exist_ok=True)

    manifest = []

    def add(path, key):
        manifest.append({
            "path": Path(path).relative_to(ROOT).as_posix(),
            "key": key,
            "bytes": os.path.getsize(path),
            "ct": CT,
        })

    report = []

    # 1. master hadith NDJSON — already NDJSON, uploaded byte-identical.
    #    tabarani is the exception: rebuilt in 1b from the complete edition.
    counts = {}
    for p in sorted(glob.glob(str(DATA / "api" / "*.ndjson"))):
        name = Path(p).name
        book = name[: -len(".ndjson")]
        if book == "tabarani":
            continue
        key = f"api/{name}"
        add(p, key)
        n = sum(1 for _ in open(p, "rb"))
        counts[book] = n
        report.append((key, "-", n))

    # 1b. tabarani rebuilt from the complete fawaz edition (21,850 rows)
    dst = OUT / "api" / "tabarani.ndjson"
    n_tab, _ = normalize_tabarani(DATA / "editions" / "ara-tabarani.ndjson", dst)
    add(dst, "api/tabarani.ndjson")
    counts["tabarani"] = n_tab
    report.append(("api/tabarani.ndjson", n_tab, "-"))

    # 2. content-keyed map, one row per hadith: ordinal, id, number, byte range.
    #    Replaces the bare [start,len] pair lists, which were position-only and
    #    satisfied none of the lookup paths (number, lidwa id, chapter).
    for local, key in [(m["path"], m["key"]) for m in manifest
                       if m["key"].startswith("api/") and m["key"].endswith(".ndjson")
                       and not m["key"].endswith("_index.ndjson")]:
        book = Path(key).stem
        dst = OUT / "api" / f"{book}_index.ndjson"
        n = build_index_map(ROOT / local, dst)
        add(dst, f"api/{book}_index.ndjson")
        report.append((f"api/{book}_index.ndjson", n, "-"))

    # 3. book registry — both counts are set from the rows actually shipped, so
    #    the registry can never advertise a number the file does not contain
    books = json.loads((DATA / "books_v2.json").read_text(encoding="utf-8"))
    for b in books:
        actual = counts.get(b.get("id"))
        if actual is not None:
            b["hadiths_count"] = actual
            b["total_hadiths"] = actual
    dst = OUT / "books.ndjson"
    write_ndjson(dst, books)
    add(dst, "books.ndjson")
    report.append(("books.ndjson", len(books), "-"))

    # small bootstrap: same rows minus the verbose fields
    boot = [{k: b[k] for k in ("id", "title_ar", "title_en", "title_id", "author_en",
                               "author_id", "total_hadiths", "hadiths_count",
                               "total_chapters", "grade_summary", "order_index")
            if k in b} for b in books]
    dst = OUT / "catalog.ndjson"
    write_ndjson(dst, boot)
    add(dst, "catalog.ndjson")
    report.append(("catalog.ndjson", len(boot), "-"))

    # 4. chapters
    for p in sorted(glob.glob(str(DATA / "chapters" / "*.json"))):
        book = Path(p).stem
        dst = OUT / "chapters" / f"{book}.ndjson"
        n = convert(p, dst, "chapter_number")
        add(dst, f"chapters/{book}.ndjson")
        report.append((f"chapters/{book}.ndjson", n, "-"))

    # 5. lidwa chapters
    for p in sorted(glob.glob(str(DATA / "lidwa-chapters" / "*.json"))):
        book = Path(p).stem
        doc = json.loads(Path(p).read_text(encoding="utf-8"))
        inner = doc.get("chapters", doc) if isinstance(doc, dict) else doc
        meta = {k: v for k, v in doc.items() if k != "chapters"} if isinstance(doc, dict) else {}
        dst = OUT / "lidwa-chapters" / f"{book}.ndjson"
        write_ndjson(dst, ({**meta, **r} if meta else r for r in rows(inner, "chapter_number")))
        n = sum(1 for _ in dst.open("rb"))
        add(dst, f"lidwa-chapters/{book}.ndjson")
        report.append((f"lidwa-chapters/{book}.ndjson", n, "-"))

    # 6. narrators — the outer key of the source dict IS the narrator id; the
    #    inner "id" field is usually an empty string, so carry the key explicitly
    src = DATA / "rawis" / "active_rawis.min.json"
    dst = OUT / "rawis" / "rawis.ndjson"
    doc = json.loads(src.read_text(encoding="utf-8"))
    dst.parent.mkdir(parents=True, exist_ok=True)
    with dst.open("w", encoding="utf-8", newline="\n") as out:
        n = 0
        for k, v in doc.items():
            row = {"rawi_id": k}
            if isinstance(v, dict):
                row.update(v)
            else:
                row["value"] = v
            out.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
            n += 1
    add(dst, "rawis/rawis.ndjson")
    report.append(("rawis/rawis.ndjson", n, "-"))

    # 7. link graph -> edge list
    doc = json.loads((DATA / "link_graph.json").read_text(encoding="utf-8"))
    edges = doc.get("fawaz_to_lidwa", doc)
    dst = OUT / "link_graph.ndjson"
    write_ndjson(dst, ({"fawaz_id": k, "lidwa_id": v} for k, v in edges.items()))
    n = sum(1 for _ in dst.open("rb"))
    add(dst, "link_graph.ndjson")
    report.append(("link_graph.ndjson", n, "-"))

    # 8. misc singletons
    for name in ("mapping-stats.json", "hotd.json"):
        p = DATA / name
        if not p.exists():
            continue
        doc = json.loads(p.read_text(encoding="utf-8"))
        key = name.replace("-", "_").replace(".json", "") + ".ndjson"
        dst = OUT / key
        write_ndjson(dst, rows(doc, "section"))
        n = sum(1 for _ in dst.open("rb"))
        add(dst, key)
        report.append((key, n, "-"))

    # 9. topics (already NDJSON)
    p = DATA / "api" / "topics_metadata.ndjson"
    if p.exists():
        dst = OUT / "topics.ndjson"
        dst.write_bytes(p.read_bytes())
        add(dst, "topics.ndjson")
        report.append(("topics.ndjson", sum(1 for _ in open(p, "rb")), "-"))

    write_ndjson(MANIFEST, manifest)
    total = sum(m["bytes"] for m in manifest)
    print(f"build: {len(manifest)} objects, {total/1e6:.2f} MB -> export_site/")
    for k, n, extra in report:
        print(f"  {k:44s} rows={n}{(' lines=' + str(extra)) if extra != '-' else ''}")
    return manifest


# ------------------------------------------------------------------- upload

def load_manifest():
    if not MANIFEST.exists():
        raise SystemExit("no manifest — run: python scripts/site_r2.py build")
    return [json.loads(l) for l in MANIFEST.read_text(encoding="utf-8").splitlines() if l]


def put(item, auth):
    path = ROOT / item["path"]
    size = item["bytes"]
    h = {"Authorization": auth, "Content-Type": item["ct"]}
    last = None
    for attempt in range(1, 6):
        try:
            with path.open("rb") as fh:
                r = requests.put(f"{API}/{item['key']}", headers=h, data=fh, timeout=1800)
            if r.status_code in (200, 201):
                got = r.json().get("result", {}).get("size")
                if got is not None and int(got) != size:
                    raise RuntimeError(f"size mismatch local={size} r2={got}")
                return
            if 500 <= r.status_code < 600:
                last = f"HTTP {r.status_code}"
            else:
                raise RuntimeError(f"HTTP {r.status_code}: {r.text[:250]}")
        except requests.RequestException as exc:
            last = str(exc)[:180]
        time.sleep(2 ** attempt)
        print(f"    retry {attempt}/5 {item['key']} ({last})", flush=True)
    raise RuntimeError(f"failed {item['key']}: {last}")


def remote_map():
    """key -> (size, etag) for everything currently in the bucket."""
    auth = {"Authorization": f"Bearer {token()}"}
    base = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT}/r2/buckets/{BUCKET}/objects"
    out, cur = {}, None
    while True:
        p = {"per_page": 1000}
        if cur:
            p["cursor"] = cur
        r = requests.get(base, headers=auth, params=p, timeout=120).json()
        for o in r.get("result", []):
            out[o["key"]] = (int(o["size"]), (o.get("etag") or "").strip('"'))
        cur = (r.get("result_info") or {}).get("cursor")
        if not cur:
            break
    return out


def md5_of(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def upload():
    items = load_manifest()
    items.sort(key=lambda m: (m["bytes"] > 5_000_000, m["key"]))  # small files first
    remote = remote_map()
    auth = f"Bearer {token()}"
    ok = bad = skip = 0
    sent = 0
    t0 = time.time()
    for i, item in enumerate(items, 1):
        rmt = remote.get(item["key"])
        if rmt and rmt[0] == item["bytes"] and rmt[1] == md5_of(ROOT / item["path"]):
            skip += 1
            continue
        try:
            put(item, auth)
            ok += 1
            sent += item["bytes"]
        except Exception as exc:
            bad += 1
            print(f"  FAIL {item['key']}: {exc}", flush=True)
        if i % 15 == 0 or i == len(items):
            el = time.time() - t0
            print(f"  [{i}/{len(items)}] {sent/1e6:.1f} MB  {sent/el/1e6:.1f} MB/s  "
                  f"{ok} ok  {bad} failed", flush=True)
    print(f"upload: {ok}/{len(items)} uploaded, {skip} unchanged/skipped, "
          f"{sent/1e6:.2f} MB, {time.time()-t0:.1f}s, {bad} failed")
    if bad:
        raise SystemExit(1)


# ------------------------------------------------------------------- verify

def list_keys():
    auth = {"Authorization": f"Bearer {token()}"}
    base = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT}/r2/buckets/{BUCKET}/objects"
    out, cur = {}, None
    while True:
        p = {"per_page": 1000}
        if cur:
            p["cursor"] = cur
        r = requests.get(base, headers=auth, params=p, timeout=120).json()
        for o in r.get("result", []):
            out[o["key"]] = int(o["size"])
        cur = (r.get("result_info") or {}).get("cursor")
        if not cur:
            break
    return out


def verify():
    items = load_manifest()
    remote = list_keys()
    missing = [m["key"] for m in items if m["key"] not in remote]
    wrong = [(m["key"], m["bytes"], remote[m["key"]])
             for m in items if m["key"] in remote and remote[m["key"]] != m["bytes"]]
    print(f"objects in batch: {len(items)}   present in R2: {len(items)-len(missing)}")
    print(f"missing: {len(missing)}   size-mismatch: {len(wrong)}")
    for k in missing[:10]:
        print("  MISSING", k)
    for k, a, b in wrong[:10]:
        print(f"  SIZE {k} local={a} r2={b}")

    # byte-identical content check on one converted file + one small sidecar
    print("\ncontent checks:")
    for key in ("catalog.ndjson", "books.ndjson"):
        local = (OUT / key).read_bytes()
        r = requests.get(f"{PUBLIC}/{key}", timeout=120)
        same = r.status_code == 200 and r.content == local
        print(f"  {key:26s} HTTP {r.status_code}  sha256 match={same}")

    # THE load-bearing check: HTTP Range on a master NDJSON
    print("\nrange check (api/bukhari.ndjson):")
    src = DATA / "api" / "bukhari.ndjson"
    with src.open("rb") as f:
        head = f.read(401)
    r = requests.get(f"{PUBLIC}/api/bukhari.ndjson",
                     headers={"Range": "bytes=0-400"}, timeout=120)
    print(f"  status={r.status_code}  bytes={len(r.content)}  identical={r.content == head}")
    ok_range = r.status_code == 206 and r.content == head

    # index alignment: first pair must address the same first record
    print("\nindex alignment (api/bukhari_index.ndjson):")
    idx = json.loads((OUT / "api" / "bukhari_index.ndjson").read_text().splitlines()[0])
    start, length = idx
    r = requests.get(f"{PUBLIC}/api/bukhari.ndjson",
                     headers={"Range": f"bytes={start}-{start+length-1}"}, timeout=120)
    first_local = Path(DATA / "api" / "bukhari.ndjson").read_bytes()[start:start + length]
    print(f"  first pair={idx}  status={r.status_code}  matches local slice={r.content == first_local}")
    ok_idx = r.status_code == 206 and r.content == first_local

    print("\nRESULT:", "PASS" if not missing and not wrong and ok_range and ok_idx else "FAIL")
    return not missing and not wrong and ok_range and ok_idx


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("step", choices=["build", "upload", "verify"])
    a = ap.parse_args()
    {"build": build, "upload": upload, "verify": verify}[a.step]()


if __name__ == "__main__":
    main()

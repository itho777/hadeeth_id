#!/usr/bin/env python3
"""Push pre-computed bge-m3 vectors into the live Meilisearch `hadiths` index.

Run on the InstaBox against 127.0.0.1:7700 (or locally against the router).
Input is the pair produced by scripts/vectorize_hadeeth.py:

    hadeeth_ids.ndjson    one document id per line, in row order
    hadeeth_vectors.bin   raw little-endian float16, shape (len(ids), 1024)

Meilisearch's POST /documents replaces a document rather than merging into it,
so each batch reads the stored documents, attaches `_vectors` and writes the
whole object back. Python stdlib only: no numpy on the box.

    python3 load_vectors_meili.py --setup      # embedder settings only
    python3 load_vectors_meili.py              # push everything, then settings
    python3 load_vectors_meili.py --dry-run
"""
import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from array import array

DIMS = 1024
ROW_BYTES = DIMS * 2
UA = {"User-Agent": "hadith-vector-loader/1.0"}  # Cloudflare 1010 blocks the urllib UA

HOST = os.environ.get("MEILI_HOST", "http://127.0.0.1:7700").rstrip("/")
KEY = os.environ.get("MEILI_MASTER_KEY", "")
INDEX = os.environ.get("MEILI_INDEX", "hadiths")
EMBEDDER = "default"


def call(method, path, body=None, ndjson=False, timeout=300):
    data = None
    headers = dict(UA)
    headers["Authorization"] = "Bearer " + KEY
    if body is not None:
        if ndjson:
            data = body.encode()
            headers["Content-Type"] = "application/x-ndjson"
        else:
            data = json.dumps(body).encode()
            headers["Content-Type"] = "application/json"
    req = urllib.request.Request(HOST + path, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read() or b"{}")


def wait(uid):
    for _ in range(600):
        t = call("GET", f"/tasks/{uid}")
        if t["status"] in ("succeeded", "failed"):
            if t["status"] != "succeeded":
                raise RuntimeError(f"task {uid} failed: {t.get('error')}")
            return t
        time.sleep(0.5)
    raise RuntimeError(f"task {uid} timed out")


def stats():
    s = call("GET", f"/indexes/{INDEX}/stats")
    return s["numberOfDocuments"], s.get("numberOfEmbeddings", 0)


def setup():
    t = call("PATCH", f"/indexes/{INDEX}/settings",
             {"embedders": {EMBEDDER: {"source": "userProvided", "dimensions": DIMS}}})
    wait(t["taskUid"])
    print("embedder settings applied", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ids", default="hadeeth_ids.ndjson")
    ap.add_argument("--vectors", default="hadeeth_vectors.bin")
    ap.add_argument("--batch", type=int, default=300)
    ap.add_argument("--setup", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if args.setup:
        setup()
        return 0

    ids = []
    for line in open(args.ids, encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        # vectorize_hadeeth.py writes one JSON string per line ("id"); tolerate
        # a plain id per line too.
        ids.append(json.loads(line) if line.startswith('"') else line)
    size = os.path.getsize(args.vectors)
    if size != len(ids) * ROW_BYTES:
        sys.exit(f"size mismatch: {size} bytes for {len(ids)} ids "
                 f"(expected {len(ids) * ROW_BYTES})")
    row_of = {doc_id: i for i, doc_id in enumerate(ids)}
    total, emb = stats()
    print(f"{len(ids)} vectors, index has {total} documents, {emb} embeddings", flush=True)
    if args.dry_run:
        print("first ids:", ids[:3])
        return 0

    fh = open(args.vectors, "rb")
    pushed = 0
    t0 = time.time()
    for offset in range(0, total, args.batch):
        docs = call("GET", f"/indexes/{INDEX}/documents?offset={offset}&limit={args.batch}")["results"]
        if not docs:
            break
        lines = []
        for d in docs:
            row = row_of.get(d["id"])
            if row is None:
                continue
            fh.seek(row * ROW_BYTES)
            vec = array("e", fh.read(ROW_BYTES))
            d["_vectors"] = {EMBEDDER: [round(float(x), 6) for x in vec]}
            lines.append(json.dumps(d, ensure_ascii=False))
        if not lines:
            continue
        t = call("POST", f"/indexes/{INDEX}/documents",
                 "".join(l + "\n" for l in lines), ndjson=True)
        wait(t["taskUid"])
        pushed += len(lines)
        if pushed % (args.batch * 10) < args.batch:
            rate = pushed / max(time.time() - t0, 1) * 60
            print(f"  {pushed}/{len(ids)} ({rate:.0f}/min)", flush=True)
    fh.close()
    print(f"pushed {pushed} vectors; applying embedder settings", flush=True)
    setup()
    docs, emb = stats()
    print(f"DONE docs={docs} embeddings={emb}", flush=True)
    return 0 if emb >= pushed else 1


if __name__ == "__main__":
    sys.exit(main())

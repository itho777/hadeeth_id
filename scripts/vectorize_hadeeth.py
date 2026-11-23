#!/usr/bin/env python3
"""Embed the hadeeth.id corpus with BAAI/bge-m3 and save vectors for Meilisearch.

Runs on a free Kaggle/Colab GPU (T4). Reads the same ``api/`` row files the
Meilisearch indexer reads, from the public R2 gateway ``data.hadeeth.id``, so the
document ids produced here are byte-identical to the ids already in the
``hadiths`` index. Nothing is written to any remote store: the run ends with two
files in the working directory.

    hadeeth_vectors_f16.npy   (N, 1024) float16, L2-normalised, row order = ids file
    hadeeth_ids.ndjson        one JSON string per line, same order
    meta.json                 counts, model, dims, per-shard breakdown

Usage (Kaggle/Colab):
    python vectorize_hadeeth.py                # full corpus
    python vectorize_hadeeth.py --limit 2000   # smoke test
    python vectorize_hadeeth.py --dry-run      # walk corpus, no model
"""
import argparse
import hashlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

import numpy as np

BASE = os.environ.get("HADEETH_DATA_URL", "https://data.hadeeth.id")
UA = "hadeeth-indexer/1.0 (+https://hadeeth.id)"
HEADERS = {"User-Agent": UA, "Accept": "application/json, application/x-ndjson, */*"}
NOT_HADITH = {"glossary", "topics_counts"}
SAFE_RE = re.compile(r"[^A-Za-z0-9_-]")

MODEL_NAME = "BAAI/bge-m3"
DIMS = 1024
MAX_SEQ = 512
MAX_CHARS = 2000          # ~500 tokens of mixed Arabic/Latin; the tokenizer truncates anyway
GPU_BATCH = 128
OUT_VEC = "hadeeth_vectors_f16.bin"
OUT_IDS = "hadeeth_ids.ndjson"
OUT_META = "meta.json"


# ---------------------------------------------------------------- corpus walk

def open_remote(path, attempts=4, timeout=120):
    """urlopen with the indexer UA and a short backoff on transient edge failures."""
    last = None
    for i in range(attempts):
        try:
            return urllib.request.urlopen(
                urllib.request.Request(BASE + path, headers=HEADERS), timeout=timeout
            )
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504):
                last = e
                time.sleep(3 * (i + 1))
                continue
            raise
        except (urllib.error.URLError, TimeoutError) as e:
            last = e
            time.sleep(3 * (i + 1))
    raise last


def stream(path):
    with open_remote(path) as r:
        for raw in r:
            line = raw.decode("utf-8", "replace").strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                continue


def safe_id(source, collection, rid):
    """Identical to hadith_sync.py::safe_id — the ids must match the live index."""
    rid = str(rid)
    safe = SAFE_RE.sub("_", rid)
    if safe != rid:
        safe = f"{safe}-{hashlib.sha1(rid.encode('utf-8')).hexdigest()[:8]}"
    return f"{source}__{collection}__{safe}"


def first_nonempty(rec, *names):
    for n in names:
        v = rec.get(n)
        if isinstance(v, str) and v.strip():
            return v.strip()
        if isinstance(v, list) and v:
            return " ".join(str(x) for x in v if isinstance(x, str))
    return ""


def hadith_objects():
    """(collection, source, path) for every hadith row file, in a stable order."""
    listing = json.load(open_remote("/_list"))
    out = []
    for key in sorted(o["key"] for o in listing["objects"]):
        if not key.startswith("api/") or not key.endswith(".ndjson") or key.endswith("_index.ndjson"):
            continue
        parts = key.split("/")
        if len(parts) == 2:
            name, source = parts[1][:-7], "lidwa"
        elif len(parts) == 3 and parts[1] == "fawaz":
            name, source = parts[2][:-7], "fawaz"
        else:
            continue
        if name in NOT_HADITH:
            continue
        out.append((name, source, "/" + key))
    return out, listing


def embed_text(rec):
    parts = [
        first_nonempty(rec, "text_ar", "text_ar_plain"),
        first_nonempty(rec, "text_id"),
        first_nonempty(rec, "text_en"),
    ]
    return " | ".join(p for p in parts if p)[:MAX_CHARS]


# ------------------------------------------------------------------- pipeline

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0, help="stop after N documents")
    ap.add_argument("--dry-run", action="store_true", help="walk the corpus, no model")
    ap.add_argument("--out-dir", default=".")
    args = ap.parse_args()

    objs, listing = hadith_objects()
    print(f"corpus: {listing['count']} objects, {listing['bytes']/1e9:.2f} GB", flush=True)
    print(f"hadith row files: {len(objs)}", flush=True)
    if args.dry_run:
        total = 0
        for name, source, path in objs:
            n = sum(1 for _ in stream(path))
            total += n
            print(f"  {source:6s} {name:14s} {n:>7}", flush=True)
        print(f"TOTAL {total}", flush=True)
        return

    import torch
    from sentence_transformers import SentenceTransformer

    if not torch.cuda.is_available():
        sys.exit("no CUDA device — enable the Kaggle GPU accelerator first")
    device = "cuda"
    print(f"device: {torch.cuda.get_device_name(0)}  fp16", flush=True)

    model = SentenceTransformer(
        MODEL_NAME, device=device, model_kwargs={"torch_dtype": torch.float16}
    )
    model.max_seq_length = MAX_SEQ
    model.eval()

    # Count first so the memmap is exactly the right shape.
    if args.limit:
        total_docs = args.limit
    else:
        total_docs = 0
        for name, source, path in objs:
            n = sum(1 for _ in stream(path))
            total_docs += n
            print(f"  counted {source:6s} {name:14s} {n:>7}", flush=True)
    print(f"total documents: {total_docs:,}", flush=True)

    vec_path = os.path.join(args.out_dir, OUT_VEC)
    ids_path = os.path.join(args.out_dir, OUT_IDS)
    meta_path = os.path.join(args.out_dir, OUT_META)
    mm = np.memmap(vec_path, mode="w+", dtype=np.float16, shape=(total_docs, DIMS))
    ids_fh = open(ids_path, "w", encoding="utf-8")

    row = 0
    started = time.time()
    per_shard = {}
    done = False

    for name, source, path in objs:
        if done:
            break
        shard_start = row
        buf_text, buf_id = [], []

        def flush():
            nonlocal row
            if not buf_text:
                return
            with torch.inference_mode():
                emb = model.encode(
                    buf_text,
                    batch_size=GPU_BATCH,
                    normalize_embeddings=True,
                    show_progress_bar=False,
                    convert_to_numpy=True,
                )
            emb = np.asarray(emb, dtype=np.float32)
            if not np.isfinite(emb).all():
                sys.exit(f"non-finite embedding at row {row} (fp16 overflow) — rerun with --fp32")
            n = emb.shape[0]
            mm[row:row + n] = emb.astype(np.float16)
            for i in buf_id:
                ids_fh.write(json.dumps(i, ensure_ascii=False) + "\n")
            row += n
            buf_text.clear()
            buf_id.clear()

        for rec in stream(path):
            rid = rec.get("id")
            if rid is None:
                continue
            text = embed_text(rec)
            if not text:
                continue
            buf_text.append(text)
            buf_id.append(safe_id(source, name, rid))
            if len(buf_text) >= GPU_BATCH * 4:
                flush()
                if row and row % 5000 < GPU_BATCH * 4:
                    el = time.time() - started
                    rate = row / max(el, 1)
                    eta = (total_docs - row) / max(rate, 1e-9)
                    print(f"  {row:>7,}/{total_docs:,}  {rate:5.1f} docs/s  ETA {eta/60:5.1f} min", flush=True)
            if args.limit and row + len(buf_text) >= args.limit:
                break
        flush()
        per_shard[f"{source}/{name}"] = row - shard_start
        print(f"  shard {source}/{name}: {row - shard_start} rows (total {row:,})", flush=True)
        if args.limit and row >= args.limit:
            done = True

    ids_fh.close()
    mm.flush()
    del mm

    elapsed = time.time() - started
    meta = {
        "model": MODEL_NAME,
        "dims": DIMS,
        "dtype": "float16",
        "normalized": True,
        "max_seq_length": MAX_SEQ,
        "max_chars": MAX_CHARS,
        "docs": row,
        "elapsed_sec": round(elapsed, 1),
        "rate_docs_per_sec": round(row / max(elapsed, 1), 2),
        "corpus_objects": listing["count"],
        "corpus_bytes": listing["bytes"],
        "shards": per_shard,
        "files": {"vectors": OUT_VEC, "ids": OUT_IDS},
        "built_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    with open(meta_path, "w", encoding="utf-8") as fh:
        json.dump(meta, fh, indent=2, ensure_ascii=False)
    print(json.dumps({k: meta[k] for k in ("docs", "elapsed_sec", "rate_docs_per_sec")}, indent=2), flush=True)
    print(f"wrote {vec_path} ({os.path.getsize(vec_path)/1e6:.1f} MB), {ids_path}, {meta_path}", flush=True)


if __name__ == "__main__":
    main()

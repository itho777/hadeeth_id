#!/usr/bin/env python3
"""Validate an offline vector artifact produced by vectorize_hadeeth.py.

Checks the things that silently break a later load: row/id count mismatch,
wrong dtype or shape, unnormalised rows, non-finite values, duplicate or
oversized ids, and coverage against the ids actually present in the corpus.

    python scripts/verify_vectors.py --dir G:/hadeeth_id/vectors
"""
import argparse
import json
import os
import sys
from collections import Counter

import numpy as np

DIMS = 1024
MAX_VECTOR_ID_BYTES = 64          # Cloudflare Vectorize cap


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default=".")
    ap.add_argument("--vectors", default="hadeeth_vectors_f16.bin")
    ap.add_argument("--ids", default="hadeeth_ids.ndjson")
    ap.add_argument("--meta", default="meta.json")
    ap.add_argument("--sample", type=int, default=20000)
    args = ap.parse_args()

    vpath = os.path.join(args.dir, args.vectors)
    ipath = os.path.join(args.dir, args.ids)
    mpath = os.path.join(args.dir, args.meta)

    for p in (vpath, ipath):
        if not os.path.exists(p):
            sys.exit(f"missing {p}")

    ids = []
    bad_json = 0
    with open(ipath, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                ids.append(json.loads(line))
            except json.JSONDecodeError:
                bad_json += 1
    n = len(ids)

    size = os.path.getsize(vpath)
    row_bytes = DIMS * 2
    ok_size = size % row_bytes == 0
    rows = size // row_bytes if ok_size else -1

    problems = []
    if bad_json:
        problems.append(f"{bad_json} unparsable id lines")
    if not ok_size:
        problems.append(f"vector file size {size} not a multiple of {row_bytes}")
    if rows != n:
        problems.append(f"vector rows {rows} != id lines {n}")

    dupes = [k for k, v in Counter(ids).items() if v > 1]
    if dupes:
        problems.append(f"{len(dupes)} duplicate ids, e.g. {dupes[:3]}")

    long_ids = [i for i in ids if isinstance(i, str) and len(i.encode()) > MAX_VECTOR_ID_BYTES]
    if long_ids:
        problems.append(f"{len(long_ids)} ids exceed {MAX_VECTOR_ID_BYTES} bytes, e.g. {long_ids[:3]}")

    non_str = [i for i in ids if not isinstance(i, str)]
    if non_str:
        problems.append(f"{len(non_str)} ids are not strings, e.g. {[type(i).__name__ for i in non_str[:3]]}")

    metrics = {}
    if not problems:
        mm = np.memmap(vpath, mode="r", dtype=np.float16, shape=(rows, DIMS))
        step = max(1, rows // args.sample)
        sample = np.asarray(mm[::step][: args.sample], dtype=np.float32)
        finite = bool(np.isfinite(sample).all())
        norms = np.linalg.norm(sample, axis=1)
        metrics = {
            "sampled": int(sample.shape[0]),
            "finite": finite,
            "norm_min": float(norms.min()),
            "norm_max": float(norms.max()),
            "norm_mean": float(norms.mean()),
            "zero_rows": int((norms == 0).sum()),
            "distinct_rows": int(len({bytes(r[0:8]).hex() for r in sample})),
        }
        if not finite:
            problems.append("non-finite values in sampled rows")
        if metrics["zero_rows"]:
            problems.append(f"{metrics['zero_rows']} all-zero rows in sample")
        if not (0.97 <= metrics["norm_mean"] <= 1.03):
            problems.append(f"mean L2 norm {metrics['norm_mean']:.4f} — rows are not L2-normalised")

    meta = {}
    if os.path.exists(mpath):
        meta = json.load(open(mpath, encoding="utf-8"))

    print(json.dumps({
        "vectors": vpath,
        "bytes": size,
        "rows": rows,
        "ids": n,
        "meta_docs": meta.get("docs"),
        "model": meta.get("model"),
        "dtype": meta.get("dtype"),
        "metrics": metrics,
        "problems": problems,
        "ok": not problems,
    }, indent=2))

    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())

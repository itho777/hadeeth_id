#!/usr/bin/env python3
"""End-to-end proof of the semantic path against the local Meilisearch instance.

Builds a throwaway index from 120 real hadiths, embeds them through the
data.hadeeth.id /_embed endpoint (Workers AI, bge-m3), stores the vectors with a
userProvided embedder, and then compares keyword-only, vector-only and hybrid
results for an Indonesian query.

    python scripts/meili_semantic_probe.py
"""
import json
import os
import time

import requests

MEILI = os.environ.get("PROBE_MEILI", "http://127.0.0.1:7700")
MKEY = os.environ.get("PROBE_MEILI_KEY", "snowy-preindex-key")
EMBED_URL = os.environ.get("HADEETH_EMBED_URL", "https://data.hadeeth.id/_embed")
INDEX = "vectest"

SECRETS = r"G:\PortableHermes\data\instabox\meili\secrets.env"
ROOT = r"G:\hadeeth_id"


def embed_key():
    with open(SECRETS, encoding="utf-8") as fh:
        for line in fh:
            if line.startswith("EMBED_KEY="):
                return line.split("=", 1)[1].strip()
    raise SystemExit("EMBED_KEY not found")


def meili(method, path, body=None, ctype="application/json", timeout=120):
    data = None
    if body is not None:
        data = body if isinstance(body, bytes) else json.dumps(body, ensure_ascii=False).encode()
    r = requests.request(method, MEILI + path, data=data, timeout=timeout,
                         headers={"Authorization": f"Bearer {MKEY}", "Content-Type": ctype})
    r.raise_for_status()
    return r.json()


def wait(uid, label=""):
    for _ in range(600):
        t = meili("GET", f"/tasks/{uid}")
        if t["status"] == "succeeded":
            return t
        if t["status"] == "failed":
            raise SystemExit(f"task failed {label}: {json.dumps(t.get('error'))[:400]}")
        time.sleep(0.3)
    raise SystemExit(f"task timeout {label}")


def embed(texts):
    key = embed_key()
    out = []
    for i in range(0, len(texts), 32):
        chunk = texts[i:i + 32]
        r = requests.post(EMBED_URL, json={"text": chunk},
                          headers={"x-embed-key": key}, timeout=180)
        r.raise_for_status()
        d = r.json()
        if "data" not in d:
            raise SystemExit(f"embed failed: {json.dumps(d)[:300]}")
        out.extend(d["data"])
    return out


def main():
    docs = []
    with open(os.path.join(ROOT, "export_site", "search", "nawawi.ndjson"), encoding="utf-8") as fh:
        for line in fh:
            d = json.loads(line)
            docs.append(d)
    with open(os.path.join(ROOT, "export_site", "search", "bukhari.ndjson"), encoding="utf-8") as fh:
        for i, line in enumerate(fh):
            if i >= 60:
                break
            docs.append(json.loads(line))
    print(f"docs: {len(docs)}")

    try:
        meili("DELETE", f"/indexes/{INDEX}")
        time.sleep(1)
    except Exception:
        pass
    wait(meili("POST", "/indexes", {"uid": INDEX, "primaryKey": "id"})["taskUid"], "create")

    slim = [{
        "id": d["id"], "book": d.get("book"), "number": d.get("number"),
        "text_ar": d.get("text_ar", ""), "text_id": d.get("text_id", ""),
        "text_en": d.get("text_en", ""), "grade": d.get("grade", ""),
    } for d in docs]

    texts = [" | ".join(x for x in (d.get("text_ar"), d.get("text_id"), d.get("text_en")) if x)[:2000]
             for d in docs]
    t0 = time.time()
    vecs = embed(texts)
    print(f"embedded {len(vecs)} in {time.time()-t0:.1f}s  dims={len(vecs[0])}")

    for d, v in zip(slim, vecs):
        d["_vectors"] = {"default": [round(float(x), 6) for x in v]}

    wait(meili("PATCH", f"/indexes/{INDEX}/settings", {
        "searchableAttributes": ["text_ar", "text_id", "text_en"],
        "filterableAttributes": ["book", "grade"],
        "embedders": {"default": {"source": "userProvided", "dimensions": 1024}},
    })["taskUid"], "settings")

    payload = "".join(json.dumps(d, ensure_ascii=False) + "\n" for d in slim)
    wait(meili("POST", f"/indexes/{INDEX}/documents?primaryKey=id", payload.encode(), "application/x-ndjson")["taskUid"], "docs")

    st = meili("GET", f"/indexes/{INDEX}/stats")
    print("index stats:", json.dumps({k: st[k] for k in ("numberOfDocuments", "numberOfEmbeddings")}))

    query = "hadis tentang niat sebelum beramal"
    qvec = embed([query])[0]

    def show(label, body):
        r = requests.post(f"{MEILI}/indexes/{INDEX}/search", json=body, timeout=60,
                          headers={"Authorization": f"Bearer {MKEY}"})
        r.raise_for_status()
        res = r.json()
        hits = res.get("hits", [])
        print(f"\n[{label}] {res.get('estimatedTotalHits', len(hits))} hits")
        for h in hits[:3]:
            print("   ", h["id"], "|", (h.get("text_id") or h.get("text_ar") or "")[:90])

    show("keyword only", {"q": query, "limit": 3, "matchingStrategy": "all"})
    show("vector only", {"vector": qvec, "hybrid": {"embedder": "default", "semanticRatio": 1.0}, "limit": 3})
    show("hybrid 0.5", {"q": query, "vector": qvec, "hybrid": {"embedder": "default", "semanticRatio": 0.5},
                        "limit": 3, "matchingStrategy": "all"})
    # cross-lingual: Indonesian query, no shared keywords with the Arabic text
    xq = "larangan marah"
    show("hybrid cross-lingual 'larangan marah'", {
        "q": xq, "vector": embed([xq])[0],
        "hybrid": {"embedder": "default", "semanticRatio": 0.7}, "limit": 3,
    })


if __name__ == "__main__":
    main()

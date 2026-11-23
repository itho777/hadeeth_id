#!/usr/bin/env python3
"""Daily, quota-bounded bge-m3 backfill for the live Meilisearch `hadiths` index.

Workers AI free tier = 10,000 neurons/day; @cf/baai/bge-m3 = 1,075 neurons per
million input tokens, so one run stays under ~8,300 neurons. Run it from cron
once a day until `done` is true.

Meilisearch POST /documents is a full replace, not a merge, so each batch reads
the stored documents and writes them back whole with `_vectors` attached.
"""
import json
import os
import sys
import time
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
SECRETS = r"G:\PortableHermes\data\instabox\meili\secrets.env"
STATE = r"G:\PortableHermes\data\instabox\meili\vector_state.json"
LOCK = r"G:\PortableHermes\data\instabox\meili\vector_backfill.lock"
INDEX = "hadiths"
EMBEDDER = "default"
DIMS = 1024
UA = {"User-Agent": "hadith-backfill/1.0"}  # Cloudflare 1010 blocks the Python-urllib UA
READ_BATCH = 500
EMBED_BATCH = 32
DEFAULT_MAX = 30000
NEURON_BUDGET = 9000          # free tier allows 10000 neurons/day; keep a margin
NEURONS_PER_MTOK = 1075.0     # @cf/baai/bge-m3
CHARS_PER_TOKEN = 0.85        # measured: ~794 chars/doc ~= 930 bge-m3 tokens/doc

def env():
    out = {}
    with open(SECRETS, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                out[k] = v
    return out

def post(url, body, headers, timeout=180):
    headers = {**UA, **headers}
    data = body if isinstance(body, bytes) else json.dumps(body).encode()
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())

def get(url, headers, timeout=120):
    headers = {**UA, **headers}
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())

def patch(url, body, headers, timeout=120):
    headers = {**UA, **headers}
    data = json.dumps(body).encode()
    req = urllib.request.Request(url, data=data, headers=headers, method="PATCH")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())

def wait_task(router, key, uid, tries=300):
    h = {"Authorization": "Bearer " + key}
    for _ in range(tries):
        t = get(f"{router}/tasks/{uid}", h, 60)
        if t["status"] in ("succeeded", "failed"):
            if t["status"] != "succeeded":
                raise RuntimeError(f"task {uid} failed: {t.get('error')}")
            return t
        time.sleep(0.5)
    raise RuntimeError(f"task {uid} did not finish")

class QuotaExhausted(Exception):
    pass


def embed(texts, embed_key, tries=4):
    body = {"text": texts}
    for i in range(tries):
        try:
            out = post("https://data.hadeeth.id/_embed", body,
                       {"Content-Type": "application/json", "x-embed-key": embed_key})
            if "data" not in out:
                raise RuntimeError(str(out)[:200])
            return out["data"]
        except urllib.error.HTTPError as ex:
            detail = ex.read().decode("utf-8", "replace")
            if ex.code == 502 and "daily free allocation" in detail:
                raise QuotaExhausted(detail[:200])
            if i == tries - 1:
                raise
            time.sleep(3 * (i + 1))
        except Exception:
            if i == tries - 1:
                raise
            time.sleep(3 * (i + 1))

def main():
    max_docs = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_MAX
    if os.path.exists(LOCK):
        print("another backfill still running, exiting")
        return 0
    open(LOCK, "w").write(str(os.getpid()))
    try:
        return run(max_docs)
    finally:
        os.path.exists(LOCK) and os.remove(LOCK)

def run(max_docs):
    e = env()
    router, vkey, ekey = e["ROUTER_URL"].rstrip("/"), e["MEILI_VECTOR_KEY"], e["EMBED_KEY"]
    h = {"Content-Type": "application/json", "Authorization": "Bearer " + vkey}
    mh = {"Content-Type": "application/json", "Authorization": "Bearer " + e["MEILI_MASTER_KEY"]}
    total = get(f"{router}/indexes/{INDEX}/stats", mh)["numberOfDocuments"]
    state = {"offset": 0, "done": False}
    if os.path.exists(STATE):
        state = json.load(open(STATE, encoding="utf-8"))
    if state.get("done"):
        print(f"already complete: {total} documents embedded")
        return 0

    start, processed, t0 = state["offset"], 0, time.time()
    tokens_est = 0.0
    quota_hit = False
    while (processed < max_docs and start + processed < total
           and tokens_est / 1e6 * NEURONS_PER_MTOK < NEURON_BUDGET):
        n = min(READ_BATCH, max_docs - processed, total - start - processed)
        docs = get(f"{router}/indexes/{INDEX}/documents?offset={start + processed}&limit={n}", h)["results"]
        if not docs:
            break
        texts = [" | ".join(x for x in (d.get("text_ar"), d.get("text_id"), d.get("text_en")) if x)[:2000]
                 for d in docs]
        vecs = []
        try:
            for i in range(0, len(texts), EMBED_BATCH):
                vecs.extend(embed(texts[i:i + EMBED_BATCH], ekey))
        except QuotaExhausted as ex:
            quota_hit = True
            print(f"Workers AI daily quota exhausted: {ex}", flush=True)
            break
        assert len(vecs) == len(docs), (len(vecs), len(docs))
        tokens_est += sum(len(t) for t in texts) / CHARS_PER_TOKEN
        lines = []
        for d, v in zip(docs, vecs):
            d["_vectors"] = {EMBEDDER: [round(float(x), 6) for x in v]}
            lines.append(json.dumps(d, ensure_ascii=False))
        task = post(f"{router}/indexes/{INDEX}/documents",
                    "".join(l + "\n" for l in lines).encode(),
                    {**h, "Content-Type": "application/x-ndjson"})
        wait_task(router, vkey, task["taskUid"])
        processed += len(docs)
        state["offset"] = start + processed
        json.dump(state, open(STATE, "w", encoding="utf-8"))

    rate = processed / max(time.time() - t0, 1) * 60
    left = total - state["offset"]
    if quota_hit:
        return 0

    neurons = tokens_est / 1e6 * NEURONS_PER_MTOK
    print(f"embedded {processed} docs this run ({rate:.0f}/min, ~{neurons:.0f} neurons); "
          f"{state['offset']}/{total} total, {left} left")

    if state["offset"] >= total:
        mkey = e["MEILI_MASTER_KEY"]
        t = patch(f"{router}/indexes/{INDEX}/settings",
                  {"embedders": {EMBEDDER: {"source": "userProvided", "dimensions": DIMS}}}, mh)
        wait_task(router, mkey, t["taskUid"])
        stats = get(f"{router}/indexes/{INDEX}/stats", mh)
        state["done"] = True
        json.dump(state, open(STATE, "w", encoding="utf-8"))
        print(f"DONE semantic search live: {stats['numberOfEmbeddings']} embeddings on {INDEX}")
    return 0

if __name__ == "__main__":
    sys.exit(main())

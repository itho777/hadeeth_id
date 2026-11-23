#!/usr/bin/env python3
"""Mirror the public hadeeth R2 corpus into a Kaggle-dataset staging folder."""
import json, os, sys, urllib.request
from concurrent.futures import ThreadPoolExecutor

BASE = "https://data.hadeeth.id"
UA = {"User-Agent": "hadeeth-indexer/1.0 (+https://hadeeth.id)"}
ROOT = r"G:\hadeeth_id\kaggle_dataset"
CORPUS = os.path.join(ROOT, "corpus")


def get(path, timeout=120):
    return urllib.request.urlopen(urllib.request.Request(BASE + path, headers=UA), timeout=timeout)


def main():
    os.makedirs(CORPUS, exist_ok=True)
    listing = json.load(get("/_list"))
    with open(os.path.join(CORPUS, "_list"), "w", encoding="utf-8") as fh:
        json.dump(listing, fh)
    keys = [o["key"] for o in listing["objects"]]
    sizes = {o["key"]: o["size"] for o in listing["objects"]}
    print(f"objects {len(keys)}  bytes {listing['bytes']/1e9:.2f} GB", flush=True)

    done = [0]
    skipped = [0]

    def fetch(key, attempts=4):
        dst = os.path.join(CORPUS, key.replace("/", os.sep))
        want = sizes.get(key, 0)
        if os.path.exists(dst) and want and os.path.getsize(dst) == want:
            skipped[0] += 1
            return
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        tmp = dst + ".part"
        for i in range(attempts):
            try:
                with get("/" + key, timeout=300) as r, open(tmp, "wb") as fh:
                    while True:
                        chunk = r.read(1 << 20)
                        if not chunk:
                            break
                        fh.write(chunk)
                got = os.path.getsize(tmp)
                if want and got != want:
                    raise IOError(f"{key}: got {got} want {want}")
                os.replace(tmp, dst)
                break
            except Exception as e:
                if i == attempts - 1:
                    print(f"  FAIL {key}: {type(e).__name__} {e}", flush=True)
                    failed.append(key)
                    return
        done[0] += 1
        if done[0] % 50 == 0:
            print(f"  fetched {done[0]}  skipped {skipped[0]}", flush=True)

    failed = []
    with ThreadPoolExecutor(max_workers=12) as ex:
        list(ex.map(fetch, keys))
    total = sum(os.path.getsize(os.path.join(dp, f)) for dp, _, fs in os.walk(CORPUS) for f in fs)
    print(f"MIRROR {'OK' if not failed else 'PARTIAL'}  fetched {done[0]}  skipped {skipped[0]}  failed {len(failed)}  size {total/1e9:.2f} GB", flush=True)
    if failed:
        print("FAILED:", " ".join(failed[:20]), flush=True)


if __name__ == "__main__":
    main()

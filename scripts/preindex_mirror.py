#!/usr/bin/env python
"""Mirror the search pre-index into D1 and Meilisearch.

R2 is the source of truth for the shards; this script pushes the same documents
to the other two stores the site is meant to be queryable from.

D1 (--d1)
    A registry table (`preindex_shards`) plus a `preindex_docs` table holding the
    documents themselves. D1 bills writes per row, so the full 153,920-document
    load is a multi-day paced job at the documented 100k/day cap; by default the
    script loads the registry and only the small shards, and `--d1-all` opts in
    to the whole corpus.

Meilisearch (--meili)
    One index (`hadeeth`) fed shard by shard, with the searchable/filterable
    settings the documents were shaped for.

Both are idempotent: shards and documents are written with INSERT OR REPLACE /
a stable primary key, so a re-run corrects rather than duplicates.
"""
import argparse
import json
import os
import sys
import time
from pathlib import Path

import requests

import cf_env

ROOT = Path(__file__).resolve().parent.parent
SEARCH = ROOT / "export_site" / "search"
API = "https://api.cloudflare.com/client/v4/accounts/" + cf_env.ACCOUNT
DB_NAME = "hadeeth-search"

SCHEMA = [
    """CREATE TABLE IF NOT EXISTS preindex_shards (
        key        TEXT PRIMARY KEY,
        book       TEXT NOT NULL,
        dataset    TEXT NOT NULL,
        docs       INTEGER NOT NULL,
        bytes      INTEGER NOT NULL,
        sha256     TEXT NOT NULL,
        loaded_at  TEXT NOT NULL
    )""",
    """CREATE TABLE IF NOT EXISTS preindex_docs (
        id        TEXT PRIMARY KEY,
        book      TEXT NOT NULL,
        dataset   TEXT NOT NULL,
        number    TEXT,
        num       INTEGER,
        chapter   TEXT,
        text_ar   TEXT,
        text_norm TEXT,
        text_id   TEXT,
        text_en   TEXT,
        grade     TEXT,
        url       TEXT
    )""",
    "CREATE INDEX IF NOT EXISTS idx_preindex_docs_book ON preindex_docs(book)",
    "CREATE INDEX IF NOT EXISTS idx_preindex_docs_grade ON preindex_docs(grade)",
]

DOC_COLS = ["id", "book", "dataset", "number", "num", "chapter",
            "text_ar", "text_norm", "text_id", "text_en", "grade", "url"]


def shards():
    path = SEARCH / "_index.ndjson"
    rows = [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines()
            if l.strip()]
    return [r for r in rows if not r["book"].startswith("_")]


def sql_quote(value):
    if value is None:
        return "NULL"
    if isinstance(value, (int, float)):
        return str(value)
    return "'" + str(value).replace("'", "''") + "'"


class QuotaExceeded(Exception):
    """D1's free daily row-write limit (code 7500) is spent for today."""


class D1:
    def __init__(self):
        self.auth = {"Authorization": f"Bearer {cf_env.token()}"}
        self.uuid = self._find_or_create()

    def _find_or_create(self):
        r = requests.get(f"{API}/d1/database", headers=self.auth, timeout=60)
        for db in r.json().get("result", []):
            if db.get("name") == DB_NAME:
                return db["uuid"]
        r = requests.post(f"{API}/d1/database", headers=self.auth,
                          json={"name": DB_NAME}, timeout=120)
        body = r.json()
        if not body.get("success"):
            raise SystemExit(f"cannot create {DB_NAME}: {body.get('errors')}")
        print(f"created D1 database {DB_NAME}: {body['result']['uuid']}")
        return body["result"]["uuid"]

    def query(self, sql, params=None):
        url = f"{API}/d1/database/{self.uuid}/query"
        body = {"sql": sql}
        if params:
            body["params"] = params
        for attempt in range(1, 5):
            r = requests.post(url, headers=self.auth, json=body, timeout=300)
            out = r.json()
            if out.get("success"):
                return out.get("result")
            errors = out.get("errors") or []
            if any(e.get("code") == 7500 for e in errors):
                # Retrying cannot help: the cap resets at 00:00 UTC.
                raise QuotaExceeded(str(errors[0].get("message"))[:200])
            print(f"  ! d1 retry {attempt}: {str(errors)[:200]}")
            time.sleep(2 * attempt)
        raise SystemExit(f"d1 query failed: {sql[:80]}")


def load_registry(db, rows):
    stamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    values = ",".join(
        "(" + ",".join([sql_quote(r["key"]), sql_quote(r["book"]),
                        sql_quote(r["dataset"]), sql_quote(r["docs"]),
                        sql_quote(r["bytes"]), sql_quote(r["sha256"]),
                        sql_quote(stamp)]) + ")"
        for r in rows)
    db.query("INSERT OR REPLACE INTO preindex_shards "
             "(key,book,dataset,docs,bytes,sha256,loaded_at) VALUES " + values)
    print(f"d1 registry: {len(rows)} shard rows")


def loaded_counts(db):
    """(dataset, book) -> rows already in D1. One query for the whole table."""
    res = db.query("SELECT dataset, book, count(*) AS n FROM preindex_docs "
                   "GROUP BY dataset, book")[0]["results"]
    return {(r["dataset"], r["book"]): r["n"] for r in res}


def load_docs(db, rows, chunk=40, resume=False):
    """Insert documents in multi-row chunks; returns (docs, statements).

    With `resume`, shards already complete in D1 are skipped and a partially
    loaded shard restarts after the rows it already holds — the shards are
    written in file order, so the first N rows of a file are the N rows D1 has.
    Raises QuotaExceeded when the daily write cap is reached; every completed
    chunk is already committed, so the next run continues from there.
    """
    have = loaded_counts(db) if resume else {}
    docs = statements = 0
    for shard in rows:
        done = have.get((shard["dataset"], shard["book"]), 0)
        if resume and done >= shard["docs"]:
            print(f"  {shard['key']:34} {shard['docs']:>7,} docs  already loaded")
            continue
        path = ROOT / "export_site" / shard["key"]
        buf = []
        skip = done if resume else 0
        with path.open(encoding="utf-8") as f:
            for i, line in enumerate(f):
                if i < skip or not line.strip():
                    continue
                d = json.loads(line)
                d["text_norm"] = d.pop("text_ar_norm", "")
                buf.append(d)
                if len(buf) == chunk:
                    docs += push(db, buf)
                    statements += 1
                    buf = []
        if buf:
            docs += push(db, buf)
            statements += 1
        print(f"  {shard['key']:34} {shard['docs']:>7,} docs"
              f"{f'  (+{skip:,} already)' if skip else ''}", flush=True)
    print(f"d1 docs: {docs:,} rows in {statements:,} statements "
          f"(~{docs * 2:,} billed writes)")
    return docs


def push(db, buf):
    values = ",".join(
        "(" + ",".join(sql_quote(d.get(c)) for c in DOC_COLS) + ")" for d in buf)
    db.query("INSERT OR REPLACE INTO preindex_docs ("
             + ",".join(DOC_COLS) + ") VALUES " + values)
    return len(buf)


MEILI_SETTINGS = {
    "searchableAttributes": ["text_norm", "text_ar", "text_id", "text_en",
                             "chapter", "rawis", "book_en", "number"],
    "filterableAttributes": ["book", "dataset", "grade", "langs", "chapter",
                             "num"],
    "sortableAttributes": ["num", "number"],
    "displayedAttributes": ["id", "book", "book_en", "book_ar", "dataset",
                            "number", "num", "chapter", "chapter_ar", "text_ar",
                            "text_id", "text_en", "grade", "rawis", "langs",
                            "url"],
    "rankingRules": ["words", "typo", "proximity", "attribute", "sort",
                     "exactness"],
}


def load_meili(base, key, rows, index="hadeeth"):
    auth = {"Authorization": f"Bearer {key}"}
    r = requests.post(f"{base}/indexes", headers=auth,
                      json={"uid": index, "primaryKey": "id"}, timeout=120)
    if r.status_code not in (200, 201, 202, 409):
        raise SystemExit(f"cannot create index: {r.status_code} {r.text[:200]}")
    print(f"meili index {index}: {r.status_code}")
    r = requests.patch(f"{base}/indexes/{index}/settings", headers=auth,
                       json=MEILI_SETTINGS, timeout=120)
    if r.status_code not in (200, 202):
        raise SystemExit(f"settings rejected: {r.status_code} {r.text[:300]}")
    task = r.json().get("taskUid")
    wait(base, key, task)

    total = 0
    for shard in rows:
        path = ROOT / "export_site" / shard["key"]
        blob = path.read_bytes()
        r = requests.post(f"{base}/indexes/{index}/documents", headers={
            **auth, "Content-Type": "application/x-ndjson"}, data=blob,
            timeout=600)
        if r.status_code not in (200, 202):
            raise SystemExit(f"shard {shard['key']} rejected: "
                             f"{r.status_code} {r.text[:200]}")
        wait(base, key, r.json().get("taskUid"))
        total += shard["docs"]
        print(f"  {shard['key']:34} {shard['docs']:>7,} docs  ok", flush=True)
    print(f"meili: {total:,} documents indexed")
    return total


def wait(base, key, task_uid, timeout=1800):
    auth = {"Authorization": f"Bearer {key}"}
    t0 = time.time()
    while time.time() - t0 < timeout:
        r = requests.get(f"{base}/tasks/{task_uid}", headers=auth, timeout=60)
        t = r.json()
        status = t.get("status")
        if status == "succeeded":
            return t
        if status == "failed":
            raise SystemExit(f"meili task failed: {t.get('error')}")
        time.sleep(0.5)
    raise SystemExit("meili task timed out")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--d1", action="store_true")
    ap.add_argument("--d1-all", action="store_true")
    ap.add_argument("--meili", action="store_true")
    ap.add_argument("--only", nargs="*", help="limit to these book ids")
    args = ap.parse_args()

    rows = shards()
    if args.only:
        rows = [r for r in rows if r["book"] in args.only]
    if not rows:
        raise SystemExit("no shards — run scripts/build_preindex.py first")

    if args.d1 or args.d1_all:
        db = D1()
        try:
            for stmt in SCHEMA:
                db.query(stmt)
            load_registry(db, rows)
            small = [r for r in rows if r["docs"] <= 1000]
            target = rows if args.d1_all else small
            print(f"d1 docs: loading {len(target)} shard(s) "
                  f"({sum(r['docs'] for r in target):,} docs)", flush=True)
            load_docs(db, target, resume=args.d1_all)
        except QuotaExceeded as exc:
            print(f"d1 STOP: daily row-write limit reached ({exc})")
            print("d1 STOP: nothing lost — re-run after 00:00 UTC to continue.")
        else:
            got = db.query("SELECT count(*) AS n FROM preindex_docs")[0]["results"]
            print("d1 verify:", got)

    if args.meili:
        base = os.environ.get("MEILI_URL", "http://127.0.0.1:7700").rstrip("/")
        key = os.environ.get("MEILI_KEY", "")
        load_meili(base, key, rows)
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Offline integrity gate for the R2 export and the D1 import set.

Run after build_offline.py. Reads local files only: no D1, no R2, no network.
Exits 1 on any failed check and prints every failure.

    python scripts/validate_offline.py
"""
import gzip
import hashlib
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "export_site")
D1 = os.path.join(ROOT, "export", "d1")
ARCHIVE = os.path.join(ROOT, "export", "syarah")

problems = []
checks = 0


def check(ok, label):
    global checks
    checks += 1
    if not ok:
        problems.append(label)
    return ok


def ndjson_rows(path):
    with open(path, "rb") as fh:
        return sum(1 for line in fh if line.strip())


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def index_contract(data_path, index_path, label):
    if not check(os.path.exists(data_path), f"{label}: data file missing"):
        return
    if not check(os.path.exists(index_path), f"{label}: index missing"):
        return
    size = os.path.getsize(data_path)
    with open(index_path, encoding="utf-8") as fh:
        idx = [json.loads(l) for l in fh if l.strip()]
    if not check(bool(idx), f"{label}: empty index"):
        return
    ok_end = idx[-1]["e"] == size - 1
    check(ok_end, f"{label}: last e={idx[-1]['e']} but file size-1={size-1}")
    raw = open(data_path, "rb").read()
    for j in sorted({0, len(idx) // 2, len(idx) - 1}):
        e = idx[j]
        try:
            row = json.loads(raw[e["s"]:e["e"] + 1].decode("utf-8"))
        except Exception as exc:
            check(False, f"{label}: offset {j} does not decode ({exc})")
            continue
        got = next((row[k] for k in ("id", "link_id", "passage_id", "entry_no")
                    if k in row), None)
        check(str(got) == str(e.get("id", "")),
              f"{label}: offset {j} decoded id mismatch ({got} != {e.get('id')})")


def check_api():
    api = os.path.join(SITE, "api")
    books = sorted(f[:-len("_index.ndjson")] for f in os.listdir(api)
                   if f.endswith("_index.ndjson"))
    check(len(books) >= 28, f"api: only {len(books)} books indexed")
    for b in books:
        p = os.path.join(api, b + ".ndjson")
        if not os.path.exists(p):
            p = os.path.join(ROOT, "data", "api", b + ".ndjson")
        index_contract(p, os.path.join(api, b + "_index.ndjson"), f"api/{b}")
    return books


def check_syarah():
    sy = os.path.join(SITE, "syarah")
    for f in ("books.ndjson", "editions.ndjson"):
        check(os.path.exists(os.path.join(sy, f)), f"syarah: {f} missing")
    if not os.path.isdir(sy):
        return
    pkgs = sorted(d for d in os.listdir(sy) if os.path.isdir(os.path.join(sy, d)))
    check(len(pkgs) == 25, f"syarah: {len(pkgs)} packages, expected 25")
    zero = set()
    ed = os.path.join(sy, "editions.ndjson")
    if os.path.exists(ed):
        for l in open(ed, encoding="utf-8"):
            if l.strip():
                row = json.loads(l)
                if int(row.get("links") or 0) == 0:
                    zero.add(row.get("package_id"))
    for pkg in pkgs:
        d = os.path.join(sy, pkg)
        if pkg in zero and not os.path.exists(os.path.join(d, "syarah_links.ndjson")):
            print(f"  syarah/{pkg}: no links by design", flush=True)
        else:
            index_contract(os.path.join(d, "syarah_links.ndjson"),
                           os.path.join(d, "syarah_links_index.ndjson"),
                           f"syarah/{pkg}/links")
        index_contract(os.path.join(d, "syarah_passages.ndjson"),
                       os.path.join(d, "syarah_passages_index.ndjson"),
                       f"syarah/{pkg}/passages")


def check_link_resolution():
    sy = os.path.join(SITE, "syarah")
    api = os.path.join(SITE, "api")
    pairs = {"muntaqa": "muntaqa", "maani": "maani",
             "masabih": "masabih", "umdat": "umdat"}
    for book, pkg in pairs.items():
        idx = os.path.join(api, f"{book}_index.ndjson")
        if not check(os.path.exists(idx), f"links/{book}: matn index missing"):
            continue
        have = {int(json.loads(l)["n"]) for l in open(idx, encoding="utf-8") if l.strip()}
        p = os.path.join(sy, pkg, "syarah_links.ndjson")
        if not os.path.exists(p):
            ed = os.path.join(sy, "editions.ndjson")
            declared = 0
            if os.path.exists(ed):
                for l in open(ed, encoding="utf-8"):
                    if l.strip():
                        row = json.loads(l)
                        if row.get("package_id") == pkg:
                            declared = int(row.get("links") or 0)
            check(declared == 0, f"links/{book}: syarah links missing but edition "
                                 f"declares {declared}")
            if declared == 0:
                print(f"  links/{book}: 0 links by design", flush=True)
            continue
        nums = set()
        for l in open(p, encoding="utf-8"):
            if l.strip():
                nums.add(json.loads(l)["source_native_number"])
        dangling = nums - have
        check(not dangling, f"links/{book}: {len(dangling)} numbers cannot resolve "
                            f"(first {sorted(dangling)[:5]})")
        print(f"  links/{book}: {len(nums - dangling)}/{len(nums)} resolve", flush=True)


def check_derived_ahmad():
    """Ahmad's links are derived from text, not shipped in Muse's package."""
    src = os.path.join(ROOT, "data", "syarah_ahmad_links.ndjson")
    if not check(os.path.exists(src), "ahmad: derived links file missing"):
        return
    links = [json.loads(l) for l in open(src, encoding="utf-8") if l.strip()]
    have = {str(json.loads(l)["hadith_number"]) for l in
            open(os.path.join(ROOT, "data", "sources", "lidwa", "ahmad.ndjson"),
                 encoding="utf-8") if l.strip()}
    bad = [r["source_native_number"] for r in links
           if str(r["source_native_number"]) not in have]
    check(not bad, f"ahmad: {len(bad)} links point at a missing lidwa hadith "
                   f"(first {bad[:5]})")
    ids = [r["link_id"] for r in links]
    check(len(ids) == len(set(ids)), "ahmad: duplicate link_id in derived links")
    pairs = {(r["source_native_number"], r["target_passage_id"]) for r in links}
    check(len(pairs) == len(links), "ahmad: duplicate (hadith, page) proof pair")
    archive = os.path.join(ARCHIVE, "ahmad", "syarah_links.ndjson.gz")
    if check(os.path.exists(archive), "ahmad: archive links missing"):
        import gzip
        with gzip.open(archive, "rt", encoding="utf-8") as fh:
            n = sum(1 for l in fh if l.strip())
        check(n == len(links), f"ahmad: archive has {n} links, derived has {len(links)}")
    for l in open(os.path.join(SITE, "syarah", "editions.ndjson"), encoding="utf-8"):
        if l.strip():
            row = json.loads(l)
            if row.get("package_id") == "ahmad":
                check(int(row.get("links") or 0) == len(links),
                      f"ahmad: editions declares {row.get('links')} links, "
                      f"derived has {len(links)}")
    print(f"  ahmad: {len(links)} derived links resolve", flush=True)


def check_registry(books):
    cat = [json.loads(l) for l in open(os.path.join(SITE, "catalog.ndjson"), encoding="utf-8")]
    reg = [json.loads(l) for l in open(os.path.join(SITE, "books.ndjson"), encoding="utf-8")]
    bv = json.load(open(os.path.join(ROOT, "data", "books_v2.json"), encoding="utf-8"))
    ids = {r["id"] for r in reg}
    check(len(cat) == len(ids), f"registry: catalog {len(cat)} != books {len(ids)}")
    check(len(bv) == len(ids), f"registry: books_v2 {len(bv)} != books {len(ids)}")
    for b in books:
        check(b in ids, f"registry: {b} has an index but no book entry")
    for b in ("muntaqa", "maani", "masabih", "umdat"):
        check(b in ids, f"registry: new matn book {b} absent")
    # catalog.ndjson counts the served hadeeth_id/mjna/ahmedbaset edition, never
    # the separate shamela:* extraction in data/sources/shamela/. A mismatch here
    # means someone reconciled two editions that must stay separate.
    for row in cat:
        b = row["id"]
        p = os.path.join(SITE, "api", b + ".ndjson")
        if not os.path.exists(p):
            p = os.path.join(ROOT, "data", "api", b + ".ndjson")
        if check(os.path.exists(p), f"registry: {b} matn file missing"):
            n = ndjson_rows(p)
            check(n == int(row["total_hadiths"]),
                  f"registry: catalog {b} declares {row['total_hadiths']} "
                  f"but served file has {n}")


def check_map():
    p = os.path.join(ROOT, "data", "hadith_map.ndjson")
    if not check(os.path.exists(p), "hadith_map: source file missing"):
        return
    n = ndjson_rows(p)
    staged = os.path.join(D1, "hadeeth-id-v2", "hadith_map.ndjson")
    check(n > 0, "hadith_map: empty")
    if check(os.path.exists(staged), "hadith_map: D1 staging copy missing"):
        check(ndjson_rows(staged) == n,
              f"hadith_map: staged {ndjson_rows(staged)} rows, source {n}")
    bad = 0
    with open(p, encoding="utf-8") as fh:
        for i, line in enumerate(fh):
            if not line.strip():
                continue
            r = json.loads(line)
            required = ("lo_dataset", "lo_book", "lo_number",
                        "hi_dataset", "hi_book", "hi_number", "relation", "confidence")
            if not all(k in r for k in required):
                bad += 1
    check(bad == 0, f"hadith_map: {bad} rows missing required fields")


def check_d1():
    p = os.path.join(D1, "MANIFEST.json")
    if not check(os.path.exists(p), "d1: MANIFEST.json missing"):
        return
    m = json.load(open(p, encoding="utf-8"))
    for table, meta in m["tables"].items():
        f = os.path.join(ROOT, meta["path"])
        if not check(os.path.exists(f), f"d1: {table} NDJSON missing"):
            continue
        n = ndjson_rows(f)
        check(n == meta["rows"], f"d1: {table} {n} rows != manifest {meta['rows']}")
        check(sha256(f) == meta["sha256"], f"d1: {table} sha256 mismatch")
        # Every row must have exactly the declared column set, in order.
        with open(f, encoding="utf-8") as fh:
            first = json.loads(fh.readline())
        check(list(first) == meta["columns"], f"d1: {table} column order mismatch")
        # A load into D1 fails the whole batch on a duplicate primary key.
        seen = set()
        dups = 0
        with open(f, encoding="utf-8") as fh:
            for line in fh:
                if line.strip():
                    pk = json.loads(line).get(meta["primary_key"])
                    if pk in seen:
                        dups += 1
                    else:
                        seen.add(pk)
        check(dups == 0, f"d1: {table} has {dups} duplicate {meta['primary_key']} values")
    # Referential integrity that D1 will not enforce for us.
    linked = {}
    for table in ("syarah_passages", "syarah_chapters"):
        meta = m["tables"].get(table)
        if not meta:
            continue
        linked[table] = {json.loads(l)[meta["primary_key"]]
                         for l in open(os.path.join(ROOT, meta["path"]), encoding="utf-8")
                         if l.strip()}
    links_meta = m["tables"].get("syarah_links")
    if links_meta and "syarah_passages" in linked:
        bad_p = bad_c = 0
        with open(os.path.join(ROOT, links_meta["path"]), encoding="utf-8") as fh:
            for line in fh:
                if not line.strip():
                    continue
                r = json.loads(line)
                if r.get("target_passage_id") and r["target_passage_id"] not in linked["syarah_passages"]:
                    bad_p += 1
                cid = r.get("source_chapter_id")
                if cid and "syarah_chapters" in linked and cid not in linked["syarah_chapters"]:
                    bad_c += 1
        check(bad_p == 0, f"d1: {bad_p} links point at a missing passage")
        check(bad_c == 0, f"d1: {bad_c} links point at a missing chapter")
    for name in ("schema.sql",):
        f = os.path.join(ROOT, m["schema"]["path"])
        check(os.path.exists(f) and os.path.getsize(f) == m["schema"]["bytes"],
              f"d1: {name} size mismatch")
    plan = m.get("night_plan")
    if check(plan, "d1: night_plan missing"):
        check(sum(n["rows"] for n in plan) == m["total_rows"],
              "d1: night_plan rows do not add up")
        check(all(n["rows"] <= m["write_budget_per_day"] for n in plan),
              "d1: a night exceeds the write budget")
        check(sum(p["limit"] for n in plan for p in n["parts"]) == m["total_rows"],
              "d1: night_plan parts do not cover every row")
    st = m.get("v2", {}).get("matn_staging")
    if check(st is not None, "d1: matn staging missing from manifest"):
        f = os.path.join(ROOT, st["path"])
        if check(os.path.exists(f), "d1: matn staging NDJSON missing"):
            n = ndjson_rows(f)
            check(n == st["rows"], f"d1: matn staging {n} rows != manifest {st['rows']}")
            check(os.path.getsize(f) == st["bytes"], "d1: matn staging size mismatch")
            with open(f, encoding="utf-8") as fh:
                check(list(json.loads(fh.readline())) == st["columns"],
                      "d1: matn staging column mismatch")


def check_r2_manifest():
    p = os.path.join(SITE, "_manifest.ndjson")
    if not check(os.path.exists(p), "r2: _manifest.ndjson missing"):
        return
    entries = [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]
    keys = {}
    for m in entries:
        keys.setdefault(m["key"], []).append(m)
    dups = [k for k, v in keys.items() if len(v) > 1]
    check(not dups, f"r2 manifest: duplicate keys {dups[:8]}")
    missing = wrong = 0
    for m in entries:
        f = os.path.join(ROOT, m.get("path", ""))
        if not os.path.exists(f):
            missing += 1
        elif os.path.getsize(f) != m.get("bytes"):
            wrong += 1
    check(missing == 0, f"r2 manifest: {missing} listed source files missing")
    check(wrong == 0, f"r2 manifest: {wrong} listed source files wrong size")
    for b in ("muntaqa", "maani", "masabih", "umdat"):
        for key in (f"api/{b}.ndjson", f"api/{b}_index.ndjson"):
            check(key in keys, f"r2 manifest: {key} not listed")
    sy = os.path.join(SITE, "syarah")
    missing_sy = 0
    for dirpath, _dirs, files in os.walk(sy):
        for name in files:
            rel = os.path.relpath(os.path.join(dirpath, name), SITE).replace("\\", "/")
            if rel not in keys:
                missing_sy += 1
    check(missing_sy == 0,
          f"r2 manifest: {missing_sy} syarah files unlisted (upload prune would delete them)")


def main():
    print("offline validation ...", flush=True)
    books = check_api()
    print(f"  api: {len(books)} books checked", flush=True)
    check_syarah()
    check_link_resolution()
    check_derived_ahmad()
    check_registry(books)
    check_map()
    check_d1()
    check_r2_manifest()
    print(f"\n{checks} checks, {len(problems)} problems")
    for p in problems:
        print("  FAIL", p)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())

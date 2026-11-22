#!/usr/bin/env python
"""Build the search pre-index: one slim, engine-ready document per hadith.

The site's row files (`api/<book>.ndjson`) are display payloads: they carry the
whole `translations` dict (every language twice), `gradings` arrays and rawi
objects. A search engine needs none of that, but it does need the text in a
form a query can hit: Arabic with harakat stripped and letters unified, plus
the Indonesian and English renderings, the grade, the narrators, and a URL.

Output (all NDJSON, all under export_site/search/):

  search/<book>.ndjson          canonical (lidwa) documents, 28 collections
  search/fawaz/<book>.ndjson    international-numbering documents, 7 books
  search/_index.ndjson          one row per shard: key, bytes, docs, sha256
  search/_catalog.ndjson        one row per collection: titles, counts, langs

A shard is read from the local build tree when it exists, otherwise streamed
from R2: 18 `api/` row files are in the bucket with no local counterpart, and a
pre-index that silently skipped them would miss 34,377 hadiths.

Documents are Meilisearch-shaped: `id` is the primary key (string), `num` is an
integer for sorting, `dataset` / `book` / `grade` / `langs` are filterable, and
`text_ar_norm` is the searchable Arabic.
"""
import hashlib
import json
import re
import sys
import time
import urllib.request
from pathlib import Path

import site_r2

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "export_site"
SEARCH = OUT / "search"
CACHE = ROOT / ".dump" / "preindex_src"
R2 = "https://pub-075ac3f4a31e4e85a876c26c815ae93d.r2.dev"

# Not hadith rows.
SKIP = {"glossary.ndjson", "topics_counts.ndjson"}

# Dataset labels as the site names them.
LIDWA = "native_lidwa"
FAWAZ = "fawazahmed"

HARAKAT = re.compile(
    "[\u0610-\u061a\u064b-\u065f\u0670\u06d6-\u06ed\u0640]")
AR_DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")
LETTERS = (("أ", "ا"), ("إ", "ا"), ("آ", "ا"), ("ٱ", "ا"),
           ("ى", "ي"), ("ة", "ه"), ("ؤ", "و"), ("ئ", "ي"))


def norm_ar(text):
    """Harakat stripped, alef/ya/ta-marbuta unified, salawat spelled out."""
    if not text:
        return ""
    s = HARAKAT.sub("", str(text))
    s = s.replace("\ufdfa", "صلى الله عليه وسلم").translate(AR_DIGITS)
    for a, b in LETTERS:
        s = s.replace(a, b)
    s = re.sub(r"[^\w\s\u0600-\u06ff]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def rawi_names(value):
    """`rawis` arrives as a list of dicts, or as the string of one."""
    if not value:
        return []
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except ValueError:
            return [value]
    out = []
    for item in value if isinstance(value, list) else [value]:
        name = item.get("name") if isinstance(item, dict) else item
        if name:
            out.append(str(name))
    return out


def load_chapters():
    """(folder, book) -> {chapter_id: (title_en, title_ar)}."""
    out = {}
    for folder in (OUT / "chapters", OUT / "chapters" / "fawaz"):
        if not folder.is_dir():
            continue
        for path in sorted(folder.glob("*.ndjson")):
            if path.name.startswith("_") or path.name.endswith("_index.ndjson"):
                continue
            book = path.name[:-len(".ndjson")]
            table = {}
            with path.open(encoding="utf-8") as f:
                for line in f:
                    if not line.strip():
                        continue
                    row = json.loads(line)
                    cid = row.get("chapter_number", row.get("id"))
                    title = (row.get("title_en") or row.get("title_id")
                             or row.get("title_ar") or "")
                    table[str(cid)] = (title, row.get("title_ar") or "")
            if table:
                out[(folder.name if folder.name != "chapters" else "", book)] = table
    return out


def book_meta():
    """id -> catalogue row, from the site's own catalogue."""
    path = ROOT / "data" / "books_v2.json"
    rows = json.loads(path.read_text(encoding="utf-8"))
    return {r["id"]: r for r in rows}


def open_source(key):
    """Local build tree first, then the bucket. Streamed either way."""
    local = OUT / key
    if local.is_file():
        return local.open("rb"), f"local {key}"
    CACHE.mkdir(parents=True, exist_ok=True)
    cached = CACHE / key.replace("/", "__")
    if not cached.is_file():
        req = urllib.request.Request(f"{R2}/{key}",
                                     headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=300) as res, \
                cached.open("wb") as fh:
            while True:
                chunk = res.read(1 << 20)
                if not chunk:
                    break
                fh.write(chunk)
    return cached.open("rb"), f"r2 {key}"


def make_doc(row, book, dataset, chapters, catalogue):
    cid = row.get("chapter_id")
    title, title_ar = chapters.get(str(cid), ("", "")) if cid is not None else ("", "")
    meta = catalogue.get(book, {})
    ar = row.get("text_ar") or ""
    idn = row.get("text_id") or ""
    eng = row.get("text_en") or ""
    rid = row.get("id", row.get("hadith_number"))
    number = row.get("hadith_number")
    if number is None:
        number = rid
    num = None
    try:
        num = int(re.sub(r"\D", "", str(number)) or 0)
    except (TypeError, ValueError):
        pass
    langs = [name for name, text in (("ar", ar), ("id", idn), ("en", eng)) if text]
    raw_id = f"{dataset}_{book}_{rid}"
    safe_id = re.sub(r"[^A-Za-z0-9_-]", "_", raw_id)
    if safe_id != raw_id:
        # Fawaz has 74 hadith numbers like "402.2"; the suffix keeps those
        # distinct from a literal "402_2" and satisfies Meilisearch's key rule.
        safe_id += "_" + hashlib.sha1(raw_id.encode("utf-8")).hexdigest()[:8]
    doc = {
        "id": safe_id,
        "dataset": dataset,
        "book": book,
        "book_en": meta.get("title_en") or book,
        "book_ar": meta.get("title_ar") or "",
        "number": str(number),
        "num": num,
        "chapter_id": cid,
        "chapter": title,
        "chapter_ar": title_ar,
        "text_ar": ar,
        "text_ar_norm": norm_ar(ar),
        "text_id": idn,
        "text_en": eng,
        "grade": row.get("grade") or "",
        "rawis": rawi_names(row.get("rawis")),
        "langs": langs,
        "url": f"hadith.html?book={book}&id={rid}",
    }
    if dataset != LIDWA:
        doc["url"] += f"&dataset={dataset}"
    return doc


def build(only=None):
    chapters = load_chapters()
    cat = book_meta()
    SEARCH.mkdir(parents=True, exist_ok=True)
    (SEARCH / "fawaz").mkdir(exist_ok=True)

    items = site_r2.load_manifest()
    keys = sorted(i["key"] for i in items
                  if i["key"].startswith("api/") and i["key"].endswith(".ndjson")
                  and not i["key"].endswith("_index.ndjson")
                  and Path(i["key"]).name not in SKIP)
    if only:
        keys = [k for k in keys if Path(k).stem == only]

    shards, catalog = [], []
    for key in keys:
        book = Path(key).stem
        dataset = FAWAZ if key.startswith("api/fawaz/") else LIDWA
        folder = SEARCH / "fawaz" if dataset == FAWAZ else SEARCH
        dst = folder / f"{book}.ndjson"
        ch = chapters.get((("fawaz" if dataset == FAWAZ else ""), book), {})

        handle, origin = open_source(key)
        docs = 0
        with handle, dst.open("w", encoding="utf-8", newline="\n") as out:
            for line in handle:
                if not line.strip():
                    continue
                try:
                    row = json.loads(line)
                except ValueError:
                    continue
                doc = make_doc(row, book, dataset, ch, cat)
                out.write(json.dumps(doc, ensure_ascii=False,
                                     separators=(",", ":")) + "\n")
                docs += 1
        blob = dst.read_bytes()
        rel = dst.relative_to(OUT).as_posix()
        shards.append({"key": rel, "book": book, "dataset": dataset,
                       "docs": docs, "bytes": len(blob),
                       "sha256": hashlib.sha256(blob).hexdigest(),
                       "source": origin})
        catalog.append({"book": book, "dataset": dataset, "docs": docs,
                        "book_en": cat.get(book, {}).get("title_en") or book,
                        "book_ar": cat.get(book, {}).get("title_ar") or "",
                        "chapters": len(ch)})
        print(f"  {rel:34} docs={docs:>7,}  {len(blob)/1048576:>7.2f} MB  ({origin})",
              flush=True)

    idx = SEARCH / "_index.ndjson"
    with idx.open("w", encoding="utf-8", newline="\n") as f:
        for row in shards:
            f.write(json.dumps(row, ensure_ascii=False,
                               separators=(",", ":")) + "\n")
    ctl = SEARCH / "_catalog.ndjson"
    with ctl.open("w", encoding="utf-8", newline="\n") as f:
        for row in catalog:
            f.write(json.dumps(row, ensure_ascii=False,
                               separators=(",", ":")) + "\n")
    shards.append({"key": "search/_index.ndjson", "book": "_index",
                   "dataset": "", "docs": len(shards) - 1,
                   "bytes": idx.stat().st_size,
                   "sha256": hashlib.sha256(idx.read_bytes()).hexdigest(),
                   "source": "generated"})
    shards.append({"key": "search/_catalog.ndjson", "book": "_catalog",
                   "dataset": "", "docs": len(catalog),
                   "bytes": ctl.stat().st_size,
                   "sha256": hashlib.sha256(ctl.read_bytes()).hexdigest(),
                   "source": "generated"})

    total = sum(s["bytes"] for s in shards)
    docs = sum(s["docs"] for s in shards if s["book"] not in ("_index", "_catalog"))
    print(f"\npre-index: {len(shards) - 2} shards, {docs:,} docs, "
          f"{total/1048576:.1f} MB")
    return shards


def merge_manifest(shards):
    """Add the shards to the upload manifest, additively (upload() prunes)."""
    items = site_r2.load_manifest()
    by_key = {i["key"]: i for i in items}
    before = len(by_key)
    for s in shards:
        path = OUT / s["key"]
        by_key[s["key"]] = {"path": f"export_site/{s['key']}",
                            "key": s["key"], "bytes": path.stat().st_size,
                            "ct": "application/x-ndjson"}
    with site_r2.MANIFEST.open("w", encoding="utf-8", newline="\n") as f:
        for k in sorted(by_key):
            f.write(json.dumps(by_key[k], ensure_ascii=False,
                               separators=(",", ":")) + "\n")
    print(f"manifest: {before} -> {len(by_key)} keys (+{len(by_key) - before})")


if __name__ == "__main__":
    t0 = time.time()
    only = sys.argv[1] if len(sys.argv) > 1 else None
    shards = build(only)
    if not only:
        merge_manifest(shards)
    print(f"done in {time.time() - t0:.0f}s")

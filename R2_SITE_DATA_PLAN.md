# hadeeth.id → R2: corrected data plan

## 1. Survey results

### Where the live site gets its data now

`hadeeth.id` is Cloudflare Pages in front of GitHub Pages (response carries
`x-github-request-id`, `server: cloudflare`). `js/api.js` resolves
`baseUrl = <site-root>/data` and reads:

| Path | Use |
|---|---|
| `data/books_v2.json` | book list |
| `data/api/<book>.ndjson` | master hadith rows, fetched by **HTTP Range** |
| `data/api/<book>_ndjson_index.json` | byte-offset index `[[start,len],…]` per hadith |
| `data/api/topics_index.json`, `topics_metadata.ndjson` | topics |
| `data/chapters/<book>.json`, `data/lidwa-chapters/<book>.json` | chapter lists |
| `data/rawis/active_rawis.min.json` | narrator list |
| `data/link_graph.json` | cross-edition links |

Verified live: `GET /data/api/bukhari_ndjson_index.json` → 200 with
`[[0,13166],[13167,15338],…]`; `GET /data/api/bukhari.ndjson` with
`Range: bytes=0-400` → **206 Partial Content**, `access-control-allow-origin: *`.

**The site already runs on NDJSON + byte ranges.** It is not a JSON app waiting to
be converted.

### Offline source tree (`G:/hadeeth_id/data/`)

| Path | Size | Role |
|---|---|---|
| `sources/` | 4,021.8 MB, 653,548 files | **master upstream inputs**, 15 collectors: `fawaz_repo`, `fawaz_api`, `lidwa`, `mjna`, `irsyadulibad`, `ahmedbaset`, `atif_hf`, `shamela`, `usm_*`, `openhadith`, `kaggle`, … |
| `api/` | 719.5 MB, 271 files | **live serving set**: 25 master `.ndjson` + 25 byte indexes + per-book dirs |
| `editions/` | 533.7 MB, 209 files | per-language `.json` + `.ndjson` editions (`ara-`, `ind-`, `eng-`, …) |
| `raw_baseline/` | 343.6 MB, 54 files | fawaz Arabic + translation JSON, keyed by book and language |
| `supabase/` | 299.2 MB, 5 files | `search_index.csv` (287 MB), `rawis.csv`, `hadith_rijal_lidwa.csv`, `schema.sql` |
| `fawaz_combined/` | 199.5 MB, 36 files | per-book combined JSON + XLSX |
| `commentaries/` | 147.3 MB, 30,080 files | per-hadith commentary |
| `rawis/`, `hadiths/`, `links/`, `chapters/`, `lidwa-chapters/` | ~120 MB | supporting indexes |
| root | small | `books_v2.json`, `books.json`, `link_graph.json`, `mapping-stats.json`, `hotd.json` |
| root | 7.1 MB | `backup_grades_v1.json` (68,929 rows), `backup_narrators_v1.json` (8,624 rows) |
| `.dump/`, `data/lidwa_work.db`, `data/backup/*.db` | ~1.1 GB | local DB snapshots (gitignored, not site data) |

### What is in D1 (`154c5a69-…`), from local snapshot

| table | rows | note |
|---|---:|---|
| `hadiths` | 106,340 | 25 `source_id` editions × 18 books; 8 `text_*` language columns |
| `sanad` | 87,612 | **9 `lidwa:*` editions only**; `narrators` is a comma-delimited id string |
| `hadith_bab` | 62,169 | lidwa only; joins on `kitab_number` + `bab_number` |
| `grades` | 74,922 | keyed on `book_id` + `hadith_number`, not source |
| `chapters` | 16,475 | |
| `narrators` | 8,624 | |
| `kitab` | 461 | |
| `text_link` | 321 | sparse cross-edition map |
| `fawaid` | 115 | |
| `imam_bio` | 9 | |
| `audio`, `syarah_links` | 0 | empty |

### Which is most complete

Neither dominates — they are complete on different axes:

- **`data/api/` (live): most complete by *book coverage and record richness*.**
  91,549 rows across 27 books. One record already merges `text_ar`, `text_id`,
  `text_en`, `lidwa_id[]`, `rawis[]` (with narrator names), `gradings`,
  `translations{}`. Contains books **absent from D1**: `tabarani` 13,555,
  `ahmad` 26,363, `mishkat` 4,428, `bulugh` 1,767, `adab` 1,326, `shamail` 402,
  `shah` 40, `riyad_arab` 850.
- **D1: most complete by *edition provenance and language columns*.** 25 explicit
  `source_id`s, 8 separate `text_*` columns, plus dedicated `sanad`, `hadith_bab`,
  `grades`, `text_link`, `narrators` tables. But only 18 books.
- **`data/raw_baseline/`: exact fawaz upstream.** Its Arabic row counts match D1's
  `fawaz:*` rows exactly for all 7 comparable books (5,274 / 7,589 / 4,343 /
  1,858 / 7,563 / 5,765 / 3,998). It also has `ara-tabarani.json` with 21,850
  hadiths — more than the 13,555 currently in `data/api/tabarani.ndjson`.

**Decision:** for the static site, the live `data/api/` tree is the right payload.
It is the only set already shaped for the site's Range-based reader and it covers
more books. D1 stays the provenance/reference store; no new data is invented.

## 2. Mistakes in the earlier attempt

1. Pulled a 437 MB SQL dump from D1 instead of reading `data/` — wrong direction.
2. Invented a new `book/<book>/<table>.ndjson.gz` schema and a 185 MB upload that
   the current UI does not read.
3. Gzipped everything. The byte-offset indexes address **uncompressed** bytes, so
   gzipping the master NDJSON would break every Range request.
4. Did a deep search of D1 quota behaviour before the trivial check of what the
   site and disk already had.

## 3. Upload plan

**Everything is NDJSON. One row per line, nothing gzipped.** Master hadith files
are already NDJSON and go up byte-identical, because the byte-offset indexes
address uncompressed bytes and are read with HTTP `Range`.

```
catalog.ndjson                 24 rows   bootstrap registry
books.ndjson                   24 rows   full book metadata
api/<book>.ndjson              25 files  master hadith rows  (NO gzip, Range-read)
api/<book>_index.ndjson        25 files  one [start,len] pair per line
chapters/<book>.ndjson         18 files
lidwa-chapters/<book>.ndjson   19 files
rawis/rawis.ndjson             14,298 rows
link_graph.ndjson              34,949 edges  {"fawaz_id","lidwa_id"}
topics.ndjson                  14 rows
mapping_stats.ndjson, hotd.ndjson
```

Total: **94 objects, 466.74 MB.**

Rules:

- Every key ends `.ndjson`. Content type `application/x-ndjson`.
- Do **not** gzip anything read with `Range`.
- Small files first, master NDJSON last, so a partial run never advertises data
  it does not have.
- Stream from disk; retry 5× with backoff; fail loudly on any non-2xx; verify the
  size R2 echoes back.

Implementation: `scripts/site_r2.py` (`build` / `upload` / `verify`). The build
step writes `export_site/_manifest.ndjson` — the batch itself is NDJSON.

## 4. Result — verified

```
objects in batch: 94   present in R2: 94
missing: 0             size-mismatch: 0
catalog.ndjson        HTTP 200  sha256 match=True
books.ndjson          HTTP 200  sha256 match=True
Range api/bukhari.ndjson  bytes=0-400   -> 206, body identical
index first pair [0,13166] Range -> 206, matches local slice
small files full sha256 match : 81
large files head+tail match   : 13
bad                           : 0
RESULT: PASS
```

## 5. Open items

1. **Resolved — stale gz tree deleted.** 108 objects (185.41 MB) from the earlier
   D1-derived attempt removed; bucket now holds only the 94 NDJSON objects.
   Regenerable at any time with `scripts/load_d1_dump.py` (`.dump/hadeeth.sqlite`
   is still on disk).
2. **Resolved — `tabarani` rebuilt from the complete source.**
   `api/tabarani.ndjson` now comes from `data/editions/ara-tabarani.ndjson`:
   **21,850 rows**, matching `total_hadiths` in the registry. Keys normalised to
   the site shape (`text_ar`, `hadith_number`, `id`, `translations.ar`), and
   `grades` / `reference` parsed from their embedded string form. The index is
   regenerated from the bytes actually written and sums exactly to the file size
   (29,521,363). Range requests verified on first, middle and last records.

   Caveat worth knowing: the source reuses numbers — 21,850 rows but only 13,555
   distinct `hadith_number` values, with up to 10 hadiths sharing one number.
   Records are addressable because each carries a unique sequential `id`, and
   `getHadith` matches on `id`. The previously served 13,555-row file was a
   different Shamela extraction, not a strict subset: its text for number 1 does
   not match the fawaz text for number 1.
3. **Syarah deferred.** `data/commentaries/` holds per-hadith files with
   `syarah_ar` / `syarah_en`; eight books already carry syarah inline (`adab`,
   `bulugh`, `mishkat`, `nawawi`, `qudsi`, `riyad`, `shah`, `shamail`). Waiting
   for the Muse import to finish before its own batch.
4. **UI not touched.** `js/api.js` still points at `/data`, and fetches the index
   as `<book>_ndjson_index.json` while R2 now serves `<book>_index.ndjson`.
   Both change in the same UI pass. Note `getHadith` expects index entries to be
   objects with `id` / `start` / `end`, but every index on disk is an array of
   `[start, len]` pairs — so today it silently falls through to
   `fetchNdjsonFull`. Fixing that is the biggest single win in the UI pass.
5. **Registry `total_hadiths` vs `hadiths_count`.** Thirteen books still differ
   (e.g. `bukhari` 7,563 declared vs 6,999 shipped). `hadiths_count` is now
   written from the rows actually uploaded, so it can no longer drift; the two
   numbers differing means the served edition is an abridgement of the declared
   collection, which predates this batch.

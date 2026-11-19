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
api/<book>_index.ndjson        25 files  content map, one row per hadith
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

## 5. The index

NDJSON has no index of any kind — it is lines of JSON, so reading row N means
scanning N lines. Everything that makes random access possible is a sidecar.

The 25 files previously served (`<book>_ndjson_index.json`) were bare
`[start, len]` pairs in file order: position only, no identity. That is not just
slow, it is **wrong** — for 11 of the 25 books the row ordinal does not equal the
hadith number (Bukhari's hadith 5 sits at row 6; its last hadith 6999 is row
6999 but carries `id` 7554), so `ranges[n-1]` returns a different hadith than the
one requested.

`api/<book>_index.ndjson` replaces them. One row per hadith, content-keyed:

```json
{"i":6,"id":6,"n":5,"s":120082,"e":131957}
```

| field | meaning |
|---|---|
| `i` | 1-based row ordinal in the master file |
| `id` | the record's own `id` |
| `n` | `hadith_number` as a string, the number a reader asks for |
| `s`,`e` | inclusive byte range in the master file, newline included |
| `c` | `chapter_id`, only where the record has one |
| `l` | `lidwa_id`, only where the record has one |

99,844 rows across 25 books, 6.36 MB total. Because it is NDJSON it can itself be
fetched with Range. Verified on all 25 books: byte ranges contiguous, last entry
ends exactly at file size − 1, three records per book reconstructed and matched
by `id`. Verified through the public R2 URL with real lookups — index fetch 200,
`Range` on the master file 206, returned `hadith_number` equal to the requested
number, real Arabic text.

## 6. Open items

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
4. **Resolved — UI wired to R2.** `js/api.js` uses R2 for the whole serving
   set: registry, chapters, narrators, hadith lookup, chapter runs, topics.
   Only `commentaries/` and the edition indexes still resolve from the site's
   own `/data` via `localDataUrl`.
5. **Resolved — chapter mapping.** `data/chapters/*.json` was generated wrong
   (every entry claimed `hadith_start: 2`, `hadith_end: 97`). D1's
   `hadith_bab` (62,169 rows) joins shipped rows through `lidwa_id`, so
   `chapter_id` is now injected at build time for the nine books D1 covers
   and both starts/ends and counts are recomputed from the rows actually
   shipped. Bukhari went from "Hadith 2 – 99 · 237 hadiths" to
   "Hadith 1 – 6 · 6 hadiths", 97 chapters covering exactly 6,999 rows.
6. **Resolved — topics.** `topics_index.json` (790 KB, local only) is now
   `topics_index.ndjson`, one row per (topic, book), so a topic page fetches
   one small object instead of the whole tree. `topics.ndjson` carries the
   14 topic labels.
7. **Resolved — double-encoded star.** `âï¸` prefix removed from 10 hardcoded
   labels in `app.js` (mojibake of the star emoji, then duplicated).
8. **Registry `total_hadiths` vs `hadiths_count`.** Thirteen books still differ
   (e.g. `bukhari` 7,563 declared vs 6,999 shipped). `hadiths_count` is now
   written from the rows actually uploaded, so it can no longer drift; the two
   numbers differing means the served edition is an abridgement of the declared
   collection, which predates this batch.

## 7. One dataset, one row set, one chapter list

The old default mixed three sources: rows from one edition, chapter names from
`data/chapters/*.json`, and chapter ids from D1 keyed by lidwa number. That is
why `malik` advertised 60 kitabs while its rows covered only 32, and why
`abudawud` had fewer chapters in the list than in the file.

Rebuilt so each dataset is internally consistent:

- `api/<book>.ndjson` for the nine core books is now built from
  `data/sources/lidwa/<book>.ndjson` — the lidwa anchor. Number, Arabic text,
  Indonesian text and `lidwa_id` all come from that file; chapter id comes from
  D1 `hadith_bab` keyed by the **same lidwa number**. Existing rows contribute
  only grade/sanad metadata matched on the identical number.
- `api/fawaz/<book>.ndjson` holds the previous international rows. Its chapter
  ids come from `reference.book` in that edition, never from lidwa chapter
  numbers.
- `chapters/<book>.ndjson` and `chapters/fawaz/<book>.ndjson` are each generated
  from the row file they describe, with ranges and counts taken from those
  exact rows. A chapter title with no rows is dropped, not rendered as a dead
  link.

`js/api.js` routes `fawaz` lookups for the nine books into `api/fawaz/` and
`chapters/fawaz/`; `lidwa` and all other books keep the canonical paths.
Topic ids, hadith-of-the-day and batch loads are explicitly `lidwa`, because
the topic index is lidwa-numbered.

Counts after the split (lidwa / international rows):
```
bukhari 7008 / 6999   muslim 5362 / 2995   abudawud 4590 / 4585
tirmidhi 3891 / 3841  nasai 5662 / 5655    ibnmajah 4332 / 4327
malik 1595 / 1592     ahmad 26363 / 26363  darimi 3367 / 3546
```
`darimi` shrinks on lidwa because the lidwa edition genuinely has 3,367
hadiths; the international file retains all 3,546 rows.

Verification: `api_smoke.js` 17/17 (including a separate check of all nine
international datasets), `link_audit.js` no dead links, `site_r2.py verify`
PASS, 126 objects present in R2.


## 8. Classical sharh from "Syarah From Muse" (19 Nov 2026)

Source: `H:\Itho\2026\Project\Hadeeth\data source\Syarah From Muse` (override with
`SYARAH_MUSE_DIR`). Each directory holds one sharh as a SQLite DB with
`syarah_links` (hadith number -> page), `syarah_passages` (verbatim page text)
and `syarah_sources` (edition title, provider, licence).

Builder: `scripts/syarah_muse.py`, called by `syarah_build.build()`. It merges
rows into the SAME `commentaries/matched/<book>.ndjson` buckets as the Dorar
data, so one Range request returns every source for a hadith and the existing
tab engine in `js/app.js` renders one tab per edition. No new client route.

Numbering: a link attaches only when its `source_native_number` exists in the
shipped `api/<book>_index.ndjson`. `fawaz` and `hadeeth_id` link datasets both
resolve by number; nothing is guessed or coerced. 60,416 links attached across
41,998 hadiths; 17,107 links whose number has no row in our anchor were
dropped (bukhari 555, muslim 2,183, abudawud 674, etc.).

Inline text is the page on which the commentary starts, plus `syarah_pages_index`
(the full page span), `syarah_vol`, printed `syarah_page`, `syarah_url`,
`link_confidence` and `link_method`. The UI prints the citation under the text.
Full page text stays in the source DBs; it is not duplicated per hadith.

Deliberately not shipped:
- `maani`, `muntaqa`, `masabih`, `umdat` — commentaries on matns this site does
  not carry, so there is no hadith page to attach them to.
- `ahmad` (`'Uqd al-Zabarjad`) — no links table; an i'rab (grammar) work whose
  inclusion in the syarah layer is still an open product decision.
- The `syarah.db` / `dump/*.sql` files — those are build inputs for D1, not
  site data, and are not NDJSON.

Result: 14 books with commentary, 44,406 hadiths, 62,829 rows, 455.6 MB in
`commentaries/`. Keep every object `.ndjson`.

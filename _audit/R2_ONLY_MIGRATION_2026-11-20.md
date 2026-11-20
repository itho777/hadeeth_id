# R2-only data migration — 2026-11-20 (WIB)

Follow-up to `HASIL_PERBAIKAN_2026-11-20.md`. Goal: one data origin. The site shell stays on GitHub Pages; every data byte now comes from the public R2 bucket.

## What changed

| Before | After |
|---|---|
| 32,994 per-narrator JSON files under `data/rawis/profiles/` | `rawis/profiles.ndjson` (32,994 rows, 23,835,564 bytes) + `rawis/profiles_index.ndjson` (1,361,432 bytes). One HTTP Range per profile. |
| `data/links/*.json` read directly by 5 JS call sites | 33 canonical `links/*.ndjson` files; `HadeethAPI.getLinks(book)` reshapes `{k,v}` rows back to the map. |
| `data/rawis/active_rawis.min.json` on scholars page | `HadeethAPI.getActiveRawis()` → `rawis/rawis.ndjson` (14,298 rows). |
| `data/books_v2.json` on books pages | `HadeethAPI.getBooks()` → `books.ndjson` (28 rows). |
| `data/api/glossary.json` on glossary + admin | `api/glossary.ndjson` (116 rows), `HadeethAPI.getGlossary()`. |
| `data/api/topics_counts.json`, `data/api/topics_metadata.ndjson`, `data/api/topics_index.json` | `api/topics_counts.ndjson` (9 rows), `topics.ndjson`, `topics_index.ndjson`; API methods `getTopicsCounts`, `getTopics`, `getTopicIndex`. |
| `data/sources/ahmedbaset/**/*.json`, `data/lidwa-chapters/*.json` fetched relative | R2 URLs via `HadeethAPI.dataUrl`; lidwa-chapters re-encoded as 19 NDJSON files with a `_meta` row + chapter rows. |
| Legacy fallbacks to `/data/*.json` and raw.githubusercontent.com | Removed from `js/api.js` and `js/app.js`. `localDataUrl` is now an alias of the R2 base. |

AhmedBaset's 624 files (147,955,694 bytes) are nested envelope objects — metadata + chapters + hadiths in one document — not row sets. They were copied byte-identical to R2. No data was discarded or rewritten.

`scripts/site_r2.py` now builds the new NDJSON subtrees itself, so `export_site/` regeneration does not drop them. The manifest was merged with the syarah entries owned by `manifest_syarah.py`; prune on upload was a no-op.

## Upload evidence

`python scripts/site_r2.py upload`: **441 uploaded, 708 unchanged, 71.80 MB, 0 failed**.

`python scripts/site_r2.py verify`:

```
objects in batch: 1149   present in R2: 1149
missing: 0   size-mismatch: 0
catalog.ndjson       HTTP 200  sha256 match=True
books.ndjson         HTTP 200  sha256 match=True
range check (api/bukhari.ndjson): status=206 bytes=401 identical=True
index alignment: n=1 / 3505 / 7008 all record matches=True
RESULT: PASS
```

## Browser verification

Chrome/Playwright against the local copy (`http://127.0.0.1:8765`), 14 pages: `index`, `books`, `topics`, `topics-in-kitab`, `topic-hadiths`, two hadith pages, two kitab pages, `scholars`, `profile-detail`, `glossary`, `master-link-viewer`, `node_diagram`.

- Requests to `hadeeth.id/data` or `127.0.0.1:8765/data`: **0**
- Data `.json` requests: **0**
- HTTP >=400 on data/R2 URLs: **0**
- Page errors: **0**

Spot checks after the migration:

- Topic EN view: 10/10 cards carry `[Terjemahan EN: Fawazahmed #n]`, 0 "unavailable".
- Profile `?id=19944`: byte-range read returned the real row (grade, family, 537 narrations, per-book counts 81/93/112/78/89/84).
- Scholars: roster renders from `rawis/rawis.ndjson`; no Supabase call.
- Frames: `master-link-viewer` and `node_diagram` load link data through `getLinks()` with `js/api.js` added where it was missing.

## Next

D1 variant discussion. No D1 schema or import was changed in this pass.

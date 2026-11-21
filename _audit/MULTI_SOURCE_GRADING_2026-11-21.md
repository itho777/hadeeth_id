# Multi-source grading + genuine Fawaz rows — 2026-11-21

## What changed

1. `api/fawaz/<book>.ndjson` is now built from `data/sources/fawaz_combined_v2/<book>.json`, not from the Lidwa master. It carries Fawaz's own numbering, Arabic text, translations, and `lidwa_id` from `data/link_graph.json`.
2. `links/fawaz_<book>.ndjson` is now a real Fawaz→Lidwa edge list. The old identity maps (`"999":"999"`) are gone; identity matches remaining are coincidental (4/5,263 for Abu Dawud).
3. Every `api/<book>.ndjson` and `api/fawaz/<book>.ndjson` row now carries a `gradings[]` array with the source and, where the source names one, the grader.
4. Hadith and sanad pages render a "Sumber penilaian / Grading sources" block. It is hidden when a row has no grading data — no placeholder, no default `Sahih`.

## Sources shipped per book

| Book | Fawaz rows | Lidwa-linked | Grade entries | Sources present |
|---|---:|---:|---:|---|
| bukhari | 7,278 | 7,179 (98.6%) | 6,728 | lidwa |
| muslim | 7,312 | 2,960 (40.5%) | 1,737 | lidwa |
| abudawud | 5,274 | 5,263 (99.8%) | 34,067 | fawaz, lidwa, atif_hf, ahmedbaset, usm |
| tirmidhi | 3,985 | 3,944 (99.0%) | 25,188 | fawaz, lidwa, atif_hf, ahmedbaset |
| nasai | 5,682 | 5,673 (99.8%) | 33,507 | fawaz, lidwa, atif_hf, ahmedbaset, usm |
| ibnmajah | 4,339 | 4,337 (100.0%) | 28,608 | fawaz, lidwa, ahmedbaset, atif_hf |
| malik | 1,653 | 1,366 (82.6%) | 3,008 | fawaz, lidwa |

`atif_hf` and `ahmedbaset` are matched to Fawaz rows by normalized Arabic text, not by number: their references use letter suffixes (`8a`) and different book boundaries. Match rates are 96–100% per book.

## Deliberate limits

- **Status (muttasil/mursal) and elevation (marfu/mauquf/maqthu)** still exist only in the Lidwa-derived rows. No second source supplies them, so the UI does not claim otherwise.
- **No jarh wa ta'dil** (thiqah/saduq/dhaif narrator reliability) in any source. The `grade` field in the Kaggle rijal file is a generation label, not a reliability ruling.
- **Bukhari and Muslim have no Fawaz grading entries.** Their only grade remains Lidwa's. Atif/AhmedBaset also ship no grades for the two Sahihayn.
- **USM** is included only where its key exists in the Fawaz row set. Its parser produced keys beyond the book range for Nasa'i (max 6,889 vs 5,682 rows); out-of-range keys are dropped, and the source is labelled `USM (daftar Munkar)`.
- **No aggregate verdict.** The page lists labels per dataset; it does not compute a majority or a percentage.

## Verification

- Local Playwright, `hadith.html?book=abudawud&id=1183&dataset=fawazahmed`: 5 sources, 8 grade rows, 0 page errors.
- Local Playwright, `sanad.html?book=abudawud&id=1183&dataset=fawazahmed`: 5 sources, 0 page errors.
- Bukhari #1: 1 source (Lidwa, `Shahih`). Tabarani #1: block hidden.
- R2 upload: 47/944 uploaded, 897 unchanged, 579.42 MB, 0 failed.
- `site_r2.py verify`: 944/944 present, 0 missing, 0 size mismatch, content SHA-256 match, Range + index PASS.
- Live R2 `api/fawaz/abudawud_index.ndjson` entry 1183 → `l` = `["999"]`; Range read returns 8 grade entries including `usm`.
- Live R2 `links/fawaz_abudawud.ndjson` contains `{"k":"1183","v":"999"}`.
- Live `https://hadeeth.id/hadith.html?book=abudawud&id=1183&dataset=fawazahmed`: 5 sources, 441 chars, 0 page errors, 0 bad responses.
- Live `https://hadeeth.id/sanad.html?book=abudawud&id=1183&dataset=fawazahmed`: same 5 sources, 0 errors.
- Live `js/app.js?v=20261121_grades2` 200. Final commit `0d116d4e9d`; Pages run `44863962153` green.
- Hadith-list → detail and detail → prev/next/inspect-sanad links now carry `dataset`, so genuine Fawaz and Lidwa numbers stay in their own numbering. Live: first Abu Dawud card links to `id=1&dataset=fawazahmed`; detail opens the matching hadith with 4 grading sources.
- Pre-existing, non-blocking: `hadith-list.html` requests `/sources/lidwa/<book>.ndjson` (404) as an optional Indonesian-text enrichment. The list renders from `api/` regardless.

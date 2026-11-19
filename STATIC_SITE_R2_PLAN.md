# hadeeth.id Static Site on Cloudflare R2 — NDJSON Export Plan

**Account**: `0f1e9510fccd3058326be7b5b5ee6802` (hadeeth.id)
**Token**: read from `CLOUDFLARE_API_TOKEN` in the gitignored `.env` (never committed)
**D1 Database**: `154c5a69-39af-477d-938a-c0a2cedeb2f7` (hadeeth-id-v2, 426.1 MB)

---

## 1. Prerequisites (Manual — needs dashboard)

- [ ] Enable R2 on account `0f1e9510fccd3058326be7b5b5ee6802` via Cloudflare Dashboard → R2 → "Enable R2"
- [ ] Verify token has `R2:Edit` permission (cfut_ tokens typically do)

---

## 2. R2 Bucket — DONE

- **Bucket name**: `hadeeth-id-static` ✓
- **Location**: APAC ✓
- **Public URL**: `https://pub-075ac3f4a31e4e85a876c26c815ae93d.r2.dev` ✓
- **CORS**: Enabled (GET/HEAD from any origin) ✓
- **Created**: 2026-11-18T22:45:56Z

---

## 3. Data Export Scope — "Finished Books Only"

From STATE.md §2: 25 source datasets in `hadiths` table, all loaded in D1. These are the **finished books**:

| source_id | book_id | rows |
|---|---|---|
| `fawaz:abudawud` | abudawud | 5,274 |
| `fawaz:bukhari` | bukhari | 7,589 |
| `fawaz:dehlawi` | dehlawi | 40 |
| `fawaz:ibnmajah` | ibnmajah | 4,343 |
| `fawaz:malik` | malik | 1,858 |
| `fawaz:muslim` | muslim | 7,563 |
| `fawaz:nasai` | nasai | 5,765 |
| `fawaz:nawawi` | nawawi | 42 |
| `fawaz:qudsi` | qudsi | 40 |
| `fawaz:tirmidhi` | tirmidhi | 3,998 |
| `lidwa:abudawud` | abudawud | 4,590 |
| `lidwa:ahmad` | ahmad | 26,363 |
| `lidwa:bukhari` | bukhari | 7,008 |
| `lidwa:darimi` | darimi | 3,367 |
| `lidwa:ibnmajah` | ibnmajah | 4,332 |
| `lidwa:malik` | malik | 1,595 |
| `lidwa:muslim` | muslim | 5,362 |
| `lidwa:nasai` | nasai | 5,662 |
| `lidwa:tirmidhi` | tirmidhi | 3,891 |
| `mjna:daruquthni` | daruquthni | 236 |
| `mjna:ibnuhibban` | ibnuhhiban | 2,769 |
| `mjna:ibnukhuzaimah` | ibnukhuzaimah | 1,808 |
| `mjna:mustadrak` | mustadrak | 673 |
| `irsyad:riyad` | riyadussalihin | 372 |
| `irsyad:syafii` | syafii | 1,800 |

**NOT included (still building via Muse)**: Shamela books — `adab` (4750), `mustadrak` (1268), `daruquthni` (3510), `tabarani` (1484). Will export separately when Muse delivers.

---

## 4. NDJSON Export Structure

Per-book, per-table NDJSON files. Compressed with gzip level 9.

### R2 Key Pattern
```
{source_id}/{table}.ndjson.gz
```

Example:
```
fawaz:bukhari/hadiths.ndjson.gz
lidwa:bukhari/hadiths.ndjson.gz
mjna:daruquthni/hadiths.ndjson.gz
```

### Tables to Export (all 11 tables in D1)
1. `hadiths` — filtered by `source_id`
2. `sanad` — filtered by `source_id` (via `hadiths` join on `hadith_id`)
3. `narrators` — global (no source filter)
4. `chapters` — filtered by `book_id` (join `kitab`)
5. `kitab` — global
6. `grades` — filtered by `source_id` (via `hadiths` join)
7. `hadith_bab` — filtered by `source_id` (via `hadiths` join)
8. `text_link` — filtered by `source_id` (both `link_source_id` and `source_id`)
9. `fawaid` — filtered by `book_id` (lidwa only, 115 rows)
10. `imam_bio` — global (9 rows)
11. `syarah_links` — empty, skip

### Cross-dataset Map
Export `hadith_map` edges as separate NDJSON:
```
map/hadith_map.ndjson.gz
```
Each line: `{source_a, book_id_a, hadith_number_a, source_b, book_id_b, hadith_number_b, basis, score}`

---

## 5. Index Manifest (index.json)

Single small object at root:
```json
{
  "generated_at": "2026-11-19T...",
  "d1_database": "154c5a69-39af-477d-938a-c0a2cedeb2f7",
  "source_datasets": 25,
  "books": {
    "bukhari": {
      "sources": ["fawaz:bukhari", "lidwa:bukhari"],
      "tables": ["hadiths", "sanad", "chapters", "grades", "hadith_bab", "text_link"],
      "row_counts": {"fawaz:bukhari": {"hadiths": 7589}, "lidwa:bukhari": {"hadiths": 7008}}
    },
    ...
  },
  "files": {
    "fawaz:bukhari/hadiths.ndjson.gz": {"sha256": "...", "bytes": 123456, "rows": 7589},
    ...
  }
}
```

---

## 6. Export Script Requirements

- Use D1 REST API (`/accounts/{acct}/d1/database/{uuid}/query`) with `SELECT` only — no write quota
- Stream results, write NDJSON line by line, gzip on the fly
- Batch `SELECT` with keyset pagination: `WHERE (source_id, hadith_number) > (?, ?) LIMIT 1000`
- Verify: NDJSON line count == D1 row count per source per table
- Compute sha256 of each gzipped file for manifest

---

## 7. GitHub Branch

- Create branch `static-r2-ndjson` from `main`
- Add export script(s) to `scripts/`
- Add R2 upload script to `scripts/`
- This plan document to repo root
- `.gitignore` for local export artifacts

---

## 8. UI Integration (Later)

After data in R2:
- Update `js/api.js` to fetch from R2 (public URLs or signed URLs)
- Replace D1 Worker calls with NDJSON streaming for book-level data
- Keep D1 Worker for cross-dataset queries (search, map, joins)
- Add `index.json` loader at app bootstrap

---

## 9. Next Steps (This Session)

1. **Enable R2** (user: visit dashboard)
2. **Create bucket** `hadeeth-id-static` via API
3. **Write export script** `scripts/export_d1_to_ndjson.py`
4. **Run export** for all 25 datasets
5. **Upload to R2** via S3 API (presigned PUT or multipart)
6. **Generate index.json** and upload
7. **Create branch** `static-r2-ndjson` and commit scripts
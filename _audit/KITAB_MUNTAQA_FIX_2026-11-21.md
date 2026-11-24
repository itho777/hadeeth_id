# kitab.html?book=muntaqa — broken container / raw chapter IDs (2026-11-21)

## Symptom

Live `https://hadeeth.id/kitab.html?book=muntaqa` rendered 1,109 chapter cards titled
`Kitab turath:1218:heading:0073`, with the same full ID crammed into the 40 px
number badge. No Arabic chapter title. Layout grid itself was intact; the cards
were unreadable because every label was a raw source ID.

## Root cause

The 2026-11-20 audit fix wrote corrected chapter sidecars **only** into
`export_site/chapters/*.ndjson` and R2. `scripts/site_r2.py build()` deletes and
regenerates that tree. The multi-source grading build on 2026-11-21 regenerated
all chapters from the raw source, restoring the old defects:

- muntaqa: 0/1,109 `title_ar`, `title_id = "Kitab turath:…"`, no `display_number`
- tabarani: 294 count/range conflicts again (`hadith_count` counted shipped rows,
  not distinct hadith numbers)
- maani / masabih / umdat / shah: lost Arabic book title and `display_number`

`build_chapters()` also keyed its lookup of existing titles by
`int(chapter_number)`, which silently dropped every non-numeric `turath:` id.

## Fix — in the builder, so regeneration keeps it

1. `data/chapters/muntaqa.json` — new source file: 1,109 id-keyed entries with
   `title_ar` from `syarah_chapters` in `syarah_muntaqa.db` and source order from
   `page_index, sequence_no`. No title invented.
2. `scripts/site_r2.py`:
   - `scan_row_chapters()` returns `[min, max, row_count, distinct]`;
     `hadith_count` is now distinct hadith, `row_count` keeps the raw total.
   - `build_chapters()` keys prior titles by raw string id, passes through
     `display_number`/`row_count`, never falls back to `"Kitab <raw id>"` when an
     Arabic title exists, and uses the book's `title_ar` plus badge `M` for
     single-chapter books (`shah` keeps "Empat Puluh Hadits" / "Forty Hadiths").
   - new `build_from_source()` drives tabarani + muntaqa from their id-keyed
     source files, sorting by number (tabarani) or source order (muntaqa) and
     renumbering badges 1..N over shipped chapters.
   - `upload()` counts manifest entries whose local file is absent as
     remote-only keeps instead of failures. 45 `map/` and `search/` objects are
     owned by other pipelines; a build no longer aborts over them or prunes them.
3. Manifest after build: 944 build objects merged with the 1,193 committed keys,
   plus the existing remote `scripts/vectorize_hadeeth.py` → 1,194 keys.
   Remote − manifest = 0 before upload.

## Verified

- Local build: `build: 944 objects, 1655.64 MB`.
- Generated chapters: muntaqa 1,109 rows / 1,109 Arabic titles / badges 1..1,109;
  tabarani 2,248 rows / 0 count-range conflicts / `row_count` on all rows;
  maani, masabih, umdat, shah have Arabic book titles and badge `M`.
- Upload: 20 uploaded, 1,174 unchanged/skipped, 1.06 MB, 0 failed, 0 pruned.
- `site_r2.py verify`: 1,194/1,194 present, 0 missing, 0 mismatch, content
  SHA-256 match, Range + index PASS.
- Live R2 chapter files match the rebuilt local files.
- Live Playwright on `kitab.html?book=<book>`: muntaqa 1,109 cards, first titles
  Arabic, first badges 1/2/3, 0 `turath:` leaks, 0 page errors, 0 bad responses;
  tabarani 2,248 cards with Arabic titles; maani and shah badge `M`.
- Visual screenshot check: 2-column card grid intact, badges small, Arabic titles
  visible.
- Chapter deep link still resolves: first card →
  `hadith-list.html?book=muntaqa&chapter=turath:1218:heading:0073`, which opens
  the correct hadith with the Arabic chapter title in the content card.
  Breadcrumbs on that list page still print the raw id — cosmetic, out of scope.
  Optional `editions/*muntaqa*` 404s are expected: no such edition exists.

# R2 Static Data — Format Spec

The site reads pre-built data from Cloudflare R2. No worker, no D1 call per page.

**Base URL** — `https://pub-075ac3f4a31e4e85a876c26c815ae93d.r2.dev`

Everything below is relative to that. Bucket `hadeeth-id-static`, public read, CORS open
to `GET`/`HEAD` from any origin, so `fetch()` works straight from the browser.

---

## 1. Files in the bucket

```
catalog.json                              bootstrap: books, editions, counts
index.json                                full manifest: every file + sha256 + bytes
book/<book>/index.json                    one book: editions, tables, row counts
book/<book>/hadiths.ndjson.gz             all editions of that book, merged
book/<book>/sanad.ndjson.gz               (only books that have sanad)
book/<book>/hadith_bab.ndjson.gz
<source>/hadiths.ndjson.gz                one edition only
<source>/sanad.ndjson.gz
<source>/hadith_bab.ndjson.gz
global/narrators.ndjson.gz
global/kitab.ndjson.gz
global/chapters.ndjson.gz
global/grades.ndjson.gz
global/imam_bio.ndjson.gz
global/fawaid.ndjson.gz
global/text_link.ndjson.gz
```

`<source>` uses `_` where the D1 `source_id` uses `:`, so `fawaz:bukhari` →
`fawaz_bukhari/`. The `source_id` field inside every record still has the colon.

**Use `book/` for the reader.** It is the whole book in one fetch; the `source_id` field on
each row tells you which edition it came from. Use `<source>/` only when you want a single
edition in isolation.

---

## 2. catalog.json — the first fetch

Small (~11 KB). Drives the book list without touching anything else.

```json
{
  "generated_at": "2026-11-19T00:14:00Z",
  "base_url": "https://pub-...r2.dev",
  "format": "ndjson.gz",
  "books": [
    {
      "book": "bukhari",
      "title_ar": "صحيح البخاري",
      "hadiths": 14597,
      "editions": [
        { "source_id": "fawaz:bukhari", "rows": 7589 },
        { "source_id": "lidwa:bukhari", "rows": 7008 }
      ],
      "tables": [
        { "table": "hadiths",    "path": "book/bukhari/hadiths.ndjson.gz",    "rows": 14597, "bytes_gz": 26260462 },
        { "table": "sanad",      "path": "book/bukhari/sanad.ndjson.gz",      "rows": 9447,  "bytes_gz": 102418 },
        { "table": "hadith_bab", "path": "book/bukhari/hadith_bab.ndjson.gz", "rows": 7008,  "bytes_gz": 30247 }
      ]
    }
  ],
  "global": ["chapters", "fawaid", "grades", "imam_bio", "kitab", "narrators", "text_link"],
  "totals": { "books": 18, "editions": 25, "hadiths": 106340, "rows": 357048, "bytes_gz": 185281028 }
}
```

`hadiths` is the sum across editions, so bukhari counts 14,597 rows because both the fawaz
and lidwa editions are present. If the UI shows "number of hadiths in this book", either
pick one edition (trust `fawaz` — it has the translations) or label it as a row count.

`book/<book>/index.json` is a smaller variant of the same thing for one book — it lists
`editions` by filesystem name (`fawaz_bukhari`, with an underscore) and per-table row counts,
so a book page can render its table of contents before pulling any NDJSON.

---

## 3. Reading an NDJSON.gz in the browser

`DecompressionStream` handles gzip natively in current Chrome, Safari, Firefox and Edge.
Streaming it means the first rows render before the whole book has arrived — important for
bukhari at 26 MB.

```js
async function* streamNdjson(url) {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`${res.status} ${url}`);
  const stream = res.body.pipeThrough(new DecompressionStream('gzip'));
  const reader = stream.getReader();
  const dec = new TextDecoder();
  let buf = '';
  for (;;) {
    const { value, done } = await reader.read();
    if (done) break;
    buf += dec.decode(value, { stream: true });
    let i;
    while ((i = buf.indexOf('\n')) >= 0) {
      const line = buf.slice(0, i);
      buf = buf.slice(i + 1);
      if (line) yield JSON.parse(line);
    }
  }
  if (buf.trim()) yield JSON.parse(buf);
}

// first page of a book
for await (const h of streamNdjson(`${BASE}/book/bukhari/hadiths.ndjson.gz`)) {
  renderRow(h);
  if (++n >= 50) break;          // breaking cancels the fetch — the rest is not downloaded
}
```

Breaking out of the loop cancels the body, so a 26 MB book costs only the bytes already
pulled. That is the reason to keep NDJSON rather than one big JSON array: a contiguous JSON
array cannot be parsed incrementally without a streaming parser.

---

## 4. Row shapes

### hadiths
```json
{
  "id": 1,
  "source_id": "fawaz:bukhari",
  "book_id": "bukhari",
  "hadith_number": 1,
  "hadith_number_alt": 1,
  "hadith_number_alt_source": "arabicnumber",
  "text_ar": "حَدَّثَنَا الْحُمَيْدِيُّ ...",
  "text_id": "Telah menceritakan kepada kami [Al Humaidi ...]",
  "text_en": null, "text_ben": null, "text_fra": null,
  "text_tur": null, "text_urd": null, "text_rus": null, "text_tam": null,
  "grade": "...", "grade_source": "...",
  "reference": "..."
}
```
The seven `text_*` language columns exist on every row but are mostly `null` outside the
editions that carry them. fawaz carries `text_en`/`text_id`; lidwa carries `text_id`.

### sanad — one row per chain link
```json
{
  "source_id": "lidwa:abudawud",
  "hadith_number": 1,
  "chain_no": 1,
  "narrators": ",1665,4903,7225,4591,5085,",
  "chain_type": "Mutashil",
  "status": "Marfu'"
}
```
`narrators` is a **comma-delimited id string with leading and trailing commas** — split on
`,` and drop the empties. Each id joins `global/narrators.ndjson.gz` on `narrator_id`.
**sanad exists only for the nine `lidwa:*` editions** — fawaz/mjna/irsyad rows have no chain
data at all, so a chain view must degrade gracefully for those editions.

### hadith_bab — hadith → chapter
```json
{ "source_id": "lidwa:abudawud", "book_id": "abudawud",
  "hadith_number": 1, "kitab_number": 1, "bab_number": 1 }
```
Joins `chapters` on `book_id` + `bab_number`. Also lidwa-only.

### grades
```json
{ "id": 1, "book_id": "abudawud", "hadith_number": 1,
  "grade": "Hasan Shahih", "grade_source": "Muhammad Nashiruddin Al Albani" }
```
Keyed on `book_id` + `hadith_number`, **not** on `source_id` — one grade applies to the
hadith across editions. This is why it is a global file.

### chapters
```json
{ "id": 1, "book_id": "abudawud", "bab_number": 1,
  "bab_name": "Menyepi saat buang hajat", "kitab_id": 1 }
```

### kitab
```json
{ "id": 1, "book_id": "abudawud", "kitab_number": 1, "kitab_name": "Bersuci" }
```

### narrators
```json
{
  "narrator_id": 1665,
  "name_ar": "Al Mughirah bin Syu'bah bin Abi 'Amir",
  "kuniyah": "Abu 'Isa", "laqob": "", "nasab": "",
  "quality": 1, "kalangan": "Shahabat",
  "negeri_hidup": "Kufah", "negeri_wafat": "Kufah", "tahun_wafat": "50 H",
  "n_bukhari": 35, "n_muslim": 31, "n_abudawud": 22, "n_tirmidhi": 23,
  "n_nasai": 24, "n_ibnmajah": 21, "n_ahmad": 103, "n_malik": 2, "n_darimi": 15
}
```
The `n_*` columns are that narrator's occurrence counts per book — usable for a narrator
profile page without scanning the sanad files.

### imam_bio — 9 rows, one per imam
```json
{ "id": 4, "name_ar": "Biografi Imam Bukhari", "name_id": "bukhari", "bio_id": "<p>…</p>" }
```
`bio_id` is HTML. Render it, don't escape it.

### fawaid — 115 rows
```json
{ "id": 1, "content": "Mufradat Hadits :\n…" }
```

### text_link — 321 rows, cross-edition hadith mapping
```json
{ "source_id": "fawaz:bukhari", "hadith_number": 5710,
  "link_source_id": "lidwa:bukhari", "link_hadith_number": 5710,
  "basis": "number", "sim": null }
```
Reads as "the hadith at `source_id`/`hadith_number` corresponds to the one at
`link_source_id`/`link_hadith_number`". `basis` says how the link was made (`number`,
else a similarity) and `sim` carries the score when it was not an exact number match. Only
321 rows exist, so this is a partial map, not a complete cross-edition alignment.

---

## 5. Not built yet

- **Search.** There is no search index in R2. The old site searched through D1. Either keep
  the D1 worker for search, or build a static index (`global/hadiths-index.ndjson.gz` —
  one row per hadith with `book`, `number`, and a trimmed text field) and filter client-side.
  357k rows is too much to hold in memory; a per-book text index is the sane middle ground.
- **Per-hadith pages.** Right now the smallest unit is a whole book. A `book/<book>/
  h<n>.json` set would make deep links a single tiny fetch. Generate on demand or as a
  build step.
- **Shamela books.** `adab` (4,750), `tabarani` (1,484) are still being built by Muse and
  are not in D1 yet. `mustadrak` and `daruquthni` in R2 today come from the `mjna:*`
  editions only, not Shamela.
- **audio** and **syarah_links** tables exist in D1 but are empty — no files emitted.

---

## 6. Rebuilding after a data change

```bash
python scripts/load_d1_dump.py        # D1 SQL export -> .dump/hadeeth.sqlite
python scripts/export_d1_to_ndjson.py # -> export/<source>/<table>.ndjson.gz
python scripts/build_book_bundles.py  # -> export/book/<book>/<table>.ndjson.gz
python scripts/build_catalog.py       # -> export/catalog.json
python scripts/upload_to_r2.py        # -> r2://hadeeth-id-static
```

Requires `CLOUDFLARE_API_TOKEN` in `.env`. The D1 export route is used on purpose: paging
the query API bills every row against the daily row-read limit and a full export needs
~357k rows, so it exhausts the free tier.

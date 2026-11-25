# hadeeth.id — User Acceptance Test & Data-Readiness Audit

**Date:** 24 November 2026 (audit); fix batch 1 appended 25 November 2026
**Status:** fixes exist in the working tree and were verified on a local server; **not deployed**. See §8.
**Target:** https://hadeeth.id (live production) + live data CDN `https://cdn.hadeeth.id/*.ndjson`
**Purpose:** gate before mobile app build. Verdict per page/function, defect list with evidence, fix priority.
**Method:** real Chrome (Playwright), desktop 1440×900 and iPhone 390×844 viewports; console + pageerror + failed-request capture; HTTP probes of every CDN payload (index byte-spans, field presence, numbering); byte-range spot checks.
**Artifacts:** `_audit/uat_2026-11-24/*.json`, `*.log`, `dom/*.txt`

---

## 1. Verdict

**Data is NOT ready to be frozen for the mobile app.** Corpus and CDN layer are largely sound — 28 books, 118,397 hadiths, byte indexes exact, zero gaps, zero offset mismatches — but the presentation layer contradicts the data in ways that will be inherited directly by the mobile client:

- 5 books have **zero reachable chapters** due to a JS `ReferenceError` (a one-line bug).
- **12 more books** render only a single dummy chapter — chapter navigation effectively absent for 43% of the catalogue.
- **Syarah tab resolves for 6 of 28 books, and Indonesian syarah has 14 rows in the entire corpus.** 28,131 commentary rows sit on the CDN with no anchor to any hadith.
- **Search never fails.** Gibberish returns "FOUND 20 AUTHENTIC MATCHES."
- Book counts printed on screen **disagree with the shipped data** for 17 of 28 books.
- One book (`tabarani`) has **8,295 duplicate hadith numbers** → deep links and prev/next are ambiguous.
- `topics_index.ndjson` was generated against the **pre-migration corpus**: 3,830 of 128,659 topic references (3.0%) point at hadiths that no longer exist, 21.6% for Malik — topic pages run out of rows mid-pagination.
- **Chapter counts on the list page do not match the chapter sidecar** — `muslim` chapter 1 is the 8-hadith *Mukadimah* in `chapters/muslim.ndjson`, but the page renders 436 hadiths. A mobile client using the sidecar will disagree with the web app.

The stale counts, the dead topic references and the 404 edition ids share one root cause: metadata, topic index and edition catalog were built from the older, larger corpus and were never regenerated after the switch to the shipped Lidwa data. Regenerating all three is a single job.

Fix list below is ordered so that items 1–9 unblock mobile; 10–14 are data corrections; 15+ are polish.

---

## 2. Coverage tested

| Area | Pages / functions | Result |
|---|---|---|
| Home | `index.html` — hero, HADITH OF THE DAY, Kitubut Tis'ah, search box, search-mode selector, book filter | Search works, but relevance floor missing (§4.1) |
| Books index | `books.html` — 28 kitab cards | 28/28 links resolve ✓ |
| Book detail | `kitab.html` — all 28 books | 9 OK / 5 JS crash / 12 stub / 1 garbage / 1 bomb |
| Chapter list | `hadith-list.html` — 16 book/chapter combos, pagination, page-size, jump-to-page, default-lang select | rows + pagination correct ✓ |
| Hadith detail | `hadith.html` — all 28 books × first/mid/last, 51 samples | Arabic always present ✓; defects §4.5, §4.6 |
| Data sources panel | "Data Sources" button — credits & anchoring | modal opens ✓ — **informational only, no switcher exists** (§4.15F) |
| Prev / Next | sequential navigation at book boundaries | works ✓ |
| Translations | AR / ID / EN panels, `lang-select-1`, dual-language mode | AR+ID 100% of samples ✓; EN defects §4.5–4.6 |
| Syarah | tabs, source selector, language select | panel renders; ID syarah missing everywhere (§4.11) |
| Grade | badge + grading sources per hadith | present but sparse for Muslim (§4.12) |
| Sanad | `sanad.html` — chain rendering | OK for core books; empty for tabarani (§4.13) |
| Topics | `topics.html`, `topics-in-kitab.html`, `topic-hadiths.html` (14 topics × 4 books) | works; localization gap (§4.16) |
| Scholars | `scholars.html` — grid, search, pagination, card metadata | works; metadata defects (§4.14) |
| Profile | `profile-detail.html` | renders ✓ |
| Glossary | `glossary.html` — 20 groups, alpha nav, search | search fails in ID mode (§4.15) |
| **Auth** | `login.html` — email, Google, Facebook, signup | renders ✓; Apple provider referenced in privacy policy but absent (§4.21) |
| Razi widget | `razi-chat.js` on every page — open, type, send, receive | **works**, answer 40 s, not streamed (§4.19) |
| Docs | `docs.html` — 83 rows, API tables | desktop ✓; mobile overflow (§4.17) |
| Privacy | `privacy.html` | ✓ |
| Mobile | 10 pages at 390×844 | no page-level overflow ✓ except docs table (§4.17); tap targets (§4.18) |
| Data | `books.ndjson`, `api/<book>_index.ndjson`, `api/<book>.ndjson`, `chapters/*.ndjson`, `editions/*`, `rawis/*` | see §5 |

---

## 3. What is healthy (do not touch)

- **Byte index integrity is perfect.** All 28 books: `s`/`e` spans contiguous, `gaps=0`, `tail=0` (index ends exactly at EOF), `dupN=0` except tabarani, 3 spot-checked byte ranges per book parse to the correct `hadith_number` — **84/84 samples correct**.
- **Arabic text 100% present** in every sampled row of every book (30 samples/book, 28 books).
- **Indonesian translation** present for all 18 books that declare it; only `text_id`-absent books (tabarani, muntaqa, maani, masabih, umdat, riyad_arab, daruquthni) lack it, and those are AR-first collections.
- **CORS + content-type correct** on `cdn.hadeeth.id` (serves `Origin: https://hadeeth.id` with `access-control-allow-origin`).
- **Hadith page latency good:** first Arabic text 1.2–2.4 s desktop, 1.3–2.1 s mobile.
- **Chapter sidecars shipped** for all 28 books.
- **No mojibake** in Arabic across 51 rendered hadith pages.
- **Search backends healthy:** embeddings 0.40 s (`data.hadeeth.id/_embed`, bge-m3/1024-d), Meilisearch 1.08 s. End-to-end search 2.1–4.4 s.
- **`books.html`** — 28/28 book links resolve to a `kitab.html` page.

---

## 4. Defects

### CRITICAL — block mobile build

#### 4.1 Search never returns "no results"; gibberish is reported as authentic
`index.html` → type `zzzzqqqxxx` → Search.

```
FOUND 20 AUTHENTIC MATCHES
Semantic — Semantic via Cloudflare AI + Supabase pgvector
Sahih al-Bukhari #4001 … Musnad Ahmad #1147…
```

Also in keyword mode: same 20 results, labelled `Semantic (fallback) — selected method unavailable`.
Reproduced 20/20 results for `zzzzqqqxxx`, `quantum chromodynamics`, `<script>alert(1)</script>`.

Cause: no similarity threshold. API response for gibberish:
```
{"q":"zzzzqqqxxx"} → similarity 0.486, 0.481, 0.480, 0.476, 0.476
{"q":"sabar"}      → similarity 0.510, 0.508, 0.506, 0.506, 0.506
```
Real match and noise differ by 0.02. `js/api.js:864-896` cascades semantic → keyword → algolia → local scan and each tier happily returns rows, so the empty state is unreachable. **A user cannot tell a hit from a miss, and the UI asserts "authentic" over random rows.** On mobile this is worse — no room to explain a fallback.

#### 4.2 `kitab.html` JavaScript crash — 5 books have zero chapters
```
ReferenceError: titleId is not defined
    at https://hadeeth.id/js/app.js?v=20261124_cdn:3393:42
    at Array.forEach (<anonymous>)
    at loadChaptersList (https://hadeeth.id/js/app.js?v=20261124_cdn:3380:23)
```
Affected: **adab, bulugh, mishkat, riyad, shamail** → `#chapters-list-container` children = 0.
The data is fine — chapter files are shipped and complete:

| book | chapter rows shipped | rendered |
|---|---|---|
| adab | 57 | **0** |
| bulugh | 16 | **0** |
| mishkat | 25 | **0** |
| riyad | 20 | **0** |
| shamail | 57 | **0** |

`titleId` is used at `app.js:3393` inside `${titleAr && titleAr !== titleId ? …}` but is never declared in that scope. One undefined variable kills the whole list, so 175 chapter rows are unreachable in the UI.

#### 4.3 Twelve books render a single dummy chapter
`kitab.html` returns `chapters-list-container.children == 1` for:
`nawawi, qudsi, shah, syafii, riyad_arab, ibnukhuzaimah, ibnuhibban, mustadrak, daruquthni, maani, masabih, umdat`

Cause is in the data, not the page — each `chapters/<book>.ndjson` holds exactly 1 row:
```json
{"book_id":"maani","id":"maani_c1","chapter_number":1,"title_id":"Semua Hadits","title_en":"All Hadiths"}
```
For `qudsi`/`riyad`/`mishkat` the single row is literally titled `"Bab 0" / "Chapter 0"`.
Effect: no chapter browsing for 12 of 28 books (43% of the catalogue, 21,000+ hadiths).

#### 4.4 `ahmad` ships 14 chapters, books.ndjson declares 90
| | value |
|---|---|
| `chapters/ahmad.ndjson` rows | **14** |
| `books.ndjson → total_chapters` | **90** |
| `kitab.html` rendered | 15 |

Musnad Ahmad (26,363 hadiths, largest book) is effectively un-navigable — 14 chapter buckets for 26k hadiths, and the declared metadata disagrees.

#### 4.5 English panel shows Indonesian text (`riyad`, `nawawi`)
Verified `en === id` (first 200 chars identical):

| book:hadith | EN panel content |
|---|---|
| `riyad:1` | `warning Alignment Notice: Translation dynamically linked from ID - Lidwa (ID #1). Bab 84. Malu Dan Keutamaannya…` |
| `nawawi:1` | `Dari [Amirul Mukminin Abu Hafsh Umar bin Al-Khattab] radhiyallahu 'anhu, ia berkata…` |

For all other books the EN panel is correctly English. Any mobile client that trusts `text_en` will show Indonesian labelled as English.

#### 4.6 `tabarani`: 8,295 duplicate hadith numbers
```
tabarani rows = 21,850
distinct hadith_number = 13,555
duplicated number values = 1,103
max repeats of one number = 10   (numbers 1–10 each appear 9–10×)
```
Every deep link `hadith.html?book=tabarani&id=N` and every prev/next step into the range 1–10 is ambiguous — the app shows whichever row matches first. Same class of defect will break bookmarking and share links in the mobile app.

#### 4.7 Displayed book counts contradict shipped data (17 of 28 books)
Hardcoded in `js/app.js` `bookMasterDict` vs `books.ndjson → hadiths_count`:

| book | shown on kitab.html | actual data | delta |
|---|---|---|---|
| bukhari | 7.563 | 7,008 | −555 |
| **muslim** | **7.563** | **5,362** | **−2,201** (copy of Bukhari's number) |
| abudawud | 5.274 | 4,590 | −684 |
| tirmidhi | 3.956 | 3,891 | −65 |
| nasai | 5.758 | 5,662 | −96 |
| ibnmajah | 4.341 | 4,332 | −9 |
| malik | 1.720 | 1,595 | −125 |
| ahmad | 27.647 | 26,363 | −1,284 |
| darimi | 3.367 | 3,367 | ✓ |
| **mishkat** | **6.294** | **4,428** | **−1,866** |
| **bulugh** | **1.568** | **1,767** | **+199** |
| shamail | 415 | 402 | −13 |
| adab | 1.322 | 1,326 | +4 |
| riyad/qudsi/tabarani/syafii/… | match | | ✓ |

Chapter counts are also wrong: `muslim` 57 vs 56, `tirmidhi` 49 vs 50, `nasai` 52 vs 51, `ibnmajah` 37 vs 39, `malik` 56 vs 61, `bukhari` 97 vs 97✓.
Muslim showing Bukhari's count is the clearest signal this table was hand-maintained and drifted.

---

### HIGH

#### 4.5A Out-of-range or ambiguous `id` silently renders a different hadith — or a blank page
No 404, no "not found", no error state on `hadith.html` for a bad id:

| request | what renders |
|---|---|
| `?book=bukhari&id=99999` | **blank** — no hud, no Arabic, no message |
| `?book=muslim&id=99999` | **blank** |
| `?book=tabarani&id=21850` | **`Hadits #460`** — a different hadith entirely |
| `?book=tabarani&id=460` | `Hadits #460`, *different Arabic text than the row above* |
| `?book=malik&id=1596` | `Hadits #1596` although `books.ndjson` and `index` both say 1,595 |
| `?book=muslim&id=5363` | renders Arabic although the book has 5,362 |

Two problems in one: out-of-range ids fall back to *some* row instead of failing, and `tabarani`'s duplicate numbering (§4.6) means two different hadiths both answer to `#460`. A shared deep link or a stale bookmark can show the wrong hadith with no indication. Any mobile client must resolve `id` against `api/<book>_index.ndjson` itself and render an explicit error when absent.

#### 4.5B Invalid topic parameter renders an empty page with no message
`topic-hadiths.html` accepts only a numeric topic id (1–14). Anything else fails silently:

| URL | body text | hadith links |
|---|---|---|
| `?book=bukhari&topic=1` | 30,163 chars | 10 |
| `?book=bukhari` (no topic) | 30,163 chars | 10 — defaults to topic 1 |
| `?book=bukhari&topic=iman` (slug) | **509 chars** | **0**, no message, no console error |
| `?book=bukhari&topic=Iman` | **509 chars** | **0** |
| `?book=bukhari&topic=99` (out of range) | **509 chars** | **0** |

The page keeps its chrome and shows nothing where the hadith list belongs. Anyone landing from an old or slug-based link sees an empty page and no way to recover.

#### 4.5C Prev / Next never disable at book boundaries
`ahmad&id=26363` (last hadith) → `Next →` present, `disabled: false`. `ahmad&id=1` (first) → `← Prev` present, `disabled: false`. Clicking Next on the last hadith yields no navigation and leaves the HUD unchanged; the button stays live. Same for `bukhari&id=7008` and `tabarani&id=21850`.

#### 4.8 Three book entries have no data behind them
`bookMasterDict` contains entries absent from `books.ndjson`: `dehlawi`, `tabarani_kabir`, `ibn_abi_shaybah`.
`kitab.html?book=dehlawi` → HTTP 200, chapter container 1 placeholder, no hadiths, no error. Same for the other two. Users can reach a dead-end page that looks intentional.

#### 4.9 `ahmad` and `darimi` have no international edition (404)
```
api/fawaz/ahmad_index.ndjson   404     chapters/fawaz/ahmad.ndjson    404
api/fawaz/darimi_index.ndjson  404     chapters/fawaz/darimi.ndjson   404
```
Both are in `CORE9` (`js/api.js:88-96`), so international numbering is advertised for them and gets 404 → silent fallback. All 7 other core books return 200.

#### 4.9A No dataset switcher exists — "Data Sources" is a credits modal
The `Data Sources` button on `hadith.html` opens a modal (`source Data Sources, Credits & Anchoring`) that only *describes* the two sources:

> PRIMARY ANCHOR — Fawazahmed0 DB … 9 languages … 54 language–collection editions, 285,647 translated hadiths. Rows from this source also carry the numbering…
> LINKED SOURCE — Lidwa Hadith DB. Dynamically mapped to supply Indonesian translations, isnad chains (Sanad), and Kedudukan (Status) / Grading specifically for the core 9 books.

There is no control to switch the displayed dataset or numbering. Every `dataset-switch:*` case in `uat_flows.py` showed before == after for all 4 books tested. If a switcher is meant to ship, it is missing; if not, the modal wording ("PRIMARY ANCHOR" vs "LINKED SOURCE") implies a capability the UI does not have.

This copy also sets expectations worth checking against data: 54 editions claimed vs 70 declared in `books.ndjson` (17 dead, §4.10), and 285,647 translated hadiths claimed against 118,397 total hadiths shipped.

#### 4.10 17 edition references in `books.ndjson` point to files that do not exist — and cost 13 failed requests per list page
`books.ndjson` declares 70 edition ids; 17 return 404 on `editions/<id>.ndjson`:

```
ara-bukhari1  ara-muslim1  ara-abudawud1  ara-tirmidhi1  ara-nasai1
ara-ibnmajah1 ara-malik1
ara-nawawi  ara-nawawi1  ben-nawawi  eng-nawawi  fra-nawawi  tur-nawawi
ara-qudsi   ara-qudsi1  eng-qudsi   fra-qudsi
```
(The `*1` variants are a systematic suffix error; nawawi/qudsi have no editions published at all.)

`hadith-list.html` also *probes* editions that were never declared. Measured failed requests per page load:

| page | HTTP ≥400 |
|---|---|
| `hadith-list.html?book=muntaqa` | **13** |
| `hadith-list.html?book=maani` | **13** |
| `hadith-list.html?book=masabih` | **13** |
| `hadith-list.html?book=umdat` | **13** |
| `hadith.html?book=<any>` | 2–4 |

Example (`muntaqa`), each URL requested twice — once on `cdn.hadeeth.id`, once on the R2 origin:
```
404 cdn.hadeeth.id/editions/eng-muntaqa_index.ndjson
404 pub-075ac3f4….r2.dev/editions/eng-muntaqa_index.ndjson
404 cdn.hadeeth.id/editions/eng-muntaqa.ndjson
404 cdn.hadeeth.id/editions/ara-muntaqa_index.ndjson
404 cdn.hadeeth.id/editions/ara-muntaqa.ndjson   …
```
These six books have no editions at all, so the probe set should be gated on `books.ndjson → editions`, not guessed from `ara-<book>` / `eng-<book>`.

Additional inconsistency: `editions/_catalog.ndjson` (54 rows, keys `book`/`lang`/`rows`) reports **bukhari 7,580** and **abudawud 5,272** rows, while the shipped `api/bukhari_index.ndjson` has **7,008** and `api/fawaz/bukhari_index.ndjson` has **7,278** — three different totals for the same book.

#### 4.11 `tabarani` chapter ids are free-text, titles blank
```json
{"book_id":"tabarani","id":"tabarani_c260","chapter_number":"260","title_id":"","title_en":"","title_ar":"أبو…"}
```
2248 chapter rows; `title_id` and `title_en` empty. `muntaqa` worse — chapter_number is a raw pipeline id:
```json
{"chapter_number":"turath:1218:heading:0073", "id":"muntaqa_cturath:1218:heading:0073"}
```
These strings reach the UI and the URL (`hadith-list.html?book=muntaqa&chapter=turath:1218:heading:0073`). A mobile router that parses `chapter` as int will break; `kitab.html` displays 2,248 and 1,109 "chapters" respectively.

Confirmed user-visible on the hadith detail page — `hadith.html?book=muntaqa&id=1` renders the chapter breadcrumb as:

```
Bab turath:1218:heading:0073
```

`hadith.html?book=muntaqa&id=<mid>` → `Bab turath:1218:heading:0779`, `id=<last>` → `Bab turath:1218:heading:1344`.
For comparison `bukhari:1` renders `Bab 1: Permulaan wahyu`, and `tabarani`/`maani`/`masabih`/`umdat` all render the placeholder `Bab 1: Semua Hadits`.

`tabarani`'s chapter numbers are not the hadith's chapter either — the label is simply a pipeline counter:

| page | rendered label |
|---|---|
| `hadith.html?book=tabarani&id=1` | `Bab 5501` |
| `hadith.html?book=tabarani&id=5500` | `Bab 1462` |

Blank title rows across the corpus: `tabarani` 2,248/2,248, `muntaqa` 1,109/1,109. Every `muntaqa` chapter_number is non-integer (1,109/1,109).

#### 4.12 Sahih Muslim: 44% of hadiths have no grade
Full-file scan `api/muslim.ndjson` (5,362 rows):
```
grade present  : 2,995  (55.9%)
status present : 2,989  (55.7%)
```
Sampled presence for the other books: `tirmidhi` 93%, all others 100%.
Muslim's own collection is graded as a whole, but per-hadith the app shows a blank badge on 2,367 hadiths — inconsistent with every other book in the UI.

#### 4.13 Sanad page empty for `tabarani`
```
sanad.html?book=bukhari&id=1    nodes=9   len=1858  arabic=99   ✓
sanad.html?book=muslim&id=1     nodes=9   len=1803  arabic=75   ✓
sanad.html?book=tabarani&id=1   nodes=1   len= 671  arabic= 7   ✗
```
No error shown; page renders the header and an empty chain. Silent blank state.

#### 4.14 Scholars page: wrong Arabic name + duplicated unit
```
PERAWI (RAWI)  أنس بن مالك بن النضر
Imam Malik bin Anas
Wafat: 91 H H • Bashrah
```
- Card for **Imam Malik bin Anas** (d. 179 H) shows the Arabic name of **Anas bin Malik** (d. 93 H) — `getCleanArabicName()` maps the wrong id.
- `Wafat: 91 H H` — `dateStr += \`Wafat: ${r.died_ah} H\`` at `scholars.html:607` when `died_ah` already carries the unit (`"91 H"`).
- `Anas` also matches `Malik bin Anas` and `Mus'ab bin Anas`; substring matching with no word boundary.

#### 4.15 Glossary search fails in Indonesian; works in English
Same page, same session (`LangSystem.get() === 'id'`):

| typed | result |
|---|---|
| `Hadith` | 17 groups |
| `hadis` | **"No terms found matching your search."** |
| `Hadis` | **"No terms found matching your search."** |
| `sunnah` | 1 group |
| `zzz` | No terms found |

`renderGlossary()` (`glossary.html:199-204`) filters `term_en / term_id / def_en / def_id` case-insensitively, so `hadis` matching nothing while the page is displaying Indonesian definitions means the Indonesian fields are empty for most terms. Indonesian users cannot search the glossary in their own language.

#### 4.15A Topics index is built against pre-migration numbering — 3,830 dead references
`topics_index.ndjson` (126 rows, `b`/`t`/`n[]`) references hadith numbers from the older, larger corpus, while `api/<book>_index.ndjson` ships the Lidwa corpus. Numbers past the end of each shipped book simply do not resolve:

| book | topic refs | unresolved | broken | rows shipped | highest ref |
|---|---|---|---|---|---|
| **malik** | 2,945 | **635** | **21.6%** | 1,595 | 1,894 |
| **abudawud** | 8,650 | **1,196** | **13.8%** | 4,590 | 5,273 |
| **bukhari** | 16,458 | **1,328** | **8.1%** | 7,008 | 7,580 |
| darimi | 6,618 | 298 | 4.5% | 3,367 | 3,367 |
| nasai | 11,740 | 219 | 1.9% | 5,662 | 5,757 |
| tirmidhi | 8,532 | 139 | 1.6% | 3,891 | 3,956 |
| ibnmajah | 8,302 | 15 | 0.2% | 4,332 | 4,341 |
| muslim | 7,481 | 0 | 0% | 5,362 | 5,362 |
| ahmad | 57,933 | 0 | 0% | 26,363 | 26,363 |
| **total** | **128,659** | **3,830** | **3.0%** | | |

Malik's highest referenced number is 1,894 against 1,595 rows; Bukhari's is 7,580 against 7,008; Abu Dawud's 5,273 against 4,590 — the same figures as the stale `bookMasterDict` counts (§4.7) and the `editions/_catalog` row counts (§4.10). All three artifacts were generated from the pre-migration corpus and were not regenerated after the switch.

**User-visible consequence:** topic pagination silently empties out.
```
bukhari  topic1  "Menampilkan 1-10 dari 1874 … (Hal 1 dari 188)"  → next → "11-20 … (Hal 2 dari 188)"  ✓
muslim   topic1  "Menampilkan 1-10 dari 1112 … (Hal 1 dari 112)"  → next → "11-20 … (Hal 2 dari 112)"  ✓
ahmad    topic1  "Menampilkan 1-10 dari 9249 … (Hal 1 dari 925)"  → next → "11-20 … (Hal 2 dari 925)"  ✓
malik    topic1  "Menampilkan 1-10 dari 261 …  (Hal 1 dari 27)"   → next → "1-10 … (Hal 1 dari 27)", list goes EMPTY (0 hadith links)
```
`malik` topic 1 has 261 claimed members, 82 of them unresolvable — and every member above 1,595 is dead, so later pages render blank with a live-looking paginator.

Healthy reference resolution: `muslim` and `ahmad` (0 broken); `topics-in-kitab.html` counts and `topic-hadiths.html` labels are otherwise correct and Indonesian (`Topik: Iman`, `Topik: Al Qur'an`).

#### 4.15B Chapter titles are placeholders that duplicate the number — 176 rows, revealed by fixing §4.2
The chapter label is built as `` `Bab ${chapter_number}: ${title_id}` ``. For six books `title_id` holds `"Bab N"` instead of a real title, so the label repeats itself:

```
hadith.html?book=riyad&id=1     → Bab 1: Bab 1
hadith.html?book=shamail&id=1   → Bab 1: Bab 1
hadith.html?book=qudsi&id=1     → Bab 0: Bab 0
bukhari (correct)               → Bab 1: Permulaan wahyu
```

| book | rows | title matches `Bab <num>` |
|---|---|---|
| adab | 57 | **57** |
| bulugh | 16 | **16** |
| mishkat | 25 | **25** |
| riyad | 20 | **20** |
| shamail | 57 | **57** |
| qudsi | 1 | **1** |
| **total** | **176** | **176** |

**These are the same five books blocked by the `titleId` crash (§4.2)** plus `qudsi`. Fixing §4.2 will surface 176 self-repeating chapter labels in place of the current empty list — the two must ship together.

Also in this data: `shamail` has `chapter_number` `"8.2"` (non-integer) as its first row, out of numeric order; `riyad` starts at `chapter_number 0`.

#### 4.15C Syarah and grade are mostly absent — the UI offers both everywhere
Measured against `commentaries/_catalog.ndjson` (21 books) and 400 rows/book of `api/<book>.ndjson`.

**Indonesian syarah is effectively non-existent: 14 rows in the entire corpus.**

| book | anchored rows | ar | en | **id** |
|---|---|---|---|---|
| bukhari | 4,719 | 4,135 | 1,337 | **0** |
| muslim | 5,184 | 5,004 | 520 | 1 |
| mishkat | 2,737 | 2,737 | 0 | **0** |
| abudawud | 2,024 | 1,986 | 75 | 8 |
| bulugh | 1,003 | 1,003 | 0 | **0** |
| riyad | 205 | 205 | 0 | **0** |
| adab | 142 | 142 | 0 | **0** |
| ibnmajah | 25 | 0 | 25 | 0 |
| qudsi / tirmidhi / shah / nawawi | 13 / 10 / 7 / 5 | — | — | 0 / 0 / 0 / 5 |
| **total** | **16,074** | **15,237** | **1,972** | **14 (0.09%)** |

The UI shows a "Syarah Bahasa Indonesia" option on every hadith page; it resolves for bukhari, mishkat, bulugh, riyad, adab → nothing, with the explanation *"Syarah Bahasa Indonesia tidak tersedia"*.

**Nine books have commentary text but zero anchors** — the join key is missing, so no syarah is reachable at all:

| book | commentary rows present | matched | **anchors** |
|---|---|---|---|
| maani | 6,635 | 6,635 | **0** |
| nasai | 11,292 | 5,662 | **0** |
| muntaqa | 3,944 | 3,944 | **0** |
| syafii | 1,446 | 1,446 | **0** |
| malik | 2,190 | 1,595 | **0** |
| masabih | 1,539 | 1,536 | **0** |
| umdat | 411 | 411 | **0** |
| shamail | 402 | 402 | **0** |
| ahmad | 272 | 269 | **0** |

That is **28,131 commentary rows** (a quarter of the corpus's commentary text) that exist on the CDN but cannot be surfaced — `ahmad:1` and `tabarani:1` render *"Syarah tidak tersedia untuk hadits ini."* with `tabs=0`.

**Grade badge also absent for 19 of 28 books** (0% of 400 sampled rows each): nawawi, qudsi, shah, adab, bulugh, mishkat, riyad, shamail, tabarani, syafii, riyad_arab, ibnukhuzaimah, ibnuhibban, mustadrak, daruquthni, muntaqa, maani, masabih, umdat. Core eight are 100% except Muslim (68% in the first 400 rows, 55.9% full-file — §4.12).

#### 4.15D Chapter counts on the list page disagree with the chapter sidecar — Muslim is mapped to the wrong chapters

> **FIXED in fix batch 3 (25 Nov 2026).** Root cause: the list page defaulted its dataset to `fawazahmed`, so chapter contents came from `api/fawaz/<book>_index.ndjson` while the chapter list came from the Lidwa sidecar — two different editions under the same chapter titles. `kitab.html` additionally read `lidwa-chapters/`, which disagrees with the index on bukhari/abudawud/tirmidhi. Both readers now resolve to one corpus. See §8.5 for the verification table.

`chapters/<book>.ndjson` carries its own `hadith_start` / `hadith_end` / `hadith_count`. `hadith-list.html?book=X&chapter=N` ignores them:

| page | sidecar `hadith_count` | UI indicator | verdict |
|---|---|---|---|
| `riyad` ch 1 | 47 | `1–10 dari 47 (Hal 1 dari 5)` | ✓ exact |
| `bukhari` ch 1 | 6 | `1–7 dari 7 (Hal 1 dari 1)` | **+1** |
| `bukhari` ch 2 | 50 | `1–10 dari 51 (Hal 1 dari 6)` | **+1** |
| `bukhari` ch 97 | 186 | `1–10 dari 188 (Hal 1 dari 19)` | **+2** |
| `muslim` ch 1 | **8** | `1–10 dari 436 (Hal 1 dari 44)` | **55× wrong** |
| `muslim` ch 2 | **319** | `1–10 dari 143 (Hal 1 dari 15)` | wrong |
| `muslim` ch 3 | **112** | `1–10 dari 157 (Hal 1 dari 16)` | wrong |

Sidecar, verbatim:
```json
{"book_id":"muslim","id":"muslim_c1","chapter_number":1,"title_id":"Mukadimah",
 "title_en":"Introduction","hadith_start":1,"hadith_end":8,"hadith_count":8}
{"book_id":"bukhari","id":"bukhari_c1","chapter_number":1,"title_id":"Permulaan wahyu",
 "hadith_start":1,"hadith_end":6,"hadith_count":6}
```
`muslim` chapter 1 is the 8-hadith *Mukadimah*, but the page returns 436 hadiths — that is the count of Muslim's first *book* (Kitab al-Iman), so the list page is resolving a different chapter namespace than the sidecar. For Bukhari the drift is smaller but systematic: +1 on every chapter (boundary hadith counted in both chapters), +2 on chapter 97.

**This is the most dangerous single defect for the mobile app:** a client that builds chapter navigation from `chapters/*.ndjson` (the correct source, with `hadith_start`/`hadith_end`) will display a different hadith set than the web app shows today for Muslim — the second-most important book in the corpus.

Related: `bukhari&chapter=0` renders `1–1 dari 1` for a chapter that does not exist (index has no `c='0'`), and `tabarani&chapter=1` / `muntaqa&chapter=1` render the label `0 of 0` while still drawing 1 row — the count says zero and the body shows content.

#### 4.15E `books.ndjson → total_chapters` disagrees with the shipped sidecar for 18 of 28 books
Declared count vs rows actually in `chapters/<book>.ndjson`:

| book | declared | shipped | delta |
|---|---|---|---|
| **malik** | 61 | **32** | **−29** |
| **ahmad** | 90 | **14** | **−76** |
| ibnmajah | 39 | 38 | −1 |
| **adab** | 1 | **57** | **+56** |
| **shamail** | 1 | **57** | **+56** |
| mishkat | 1 | 25 | +24 |
| riyad | 1 | 20 | +19 |
| bulugh | 1 | 16 | +15 |
| tabarani | 1 | 2,248 | +2,247 |
| abudawud | 43 | 50 | +7 |
| tirmidhi | 50 | 52 | +2 |
| muslim / nasai | 56 / 51 | 57 / 52 | +1 |
| maani / masabih / umdat / syafii / riyad_arab | 0 | 1 | +1 |
| bukhari / darimi / nawawi / qudsi / shah / muntaqa | correct | | 0 |

The deltas run in both directions, so this is not a single off-by-one — the field was populated from inconsistent sources. `ahmad` (−76) and `malik` (−29) understate the real gap; `tabarani` (+2,247) and the six stub books (+15…+56) overstate it. Anything that trusts `total_chapters` — a mobile catalogue screen, a progress estimate — will be wrong for two thirds of the corpus.

**Chapter bound defects (from `hadith_start`/`hadith_end` coverage):**

| book | last `hadith_end` | index rows | defect |
|---|---|---|---|
| `malik` | 1,594 | 1,595 | **hadith #1595 belongs to no chapter** — unreachable by chapter navigation |
| `daruquthni` | 239 | 236 | chapter claims 3 hadiths that do not exist |
| `masabih` | 4,931 | 4,929 | chapter claims 2 hadiths that do not exist |
| `tabarani` | 13,622 | 21,850 rows / 13,555 distinct numbers | 32 distinct numbers inside the span have no chapter |

All other 24 books: chapter coverage exact, 0 uncovered, `hadith_end` equals the highest hadith number.

---

### MEDIUM

#### 4.16 Only Bukhari has Indonesian chapter titles
`indonesianChapterTitles` in `js/app.js` contains **90 keys, all `bukhari_*`** — 0 keys for the other 27 books, and only 90 of Bukhari's 97 chapters. With UI in Indonesian, every other book's chapter list falls back to English titles (`"Chapter 260"`, `"Bab 8.2"`).

#### 4.17 Mobile: docs.html table overflows the viewport
At 390×844 `docs.html`: `documentElement.scrollWidth − innerWidth = 0` but 6 elements exceed the viewport, widest `TABLE.w-full.text-xs.border-collapse` at **412 px** (>390). Horizontal scroll inside the docs tables. All 9 other pages tested: 0 overflowing elements.

#### 4.18 Mobile: tap targets under 32 px
| page | targets < 32 px |
|---|---|
| `topic-hadiths.html` | **75** |
| `scholars.html` | 25 |
| `hadith.html` | 18 |
| `index.html` | 10 |
| `kitab.html` | 10 |
| `docs.html` | 10 |

Plus 93 text nodes below 11 px on `sanad.html`, 41 on `docs.html`.

#### 4.19 Razi assistant: functional, but 20–40 s to an answer, no streaming
End-to-end test on `index.html` — open launcher, type `Apa hadis tentang niat?`, press send:

```
panel class: 'razi-closed' -> ''            (opens correctly)
textarea  : visible, 321 px
send btn  : 'razi-send', visible, enabled, 40 px
POST https://razi.hadeeth.id/api/chat -> 200  application/json
```

Response body:
```json
{"reply":"[Hadis Riyad #1229](https://hadeeth.id/hadith.html?book=riyad&id=1229) | [Ayat 11:15](https://tafseer.id/#sura/11/verse/15) …
 \"session_id\":\"web_2f952e…\",\"box\":\"https://raziapi2.broadandbright.id\"}
```
Answer quality good — cites Riyad #1229 and Qur'an 11:15/16:106 with working links.

But the timeline is a problem for mobile:
```
t+10s  panel 365 chars, spinner on, no answer
t+20s  412 chars, status "Masih mencari — yang ini but…"
t+40s  946 chars, full answer appears at once   (no streaming)
```
**40 s to first answer, and it arrives as one block** — the reply is not streamed, so there is no progressive text. On mobile data this is a 40 s dead screen behind a spinner. `razi.hadeeth.id/api/chat` is `application/json`, so streaming requires a server change, not just client.

Earlier observation of 3× HTTP 500 from the Razi backend appeared in one crawl and did not reproduce in four subsequent runs — treat as transient but log it server-side before mobile ships.

#### 4.19A Two different API hosts behind one widget
The widget posts to `razi.hadeeth.id/api/chat`, and the payload returns `"box":"https://raziapi2.broadandbright.id"`. Two origins, one feature — confirm the mobile client targets the same one and that CORS is configured for the app origin.

#### 4.20 Two failing requests on every hadith page load
```
GET https://cdn.hadeeth.id/commentaries/matched/qudsi_index.ndjson      404
GET https://cdn.hadeeth.id/commentaries/matched/tabarani_index.ndjson   404
GET https://cdn.hadeeth.id/commentaries/matched/shah_index.ndjson       404
GET https://cdn.hadeeth.id/commentaries/matched/darimi_index.ndjson     404
GET https://cdn.hadeeth.id/links/maani.ndjson                           404
```
Each book requests both `cdn.hadeeth.id` and the R2 origin, so a single hadith view logs 2 failed requests. Harmless to the render but pollutes mobile telemetry and any "offline-safe" logic.

#### 4.21 Privacy policy promises Apple sign-in; login page has none
`privacy.html` §8: *"…created an account (via Email, Google, Apple, or Facebook)"*.
`login.html` offers Email, Google, Facebook — **no Apple**. Relevant because App Store review requires Sign in with Apple when other social logins are offered.

#### 4.22 `<html lang>` inconsistent across pages
Repeated loads (3× each):
```
index.html          lang="en"
books.html          lang="id"
hadith.html         lang="en"
topic-hadiths.html  lang="en"
```
Nav labels stay Indonesian throughout. Wrong `lang` on a page with Indonesian body text breaks screen readers and mobile font shaping (Arabic-Indic digit selection).

#### 4.23 Test artifact deployed to production
`https://hadeeth.id/test_hotd.html` → 200.

#### 4.24 Topic title localization inconsistent
`topic-hadiths.html?book=bukhari&topic=1` renders Indonesian (`Topik: Iman`); `…&topic=5` renders English (`Topic: The Quran`). Same page, same session. `topics_index.ndjson` carries no title fields (`keys: b, n, t`) so titles come from a partial static map.

---

### LOW

#### 4.25 `topics_index.ndjson` is thin
126 rows, 14 topics × 9 books. `topics.html` advertises "~18,921 Hadiths" while the shipped topic index references a subset only.
#### 4.26 Grade vocabulary mixed AR-transliteration and EN
`ISNAD SHAHIH`, `SAHIH`, `HASAN SAHIH`, `Shahih`, `Sahih` all appear as badge text; `malik` shows both `SAHIH` and `Shahih` on the same page. Normalize before the mobile client renders badges.
#### 4.27 `hadith.html` renders 3 legacy 404 requests before falling back (same class as 4.20).
#### 4.28 `profile-detail.html` breadcrumb never leaves "Loading..."
Breadcrumb span `#breadcrumb-name` (`profile-detail.html:92`) keeps the literal placeholder after the profile has fully rendered:
```
Home / Profile / Loading...
```
Every other placeholder on the same page is filled (`Nasab`, `Kunyah`, `Tahun Lahir & Wafat`, the 5,374-narration breakdown, Jarh wa Ta'dil). Reproduced with and without `?id=`; 0 page errors, 0 failed requests. Load time 0.55–1.35 s — this is a display bug, not a slow render.
#### 4.29 `profile.html` and `scholars.html` emit unresolved template literals into `href`/`src` when a user has no avatar (`https://hadeeth.id/${profileUrl}`) — only reachable for logged-in users with partial metadata.
#### 4.30 Tailwind loaded from CDN in production
`cdn.tailwindcss.com` logs on every page: *"cdn.tailwindcss.com should not be used in production."* Adds a runtime JIT compiler to every route — a direct cost to mobile cold-start. Also affects the mobile shell if the same pages are wrapped.

---

## 5. Data-readiness summary (CDN)

| book | index rows | file | gaps | tail | dup numbers | chapters declared / shipped |
|---|---|---|---|---|---|---|
| bukhari | 7,008 | 40.19 MB | 0 | 0 | 0 | 97 / 97 |
| muslim | 5,362 | 35.21 MB | 0 | 0 | 0 | 56 / 57 |
| abudawud | 4,590 | 23.27 MB | 0 | 0 | 0 | 43 / 50 |
| tirmidhi | 3,891 | 23.11 MB | 0 | 0 | 0 | 50 / 52 |
| nasai | 5,662 | 24.28 MB | 0 | 0 | 0 | 51 / 52 |
| ibnmajah | 4,332 | 18.07 MB | 0 | 0 | 0 | 39 / 38 |
| malik | 1,595 | 5.09 MB | 0 | 0 | 0 | **61 / 32 (1 hadith uncovered)** |
| darimi | 3,367 | 11.04 MB | 0 | 0 | 0 | 24 / 24 |
| **ahmad** | 26,363 | 99.38 MB | 0 | 0 | 0 | **90 / 14** |
| nawawi | 42 | 0.11 MB | 0 | 0 | 0 | 1 / 1 |
| qudsi | 40 | 0.12 MB | 0 | 0 | 0 | 1 / 1 |
| shah | 40 | 0.02 MB | 0 | 0 | 0 | 1 / 1 |
| adab | 1,326 | 2.65 MB | 0 | 0 | 0 | 1 / 57 |
| bulugh | 1,767 | 3.41 MB | 0 | 0 | 0 | 1 / 16 |
| mishkat | 4,428 | 7.82 MB | 0 | 0 | 0 | 1 / 25 |
| riyad | 1,896 | 7.19 MB | 0 | 0 | 0 | 1 / 20 |
| shamail | 402 | 0.80 MB | 0 | 0 | 0 | 1 / 57 |
| **tabarani** | 21,850 | 29.95 MB | 0 | 0 | **8,295** | 1 / 2248 |
| syafii | 1,800 | 4.90 MB | 0 | 0 | 0 | 0 / 1 |
| riyad_arab | 850 | 2.06 MB | 0 | 0 | 0 | 0 / 1 |
| ibnukhuzaimah | 1,808 | 3.98 MB | 0 | 0 | 0 | – / 1 |
| ibnuhibban | 2,769 | 6.08 MB | 0 | 0 | 0 | – / 1 |
| mustadrak | 673 | 1.77 MB | 0 | 0 | 0 | – / 1 |
| daruquthni | 236 | 0.50 MB | 0 | 0 | 0 | – / 1 (**end 239 > 236 rows**) |
| muntaqa | 3,944 | 2.61 MB | 0 | 0 | 0 | 1109 / 1109 |
| maani | 7,013 | 5.89 MB | 0 | 0 | 0 | 0 / 1 |
| masabih | 4,929 | 2.80 MB | 0 | 0 | 0 | 0 / 1 (**end 4,931 > 4,929 rows**) |
| umdat | 414 | 0.35 MB | 0 | 0 | 0 | 0 / 1 |

Totals: **28 books, 118,397 hadiths** (core nine 62,170 / others 56,227).

**Row-count agreement (checked for all 28 books, exact):** `books.ndjson → hadiths_count` = rows in `api/<book>_index.ndjson` = rows in `api/<book>.ndjson`, **0 deltas**. The shipped corpus is self-consistent — so every wrong number a user sees (§4.7 stale `bookMasterDict` labels, §4.10 `editions/_catalog` totals, §4.15E `total_chapters`) is a **stale constant or stale derived file**, not a defect in the hadith payload itself. That is the single most encouraging result in this audit: the data is sound, the metadata layered on top of it is not.
Byte offsets: **84/84 spot checks correct**, zero gaps, zero tail drift — the index layer is production-grade.
Defects are in **metadata (counts, chapter maps, editions) and numbering (tabarani)**, not in the text payloads.

Field presence (30 samples/book over HTTP Range):

| book | text_ar | text_id | text_en (native) | rawis | grade |
|---|---|---|---|---|---|
| bukhari | 100% | 100% | 100% | 100% | 100% |
| muslim | 100% | 100% | 100% | 100% | **56%** (full file) |
| abudawud–ahmad | 100% | 100% | 0% (via `api/fawaz/`) | 100% | 93–100% |
| nawawi/qudsi/shah/adab/bulugh/mishkat/riyad/shamail | 100% | 0–90% | 100% | 0% | 0% |
| tabarani/muntaqa/maani/masabih/umdat/syafii/… | 100% | 0% | 0% | 0% | 0% |

Note `rawis: 0%` for the 8 non-core books with `text_en` — sanad/scholar links do not exist for them, which is why §4.13 (empty sanad) is structural, not a render bug.

---

## 6. Fix order

**Before any mobile work (blocking):**
1. §4.2 declare `titleId` — unblocks 175 chapter rows across 5 books. *One line.*
2. §4.15B supply real chapter titles for those same 5 books (176 rows currently read `Bab 1: Bab 1`) — do it in the same commit as item 1 or the fix exposes a second visible defect.
3. §4.15D reconcile chapter resolution between `chapters/*.ndjson` (`hadith_start`/`hadith_end`) and `hadith-list.html` — Muslim chapter 1 shows 436 hadiths where the sidecar says 8. Lock the mobile client to one source before writing any chapter UI.
4. §4.1 add a similarity floor + real empty state; stop printing "AUTHENTIC MATCHES" for zero-score rows.
5. §4.3/§4.4/§4.15E generate chapter maps for the 12 stub books + the missing 76 for `ahmad` and 29 for `malik`; stop shipping `"Bab 0"`; regenerate `books.ndjson → total_chapters` (wrong for 18 of 28). Note `maani` has `c=null` on all 7,013 index rows and `malik` hadith #1595 has no chapter.
6. §4.6 renumber `tabarani` (13,555 distinct numbers for 21,850 rows must be resolved before deep links are shipped).
7. §4.15A regenerate `topics_index.ndjson` against the current corpus — 3,830 dead topic references, 21.6% of Malik's. Regenerate `bookMasterDict` counts (§4.7) and `editions/_catalog` (§4.10) in the same pass; all three are the same stale-corpus bug.
8. §4.7 compute counts from `books.ndjson` at render time — delete `bookMasterDict` counts.
9. §4.5 fix `riyad`/`nawawi` EN mapping (or hide the EN tab when `text_en` is absent).

**Data corrections (same sprint):**
10. §4.8 delete or populate `dehlawi`, `tabarani_kabir`, `ibn_abi_shaybah`.
11. §4.9/§4.10 fix `CORE9` membership for ahmad/darimi; drop the 17 dead edition ids; gate edition probes on `books.ndjson → editions` (kills 13 404s per list page); reconcile the three bukhari totals (7,008 / 7,278 / 7,580).
12. §4.11 normalize `tabarani`/`muntaqa` chapter ids to integers and fill the 3,357 blank titles.
13. §4.12/§4.15C decide grade + syarah as product scope: either backfill (Muslim grades, 19 books' grade fields, 28,131 unanchored commentary rows) or hide the badge/tab per book. **Do not ship a mobile syarah tab that resolves for 6 of 28 books and an Indonesian syarah tab that has 14 rows in the whole corpus.**
14. §4.15 fix glossary ID search.

**Before public mobile release:**
15. §4.5A–§4.5C error states: reject out-of-range/duplicate ids, message for bad `topic`, disable Prev/Next at edges.
16. §4.17–4.18 mobile docs table + tap targets.
17. §4.21 add Apple sign-in or remove the promise from `privacy.html`.
18. §4.16 Indonesian chapter titles for the 27 remaining books.
19. §4.19 Razi 40 s non-streamed reply (server change needed for mobile); §4.20 remove the 404 probes; §4.22 `lang`; §4.23 delete `test_hotd.html`; §4.28 breadcrumb; §4.30 Tailwind CDN.

---

## 7. Not verified / out of scope

- **Authenticated flows** (signup, Google/Facebook OAuth completion, bookmark sync, reading-history persistence) — no test account, no credentials handled. Login page render only.
- **Razi answer correctness** — widget opens and accepts input; answer quality not judged.
- **Syrah text correctness** (only presence and tab availability checked).
- **Hadith text accuracy against print sources** — corpus integrity (offsets, numbering, field presence) verified, theological/editorial accuracy not.
- **Admin console** (`admin.html`) — served (200) but not exercised; it is 57,819 bytes with 10 duplicated `glossaryDrafts` declarations, worth a separate review before it is exposed on mobile.
- **Bulk data mutation** — no writes attempted anywhere; read-only audit.

---

*Artifacts:* `_audit/uat_2026-11-24/` — `uat_kitab_matrix.json`, `uat_list.json`, `uat_panels.json`, `uat_fails.json`, `uat_clickthrough.json`, `uat_home_search.json`, `uat_latency.json`, `uat_glossary_probe.json`, `uat_search_pages.json`, `uat_mobile.json`, `uat_perf.json`, `integrity_index.json`, `field_matrix.json`, `linkcheck.json`, plus `*.log` and `dom/*` dumps.

---

## 8. Fix batch 1 — 25 November 2026

Verified on `http://127.0.0.1:8765` (edited `js/` from the working tree, live CDN data, local chapter sidecars, `/api/search` proxied to the deployed worker). Evidence: `verify_batch1.json`, `verify_fixes_1_2.json`, `verify_search_gate.json`, `verify_errorstates.json`, `verify_failcount.json`, `similarity_spread.json`, `probe_grounding.py`, `probe_keyword_gate.py`.

### 8.1 Applied and verified

| Finding | Change | Verified result |
|---|---|---|
| §4.2 | `js/app.js`: BRANCH B compared `titleAr` against undeclared `titleId`; now compares `titleEn` | adab 57, bulugh 16, mishkat 25, riyad 20, shamail 57, qudsi 1 chapter cards render; **0 `pageerror`** (was 0 cards + `ReferenceError`) |
| §4.15B | `_audit/fix_chapter_titles_2026-11-24.py`: joined each sidecar chapter to its AhmedBaset `by_book` title; wrote `data/chapters/{adab,bulugh,mishkat,riyad,shamail,qudsi}.json` and the six shipped `export_site/chapters/*.ndjson` | **176/176** placeholder titles replaced; ranges, counts and row order asserted unchanged, exact 1:1 chapter-id join (57/57, 16/16, 25/25, 20/20, 57/57, 1/1). e.g. `adab_c1` `Bab 1 → Parents`, `qudsi_c0` `Bab 0 → Forty Hadith Qudsi`. No Indonesian titles exist for these books, so `title_id` takes the real English title. |
| §4.7 (chapter count) | `js/app.js`: derive `[data-book-kitab-count]` from the cards actually rendered | mishkat 29 → **25**, bukhari 97 → **98**, adab 1 → **57**, riyad 1 → **20**; control books unchanged |
| §4.1 | `js/api.js`: Meilisearch gate for the semantic tier; `js/app.js`: drop "authentic" from the result header | Stubbed gate: 0 lexical candidates → semantic skipped, 0 results, real empty state; candidates present → semantic answers; keyword tier down → fail-open. Similarity floor deliberately **not** used: `niat` (real, 0.489) scores below `zzzzqqqxxx` (junk, 0.486). Meilisearch returns 0 hits for all 8 gibberish queries and 2–20 for all real queries. |
| §4.5A (range) | `js/api.js`: `isOutOfRange()` + `getHadithRange()`; `js/app.js`: bilingual not-found panel with book range and back links | `hadith.html?book=bukhari&id=99999` → "Hadis #99999 tidak ditemukan di BUKHARI. Kitab ini memuat hadis 1–7.563" + two working links; `?book=bukhari&id=1` unaffected (8,236 chars, Arabic present) |
| §4.10 / §4.20 | `js/api.js`: catalogue-gated `getEdition()`/`getEditionText()`, cached `getEditionCatalog()`, `fetchNdjsonFull('sources/lidwa')` short-circuit; `js/app.js`: skip unmapped AhmedBaset book | `hadith-list?book=muntaqa` **13 → 2** failed requests (only the two `links/muntaqa.ndjson` probes remain); bukhari list **2 → 0**; hadith detail **0 → 0** |
| §4.22 | `js/app.js`: `LangSystem.apply()` writes `document.documentElement.lang` | `id` by default, `en` after toggle, `id` after toggle back; `data-lang` matches |
| §4.23 | `git rm test_hotd.html` | unreferenced debug page removed from the tree |

`node --check js/app.js` and `node --check js/api.js`: **both pass**.

### 8.2 Audit findings corrected on re-test

These were reported from the 24 Nov run but **do not reproduce** against the deployed build (at audit time its JS hashes matched local `HEAD` exactly). They are not defects to fix:

- **§4.7 hadith counts** — `getBooks()` already overrides the constants at render time. Live kitab.html shows bukhari `7.008`, muslim `5.362`, mishkat `4.428`, bulugh `1.767`. Only the *chapter* count literal was still stale (fixed above).
- **§4.5A "silently renders a different hadith"** — `malik&id=1596` is **valid** in International numbering: `api/fawaz/malik_index.ndjson` has 1,653 rows, `n` 1–1,858. The audit compared it against the 1,595-row Lidwa corpus. `tabarani&id=21850` is in range and has a numbering problem (§4.6), not an error-state problem.
- **§4.5B bad topic** — `topic=iman`, `topic=99` and `topic=1` all render the same 38,962-char list with 7 links. The 509-char blank list was a load race. An unknown topic silently falls back to the default list (low severity, not high).
- **§4.5C Prev/Next** — already disabled at edges via `pointer-events-none` + `opacity-50`: `ahmad&id=26363` next off, `ahmad&id=1` prev off. The audit checked a `disabled` attribute that anchors do not have.
- **§4.20 "2–4 failed CDN requests per hadith page"** — fresh capture: **0** on `bukhari:1` and `shamail:1`. The 404s were on `hadith-list.html`, addressed above.
- **§4.1 "empty state unreachable because no similarity floor"** — the empty-state markup existed and works; the cascade never reached it. The gate replaces the proposed threshold for the reason above.

### 8.3 Still open

1. **12 stub chapters, ahmad −76 / malik −29 chapters, `total_chapters` wrong for 18 books, malik #1595 unchaptered** (§4.3/§4.4/§4.15E) — build job, no upload yet.
2. **§4.6 tabarani 8,295 duplicate numbers** — build job.
3. **§4.15A 3,830 dead topic references** — regenerate `topics_index.ndjson` against the shipped corpus.
4. **§4.15D muslim chapter 1: sidecar 8 vs UI 436** — needs a product decision on the canonical chapter source before any mobile chapter UI.
5. **§4.15C syarah/grade scope, §4.8 dead books, §4.9A dataset switcher, §4.21 Apple sign-in, §4.16 ID chapter titles** — all need a decision; none touched.
6. **Deploy**: nothing in §8.1 is live. Site JS deploys by push to `main`; data by `scripts/site_r2.py upload`. Neither was run.

### 8.4 Fix batch 2 — 25 November 2026

Verified the same way (local server `:8765`, live CDN data).

| Finding | Change | Verified |
|---|---|---|
| §4.15 glossary ID search | `glossary.html` folds Indonesian spelling variants (`hadis`/`hadist` → `hadits`, `sunnah` → `sunna`, `rowi` → `rawi`) on both query and haystack | `hadis` 0 → **18** groups; `Hadits` 18; `sunnah` 2 |
| §4.28 profile breadcrumb | `profile-detail.html` writes the resolved name into `#breadcrumb-name` | `Anas bin Malik al-Anshari`, no longer "Loading..." |
| §4.14 `Wafat: 91 H H` | era suffix stripped from `died_ah` before re-appending, on both profile and scholars card | `Wafat: 57 H`, `93 AH / 712 CE`, zero double-era matches |

Still not deployed. The five decisions in §8.3 items 4–5 are unanswered, and §8.3 items 1–3 are the build jobs that need an upload window.

### 8.5 Fix batch 3 — chapter sources unified, Lidwa is the default (25 November 2026)

Decision taken: **Lidwa is the default dataset for the nine core books.**

**What was actually wrong.** The chapter *list* and the chapter *contents* were resolved by two different functions, and `lidwa-chapters/` is a stale fourth copy:

| reader | source used | for muslim ch1 |
|---|---|---|
| `kitab.html` chapter cards (BRANCH A) | `chapters/fawaz/` | 436 |
| `kitab.html` chapter cards (Lidwa branch) | `lidwa-chapters/` | 8 (but 237 on bukhari) |
| `hadith-list.html` chapter contents | `api/fawaz/` | 436 |
| `api/<book>_index.ndjson` → `c` column | Lidwa | 8 |

`lidwa-chapters/` disagrees with the index in the direction that matters:

| book | `chapters/` ch1 | `lidwa-chapters/` ch1 | index `c=='1'` |
|---|---|---|---|
| bukhari | 6 | 237 | **6** |
| abudawud | 330 | 390 | **330** |
| tirmidhi | 137 | 148 | **137** |

**Changes**

- `resolveDataset(bookId, …)` is now the single default resolver, used by the dataset switcher pills, `hadith.html`, `hadith-list.html` and `kitab.html`. No stored choice resolves to `BOOK_DATASETS[bookId][0]`, which is `native_lidwa` for the nine core books. Previously the fallback literal `'fawazahmed'` was a *valid* entry, so it was accepted and the site silently ran on the International edition while labelling Lidwa "Utama".
- `HadeethAPI.defaultDataset(bookId)` — `getChapters()` and `getChapterHadiths()` now fall back to it instead of `fawazahmed`.
- `getLidwaChapters()` delegates to `getChapters(bookId, 'native_lidwa')`. `lidwa-chapters/` is no longer read.

**Verified** (local build + live data, fresh browser profile, `verify_lidwa_default.py`):

| check | before (live) | after (local) |
|---|---|---|
| `kitab.html?book=muslim` first card | `Kitab 0 … 93 hadits` | `Mukadimah … 1–8 • 8 hadits`, link carries `dataset=native_lidwa` |
| `kitab.html?book=muslim` cards | — | 57 |
| `kitab.html?book=bukhari` cards / ch1 | — | 97 / `1–6 • 6 hadits` |
| `kitab.html?book=abudawud` cards | 43 (stale sidecar) | **50** |
| `kitab.html?book=malik` cards | 60 (stale sidecar) | **32** |
| `kitab.html?book=ahmad` cards | 15 (stale sidecar) | **14** |
| `hadith-list.html?book=muslim&chapter=1` | `1–10 dari 436 (Hal 1 dari 44)` | **`1–8 dari 8 (Hal 1 dari 1)`** |
| `hadith-list.html?book=muslim&chapter=1&dataset=fawazahmed` | 436 | **436 — International edition still reachable** |
| `hadith-list.html?book=muslim&chapter=1` (no dataset) | 436 | **8** |
| `hadith-list.html?book=bukhari&chapter=1` | 7 | **6** |
| search `sabar` → first result → `?book=bukhari&id=4001` | `#4001 (Lidwa: 3700) (Penomoran Internasional)` — the hit was Lidwa #4001, the page showed International #4001 (Lidwa #3700) | **`#4001 (Penomoran Lidwa)`** |
| non-core `?book=muntaqa&chapter=1` | 1 card, `1–1` | identical locally, no regression |
| 14-page smoke (`smoke_all.log`) | — | no page errors, no failed requests on any page |

Two consequences worth naming: `hadith.html` now defaults to Lidwa numbering, so a shared URL carrying no `dataset` resolves against the corpus the site itself calls "Main"; and a link to a Lidwa number that does not exist in a book now reaches the panel from §4.5A instead of silently showing a different hadith. Chapter numbers on the nine books are unchanged from what the sidecars always said.

### 8.6 Fix batch 4 — data layer rebuilt and published (25 Nov 2026)

Everything below is live on `https://hadeeth.id` and `https://cdn.hadeeth.id`.
Commit `c3cca6d` (fixes) + `ccf8fa7` (asset version bump); 13 R2 keys replaced,
each verified by re-fetching and comparing MD5. Prior objects saved under
`_audit/backup_2026-11-25/`.

**§4.15A topic index — fixed.** 3,830 of 128,659 numbers in `topics_index.ndjson`
did not exist in the shipped corpus: the file predated the corpus migration. The
tags themselves were never lost — `data/lidwa_extracts/ind_1..14.json` keys every
tag by `(Sumber, NoHdt)`, and each shipped row still carries `lidwa_id`. Rebuilt
the whole topic layer through that join: **133,044 refs, 0 dead**. Independent
cross-check: the per-topic totals the rebuild computes match `topics.ndjson`
exactly (Faith 18,921, Knowledge 11,875, …, Jihad 4,506), which is the sum the
old metadata file already declared — so the mapping is reproducing a known-true
aggregate, not inventing one. Per-book refs: ahmad 57,933, bukhari 16,468,
muslim 12,066, nasai 11,758, abudawud 8,658, tirmidhi 8,600, ibnmajah 8,308,
darimi 6,306, malik 2,947.

**§4.6 tabarani — fixed, and the finding was mis-stated.** The duplicates were not
8,295 bad rows; they were a numbering model. `normalize_tabarani()` copies fawaz's
`hadithnumber`, which restarts at 1 in each of the 5,262 sub-collections, so
21,850 rows carried 13,555 distinct numbers and `?id=N` opened whichever row came
first. Renumbered 1..N in file order; the fawaz number stays in `arabic_number`
and `reference.book`/`reference.hadith`.

The chapter layer had a second, unreported defect: it grouped by `chapter_id`, a
thematic heading whose members are scattered through the file — 2,249 ids across
4,481 contiguous blocks — so its `hadith_start`/`hadith_end` ranges described
nothing (a ch1 click reported `Hadits 1 – 20307`). `reference.book` is the real
structure: 5,262 contiguous sub-collections in file order. Chapters rebuilt from
those blocks, Arabic heading kept where the old row had one.
`total_chapters` 1 → 5,262.

**§4.15E `total_chapters` — fixed.** Hand-maintained and wrong for 22 of 28 books
(malik 61 → 32, ahmad 90 → 14, tirmidhi 50 → 52, ibnmajah 39 → 38,
abudawud 43 → 50, nasai 51 → 52, the five AhmedBaset kitabs 1 → 57/16/25/20/57,
tabarani 1 → 5,262). Now derived from the shipped sidecars, not stored by hand.

**§4.6 "12 books ship one dummy Bab 0" — partially disproved.** They ship one
chapter titled "All Hadiths" / "Semua Hadits" with `display_number: "M"`, which is
an honest single-chapter book, not a placeholder. What they genuinely lack is a
chapter *structure*: their rows carry `chapter_id: null` (or `"0"`, `"1"`), no
`chapters/fawaz/<book>.ndjson` exists, and no source in the repo has the
headings. Deriving one would mean inventing it, so total_chapters now reports 1 —
true — and the remaining work is sourcing the headings, not fixing a bug.

**Malik hadith 1595** now belongs to chapter 32 (sidecar 1,374–1,595 • 222, index
`c:"32"` on the row), so the last hadith of the book is reachable from the kitab
page.

**Published and verified live** (fresh browser profile per check):

| check | live result |
|---|---|
| `hadith-list.html?book=muslim&chapter=1` | `Lidwa Hadits 1 – 8 • 8 Hadits` |
| `hadith-list.html?book=bukhari&chapter=1` | `Lidwa Hadits 1 – 6 • 6 Hadits` |
| `hadith-list.html?book=malik&chapter=32` | `Lidwa Hadits 1374 – 1595 • 222 Hadits` |
| `?book=muslim&chapter=1&dataset=fawazahmed` | `Hadits 93 – 533 • 436 Hadits` (International still reachable) |
| `kitab.html?book=tabarani` | 5,262 chapter cards |
| `kitab.html?book=riyad` | 20 cards, real titles |
| `hadith.html?book=tabarani&id=2` | renders, distinct from `id=3` |
| `topic-hadiths.html?book=bukhari&topic=1` | 35,601 chars, non-empty |
| page errors across the set | none (the `titleId is not defined` crash is gone) |

**Deploy mechanics worth recording.** Two traps, both measured today:
`site_r2.py upload` mirrors the manifest and *prunes* anything absent from it —
the wrong tool while another session may hold the manifest, so the publish script
does per-key PUTs and verifies each by re-fetch (`_audit/publish_batch4.py`). And
Cloudflare caches per query string: after the Worker rebuilt, `js/app.js?v=20261124_cdn`
kept serving the pre-fix bundle and still threw at line 3393, while the same file
under any other query string was the new one — the asset version had to be bumped
across 19 HTML files before the fix reached a browser.

---

## §8.7 Admin console, Hadith of the Day rotation, and user-state sync (2026-11-25)

**Shipped in `342034ff00` (pushed to `main`, live).** Supabase stores only user
state and editorial pins; the corpus stays on R2, as instructed.

| Item | Result |
|---|---|
| Old `admin.html` | Was a 3,787-byte localStorage stub: changing HOTD changed only the operator's own browser. Replaced with a Supabase-backed console (`admin.html` + `js/admin.js`). |
| HOTD auto rotation | Deterministic WIB-day selection across the seven sahih-pure collections in `books.ndjson` (bukhari, muslim, malik, nawawi, riyad, ibnukhuzaimah, ibnuhibban). No cron, no corpus copy. Manual pins in `hotd_overrides` win over rotation. |
| Non-core grade gap | Non-core rows carry no per-hadith grade (ibnuhibban #1169 → `grade: null`). The first implementation skipped them and silently fell back to bukhari 1. Fixed in both web and Flutter: a row with no grade is accepted inside a sahih-pure collection; a recorded weak grade is not. |
| Live check | `https://hadeeth.id/index.html` → `Shahih Ibn Hibban 1169`, 401 Arabic chars, no page errors. |
| Admin UI (mocked Supabase) | Gate hidden, dashboard visible, `7` rotation books, auto `On`, resolution “auto rotation across 7 sahih-pure collections on CDN”, preview `bukhari #8 · Shahih`, no JS errors. |
| Profile UI (mocked session) | Name `Admin`, preference `id`, counts `3` bookmarks / `1` reading-progress, status “Connected. Changes sync with the mobile app on this account.”, admin link visible, no JS errors. |
| Live unauthenticated pages | `admin.html` shows the auth gate; `profile.html` redirects to `login.html`; no page errors. |
| Syntax | `node --check` on `app.js`, `admin.js`, `user-sync.js`, `auth.js`; `py_compile` on `apply_supabase_migration.py` → `ALL_OK`. |

**Schema not applied — blocker.** Project `idokyspokenbmzoegahq` currently has only the
vector table `hadiths`; `profiles`, `bookmarks`, `reading_progress`,
`hotd_overrides`, and `hotd_settings` return 404. The supplied personal access
token belongs to a different Supabase account (it can list only project
`zgey…`), so `POST /v1/projects/idokys…/database/query` returns 403. The
migration parses under `pglast` and executes under PGlite; it needs the project
owner to run it once in Dashboard → SQL Editor:

```text
G:/hadeeth_id/supabase/migrations/20261125000000_mobile_sync_and_hotd.sql
```

Until then the UI degrades safely: HOTD uses deterministic rotation, the admin
page shows its schema warning, and profile sync stays local.

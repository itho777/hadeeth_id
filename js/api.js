/**
 * HADEETH.ID — Client Data API Adapter
 * High-performance asynchronous loader for pre-indexed CDN JSON files.
 * Provides fallback and instant retrieval for offline-first and online web app.
 */

/**
 * fetch() with an AbortController timeout to prevent hanging requests.
 * Default timeout is 15 seconds.
 */
function fetchWithTimeout(url, options = {}, timeoutMs = 15000) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  return fetch(url, { ...options, signal: controller.signal })
    .then(res => { clearTimeout(timer); return res; })
    .catch(err => { clearTimeout(timer); throw err; });
}

/**
 * Data lives in Cloudflare R2. The bucket serves HTTP Range correctly (206), which
 * is what every lookup in this file depends on. Override with window.__HADEETH_DATA__.
 */
const R2_DATA_URL = window.__HADEETH_DATA__ || 'https://cdn.hadeeth.id';

/**
 * The bucket's r2.dev development endpoint is kept only as a last-resort
 * mirror. Cloudflare rate-limits r2.dev and explicitly restricts it to
 * non-production traffic, and no cache rules can be attached to it, so the
 * custom domain above is the serving origin.
 */
const R2_DEV_FALLBACK = 'https://pub-075ac3f4a31e4e85a876c26c815ae93d.r2.dev';

/**
 * Display names for the nine lidwa books held in the semantic index.
 * Anything else falls back to the uppercased book id.
 */
const BOOK_NAMES = {
  bukhari:  'Sahih al-Bukhari',
  muslim:   'Sahih Muslim',
  abudawud: 'Sunan Abu Dawood',
  tirmidhi: "Jami' at-Tirmidhi",
  nasai:    "Sunan an-Nasa'i",
  ibnmajah: 'Sunan Ibn Majah',
  malik:    'Muwatta Malik',
  darimi:   'Sunan ad-Darimi',
  ahmad:    'Musnad Ahmad',
  nawawi:   'Forty Nawawi',
};


/**
 * Meilisearch keyword engine — index `hadiths` behind the meili-handoff-router
 * Worker, which follows whichever InstaBox currently holds the active copy.
 * The key is search-only: it grants nothing beyond `search` on any index.
 */
/**
 * Algolia keyword engine — hosted fallback that sits between Meilisearch and the
 * local keyword scan. Left blank until credentials are supplied; while appId or
 * searchKey are empty this tier reports "not configured" and is skipped, so the
 * results page never claims Algolia ran when it did not.
 */
const ALGOLIA_CONFIG = {
  appId: '',
  searchKey: '',
  index: 'hadiths',
  timeoutMs: 4000,
};

const MEILI_CONFIG = {
  host: 'https://meili-handoff-router.irianto-suryoputro.workers.dev',
  searchKey: '5097f0a23f1728b653e9f31a8cefba073f47ab04e47fd3ed75348a46c8182a4e',
  index: 'hadiths',
  timeoutMs: 4500,
  maxHits: 50,
  // Query embedding runs on Workers AI behind data.hadeeth.id, so no key is
  // needed here. Keyword-only search remains the fallback if it times out.
  embedUrl: 'https://data.hadeeth.id/_embed',
  embedTimeoutMs: 2500,
  semanticRatio: 0.6,
  // Flipped off for the rest of the session the first time the index
  // rejects a hybrid query (embedder not built yet, or mid-rebuild).
  semanticEnabled: true,
};

const CORE9 = new Set(['bukhari', 'muslim', 'abudawud', 'tirmidhi', 'nasai',
  'ibnmajah', 'malik', 'ahmad', 'darimi']);

// Each dataset is a complete row set with its own numbering and chapters.
// Canonical api/ and chapters/ are lidwa for the nine core books; the
// international edition lives under api/fawaz/ and chapters/fawaz/.
function apiFolder(bookId, dsPrefix) {
  return (dsPrefix === 'fawaz' && CORE9.has(bookId)) ? 'api/fawaz' : 'api';
}

function chapterFolder(bookId, dsPrefix) {
  return (dsPrefix === 'fawaz' && CORE9.has(bookId)) ? 'chapters/fawaz' : 'chapters';
}

/** Parse an NDJSON payload into an array of objects. */
function parseNdjson(text) {
  const out = [];
  for (const line of text.split('\n')) {
    const t = line.trim();
    if (!t) continue;
    try { out.push(JSON.parse(t)); } catch (e) { /* boundary fragment */ }
  }
  return out;
}

/**
 * Coalesce index entries into contiguous byte runs, so a chapter or a batch is
 * one Range request per contiguous block instead of one per hadith.
 */
function coalesceRuns(entries) {
  const runs = [];
  let cur = null;
  for (const e of entries) {
    if (cur && e.s === cur.end + 1) cur.end = e.e;
    else { cur = { start: e.s, end: e.e }; runs.push(cur); }
  }
  return runs;
}

const HadeethAPI = {
  // R2 is the serving origin. The old logic is kept as localDataUrl so anything
  // not yet migrated (commentaries, editions, topics) still resolves from /data.
  get baseUrl() {
    if (window.__HADEETH_DATA__) return window.__HADEETH_DATA__;
    if (window.__HADEETH_BASE__) return window.__HADEETH_BASE__ + '/data';
    return R2_DATA_URL;
  },

  get localDataUrl() {
    // Kept as an alias: all site data lives on R2 now. The /data tree in this
    // repo is a different build (fawaz numbering), so retrying there would
    // return mismatched rows instead of the requested hadith.
    return this.baseUrl;
  },

  get dataUrl() {
    return this.baseUrl;
  },

  datasetPrefix(datasetId) {
    if (datasetId === 'native_lidwa' || datasetId === 'native_mjna' || datasetId === 'native_irsyad') return 'lidwa';
    if (datasetId === 'native_ahmedbaset') return 'ab';
    return 'fawaz';
  },

  /**
   * The dataset a book falls back to when the caller expressed no preference.
   * Canonical api/ and chapters/ are Lidwa for the nine core books; asking for
   * 'fawazahmed' here made the International edition the silent default and put
   * chapter contents in a different numbering than the chapter list.
   */
  defaultDataset(bookId) {
    return CORE9.has(bookId) ? 'native_lidwa' : 'fawazahmed';
  },

  /**
   * Try R2 first, then the same key under the site's own /data.
   * Returns the Response, or null.
   */
  async _get(path, options = {}, timeoutMs = 15000) {
    const urls = [`${this.baseUrl}/${path}`];
    if (this.localDataUrl !== this.baseUrl) urls.push(`${this.localDataUrl}/${path}`);
    // Last resort only: the custom domain is the serving origin, but a bucket
    // misconfiguration or an edge fault should degrade to r2.dev rather than
    // break the page outright.
    if (this.baseUrl !== R2_DEV_FALLBACK) urls.push(`${R2_DEV_FALLBACK}/${path}`);
    for (const url of urls) {
      const res = await fetchWithTimeout(url, options, timeoutMs).catch(() => null);
      if (res && (res.ok || res.status === 206)) return res;
    }
    return null;
  },

  /**
   * Fetch a content-keyed index. API books use the NDJSON map at
   * api/<book>_index.ndjson: one row per hadith carrying i/id/n/s/e (+c/l).
   * Other prefixes (editions) still use the legacy JSON index.
   */
  async fetchNdjsonIndex(prefix, bookId, dsPrefix = 'lidwa') {
    if (!this.ndjsonIndexes) this.ndjsonIndexes = {};
    const folder = prefix === 'api' ? apiFolder(bookId, dsPrefix) : prefix;
    const key = `${folder}_${bookId}`;
    if (this.ndjsonIndexes[key]) return this.ndjsonIndexes[key];

    if (folder.startsWith('api') || folder === 'editions') {
      const res = await this._get(`${folder}/${bookId}_index.ndjson`, {}, 20000);
      if (res) {
        const rows = parseNdjson(await res.text());
        if (rows.length) {
          this.ndjsonIndexes[key] = rows;
          return rows;
        }
      }
      return null;
    }

    const res = await this._get(`${prefix}/${bookId}_ndjson_index.json`, {}, 20000);
    if (res) {
      this.ndjsonIndexes[key] = await res.json();
      return this.ndjsonIndexes[key];
    }
    return null;
  },

  /** Look up one index entry by hadith number, record id, or lidwa id. */
  findIndexEntry(index, hadithNumber, dsPrefix = 'fawaz') {
    if (!Array.isArray(index) || !index.length) return null;
    const want = String(hadithNumber);
    const byLidwa = () => index.find(e => Array.isArray(e.l)
      ? e.l.some(id => String(id) === want)
      : String(e.l) === want) || null;
    const byNumber = () => index.find(e => String(e.n) === want) || null;
    const byId = () => index.find(e => String(e.id) === want) || null;
    // Every form falls back to the others: a link must never dead-end just
    // because it was built against another dataset's numbering.
    if (dsPrefix === 'lidwa') return byLidwa() || byNumber() || byId();
    if (dsPrefix === 'ab') return byId() || byNumber() || byLidwa();
    // hadith number first: `id` and `n` diverge (bukhari #5 has id 6, #6999 has id 7554)
    return byNumber() || byId() || byLidwa();
  },

  /**
   * True when a purely numeric request falls outside the numbers this book
   * actually ships. Cross-numbering fallback is only safe inside the range:
   * outside it, `findIndexEntry` would answer with a different hadith.
   */
  isOutOfRange(index, hadithNumber, dsPrefix = 'fawaz') {
    if (!Array.isArray(index) || !index.length) return false;
    const want = String(hadithNumber).trim();
    if (!/^\d+$/.test(want)) return false;
    const n = Number(want);
    let min = Infinity, max = -Infinity;
    for (const e of index) {
      const raw = dsPrefix === 'lidwa'
        ? (Array.isArray(e.l) ? e.l[0] : e.l)
        : (e.n !== undefined ? e.n : e.id);
      const v = Number(raw);
      if (Number.isFinite(v)) { if (v < min) min = v; if (v > max) max = v; }
    }
    if (!Number.isFinite(min)) return false;
    return n < min || n > max;
  },

  /** Shipped number range for a book, for an honest "not found" message. */
  async getHadithRange(bookId, dsPrefix = 'fawaz') {
    const idx = await this.fetchNdjsonIndex('api', bookId, dsPrefix);
    if (!Array.isArray(idx) || !idx.length) return null;
    let min = Infinity, max = -Infinity;
    for (const e of idx) {
      const raw = dsPrefix === 'lidwa'
        ? (Array.isArray(e.l) ? e.l[0] : e.l)
        : (e.n !== undefined ? e.n : e.id);
      const v = Number(raw);
      if (Number.isFinite(v)) { if (v < min) min = v; if (v > max) max = v; }
    }
    return Number.isFinite(min) ? { min, max, count: idx.length } : null;
  },

  /** Addressable number for a record under the active dataset. */
  hadithNumberOf(item, dsPrefix = 'fawaz') {
    if (!item) return null;
    if (dsPrefix === 'lidwa') {
      const l = Array.isArray(item.lidwa_id) ? item.lidwa_id[0] : item.lidwa_id;
      if (l !== undefined && l !== null && l !== '') return l;
    }
    return item.hadith_number !== undefined && item.hadith_number !== null
      ? item.hadith_number : item.id;
  },

  /** Previous / next hadith that actually exists in this book's index. */
  async getHadithNeighbours(bookId, hadithNumber, dsPrefix = 'fawaz') {
    const idx = await this.fetchNdjsonIndex('api', bookId, dsPrefix);
    if (!Array.isArray(idx) || !idx.length) return null;
    const entry = this.findIndexEntry(idx, hadithNumber, dsPrefix);
    if (!entry) return null;
    const pos = idx.indexOf(entry);
    const numOf = e => {
      if (!e) return null;
      if (dsPrefix === 'lidwa' && e.l !== undefined && e.l !== null) {
        return Array.isArray(e.l) ? e.l[0] : e.l;
      }
      return e.n !== undefined ? e.n : e.id;
    };
    return {
      prev: pos > 0 ? numOf(idx[pos - 1]) : null,
      next: pos < idx.length - 1 ? numOf(idx[pos + 1]) : null,
      position: pos + 1,
      total: idx.length
    };
  },

  /**
   * Fetch a specific byte range from an NDJSON file.
   */
  async fetchNdjsonRange(prefix, bookId, startByte, endByte, dsPrefix = 'lidwa') {
    this.fullTextCache = this.fullTextCache || {};
    const folder = prefix === 'api' ? apiFolder(bookId, dsPrefix) : prefix;
    const cacheKey = `${folder}/${bookId}`;
    let text = "";

    if (this.fullTextCache[cacheKey]) {
        const slice = this.fullTextCache[cacheKey].slice(startByte, endByte + 1);
        text = new TextDecoder('utf-8').decode(slice);
    } else {
        const path = `${folder}/${bookId}.ndjson`;
        let res = null;
        for (const url of [`${this.baseUrl}/${path}`, `${this.localDataUrl}/${path}`]) {
            res = await fetchWithTimeout(url, {
                headers: { 'Range': `bytes=${startByte}-${endByte}` }
            }).catch(() => null);
            if (res && (res.ok || res.status === 206)) break;
            res = null;
        }
        if (!res) throw new Error('Range Failed');

        const buffer = await res.arrayBuffer();

        if (res.status === 200) {
            // Server ignored Range: cache the whole file and slice locally
            this.fullTextCache[cacheKey] = buffer;
            text = new TextDecoder('utf-8').decode(buffer.slice(startByte, endByte + 1));
        } else {
            text = new TextDecoder('utf-8').decode(buffer);
        }
    }

    return parseNdjson(text);
  },

  /**
   * Fallback to fetch the entire NDJSON file
   */
  async fetchNdjsonFull(prefix, bookId, dsPrefix = 'lidwa') {
    // sources/lidwa was never shipped — Indonesian text rides on api/<book>.ndjson
    // as text_id. Probing it costs two 404s (CDN + R2) on every page.
    if (prefix === 'sources/lidwa') return null;
    const folder = prefix === 'api' ? apiFolder(bookId, dsPrefix) : prefix;
    const res = await this._get(`${folder}/${bookId}.ndjson`, {}, 30000);
    if (!res) throw new Error('Network Error');
    return parseNdjson(await res.text());
  },

  /**
   * Fetch master list of books (NDJSON: one book per line)
   */
  async getBooks() {
    try {
      const res = await this._get('books.ndjson', {}, 15000);
      if (res) {
        const rows = parseNdjson(await res.text());
        if (rows.length) return rows;
      }
      throw new Error('no book registry');
    } catch (err) {
      console.error('Failed to load book registry:', err);
      return [];
    }
  },

  /**
   * Fetch narrator registry. R2 carries it as NDJSON rows; callers expect a
   * map keyed by narrator id, so key it here.
   */
  async getActiveRawis() {
    if (this.rawisCache) return this.rawisCache;
    try {
      const res = await this._get('rawis/rawis.ndjson', {}, 20000);
      if (res) {
        const rows = parseNdjson(await res.text());
        const map = {};
        for (const r of rows) {
          const id = r.rawi_id !== undefined ? r.rawi_id : r.id;
          if (id !== undefined && id !== '') map[String(id)] = r;
        }
        this.rawisCache = map;
      } else {
        this.rawisCache = {};
      }
    } catch (e) {
      this.rawisCache = {};
    }
    return this.rawisCache;
  },

  async getChapters(bookId, datasetId) {
    // Chapters are built from the shipped rows, whose numbering is the lidwa
    // numbering for the nine core books. The old lidwa-chapters files carry the
    // known 2..97 range corruption, so `chapters/` is the only source used here.
    if (!datasetId) datasetId = this.defaultDataset(bookId);
    const dsPrefix = this.datasetPrefix(datasetId);
    const folder = chapterFolder(bookId, dsPrefix);
    const cacheKey = folder + '_' + bookId;

    if (this.chaptersCache && this.chaptersCache[cacheKey]) return this.chaptersCache[cacheKey];
    try {
      this.chaptersCache = this.chaptersCache || {};
      const res = await this._get(`${folder}/${bookId}.ndjson`, {}, 15000);
      if (res) {
        const rows = parseNdjson(await res.text());
        if (rows.length) {
          this.chaptersCache[cacheKey] = rows;
          return rows;
        }
      }
      throw new Error('chapters unavailable');
    } catch (err) {
      console.error(`Failed to load ${folder} for ${bookId}:`, err);
      return [];
    }
  },

  /**
   * Fetch hadiths for a specific chapter using the content map + HTTP Range.
   * Entries carrying the same chapter id are contiguous in practice, so they
   * collapse into one request per contiguous run.
   */
  async getChapterHadiths(bookId, chapterId, datasetId) {
    if (!datasetId) datasetId = this.defaultDataset(bookId);
    const dsPrefix = this.datasetPrefix(datasetId);
    try {
      const idx = await this.fetchNdjsonIndex('api', bookId, dsPrefix);
      let chapterHadiths = [];

      if (Array.isArray(idx) && idx.length) {
        const entries = idx.filter(e => e.c !== undefined && String(e.c) === String(chapterId));
        if (entries.length) {
          for (const run of coalesceRuns(entries)) {
            const rows = await this.fetchNdjsonRange('api', bookId, run.start, run.end, dsPrefix);
            for (const r of rows) {
              if (r.chapter_id === undefined || String(r.chapter_id) === String(chapterId)) {
                chapterHadiths.push(r);
              }
            }
          }
        } else if (!idx.some(e => e.c !== undefined)) {
          // No chapter column in the records: the book has a single pseudo-chapter,
          // so serving the whole file (these books are small) is the honest listing.
          const firstChapter = String(chapterId) === '1' || String(chapterId) === '0';
          if (!firstChapter) return [];
          chapterHadiths = await this.fetchNdjsonFull('api', bookId, dsPrefix);
        } else {
          return [];
        }
      } else {
        const allHadiths = await this.fetchNdjsonFull('api', bookId, dsPrefix);
        chapterHadiths = allHadiths.filter(h => String(h.chapter_id) === String(chapterId));
      }

      return chapterHadiths.map(h => ({
        id: h.id,
        hadithnumber: this.hadithNumberOf(h, dsPrefix),
        hadith_number: this.hadithNumberOf(h, dsPrefix),
        lidwa_id: h.lidwa_id || null,
        chapter_id: h.chapter_id,
        data: {
          text_ar: h.text_ar || '',
          text_en: h.text_en || '',
          text_id: h.text_id || '',
          grade: h.grade || ''
        }
      }));
    } catch (err) {
      console.error(`Failed to load chapter hadiths ${bookId} c${chapterId}:`, err);
      return [];
    }
  },

  /**
   * Fetch full unified record for a single Hadith using HTTP Range Requests.
   * `hadithNumber` means the hadith's own number (index field `n`), not the row
   * ordinal and not `id` — those three differ for 11 of the 25 books.
   */
  async getHadith(bookId, hadithNumber, dsPrefix = 'fawaz') {
    try {
      let h = null;
      const idx = await this.fetchNdjsonIndex('api', bookId, dsPrefix);
      // A number outside the shipped range must not fall through to another
      // numbering scheme: the fallbacks in findIndexEntry exist for the same
      // hadith addressed differently, not for a hadith that does not exist.
      if (idx && this.isOutOfRange(idx, hadithNumber, dsPrefix)) return null;
      const entry = this.findIndexEntry(idx, hadithNumber, dsPrefix);

      if (entry) {
        const hadiths = await this.fetchNdjsonRange('api', bookId, entry.s, entry.e, dsPrefix);
        h = hadiths[0] || null;
      } else if (!idx) {
        // No index at all (both origins): only then pay for the full file.
        const allHadiths = await this.fetchNdjsonFull('api', bookId, dsPrefix);
        const want = String(hadithNumber);
        h = allHadiths.find(item => {
          if (dsPrefix === 'lidwa') return Array.isArray(item.lidwa_id)
            ? item.lidwa_id.some(id => String(id) === want)
            : String(item.lidwa_id) === want;
          // A numeric request addresses the hadith number; the internal record
          // id is only an address for composite ids like "bukhari_5".
          if (String(item.hadith_number) === want) return true;
          return !/^\d+$/.test(want) && String(item.id) === want;
        }) || null;
      }
      // Index loaded but the number is absent: report "not found" instead of
      // pulling a 40–96 MB file over mobile data.
      
      // Backward compatibility wrapper for old hadith.html
      if (h) {
          if (h.hadith_number === undefined || h.hadith_number === null) h.hadith_number = h.id;
          if (h.translations) {
              if (h.translations.ar && h.translations.ar.length > 0 && !h.text_ar) h.text_ar = h.translations.ar[0].text;
              if (h.translations.en && h.translations.en.length > 0 && !h.text_en) h.text_en = h.translations.en[0].text;
              if (h.translations.id && h.translations.id.length > 0 && !h.text_id) h.text_id = h.translations.id[0].text;
          }
          if (h.sanad) {
              h.rawis = h.sanad;
          }
          if (h.gradings && h.gradings.length > 0) {
              h.grade = h.gradings[0].grade;
              h.grade_en = h.grade;
              h.grade_id = h.grade;
          }
      }
      return h;
    } catch (err) {
      console.error(`Failed to load Hadith ${bookId}:${hadithNumber}:`, err);
      return null;
    }
  },

  /**
   * Fetch topic index mapping
   */
  async getTopicIndex() {
    if (this.topicIndexCache) return this.topicIndexCache;
    // Rows are {t: topic, b: book, n: [hadith numbers]}; reshape into the
    // {topics: {id: {books: {...}}}} object the callers already expect.
    const res = await this._get('topics_index.ndjson', {}, 20000);
    if (res) {
      const topics = {};
      for (const r of parseNdjson(await res.text())) {
        const t = (topics[String(r.t)] = topics[String(r.t)] || { id: r.t, books: {} });
        t.books[r.b] = r.n;
      }
      this.topicIndexCache = { topics };
      return this.topicIndexCache;
    }
    return null;
  },

  /**
   * Topic metadata (14 rows: id, name_en, name_id, hadith_count)
   */
  async getTopics() {
    if (this.topicsCache) return this.topicsCache;
    const res = await this._get('topics.ndjson', {}, 15000);
    if (res) {
      this.topicsCache = parseNdjson(await res.text());
      return this.topicsCache;
    }
    return [];
  },

  /**
   * Get list of hadith numbers for a specific topic and book
   */
  async getTopicHadithIds(topicId, bookId) {
    const idx = await this.getTopicIndex();
    if (idx && idx.topics && idx.topics[String(topicId)]) {
      const t = idx.topics[String(topicId)];
      if (t.books && t.books[bookId.toLowerCase()]) {
        return t.books[bookId.toLowerCase()];
      }
    }
    return [];
  },

  /**
   * Fetch a batch of hadiths concurrently using HTTP Range Requests directly from master NDJSON
   */
  async getHadithsBatch(bookId, hadithNumbers, dsPrefix = 'lidwa') {
    if (!hadithNumbers || hadithNumbers.length === 0) return [];
    const results = [];
    for (const num of hadithNumbers) {
       results.push(await this.getHadith(bookId, num, dsPrefix));
    }
    return results.filter(h => h !== null);
  },

  /**
   * Normalize an edition JSON to the standard {metadata, hadiths} format.
   */
  normalizeEdition(data) {
    if (!data) return null;
    if (Array.isArray(data)) {
      data = { metadata: {}, hadiths: data };
    }
    if (!data.hadiths) return data;
    data.hadiths = data.hadiths.map(h => {
      if (h.hadithnumber === undefined && h.id !== undefined) {
        return { ...h, hadithnumber: h.id };
      }
      return h;
    });
    return data;
  },

  /**
   * Fetch full language edition file using NDJSON Fallback
   */
  async getEdition(langCode, bookId) {
    try {
      // Never probe a file the catalogue says is not shipped: each miss costs two
      // round trips (CDN, then the R2 origin) on every list and detail page.
      if (!(await this.editionExists(langCode, bookId))) return null;
      let raw = [];
      const prefix = 'editions';
      const fileId = `${langCode}-${bookId}`;
      const idx = await this.fetchNdjsonIndex(prefix, fileId);
      if (idx && idx.array_key) {
          raw = await this.fetchNdjsonFull(prefix, fileId);
          return this.normalizeEdition({ metadata: idx.metadata || {}, [idx.array_key]: raw });
      } else {
          raw = await this.fetchNdjsonFull(prefix, fileId);
          if (Array.isArray(raw) && raw.length) {
            return this.normalizeEdition({ metadata: {}, hadiths: raw });
          }
          return null;
      }
    } catch (err) {
      console.error(`Failed to load edition ${langCode}-${bookId}:`, err);
      return null;
    }
  },

  /**
   * One translation, one Range request. Editions are indexed by hadith number
   * so the dropdown never has to pull a whole language file for one hadith.
   */
  async getEditionText(langCode, bookId, hadithNumber) {
    try {
      const fileId = `${langCode}-${bookId}`;
      if (!(await this.editionExists(langCode, bookId))) return null;
      const idx = await this.fetchNdjsonIndex('editions', fileId);
      const entry = this.findIndexEntry(idx, hadithNumber, 'fawaz');
      if (entry) {
        let rows;
        try {
          rows = await this.fetchNdjsonRange('editions', fileId, entry.s, entry.e);
        } catch (e) {
          rows = null;
        }
        if (Array.isArray(rows) && rows.length) {
          const hit = rows.find(r => String(r.n) === String(hadithNumber)) || rows[0];
          if (hit && hit.t) return hit.t;
        }
      }
      const whole = await this.getEdition(langCode, bookId);
      const found = whole && whole.hadiths
        ? whole.hadiths.find(h => String(h.hadithnumber ?? h.n ?? h.id) === String(hadithNumber))
        : null;
      return found ? (found.text ?? found.t ?? null) : null;
    } catch (err) {
      console.warn(`edition ${langCode}-${bookId} #${hadithNumber} unavailable`, err);
      return null;
    }
  },

  /** Which (language, book) translation files actually exist on R2. */
  async getEditionCatalog() {
    if (this.editionCatalogCache) return this.editionCatalogCache;
    try {
      const res = await this._get('editions/_catalog.ndjson', {}, 15000);
      if (!res) return [];
      this.editionCatalogCache = parseNdjson(await res.text());
      return this.editionCatalogCache;
    } catch (e) {
      return [];
    }
  },

  /**
   * True when the catalogue says this edition is shipped. An unknown catalogue
   * (fetch failed) reports true so the caller behaves as before.
   */
  async editionExists(langCode, bookId) {
    const catalog = await this.getEditionCatalog();
    if (!Array.isArray(catalog) || !catalog.length) return true;
    return catalog.some(e => e.lang === langCode && e.book === bookId);
  },

  /**
   * Embed a query with the same bge-m3 model the hadiths vectors were built
   * with. Failure is non-fatal: meiliSearch then ranks by keyword only.
   */
  async embedQuery(query) {
    const res = await fetchWithTimeout(
      MEILI_CONFIG.embedUrl,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: String(query).slice(0, 2000) }),
      },
      MEILI_CONFIG.embedTimeoutMs
    );
    if (!res.ok) throw new Error(`Embed HTTP ${res.status}`);
    const data = (await res.json()).data;
    if (!data || !data[0] || data[0].length !== 1024) throw new Error('bad embedding shape');
    return data[0];
  },

  /**
   * Hybrid keyword + vector search against the `hadiths` Meilisearch index.
   * Returns rows in the shape renderSearchResults() already consumes.
   */
  async meiliSearch(query, bookFilter = 'all', limit = 20) {
    let vector = null;
    if (MEILI_CONFIG.semanticEnabled) {
      try {
        vector = await this.embedQuery(query);
      } catch (e) {
        console.warn('Semantic embedding unavailable, keyword-only search:', e);
      }
    }

    const buildBody = (matchingStrategy) => {
      const body = {
        q: query,
        limit: Math.max(1, Math.min(limit || 20, MEILI_CONFIG.maxHits)),
        // Mandatory for Arabic: the tokenizer splits off the definite article
        // `ال`, and the default `last` strategy matches almost every hadith as
        // soon as that token hits.
        matchingStrategy,
        attributesToHighlight: ['text_ar', 'text_id', 'text_en'],
        // Hybrid fuses keyword ranking with bge-m3 cosine ranking. Leave
        // these out when the embedder is down: Meili then does plain search.
        ...(vector ? {
          vector,
          hybrid: { embedder: 'default', semanticRatio: MEILI_CONFIG.semanticRatio },
        } : {}),
      };
      if (bookFilter && bookFilter !== 'all') {
        body.filter = `collection = "${bookFilter}"`;
      }
      return body;
    };

    const request = async (matchingStrategy) => {
      const res = await fetchWithTimeout(
        `${MEILI_CONFIG.host}/indexes/${MEILI_CONFIG.index}/search`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${MEILI_CONFIG.searchKey}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(buildBody(matchingStrategy)),
        },
        MEILI_CONFIG.timeoutMs
      );
      if (!res.ok) throw new Error(`Meilisearch HTTP ${res.status}`);
      return (await res.json()).hits || [];
    };

    let hits;
    try {
      hits = await request('all');
    } catch (e) {
      if (!vector) throw e;
      // No embedder on the index yet: drop to keyword search and stop
      // paying for a hybrid request that will keep failing.
      MEILI_CONFIG.semanticEnabled = false;
      vector = null;
      console.warn('Hybrid search unavailable, using keyword search:', e);
      hits = await request('all');
    }
    // `all` is precise but unforgiving on a long query; `frequency` drops the
    // fewest words instead of falling back to `last`, which matches everything.
    if (hits.length === 0 && String(query).trim().split(/\s+/).length > 1) {
      hits = await request('frequency');
    }

    return hits.map(hit => ({
      id: hit.id,
      book_slug: hit.collection,
      book_name: hit.book_title_en || hit.book_title_id || hit.collection,
      hadith_number: hit.hadith_number,
      reference: `#${hit.hadith_number}`,
      arabic_text: hit.text_ar || '',
      primary_translation: hit.text_id || hit.text_en || '',
      english_text: hit.text_en || '',
      indonesian_text: hit.text_id || '',
      grade: hit.grade || '',
      grade_en: hit.grade || '',
      grade_id: hit.grade || '',
      source: hit.source,
      source_label: hit.source_label,
      collection: hit.collection,
    }));
  },

  /**
   * Semantic engine: Cloudflare AI embeds the query, Supabase pgvector ranks.
   * The Worker returns ids only; text is hydrated from R2 through getHadith().
   * Throws on any failure so search() can fall through to the other engine.
   */
  async semanticSearch(query, bookFilter = 'all', limit = 20) {
    const res = await fetchWithTimeout(
      '/api/search',
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          q: String(query).slice(0, 500),
          book: bookFilter,
          limit: Math.max(1, Math.min(limit, 20)),
        }),
      },
      18000
    );
    if (!res.ok) throw new Error(`Semantic API HTTP ${res.status}`);
    const data = await res.json();
    if (!data || data.mode !== 'semantic' || !data.vectorGenerated ||
        !Array.isArray(data.results) || data.results.length === 0) {
      throw new Error(data?.aiError || data?.rpcError || 'semantic engine returned no results');
    }

    // Hydrate ranked ids with text. Parallel: sequential costs ~10s for 20 rows.
    const rows = await Promise.all(data.results.map(async (r) => {
      const h = await this.getHadith(r.book_id, r.hadith_number, 'lidwa');
      if (!h) return null;
      const name = BOOK_NAMES[r.book_id] || String(r.book_id || '').toUpperCase();
      return {
        id: r.id,
        book_slug: r.book_id,
        book_name: name,
        hadith_number: h.hadith_number ?? r.hadith_number,
        reference: `#${h.hadith_number ?? r.hadith_number}`,
        arabic_text: h.text_ar || '',
        primary_translation: h.text_id || h.text_en || '',
        english_text: h.text_en || '',
        indonesian_text: h.text_id || '',
        grade: h.grade || h.gradings?.[0]?.grade || '',
        grade_en: h.grade_en || h.grade || '',
        grade_id: h.grade_id || h.grade || '',
        source: h.source || 'lidwa',
        collection: r.book_id,
        similarity: Number(r.similarity),
      };
    }));
    const hits = rows.filter(Boolean);
    if (!hits.length) throw new Error('semantic matches could not be hydrated');
    return hits;
  },

  /**
   * Algolia keyword engine. Throws when unconfigured so search() records the tier
   * as unavailable rather than silently pretending it was tried.
   */
  async algoliaSearch(query, bookFilter = 'all', limit = 20) {
    if (!ALGOLIA_CONFIG.appId || !ALGOLIA_CONFIG.searchKey) {
      throw new Error('not configured');
    }
    const res = await fetchWithTimeout(
      `https://${ALGOLIA_CONFIG.appId}-dsn.algolia.net/1/indexes/${ALGOLIA_CONFIG.index}/query`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Algolia-Application-Id': ALGOLIA_CONFIG.appId,
          'X-Algolia-API-Key': ALGOLIA_CONFIG.searchKey,
        },
        body: JSON.stringify({
          query: String(query),
          hitsPerPage: Math.max(1, Math.min(limit, 50)),
          filters: bookFilter && bookFilter !== 'all' ? `book_slug:"${bookFilter}"` : undefined,
        }),
      },
      ALGOLIA_CONFIG.timeoutMs
    );
    if (!res.ok) throw new Error(`Algolia HTTP ${res.status}`);
    const data = await res.json();
    const hits = (data.hits || []).map(h => ({
      id: h.objectID || h.id,
      book_slug: h.book_slug || h.book_id,
      book_name: BOOK_NAMES[h.book_slug || h.book_id] || String(h.book_slug || h.book_id || '').toUpperCase(),
      hadith_number: h.hadith_number,
      reference: `#${h.hadith_number}`,
      arabic_text: h.arabic_text || h.text_ar || '',
      primary_translation: h.text_id || h.text_en || h.indonesian_text || '',
      english_text: h.text_en || '',
      indonesian_text: h.text_id || '',
      grade: h.grade || '',
      grade_en: h.grade_en || h.grade || '',
      grade_id: h.grade_id || h.grade || '',
    })).filter(h => h.id);
    if (!hits.length) throw new Error('algolia returned no results');
    return hits;
  },

  /**
   * Hadith search — one chain shared by both modes.
   *
   *   1. the mode the user selected        ('semantic' | 'keyword')
   *   2. the other mode                    (cross-fallback)
   *   3. Algolia                           (hosted keyword, when configured)
   *   4. basic keyword scan                (client-side, last resort)
   *
   * The tier that actually answered is reported on `results.searchMeta`; the UI
   * prints its generic label plus the engine behind it. A tier that could not run
   * is recorded as unavailable — never dressed up as a result.
   *
   * @param {string} preferred 'semantic' | 'keyword' (legacy value 'exact' accepted)
   */
  async search(query, bookFilter = 'all', limit = 20, preferred = 'semantic') {
    if (!query || !query.trim()) return [];
    const q = query.trim();
    const want = preferred === 'keyword' || preferred === 'exact' ? 'keyword' : 'semantic';

    const engines = {
      semantic: () => this.semanticSearch(q, bookFilter, limit),
      keyword: async () => {
        const hits = await this.meiliSearch(q, bookFilter, limit);
        if (!hits || !hits.length) throw new Error('keyword engine returned no results');
        return hits;
      },
      algolia: () => this.algoliaSearch(q, bookFilter, limit),
    };
    const META = {
      semantic: { label: 'Semantic', engine: 'Cloudflare AI + Supabase pgvector' },
      keyword: { label: 'Keyword', engine: 'Meilisearch' },
      algolia: { label: 'Keyword', engine: 'Algolia' },
      basic: { label: 'Keyword', engine: 'basic keyword · local index' },
    };

    const order = [want, want === 'semantic' ? 'keyword' : 'semantic', 'algolia'];
    const attempts = [];

    // The semantic tier alone cannot tell a hit from a miss: on this corpus real
    // Indonesian queries score 0.39–0.62 and gibberish 0.33–0.49, so `niat` (0.489)
    // ranks below `zzzzqqqxxx` (0.486). Any similarity floor either drops real
    // queries or keeps noise. Meilisearch does separate them cleanly (gibberish → 0
    // hits, real → 2–20), so it gates the semantic tier: embeddings re-rank lexical
    // candidates, and with no candidates there is nothing to report.
    let lexicalCandidates = null;
    if (want === 'semantic') {
      try {
        lexicalCandidates = ((await this.meiliSearch(q, bookFilter, limit)) || []).length;
      } catch (err) {
        // Keyword tier unreachable: fail open rather than blank the page on a
        // Meilisearch outage. The gate is a quality filter, not a dependency.
        lexicalCandidates = null;
      }
    }

    for (const tier of order) {
      if (tier === 'semantic' && lexicalCandidates === 0) {
        attempts.push({ tier, ok: false, note: 'no lexical candidates' });
        continue;
      }
      try {
        const hits = await engines[tier]();
        if (hits && hits.length) {
          attempts.push({ tier, ok: true, count: hits.length });
          hits.searchMeta = {
            method: tier,
            label: META[tier].label,
            engine: META[tier].engine,
            primary: want,
            fellBack: tier !== want,
            lexicalCandidates,
            attempts,
          };
          return hits;
        }
        attempts.push({ tier, ok: false, note: 'no results' });
      } catch (err) {
        attempts.push({ tier, ok: false, note: String((err && err.message) || err) });
      }
    }

    // Last resort: basic keyword scan over the local index.
    const local = (await this.fallbackLocalSearch(q, bookFilter)) || [];
    attempts.push({ tier: 'basic', ok: local.length > 0, count: local.length });
    local.searchMeta = {
      method: 'basic',
      label: META.basic.label,
      engine: META.basic.engine,
      primary: want,
      fellBack: true,
      attempts,
    };
    return local;
  },

  /**
   * Fallback client-side search using local edition JSON data
   */
  async fallbackLocalSearch(query, bookFilter = 'all') {
    const q = query.toLowerCase().trim();
    const matches = [];

    // Search Forty Nawawi first (lightweight 37KB)
    if (bookFilter === 'all' || bookFilter === 'nawawi') {
      const [nawawiEng, nawawiInd] = await Promise.all([
        this.getEdition('eng', 'nawawi'),
        this.getEdition('ind', 'nawawi')
      ]);

      if (nawawiEng && nawawiEng.hadiths) {
        nawawiEng.hadiths.forEach((h, i) => {
          const indText = (nawawiInd && nawawiInd.hadiths && nawawiInd.hadiths[i]) ? nawawiInd.hadiths[i].text : '';
          const enText = h.text || '';
          if (String(h.hadithnumber) === q || enText.toLowerCase().includes(q) || indText.toLowerCase().includes(q)) {
            matches.push({
              id: `nawawi_${h.hadithnumber}`,
              book_slug: 'nawawi',
              book_name: 'Forty Nawawi',
              hadith_number: h.hadithnumber,
              reference: `#${h.hadithnumber}`,
              arabic_text: '',
              primary_translation: indText || enText,
              english_text: enText,
              indonesian_text: indText,
              grade: 'Sahih'
            });
          }
        });
      }
    }

    // Search Sahih Bukhari English if needed
    if (matches.length < 10 && (bookFilter === 'all' || bookFilter === 'bukhari')) {
      const bukhariEng = await this.getEdition('eng', 'bukhari');
      if (bukhariEng && bukhariEng.hadiths) {
        for (const h of bukhariEng.hadiths) {
          if ((h.text && h.text.toLowerCase().includes(q)) || String(h.hadithnumber) === q) {
            matches.push({
              id: `bukhari_${h.hadithnumber}`,
              book_slug: 'bukhari',
              book_name: 'Sahih al-Bukhari',
              hadith_number: h.hadithnumber,
              reference: `#${h.hadithnumber}`,
              arabic_text: '',
              primary_translation: h.text,
              english_text: h.text,
              indonesian_text: '',
              grade: 'Sahih'
            });
            if (matches.length >= 20) break;
          }
        }
      }
    }

    return matches;
  },

  /**
   * Resolve primary anchor ID for a Hadith (used for Syarah and cross-dataset mapping)
   */
  async getPrimaryAnchorId(bookId, hadithNumber) {
    // For now, return the provided hadithNumber directly as Lidwa data doesn't map to a different anchor natively.
    return hadithNumber;
  },

  /**
   * Fetch commentary & sharh explanation for one hadith (supports multiple
   * sources). Served from commentaries/<book>.ndjson through its
   * content-keyed index: one Range request returns every source for that
   * number. The old per-hadith JSON files (30,080 separate objects) are gone.
   */
  async getCommentaries(bookId, hadithNumber) {
    try {
      const index = await this.fetchCommentaryIndex(bookId);
      if (!Array.isArray(index) || !index.length) return [];
      const want = String(hadithNumber);
      const entry = index.find(e => String(e.n) === want);
      if (!entry) return [];
      const path = `commentaries/matched/${bookId}.ndjson`;
      let res = null;
      for (const url of [`${this.baseUrl}/${path}`, `${this.localDataUrl}/${path}`]) {
        res = await fetchWithTimeout(url, {
          headers: { 'Range': `bytes=${entry.s}-${entry.e}` }
        }).catch(() => null);
        if (res && (res.ok || res.status === 206)) break;
        res = null;
      }
      if (!res) return [];
      return parseNdjson(await res.text());
    } catch (err) {
      console.warn(`Commentary fetch error for ${bookId}_${hadithNumber}:`, err);
      return [];
    }
  },

  /**
   * Content-keyed commentary index for one book (number -> byte range).
   * Cached per book: the file is small and every hadith in the book needs it.
   */
  async fetchCommentaryIndex(bookId) {
    if (!this.commentaryIndexes) this.commentaryIndexes = {};
    if (bookId in this.commentaryIndexes) return this.commentaryIndexes[bookId];
    const res = await this._get(`commentaries/matched/${bookId}_index.ndjson`, {}, 20000);
    let index = null;
    if (res) {
      const rows = parseNdjson(await res.text());
      if (rows.length) index = rows;
    }
    this.commentaryIndexes[bookId] = index;
    return index;
  },

  /**
   * Which books carry commentary, and in which languages. Drives the
   * disabled source/language options instead of an empty panel.
   */
  async getCommentaryCatalog() {
    if (this.commentaryCatalog !== undefined) return this.commentaryCatalog;
    const res = await this._get('commentaries/_catalog.ndjson', {}, 20000);
    this.commentaryCatalog = res ? parseNdjson(await res.text()) : [];
    return this.commentaryCatalog;
  },

  /**
   * The classical sharh corpus on R2: one package per printed edition, each
   * holding every page of that commentary. A matched row in commentaries/
   * carries only the first page of its span (syarah_pages_index = "494-502"),
   * so the rest of the span is read from here. syarah/editions.ndjson indexes
   * all 25 packages and maps each directory to its turath book id.
   */
  async getSyarahEditions() {
    if (this.syarahEditions) return this.syarahEditions;
    const res = await this._get('syarah/editions.ndjson', {}, 20000);
    this.syarahEditions = res ? parseNdjson(await res.text()) : [];
    return this.syarahEditions;
  },

  /** Passage-id -> byte range for one sharh package. Cached per package. */
  async getSyarahPassageIndex(edition) {
    if (!this.syarahPassageIndexes) this.syarahPassageIndexes = {};
    if (edition in this.syarahPassageIndexes) return this.syarahPassageIndexes[edition];
    const res = await this._get(`syarah/${edition}/syarah_passages_index.ndjson`, {}, 25000);
    const rows = res ? parseNdjson(await res.text()) : [];
    this.syarahPassageIndexes[edition] = rows;
    return rows;
  },

  /**
   * Every page of one commentary span, in one Range request. Page numbers are
   * the package's own page indexes: sequential by construction, so the run is
   * contiguous and a single read covers the pages the matched row omitted.
   */
  async getSyarahPages(edition, fromPage, toPage) {
    const from = parseInt(fromPage, 10);
    let to = parseInt(toPage, 10);
    if (!isFinite(from) || !isFinite(to) || to < from) return [];
    if (to - from > 30) to = from + 30;
    const editions = await this.getSyarahEditions();
    const pkg = editions.find(e => e.package_dir === edition || e.package_id === edition);
    if (!pkg) return [];
    const index = await this.getSyarahPassageIndex(pkg.package_dir);
    if (!index.length) return [];
    const byId = {};
    for (const e of index) byId[e.id] = e;
    const wanted = [];
    for (let p = from; p <= to; p++) {
      const e = byId[`turath:${pkg.turath_id}:page:${p}`];
      if (e) wanted.push(e);
    }
    if (!wanted.length) return [];
    const out = [];
    for (const run of coalesceRuns(wanted)) {
      const res = await this._get(`syarah/${pkg.package_dir}/syarah_passages.ndjson`, {
        headers: { 'Range': `bytes=${run.start}-${run.end}` }
      }, 30000);
      if (res) out.push(...parseNdjson(await res.text()));
    }
    return out;
  },

  /** Fetch a link map for one book from links/<book>.ndjson on R2. */
  async getLinks(bookId) {
    if (!this.linksCache) this.linksCache = {};
    if (this.linksCache[bookId]) return this.linksCache[bookId];
    const res = await this._get(`links/${bookId}.ndjson`, {}, 20000);
    if (!res) return null;
    const map = {};
    for (const row of parseNdjson(await res.text())) {
      if (row && row.k !== undefined) map[String(row.k)] = row.v;
      else if (row && row.id !== undefined) {
        const { id, ...rest } = row;
        map[String(id)] = rest;
      }
    }
    this.linksCache[bookId] = map;
    return map;
  },

  /** Fawaz edition metadata, regrouped to { book: { collection: [...] } }. */
  async getFawazEditions() {
    if (this.fawazEditionsCache) return this.fawazEditionsCache;
    const res = await this._get('meta/fawaz_editions.ndjson', {}, 20000);
    const map = {};
    if (res) {
      for (const row of parseNdjson(await res.text())) {
        const book = row.book_id || row.book;
        if (!book) continue;
        if (!map[book]) map[book] = { collection: [] };
        map[book].collection.push(row);
      }
    }
    this.fawazEditionsCache = map;
    return map;
  },

  async getGlossary() {
    if (this.glossaryCache) return this.glossaryCache;
    const res = await this._get('api/glossary.ndjson', {}, 20000);
    this.glossaryCache = res ? parseNdjson(await res.text()) : [];
    return this.glossaryCache;
  },

  async getTopicsCounts() {
    if (this.topicsCountsCache) return this.topicsCountsCache;
    const res = await this._get('api/topics_counts.ndjson', {}, 20000);
    const map = {};
    if (res) {
      for (const row of parseNdjson(await res.text())) {
        if (row && row.book) map[row.book] = row.counts || {};
      }
    }
    this.topicsCountsCache = map;
    return map;
  },

  /**
   * Lidwa chapter index for a book: {chapters, title_en_source, title_id_source}.
   * Reads the canonical `chapters/` sidecar — the one `getChapters` returns and the
   * one whose hadith_count agrees with the `c` column of api/<book>_index.ndjson.
   * The legacy `lidwa-chapters/` files disagree with that index (bukhari ch1 237 vs
   * 6, abudawud 390 vs 330, tirmidhi 148 vs 137) and are no longer read.
   */
  async getLidwaChapters(bookId) {
    if (!this.lidwaChapterCache) this.lidwaChapterCache = {};
    if (this.lidwaChapterCache[bookId]) return this.lidwaChapterCache[bookId];
    const chapters = await this.getChapters(bookId, 'native_lidwa');
    if (!chapters || !chapters.length) return null;
    const out = {
      title_en_source: 'AhmedBaset',
      title_id_source: 'Lidwa / Irsyad',
      chapters,
    };
    this.lidwaChapterCache[bookId] = out;
    return out;
  },

  /** Fetch one narrator profile by byte range from rawis/profiles.ndjson. */
  async getRawiProfile(rawiId) {
    const key = String(rawiId);
    if (this.rawiProfileCache && this.rawiProfileCache[key]) return this.rawiProfileCache[key];
    const idxRes = await this._get('rawis/profiles_index.ndjson', {}, 20000);
    if (idxRes) {
      const wanted = [key, key.replace(/^rawi_/, '')];
      const hit = parseNdjson(await idxRes.text()).find(r => wanted.includes(String(r.id)));
      if (hit) {
        const res = await this._get('rawis/profiles.ndjson',
          { headers: { 'Range': `bytes=${hit.s}-${hit.e}` } }, 20000);
        if (res) {
          const row = parseNdjson(await res.text())[0];
          if (row && row.data) {
            this.rawiProfileCache = this.rawiProfileCache || {};
            this.rawiProfileCache[key] = Object.assign({}, row.data, { _key: row._key });
            return this.rawiProfileCache[key];
          }
        }
      }
    }
    try {
      const rawis = await this.getActiveRawis();
      return rawis[key] || null;
    } catch (err) {
      return null;
    }
  }
};

window.HadeethAPI = HadeethAPI;

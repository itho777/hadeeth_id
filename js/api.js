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
const R2_DATA_URL = 'https://pub-075ac3f4a31e4e85a876c26c815ae93d.r2.dev';

/**
 * Meilisearch keyword engine — index `hadiths` behind the meili-handoff-router
 * Worker, which follows whichever InstaBox currently holds the active copy.
 * The key is search-only: it grants nothing beyond `search` on any index.
 */
const MEILI_CONFIG = {
  host: 'https://meili-handoff-router.irianto-suryoputro.workers.dev',
  searchKey: '5097f0a23f1728b653e9f31a8cefba073f47ab04e47fd3ed75348a46c8182a4e',
  index: 'hadiths',
  timeoutMs: 4500,
  maxHits: 50,
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
   * Try R2 first, then the same key under the site's own /data.
   * Returns the Response, or null.
   */
  async _get(path, options = {}, timeoutMs = 15000) {
    const urls = [`${this.baseUrl}/${path}`];
    if (this.localDataUrl !== this.baseUrl) urls.push(`${this.localDataUrl}/${path}`);
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
  async getChapterHadiths(bookId, chapterId, datasetId = 'fawazahmed') {
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
          return String(item.hadith_number) === want || String(item.id) === want;
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
    try {
      const res = await this._get('editions/_catalog.ndjson', {}, 15000);
      if (!res) return [];
      return parseNdjson(await res.text());
    } catch (e) {
      return [];
    }
  },

  /**
   * Keyword search against the `hadiths` Meilisearch index.
   * Returns rows in the shape renderSearchResults() already consumes.
   */
  async meiliSearch(query, bookFilter = 'all', limit = 20) {
    const buildBody = (matchingStrategy) => {
      const body = {
        q: query,
        limit: Math.max(1, Math.min(limit || 20, MEILI_CONFIG.maxHits)),
        // Mandatory for Arabic: the tokenizer splits off the definite article
        // `ال`, and the default `last` strategy matches almost every hadith as
        // soon as that token hits.
        matchingStrategy,
        attributesToHighlight: ['text_ar', 'text_id', 'text_en'],
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

    let hits = await request('all');
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
   * Multilingual Hadith Search (Meilisearch -> Supabase REST -> RPC -> local)
   */
  async search(query, bookFilter = 'all', limit = 20) {
    if (!query || !query.trim()) return [];
    const q = query.trim();
    const supabaseUrl = 'https://idokyspokenbmzoegahq.supabase.co';
    const anonKey = 'sb_publishable_Hz6k4Jp7rdSxwXCk1AO-sQ_r93N88QR';

    // 0. Meilisearch — primary keyword engine. Everything below stays as the
    //    in-house fallback for when the index is unreachable or has no match.
    try {
      const meiliHits = await this.meiliSearch(q, bookFilter, limit);
      if (meiliHits.length > 0) return meiliHits;
    } catch (err) {
      console.warn('Meilisearch unavailable, using in-house keyword search:', err);
    }

    // 1. Direct Supabase REST Full-Text / Keyword Query (Fastest & most reliable)
    try {
      const num = parseInt(q);
      let filter = `or=(text_en.ilike.*${encodeURIComponent(q)}*,text_id.ilike.*${encodeURIComponent(q)}*,text_ar.ilike.*${encodeURIComponent(q)}*)`;
      if (!isNaN(num)) {
        filter = `or=(hadith_number.eq.${num},text_en.ilike.*${encodeURIComponent(q)}*,text_id.ilike.*${encodeURIComponent(q)}*)`;
      }

      let url = `${supabaseUrl}/rest/v1/hadiths?${filter}&limit=${limit}`;
      if (bookFilter && bookFilter !== 'all') {
        url += `&book_id=eq.${encodeURIComponent(bookFilter)}`;
      }

      const res = await fetch(url, {
        headers: { 'apikey': anonKey, 'Authorization': `Bearer ${anonKey}` }
      });

      if (res.ok) {
        const data = await res.json();
        if (data && data.length > 0) {
          return data.map(item => ({
            id: item.id,
            book_slug: item.book_id,
            book_name: item.book_id === 'nawawi' ? 'Forty Nawawi' : (item.book_id === 'bukhari' ? 'Sahih al-Bukhari' : item.book_id.toUpperCase()),
            hadith_number: item.hadith_number,
            reference: `#${item.hadith_number}`,
            arabic_text: item.text_ar || '',
            primary_translation: item.text_id || item.text_en || '',
            english_text: item.text_en || '',
            indonesian_text: item.text_id || '',
            grade: item.grade || 'Sahih'
          }));
        }
      }
    } catch (err) {
      console.warn('Supabase REST search failed, trying RPC:', err);
    }

    // 2. RPC search_hadiths fallback
    try {
      const response = await fetch(`${supabaseUrl}/rest/v1/rpc/search_hadiths`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'apikey': anonKey,
          'Authorization': `Bearer ${anonKey}`
        },
        body: JSON.stringify({ query_text: q, match_limit: limit })
      });

      if (response.ok) {
        const rawResults = await response.json();
        if (rawResults && rawResults.length > 0) {
          let mapped = rawResults.map(item => ({
            id: item.id,
            book_slug: item.book_id,
            book_name: item.book_id === 'nawawi' ? 'Forty Nawawi' : 'Sahih al-Bukhari',
            hadith_number: item.hadith_number,
            reference: `#${item.hadith_number}`,
            arabic_text: item.text_ar || '',
            primary_translation: item.text_id || item.text_en || '',
            english_text: item.text_en || '',
            indonesian_text: item.text_id || '',
            grade: item.grade || 'Sahih'
          }));

          if (bookFilter && bookFilter !== 'all') {
            mapped = mapped.filter(m => m.book_slug.toLowerCase() === bookFilter.toLowerCase());
          }
          if (mapped.length > 0) return mapped;
        }
      }
    } catch (err) {
      console.warn('Supabase RPC search failed:', err);
    }

    // 3. Lightweight Client-side Fallback
    return await this.fallbackLocalSearch(q, bookFilter);
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

  /** Lidwa/MJNA chapter index, stored as {_meta, ...chapter rows} NDJSON. */
  async getLidwaChapters(bookId) {
    if (!this.lidwaChapterCache) this.lidwaChapterCache = {};
    if (this.lidwaChapterCache[bookId]) return this.lidwaChapterCache[bookId];
    const res = await this._get(`lidwa-chapters/${bookId}.ndjson`, {}, 20000);
    if (!res) return null;
    const rows = parseNdjson(await res.text());
    const meta = (rows[0] && rows[0]._meta) || {};
    const out = Object.assign({}, meta, { chapters: rows.slice(1) });
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

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
    if (window.__HADEETH_BASE__) return window.__HADEETH_BASE__ + '/data';
    const scriptEl = document.querySelector('script[src*="api.js"]');
    if (scriptEl) {
      const src = scriptEl.getAttribute('src');
      const srcUrl = new URL(src, window.location.href);
      const rootPath = srcUrl.pathname.replace(/\/js\/api\.js.*$/, '');
      return srcUrl.origin + rootPath + '/data';
    }
    const base = window.location.pathname.replace(/\/[^/]*$/, '');
    return window.location.origin + base + '/data';
  },

  get dataUrl() {
    return this.baseUrl;
  },

  /**
   * Try R2 first, then the same key under the site's own /data.
   * Returns the Response, or null.
   */
  async _get(path, options = {}, timeoutMs = 15000) {
    const urls = [`${this.baseUrl}/${path}`, `${this.localDataUrl}/${path}`];
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
  async fetchNdjsonIndex(prefix, bookId) {
    if (!this.ndjsonIndexes) this.ndjsonIndexes = {};
    const key = `${prefix}_${bookId}`;
    if (this.ndjsonIndexes[key]) return this.ndjsonIndexes[key];

    if (prefix === 'api') {
      const res = await this._get(`api/${bookId}_index.ndjson`, {}, 20000);
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
    if (dsPrefix === 'lidwa') {
      return index.find(e => Array.isArray(e.l)
        ? e.l.some(id => String(id) === want)
        : String(e.l) === want) || null;
    }
    if (dsPrefix === 'ab') {
      return index.find(e => String(e.id) === want || String(e.n) === want) || null;
    }
    // hadith number first: `id` and `n` diverge (bukhari #5 has id 6, #6999 has id 7554)
    return index.find(e => String(e.n) === want)
        || index.find(e => String(e.id) === want)
        || null;
  },

  /**
   * Fetch a specific byte range from an NDJSON file.
   */
  async fetchNdjsonRange(prefix, bookId, startByte, endByte) {
    this.fullTextCache = this.fullTextCache || {};
    let text = "";

    if (this.fullTextCache[bookId]) {
        const slice = this.fullTextCache[bookId].slice(startByte, endByte + 1);
        text = new TextDecoder('utf-8').decode(slice);
    } else {
        const path = `${prefix}/${bookId}.ndjson`;
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
            this.fullTextCache[bookId] = buffer;
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
  async fetchNdjsonFull(prefix, bookId) {
    const res = await this._get(`${prefix}/${bookId}.ndjson`, {}, 30000);
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
      // legacy JSON shape, from the site's own /data
      const legacy = await fetchWithTimeout(`${this.localDataUrl}/books_v2.json?cb=${Date.now()}`).catch(() => null);
      if (legacy && legacy.ok) return await legacy.json();
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
        const legacy = await fetchWithTimeout(`${this.localDataUrl}/rawis/active_rawis.min.json?v=${Date.now()}`).catch(() => null);
        this.rawisCache = (legacy && legacy.ok) ? await legacy.json() : {};
      }
    } catch (e) {
      this.rawisCache = {};
    }
    return this.rawisCache;
  },

  async getChapters(bookId, datasetId) {
    const activeDataset = datasetId || localStorage.getItem('dataset_version') || 'fawazahmed';
    const isLidwa = activeDataset === 'native_lidwa' || activeDataset === 'native_mjna' || activeDataset === 'native_irsyad';
    const folder = isLidwa ? 'lidwa-chapters' : 'chapters';
    const cacheKey = `${folder}_${bookId}`;

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
      // legacy JSON shape, from the site's own /data
      const legacy = await fetchWithTimeout(`${this.localDataUrl}/${folder}/${bookId}.json`).catch(() => null);
      if (!legacy || !legacy.ok) throw new Error('chapters unavailable');
      const data = await legacy.json();
      let chaps = data.chapters || data;
      if (chaps && typeof chaps === 'object' && !Array.isArray(chaps)) chaps = Object.values(chaps);
      this.chaptersCache[cacheKey] = chaps;
      return chaps;
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
  async getChapterHadiths(bookId, chapterId) {
    try {
      const idx = await this.fetchNdjsonIndex('api', bookId);
      let chapterHadiths = [];

      if (Array.isArray(idx) && idx.length) {
        const entries = idx.filter(e => e.c !== undefined && String(e.c) === String(chapterId));
        if (entries.length) {
          for (const run of coalesceRuns(entries)) {
            const rows = await this.fetchNdjsonRange('api', bookId, run.start, run.end);
            for (const r of rows) {
              if (r.chapter_id === undefined || String(r.chapter_id) === String(chapterId)) {
                chapterHadiths.push(r);
              }
            }
          }
        } else if (!idx.some(e => e.c !== undefined)) {
          // This book carries no chapter column in its records. Scanning the whole
          // file would download the entire book to filter on a field that is not
          // there, so say so instead of paying for it.
          console.warn(`[hadeeth] ${bookId} has no chapter_id field; chapter listing cannot be filtered client-side`);
          return [];
        }
      } else {
        const allHadiths = await this.fetchNdjsonFull('api', bookId);
        chapterHadiths = allHadiths.filter(h => String(h.chapter_id) === String(chapterId));
      }

      return chapterHadiths.map(h => ({
        id: h.id,
        hadithnumber: h.hadith_number !== undefined ? h.hadith_number : h.id,
        lidwa_id: h.lidwa_id || null,
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
      const idx = await this.fetchNdjsonIndex('api', bookId);
      const entry = this.findIndexEntry(idx, hadithNumber, dsPrefix);

      if (entry) {
        const hadiths = await this.fetchNdjsonRange('api', bookId, entry.s, entry.e);
        h = hadiths[0] || null;
      } else {
        const allHadiths = await this.fetchNdjsonFull('api', bookId);
        const want = String(hadithNumber);
        h = allHadiths.find(item => {
          if (dsPrefix === 'lidwa') return Array.isArray(item.lidwa_id)
            ? item.lidwa_id.some(id => String(id) === want)
            : String(item.lidwa_id) === want;
          return String(item.hadith_number) === want || String(item.id) === want;
        }) || null;
      }
      
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
    try {
      let res2 = await fetchWithTimeout(`${this.localDataUrl}/api/topics_index.json?v=20260826_1`).catch(() => null);
      if (!res2 || !res2.ok) {
        res2 = await fetchWithTimeout(`https://raw.githubusercontent.com/itho777/hadeeth_id/main/data/api/topics_index.json?v=20260826_1`).catch(() => null);
      }
      if (res2 && res2.ok) {
        this.topicIndexCache = await res2.json();
        return this.topicIndexCache;
      }
    } catch (e) {
      console.warn('Failed to load topics_index:', e);
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
    try {
      const r2 = await fetchWithTimeout(`${this.localDataUrl}/api/topics_metadata.ndjson`).catch(() => null);
      if (r2 && r2.ok) {
        this.topicsCache = parseNdjson(await r2.text());
        return this.topicsCache;
      }
    } catch (e) {}
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
  async getHadithsBatch(bookId, hadithNumbers) {
    if (!hadithNumbers || hadithNumbers.length === 0) return [];
    const results = [];
    for (const num of hadithNumbers) {
       results.push(await this.getHadith(bookId, num));
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
          return this.normalizeEdition({ metadata: {}, hadiths: raw });
      }
    } catch (err) {
      console.error(`Failed to load edition ${langCode}-${bookId}:`, err);
      return null;
    }
  },

  /**
   * Multilingual Hadith Search (Supabase REST + RPC + Lightweight Local Fallback)
   */
  async search(query, bookFilter = 'all', limit = 20) {
    if (!query || !query.trim()) return [];
    const q = query.trim();
    const supabaseUrl = 'https://idokyspokenbmzoegahq.supabase.co';
    const anonKey = 'sb_publishable_Hz6k4Jp7rdSxwXCk1AO-sQ_r93N88QR';

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
   * Fetch commentary & sharh explanation (supports multiple)
   */
  async getCommentaries(bookId, hadithNumber) {
    // Not served from R2 yet — the syarah import is still running.
    const commentaries = [];
    try {
      const res = await fetch(`${this.localDataUrl}/commentaries/${bookId}_${hadithNumber}.json`);
      if (res.ok) commentaries.push(await res.json());
      
      // Probe for alternative/multiple commentaries (e.g. bukhari_1_2.json)
      for (let i = 2; i <= 5; i++) {
        const altRes = await fetch(`${this.localDataUrl}/commentaries/${bookId}_${hadithNumber}_${i}.json`);
        if (altRes.ok) commentaries.push(await altRes.json());
        else break;
      }
    } catch (err) {
      console.warn(`Commentary fetch error for ${bookId}_${hadithNumber}:`, err);
    }
    return commentaries;
  },

  /**
   * Fetch individual rawi (narrator) profile. Profile files are not in R2 yet;
   * fall back to the narrator registry that is.
   */
  async getRawiProfile(rawiId) {
    try {
      const res = await fetch(`${this.localDataUrl}/rawis/profiles/${rawiId}.json`);
      if (res.ok) return await res.json();
    } catch (err) {
      // fall through to the registry
    }
    try {
      const rawis = await this.getActiveRawis();
      return rawis[String(rawiId)] || null;
    } catch (err) {
      return null;
    }
  }
};

window.HadeethAPI = HadeethAPI;

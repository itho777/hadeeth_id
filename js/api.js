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

const HadeethAPI = {
  // Resolve base URL robustly across GitHub Pages (sub-path) and Cloudflare Pages (root).
  // Strategy: find the <script src="js/api.js"> tag and go up one level to get the site root.
  get baseUrl() {
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
   * Fetch and cache the NDJSON byte offset index for a specific file
   */
  async fetchNdjsonIndex(prefix, bookId) {
    if (!this.ndjsonIndexes) this.ndjsonIndexes = {};
    const key = `${prefix}_${bookId}`;
    if (this.ndjsonIndexes[key]) return this.ndjsonIndexes[key];
    
    let url = `${this.dataUrl}/${prefix}/${bookId}_ndjson_index.json`;
    let res = await fetchWithTimeout(url).catch(() => null);
    if (!res || !res.ok) {
        res = await fetchWithTimeout(`https://raw.githubusercontent.com/itho777/hadeeth_id/main/data/${prefix}/${bookId}_ndjson_index.json`).catch(() => null);
    }
    if (res && res.ok) {
        this.ndjsonIndexes[key] = await res.json();
        return this.ndjsonIndexes[key];
    }
    return null;
  },

  /**
   * Fetch a specific byte range from an NDJSON file
   */
  async fetchNdjsonRange(prefix, bookId, startByte, endByte) {
    this.fullTextCache = this.fullTextCache || {};
    let text = "";

    if (this.fullTextCache[bookId]) {
        const slice = this.fullTextCache[bookId].slice(startByte, endByte + 1);
        text = new TextDecoder('utf-8').decode(slice);
    } else {
        let url = `${this.dataUrl}/${prefix}/${bookId}.ndjson`;
        let res = await fetchWithTimeout(url, {
            headers: { 'Range': `bytes=${startByte}-${endByte}` }
        }).catch(() => null);
        if (!res || (!res.ok && res.status !== 206)) {
            res = await fetchWithTimeout(`https://raw.githubusercontent.com/itho777/hadeeth_id/main/data/${prefix}/${bookId}.ndjson`, {
                headers: { 'Range': `bytes=${startByte}-${endByte}` }
            }).catch(() => null);
        }
        if (!res || (!res.ok && res.status !== 206)) throw new Error(`HTTP ${res ? res.status : 'Range Failed'}`);
        
        let buffer = await res.arrayBuffer();
        
        if (res.status === 200) {
            // Server ignored Range, cache the full ArrayBuffer for future use
            this.fullTextCache[bookId] = buffer;
            const slice = buffer.slice(startByte, endByte + 1);
            text = new TextDecoder('utf-8').decode(slice);
        } else {
            text = new TextDecoder('utf-8').decode(buffer);
        }
    }
    
    const lines = text.split('\n').filter(l => l.trim().length > 0);
    let results = [];
    for (const line of lines) {
      try {
        results.push(JSON.parse(line));
      } catch (e) {
        // Truncated boundary fragment — skip it (expected when range cuts mid-line)
      }
    }
    
    // If we got zero results and we didn't fetch from GitHub raw, it means we probably received
    // compressed binary gibberish (Cloudflare/GitHub Pages compresses responses and breaks Range requests).
    if (results.length === 0) {
      const ghUrl = `https://raw.githubusercontent.com/itho777/hadeeth_id/main/data/${prefix}/${bookId}.ndjson`;
      const fallbackRes = await fetchWithTimeout(ghUrl, {
          headers: { 'Range': `bytes=${startByte}-${endByte}` }
      }).catch(() => null);
      
      if (fallbackRes && (fallbackRes.status === 200 || fallbackRes.status === 206)) {
          let fbBuffer = await fallbackRes.arrayBuffer();
          let fbText = "";
          if (fallbackRes.status === 200) {
              this.fullTextCache[bookId] = fbBuffer;
              fbText = new TextDecoder('utf-8').decode(fbBuffer.slice(startByte, endByte + 1));
          } else {
              fbText = new TextDecoder('utf-8').decode(fbBuffer);
          }
          const fbLines = fbText.split('\n').filter(l => l.trim().length > 0);
          for (const line of fbLines) {
            try { results.push(JSON.parse(line)); } catch(e) {}
          }
      }
    }

    return results;
  },
  
  /**
   * Fallback to fetch the entire NDJSON file
   */
  async fetchNdjsonFull(prefix, bookId) {
    const url = `${this.dataUrl}/${prefix}/${bookId}.ndjson`;
    const res = await fetchWithTimeout(url, {}, 20000).catch(() => null);
    if (!res || !res.ok) throw new Error(`HTTP ${res ? res.status : 'Network Error'}`);
    const text = await res.text();
    const lines = text.split('\n').filter(l => l.trim().length > 0);
    return lines.map(l => JSON.parse(l));
  },

  /**
   * Fetch master list of books
   */
  async getBooks() {
    try {
      const cb = Date.now(); // Dynamic cache buster to completely avoid stale books.json
      const res = await fetch(`${this.baseUrl}/books_v2.json?cb=${cb}`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      return await res.json();
    } catch (err) {
      console.error('Failed to load books.json:', err);
      return [];
    }
  },

  /**
   * Fetch chapter index for a book (e.g. 'bukhari')
   */
  async getActiveRawis() {
    if (this.rawisCache) return this.rawisCache;
    try {
      const cacheBuster = Date.now();
      const res = await fetchWithTimeout(`${this.baseUrl}/rawis/active_rawis.min.json?v=${cacheBuster}`).catch(() => null);
      if (res && res.ok) {
        this.rawisCache = await res.json();
      } else {
        this.rawisCache = {};
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
      const res = await fetch(`${this.baseUrl}/${folder}/${bookId}.json`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      
      this.chaptersCache = this.chaptersCache || {};
      let chaps = data.chapters || data; // handle both formats
      if (chaps && typeof chaps === 'object' && !Array.isArray(chaps)) {
          chaps = Object.values(chaps);
      }
      this.chaptersCache[cacheKey] = chaps;
      return this.chaptersCache[cacheKey];
    } catch (err) {
      console.error(`Failed to load ${folder} for ${bookId}:`, err);
      return [];
    }
  },

  /**
   * Fetch hadiths for a specific chapter from the consolidated API using HTTP Range Requests
   */
  async getChapterHadiths(bookId, chapterId) {
    try {
      const idx = await this.fetchNdjsonIndex('api', bookId);
      let chapterHadiths = [];
      
      if (idx && idx.chapters && idx.chapters[chapterId]) {
          const range = idx.chapters[chapterId];
          chapterHadiths = await this.fetchNdjsonRange('api', bookId, range.start, range.end);
      } else {
          // Fallback to full fetch if no index
          const allHadiths = await this.fetchNdjsonFull('api', bookId);
          chapterHadiths = allHadiths.filter(h => String(h.chapter_id) === String(chapterId));
      }
      
      return chapterHadiths.map(h => ({
        id: h.id,
        hadithnumber: h.hadith_number || h.id,
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
   * Fetch full unified record for a single Hadith using HTTP Range Requests
   */
  async getHadith(bookId, hadithNumber, dsPrefix = 'fawaz') {
    try {
      let h = null;
      const idx = await this.fetchNdjsonIndex('api', bookId);
      const indexArray = Array.isArray(idx) ? idx : (idx && idx.hadiths ? idx.hadiths : []);
      if (indexArray && indexArray.length > 0) {
          const entry = indexArray.find(e => {
              if (dsPrefix === 'lidwa') { if (Array.isArray(e.lidwa_id)) return e.lidwa_id.some(id => String(id) === String(hadithNumber)); return String(e.lidwa_id) === String(hadithNumber); }
              if (dsPrefix === 'ab') return String(e.idInBook) === String(hadithNumber) || String(e.ab_id) === String(hadithNumber);
              return String(e.id) === String(hadithNumber);
          });
          if (entry) {
              const hadiths = await this.fetchNdjsonRange('api', bookId, entry.start, entry.end);
              h = hadiths[0] || null;
          } else {
              const allHadiths = await this.fetchNdjsonFull('api', bookId);
              h = allHadiths.find(item => {
                  if (dsPrefix === 'lidwa') { if (Array.isArray(item.lidwa_id)) return item.lidwa_id.some(id => String(id) === String(hadithNumber)); return String(item.lidwa_id) === String(hadithNumber); }
                  if (dsPrefix === 'ab') return String(item.idInBook) === String(hadithNumber) || String(item.ab_id) === String(hadithNumber);
                  return String(item.id) === String(hadithNumber) || String(item.hadith_number) === String(hadithNumber);
              }) || null;
          }
      } else if (idx && idx.hadiths && idx.hadiths[hadithNumber]) {
          const range = idx.hadiths[hadithNumber];
          const hadiths = await this.fetchNdjsonRange('api', bookId, range[0], range[1]);
          h = hadiths[0] || null;
      } else {
          const allHadiths = await this.fetchNdjsonFull('api', bookId);
          h = allHadiths.find(item => {
                  if (dsPrefix === 'lidwa') { if (Array.isArray(item.lidwa_id)) return item.lidwa_id.some(id => String(id) === String(hadithNumber)); return String(item.lidwa_id) === String(hadithNumber); }
                  if (dsPrefix === 'ab') return String(item.idInBook) === String(hadithNumber) || String(item.ab_id) === String(hadithNumber);
                  return String(item.id) === String(hadithNumber) || String(item.hadith_number) === String(hadithNumber);
              }) || null;
      }
      
      // Backward compatibility wrapper for old hadith.html
      if (h) {
          h.hadith_number = h.id;
          if (h.translations) {
              if (h.translations.ar && h.translations.ar.length > 0) h.text_ar = h.translations.ar[0].text;
              if (h.translations.en && h.translations.en.length > 0) h.text_en = h.translations.en[0].text;
              if (h.translations.id && h.translations.id.length > 0) h.text_id = h.translations.id[0].text;
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
    try {
      let url = `${this.dataUrl}/api/topics_index.json?v=20260826_1`;
      let res = await fetchWithTimeout(url).catch(() => null);
      if (!res || !res.ok) {
        res = await fetchWithTimeout(`https://raw.githubusercontent.com/itho777/hadeeth_id/main/data/api/topics_index.json?v=20260826_1`).catch(() => null);
      }
      if (res && res.ok) {
        this.topicIndexCache = await res.json();
        return this.topicIndexCache;
      }
    } catch (e) {
      console.warn('Failed to load topics_index.json:', e);
    }
    return null;
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
    const commentaries = [];
    try {
      const res = await fetch(`${this.baseUrl}/commentaries/${bookId}_${hadithNumber}.json`);
      if (res.ok) commentaries.push(await res.json());
      
      // Probe for alternative/multiple commentaries (e.g. bukhari_1_2.json)
      for (let i = 2; i <= 5; i++) {
        const altRes = await fetch(`${this.baseUrl}/commentaries/${bookId}_${hadithNumber}_${i}.json`);
        if (altRes.ok) commentaries.push(await altRes.json());
        else break;
      }
    } catch (err) {
      console.warn(`Commentary fetch error for ${bookId}_${hadithNumber}:`, err);
    }
    return commentaries;
  },

  /**
   * Fetch individual rawi (narrator) profile
   */
  async getRawiProfile(rawiId) {
    try {
      const res = await fetch(`${this.baseUrl}/rawis/profiles/${rawiId}.json`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      return await res.json();
    } catch (err) {
      console.warn(`Rawi profile not found for ${rawiId}`);
      return null;
    }
  }
};

window.HadeethAPI = HadeethAPI;

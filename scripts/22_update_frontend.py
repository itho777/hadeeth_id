import os

JS_PATH = "js/api.js"

with open(JS_PATH, 'r', encoding='utf-8') as f:
    content = f.read()

# Define blocks
BLOCK_OLD_GET_BASE = """  get baseUrl() {
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
  },"""

BLOCK_NEW_GET_BASE = """  get baseUrl() {
    if (window.__HADEETH_BASE__) return window.__HADEETH_BASE__ + '/data';
    const scriptEl = document.querySelector('script[src*="api.js"]');
    if (scriptEl) {
      const src = scriptEl.getAttribute('src');
      const srcUrl = new URL(src, window.location.href);
      const rootPath = srcUrl.pathname.replace(/\\/js\\/api\\.js.*$/, '');
      return srcUrl.origin + rootPath + '/data';
    }
    const base = window.location.pathname.replace(/\\/[^/]*$/, '');
    return window.location.origin + base + '/data';
  },

  get dataUrl() {
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        return this.baseUrl;
    }
    return 'https://raw.githubusercontent.com/itho777/hadeeth_id/main/data';
  },"""

content = content.replace(BLOCK_OLD_GET_BASE, BLOCK_NEW_GET_BASE)

# Now find the fetchChunkedJson block and everything down to getEdition
start_marker = """  /**\n   * Universal chunked JSON fetcher."""
end_marker = """  /**\n   * Multilingual Hadith Search"""

start_idx = content.find(start_marker)
end_idx = content.find(end_marker)

NEW_FUNCS = """  /**
   * Fetch and cache the NDJSON byte offset index for a specific file
   */
  async fetchNdjsonIndex(prefix, bookId) {
    if (!this.ndjsonIndexes) this.ndjsonIndexes = {};
    const key = `${prefix}_${bookId}`;
    if (this.ndjsonIndexes[key]) return this.ndjsonIndexes[key];
    
    const url = `${this.dataUrl}/${prefix}/${bookId}_ndjson_index.json`;
    const res = await fetch(url).catch(() => null);
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
    const url = `${this.dataUrl}/${prefix}/${bookId}.ndjson`;
    const res = await fetch(url, {
        headers: { 'Range': `bytes=${startByte}-${endByte}` }
    });
    if (!res.ok && res.status !== 206) throw new Error(`HTTP ${res.status}`);
    const text = await res.text();
    const lines = text.split('\\n').filter(l => l.trim().length > 0);
    return lines.map(l => JSON.parse(l));
  },
  
  /**
   * Fallback to fetch the entire NDJSON file
   */
  async fetchNdjsonFull(prefix, bookId) {
    const url = `${this.dataUrl}/${prefix}/${bookId}.ndjson`;
    const res = await fetch(url).catch(() => null);
    if (!res || !res.ok) throw new Error(`HTTP ${res ? res.status : 'Network Error'}`);
    const text = await res.text();
    const lines = text.split('\\n').filter(l => l.trim().length > 0);
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
      const res = await fetch(`${this.baseUrl}/rawis/active_rawis.min.json?v=${cacheBuster}`);
      if (res.ok) {
        this.rawisCache = await res.json();
      } else {
        this.rawisCache = {};
      }
    } catch (e) {
      this.rawisCache = {};
    }
    return this.rawisCache;
  },

  async getChapters(bookId) {
    const activeDataset = localStorage.getItem('dataset_version') || 'fawazahmed';
    const isLidwa = activeDataset === 'native_lidwa';
    const folder = isLidwa ? 'lidwa-chapters' : 'chapters';
    const cacheKey = `${folder}_${bookId}`;

    if (this.chaptersCache && this.chaptersCache[cacheKey]) return this.chaptersCache[cacheKey];
    try {
      const res = await fetch(`${this.baseUrl}/${folder}/${bookId}.json`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      
      this.chaptersCache = this.chaptersCache || {};
      this.chaptersCache[cacheKey] = data.chapters || data; // handle both formats
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
  async getHadith(bookId, hadithNumber) {
    try {
      const idx = await this.fetchNdjsonIndex('api', bookId);
      if (idx && idx.hadiths && idx.hadiths[hadithNumber]) {
          const range = idx.hadiths[hadithNumber];
          const hadiths = await this.fetchNdjsonRange('api', bookId, range[0], range[1]);
          return hadiths[0] || null;
      }
      
      const allHadiths = await this.fetchNdjsonFull('api', bookId);
      return allHadiths.find(h => String(h.hadith_number) === String(hadithNumber) || String(h.id) === String(hadithNumber)) || null;
    } catch (err) {
      console.error(`Failed to load Hadith ${bookId}:${hadithNumber}:`, err);
      return null;
    }
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

"""

content = content[:start_idx] + NEW_FUNCS + content[end_idx:]

with open(JS_PATH, 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated js/api.js")

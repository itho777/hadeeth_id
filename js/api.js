/**
 * HADEETH.ID — Client Data API Adapter
 * High-performance asynchronous loader for pre-indexed CDN JSON files.
 * Provides fallback and instant retrieval for offline-first and online web app.
 */

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
      const res = await fetch(`${this.baseUrl}/rawis/active_rawis.min.json?v=20260814`);
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
    if (this.chaptersCache && this.chaptersCache[bookId]) return this.chaptersCache[bookId];
    try {
      const res = await fetch(`${this.baseUrl}/chapters/${bookId}.json`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      this.chaptersCache = this.chaptersCache || {};
      this.chaptersCache[bookId] = data;
      return data;
    } catch (err) {
      console.error(`Failed to load chapters for ${bookId}:`, err);
      return [];
    }
  },

  /**
   * Fetch full unified record for a single Hadith
   */
  async getHadith(bookId, hadithNumber) {
    try {
      const res = await fetch(`${this.baseUrl}/hadiths/${bookId}/${hadithNumber}.json`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      return await res.json();
    } catch (err) {
      console.error(`Failed to load Hadith ${bookId}:${hadithNumber}:`, err);
      return null;
    }
  },

  /**
   * Normalize an edition JSON to the standard {metadata, hadiths} format.
   * Handles edge cases:
   *   - Flat arrays (e.g. old ind-muslim format)
   *   - Hadiths using 'id' instead of 'hadithnumber'
   */
  normalizeEdition(data) {
    if (!data) return null;

    // If it's a raw array, wrap it
    if (Array.isArray(data)) {
      data = { metadata: {}, hadiths: data };
    }

    if (!data.hadiths) return data;

    // Ensure each hadith has 'hadithnumber' (fallback to 'id')
    data.hadiths = data.hadiths.map(h => {
      if (h.hadithnumber === undefined && h.id !== undefined) {
        return { ...h, hadithnumber: h.id };
      }
      return h;
    });

    return data;
  },

  /**
   * Fetch full language edition file (e.g. 'ara-bukhari', 'ind-bukhari')
   */
  async getEdition(langCode, bookId) {
    try {
      const cacheBuster = '20260814';
      const res = await fetch(`${this.baseUrl}/editions/${langCode}-${bookId}.json?v=${cacheBuster}`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const raw = await res.json();
      return this.normalizeEdition(raw);
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

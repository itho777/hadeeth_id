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
      const res = await fetch(`${this.baseUrl}/books.json`);
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
  async getChapters(bookId) {
    try {
      const res = await fetch(`${this.baseUrl}/chapters/${bookId}.json`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      return await res.json();
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
   * Fetch full language edition file (e.g. 'ara-bukhari', 'ind-bukhari')
   */
  async getEdition(langCode, bookId) {
    try {
      const res = await fetch(`${this.baseUrl}/editions/${langCode}-${bookId}.json`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      return await res.json();
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
   * Fetch commentary & sharh explanation
   */
  async getCommentary(bookId, hadithNumber) {
    try {
      const res = await fetch(`${this.baseUrl}/commentaries/${bookId}_${hadithNumber}.json`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      return await res.json();
    } catch (err) {
      console.warn(`Commentary not found for ${bookId}_${hadithNumber}`);
      return null;
    }
  }
};

window.HadeethAPI = HadeethAPI;

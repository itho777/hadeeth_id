/**
 * HADEETH.ID — Client Data API Adapter
 * High-performance asynchronous loader for pre-indexed CDN JSON files.
 * Provides fallback and instant retrieval for offline-first and online web app.
 */

const HadeethAPI = {
  baseUrl: window.location.pathname.endsWith('/') 
    ? window.location.pathname + 'data'
    : window.location.pathname.substring(0, window.location.pathname.lastIndexOf('/')) + '/data',

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
   * Perform real-time multilingual full-text search via Supabase RPC
   */
  async search(query, limit = 20) {
    if (!query || !query.trim()) return [];
    const supabaseUrl = 'https://idokyspokenbmzoegahq.supabase.co';
    const anonKey = 'sb_publishable_Hz6k4Jp7rdSxwXCk1AO-sQ_r93N88QR';

    try {
      const response = await fetch(`${supabaseUrl}/rest/v1/rpc/search_hadiths`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'apikey': anonKey,
          'Authorization': `Bearer ${anonKey}`
        },
        body: JSON.stringify({
          query_text: query.trim(),
          match_limit: limit
        })
      });

      if (!response.ok) {
        throw new Error(`Search failed: HTTP ${response.status}`);
      }

      const rawResults = await response.json();
      
      // Map database column names to UI rendering properties
      return rawResults.map(item => ({
        id: item.id,
        book_slug: item.book_id,
        book_name: item.book_id === 'nawawi' ? 'Forty Nawawi' : 'Sahih al-Bukhari',
        hadith_number: item.hadith_number,
        reference: `#${item.hadith_number}`,
        arabic_text: item.text_ar,
        primary_translation: item.text_en || item.text_id,
        english_text: item.text_en,
        indonesian_text: item.text_id,
        grade: item.grade || 'Sahih',
        rank: item.rank
      }));
    } catch (err) {
      console.error('Supabase Search Error:', err);
      // Fallback search using local JSON edition data if network/RPC fails
      return this.fallbackLocalSearch(query);
    }
  },

  /**
   * Fallback client-side search using loaded JSON edition data
   */
  async fallbackLocalSearch(query) {
    const q = query.toLowerCase().trim();
    const bukhariEng = await this.getEdition('eng', 'bukhari');
    if (!bukhariEng || !bukhariEng.hadiths) return [];

    const matches = [];
    for (const h of bukhariEng.hadiths) {
      if ((h.text && h.text.toLowerCase().includes(q)) || 
          (h.hadithnumber && h.hadithnumber.toString() === q)) {
        matches.push({
          id: h.hadithnumber,
          book_slug: 'bukhari',
          book_name: 'Sahih al-Bukhari',
          hadith_number: h.hadithnumber,
          reference: `#${h.hadithnumber}`,
          arabic_text: '',
          primary_translation: h.text,
          grade: 'Sahih',
          rank: 1.0
        });
        if (matches.length >= 20) break;
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

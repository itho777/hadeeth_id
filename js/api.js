/**
 * HADEETH.ID — Client Data API Adapter
 * High-performance asynchronous loader for pre-indexed CDN JSON files.
 * Provides fallback and instant retrieval for offline-first and online web app.
 */

const HadeethAPI = {
  baseUrl: '/data',

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

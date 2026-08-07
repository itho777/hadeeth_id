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
   * Algolia Search Client Adapter Skeleton
   */
  algoliaClient: {
    appId: 'HADEETH_ALGOLIA_APP_ID',
    searchKey: 'HADEETH_ALGOLIA_SEARCH_KEY',
    indexName: 'hadeeth_index',
    async search(query, bookFilter = 'all', limit = 20) {
      try {
        const url = `https://${this.appId}-dsn.algolia.net/1/indexes/${this.indexName}/query`;
        const filters = bookFilter !== 'all' ? `book_id:${bookFilter}` : '';
        const res = await fetch(url, {
          method: 'POST',
          headers: {
            'X-Algolia-Application-Id': this.appId,
            'X-Algolia-API-Key': this.searchKey,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ query, filters, hitsPerPage: limit })
        });
        if (res.ok) {
          const data = await res.json();
          if (data.hits && data.hits.length > 0) {
            return data.hits.map(hit => ({
              id: hit.objectID || hit.id,
              book_slug: hit.book_id,
              book_name: hit.book_name || (hit.book_id === 'nawawi' ? 'Forty Nawawi' : 'Sahih al-Bukhari'),
              hadith_number: hit.hadith_number,
              reference: `#${hit.hadith_number}`,
              arabic_text: hit.text_ar || '',
              primary_translation: hit.text_id || hit.text_en || '',
              english_text: hit.text_en || '',
              indonesian_text: hit.text_id || '',
              grade: hit.grade || 'Sahih'
            }));
          }
        }
      } catch (err) {
        console.warn('Algolia API call fallback to primary search pipeline:', err);
      }
      return null;
    }
  },

  /**
   * Cloudflare AI Worker Semantic Vector Search Client Adapter Skeleton
   */
  cloudflareAiClient: {
    endpoint: 'https://ai-search.hadeeth.workers.dev/search',
    async search(query, bookFilter = 'all', limit = 20) {
      try {
        const res = await fetch(this.endpoint, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ prompt: query, book: bookFilter, limit })
        });
        if (res.ok) {
          const data = await res.json();
          if (data.results && data.results.length > 0) {
            return data.results;
          }
        }
      } catch (err) {
        console.warn('Cloudflare AI search worker fallback to primary search pipeline:', err);
      }
      return null;
    },
  },

  /**
   * Unified Search Router (Algolia Keyword vs Cloudflare AI Semantic vs Supabase RPC vs Local Fallback)
   */
  async search(query, searchType = 'semantic', bookFilter = 'all', limit = 20) {
    if (!query || !query.trim()) return [];
    const q = query.trim();

    // 1. Algolia Keyword Search Adapter
    if (searchType === 'exact') {
      const algoliaHits = await this.algoliaClient.search(q, bookFilter, limit);
      if (algoliaHits && algoliaHits.length > 0) return algoliaHits;
    }

    // 2. Cloudflare AI Semantic Vector Search Adapter
    if (searchType === 'semantic') {
      const cfHits = await this.cloudflareAiClient.search(q, bookFilter, limit);
      if (cfHits && cfHits.length > 0) return cfHits;
    }

    // 3. Supabase RPC search_hadiths
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
          query_text: q,
          match_limit: limit
        })
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
            grade: item.grade || 'Sahih',
            rank: item.rank
          }));

          if (bookFilter !== 'all') {
            mapped = mapped.filter(m => m.book_slug.toLowerCase() === bookFilter.toLowerCase());
          }
          if (mapped.length > 0) return mapped;
        }
      }
    } catch (err) {
      console.warn('Supabase Search Error:', err);
    }

    // 4. Client-side Multi-Edition Fallback Search Engine
    return await this.fallbackLocalSearch(q, bookFilter);
  },

  /**
   * Fallback client-side search using pre-loaded JSON edition data
   */
  async fallbackLocalSearch(query, bookFilter = 'all') {
    const q = query.toLowerCase().trim();
    const booksToSearch = (bookFilter !== 'all') ? [bookFilter] : ['bukhari', 'nawawi'];
    const matches = [];

    for (const bId of booksToSearch) {
      const bookName = bId === 'nawawi' ? 'Forty Nawawi' : 'Sahih al-Bukhari';
      const [engEd, indEd, araEd] = await Promise.all([
        this.getEdition('eng', bId),
        this.getEdition('ind', bId),
        this.getEdition('ara', bId)
      ]);

      const list = (engEd && engEd.hadiths) ? engEd.hadiths : [];
      const indList = (indEd && indEd.hadiths) ? indEd.hadiths : [];
      const araList = (araEd && araEd.hadiths) ? araEd.hadiths : [];

      const maxLen = Math.max(list.length, indList.length, araList.length);
      for (let i = 0; i < maxLen; i++) {
        const engObj = list[i] || {};
        const indObj = indList[i] || {};
        const araObj = araList[i] || {};
        const hNum = engObj.hadithnumber || indObj.hadithnumber || (i + 1);

        const textEn = engObj.text || '';
        const textId = indObj.text || '';
        const textAr = araObj.text || '';

        if (String(hNum) === q || textEn.toLowerCase().includes(q) || textId.toLowerCase().includes(q) || textAr.includes(q)) {
          matches.push({
            id: `${bId}_${hNum}`,
            book_slug: bId,
            book_name: bookName,
            hadith_number: hNum,
            reference: `#${hNum}`,
            arabic_text: textAr,
            primary_translation: textId || textEn,
            english_text: textEn,
            indonesian_text: textId,
            grade: 'Sahih',
            rank: 1.0
          });
          if (matches.length >= 20) break;
        }
      }
      if (matches.length >= 20) break;
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

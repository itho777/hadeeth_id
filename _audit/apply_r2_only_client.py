#!/usr/bin/env python3
"""Point js/api.js at R2 only and add NDJSON readers for the migrated sets."""
from pathlib import Path

p = Path(r"G:/hadeeth_id/js/api.js")
s = p.read_text(encoding="utf-8")


def rep(old, new, n=1):
    global s
    assert s.count(old) == n, f"expected {n}, found {s.count(old)}: {old[:90]!r}"
    s = s.replace(old, new, n)


rep("""  get localDataUrl() {
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
  },""",
"""  get localDataUrl() {
    // Kept as an alias: all site data lives on R2 now.
    return this.baseUrl;
  },""")

rep("""    const urls = [`${this.baseUrl}/${path}`, `${this.localDataUrl}/${path}`];""",
    """    const urls = [`${this.baseUrl}/${path}`];
    if (this.localDataUrl !== this.baseUrl) urls.push(`${this.localDataUrl}/${path}`);""")

rep("""      // legacy JSON shape, from the site's own /data
      const legacy = await fetchWithTimeout(`${this.localDataUrl}/books_v2.json?cb=${Date.now()}`).catch(() => null);
      if (legacy && legacy.ok) return await legacy.json();
      throw new Error('no book registry');""",
    """      throw new Error('no book registry');""")

rep("""      } else {
        const legacy = await fetchWithTimeout(`${this.localDataUrl}/rawis/active_rawis.min.json?v=${Date.now()}`).catch(() => null);
        this.rawisCache = (legacy && legacy.ok) ? await legacy.json() : {};
      }""",
    """      } else {
        this.rawisCache = {};
      }""")

rep("""  /**
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
  }""",
"""  /** Fetch a link map for one book from links/<book>.ndjson on R2. */
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

  /** Fetch one narrator profile by byte range from rawis/profiles.ndjson. */
  async getRawiProfile(rawiId) {
    const key = String(rawiId);
    if (this.rawiProfileCache && this.rawiProfileCache[key]) return this.rawiProfileCache[key];
    const idxRes = await this._get('rawis/profiles_index.ndjson', {}, 20000);
    if (idxRes) {
      const hit = parseNdjson(await idxRes.text()).find(r => String(r.id) === key);
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
  }""")

p.write_text(s, encoding="utf-8", newline="\r\n")
print("patched js/api.js")

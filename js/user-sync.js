/* Shared web <-> Supabase user state.
 *
 * The mobile client uses the same three tables:
 *   profiles, bookmarks, reading_progress
 * so a bookmark or last-read position created here is visible there after the
 * same account signs in. Failures are non-fatal: the site keeps using
 * localStorage when the schema has not been applied yet. */
(() => {
  'use strict';

  const cfg = window.SUPABASE_CONFIG || {};
  const client = window.supabaseClient || (window.supabase && cfg.URL && cfg.ANON_KEY
    ? window.supabase.createClient(cfg.URL, cfg.ANON_KEY)
    : null);

  const BOOKMARKS_KEY = 'hadeeth_bookmarks';
  const PROFILE_KEY = 'hadeeth_profile_cache';

  const readJson = (key, fallback) => {
    try { return JSON.parse(localStorage.getItem(key) || 'null') ?? fallback; } catch (_) { return fallback; }
  };
  const writeJson = (key, value) => {
    try { localStorage.setItem(key, JSON.stringify(value)); } catch (_) {}
  };

  function localBookmarks() {
    const raw = readJson(BOOKMARKS_KEY, []);
    return Array.isArray(raw) ? raw : [];
  }

  function localProgress() {
    const raw = readJson('hadeeth_last_read', null);
    if (!raw || !raw.bookId || !raw.hadithId) return null;
    return {
      book_id: raw.bookId,
      hadith_number: String(raw.hadithId),
      book_title: raw.bookName || '',
      chapter: raw.hadithTitle || '',
      read_at: new Date(raw.timestamp || Date.now()).toISOString()
    };
  }

  function bookmarkRow(b) {
    return {
      book_id: b.bookId || b.book_id,
      hadith_number: String(b.hadithId ?? b.hadith_number ?? ''),
      book_title: b.bookName || b.book_title || '',
      arabic: b.arabic || '',
      translation: b.translation || '',
      grade: b.grade || '',
      note: b.note || '',
      collection: b.collection || 'Unsorted',
      saved_at: b.savedAt || b.saved_at || new Date().toISOString()
    };
  }

  async function session() {
    if (!client) return null;
    const { data } = await client.auth.getSession();
    return data?.session || null;
  }

  async function ensureProfile(user) {
    const meta = user.user_metadata || {};
    const { data, error } = await client.from('profiles')
      .select('display_name,avatar_url,preferred_language').eq('id', user.id).maybeSingle();
    if (!error && data) {
      writeJson(PROFILE_KEY, data);
      return data;
    }
    if (error && !/relation|does not exist|schema cache/i.test(error.message)) throw error;
    const row = {
      id: user.id,
      display_name: meta.full_name || meta.name || (user.email || '').split('@')[0],
      avatar_url: meta.avatar_url || meta.picture || null,
      preferred_language: localStorage.getItem('hadeeth_lang') || 'id'
    };
    if (!error) await client.from('profiles').upsert(row, { onConflict: 'id' });
    writeJson(PROFILE_KEY, row);
    return row;
  }

  async function syncBookmarks(user) {
    const local = localBookmarks();
    const { data: remote, error } = await client.from('bookmarks')
      .select('book_id,hadith_number,book_title,arabic,translation,grade,note,collection,saved_at')
      .eq('user_id', user.id);
    if (error) throw error;
    const remoteRows = remote || [];
    const byKey = new Map(remoteRows.map((r) => [`${r.book_id}__${r.hadith_number}`, r]));
    const merged = new Map(byKey);
    for (const b of local) {
      const row = bookmarkRow(b);
      if (!row.book_id || !row.hadith_number) continue;
      const key = `${row.book_id}__${row.hadith_number}`;
      const prior = merged.get(key);
      if (!prior || new Date(row.saved_at) >= new Date(prior.saved_at)) merged.set(key, { ...prior, ...row });
    }
    const rows = [...merged.values()].map((r) => ({
      user_id: user.id,
      book_id: r.book_id,
      hadith_number: String(r.hadith_number),
      book_title: r.book_title || '',
      arabic: r.arabic || '',
      translation: r.translation || '',
      grade: r.grade || '',
      note: r.note || '',
      collection: r.collection || 'Unsorted',
      saved_at: r.saved_at || new Date().toISOString()
    }));
    if (rows.length) {
      const { error: upErr } = await client.from('bookmarks').upsert(rows, { onConflict: 'user_id,book_id,hadith_number' });
      if (upErr) throw upErr;
    }
    writeJson(BOOKMARKS_KEY, rows.map((r) => ({
      bookId: r.book_id, hadithId: r.hadith_number, bookName: r.book_title,
      arabic: r.arabic, translation: r.translation, grade: r.grade,
      note: r.note, collection: r.collection, savedAt: r.saved_at
    })));
    return rows.length;
  }

  async function syncProgress(user) {
    const local = localProgress();
    const { data: remote, error } = await client.from('reading_progress')
      .select('book_id,hadith_number,book_title,chapter,read_at')
      .eq('user_id', user.id);
    if (error) throw error;
    let chosen = null;
    for (const r of remote || []) {
      if (!chosen || new Date(r.read_at) > new Date(chosen.read_at)) chosen = r;
    }
    if (local && (!chosen || new Date(local.read_at) >= new Date(chosen.read_at))) {
      const row = { user_id: user.id, ...local };
      const { error: upErr } = await client.from('reading_progress')
        .upsert(row, { onConflict: 'user_id,book_id' });
      if (upErr) throw upErr;
      return 1;
    }
    if (chosen) {
      localStorage.setItem('hadeeth_last_read', JSON.stringify({
        bookId: chosen.book_id,
        hadithId: chosen.hadith_number,
        bookName: chosen.book_title,
        hadithTitle: chosen.chapter,
        timestamp: new Date(chosen.read_at).getTime()
      }));
    }
    return 1;
  }

  async function sync() {
    if (!client) return { ok: false, error: 'Supabase client unavailable' };
    const s = await session();
    if (!s) return { ok: false, error: 'not signed in' };
    try {
      const profile = await ensureProfile(s.user);
      const bookmarks = await syncBookmarks(s.user);
      await syncProgress(s.user);
      return { ok: true, profile, bookmarks };
    } catch (err) {
      return { ok: false, error: err.message || String(err) };
    }
  }

  async function saveProfile(patch) {
    if (!client) return { ok: false, error: 'Supabase client unavailable' };
    const s = await session();
    if (!s) return { ok: false, error: 'not signed in' };
    const row = {
      id: s.user.id,
      display_name: patch.display_name ?? null,
      preferred_language: patch.preferred_language || 'id',
      updated_at: new Date().toISOString()
    };
    const { error } = await client.from('profiles').upsert(row, { onConflict: 'id' });
    if (error) return { ok: false, error: error.message };
    writeJson(PROFILE_KEY, row);
    return { ok: true, profile: row };
  }

  async function counts() {
    if (!client) return null;
    const s = await session();
    if (!s) return null;
    const [b, r] = await Promise.all([
      client.from('bookmarks').select('*', { head: true, count: 'exact' }).eq('user_id', s.user.id),
      client.from('reading_progress').select('*', { head: true, count: 'exact' }).eq('user_id', s.user.id)
    ]);
    return { bookmarks: b.error ? null : b.count, progress: r.error ? null : r.count };
  }

  async function isAdmin() {
    if (!client) return false;
    const s = await session();
    if (!s) return false;
    const { data, error } = await client.rpc('is_hadeeth_admin');
    if (!error) return data === true;
    return (window.ADMIN_EMAILS || []).includes(s.user.email);
  }

  function addBookmark(entry) {
    const rows = localBookmarks().filter((b) =>
      !(b.bookId === entry.bookId && String(b.hadithId) === String(entry.hadithId)));
    rows.push({ ...entry, savedAt: entry.savedAt || new Date().toISOString() });
    writeJson(BOOKMARKS_KEY, rows);
    sync();
  }

  function trackProgress(bookId, hadithId, bookName, chapter) {
    // LastReadTracker already wrote the canonical local record; mirror it.
    sync();
  }

  window.HadeethUserSync = { sync, saveProfile, counts, isAdmin, addBookmark, trackProgress, localBookmarks };
})();

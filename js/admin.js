/* Admin console: Supabase-backed HOTD pins; no copied corpus.
 *
 * Supabase stores the editorial decision (hotd_overrides, hotd_settings).
 * The narration text and the daily deterministic sahih pick come from the R2
 * CDN through HadeethAPI, exactly as the web reader and mobile app use them. */
(() => {
  'use strict';

  const cfg = window.SUPABASE_CONFIG || {};
  const client = window.supabase && cfg.URL && cfg.ANON_KEY
    ? window.supabase.createClient(cfg.URL, cfg.ANON_KEY)
    : null;

  const $ = (id) => document.getElementById(id);
  const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
  }[c]));

  const state = {
    session: null,
    isAdmin: false,
    tables: { overrides: false, settings: false },
    books: [],
    poolSize: 0,
    autoRotate: true,
    today: wibToday()
  };

  function wibToday() {
    return new Date(Date.now() + 7 * 3600 * 1000).toISOString().slice(0, 10);
  }

  function toast(msg, kind = 'ok') {
    const el = $('toast');
    el.textContent = msg;
    el.className = 'toast rounded-lg px-4 py-3 text-sm shadow-lg ' +
      (kind === 'error' ? 'bg-red-600 text-white' : 'bg-emerald text-white');
    clearTimeout(toast._t);
    toast._t = setTimeout(() => el.classList.add('hidden'), 4200);
  }

  function showGate(msg = '') {
    $('gate-msg').textContent = msg;
    $('gate').classList.remove('hidden');
    $('dash').classList.add('hidden');
    $('sign-out').classList.remove('hidden');
  }

  function showDash() {
    $('gate').classList.add('hidden');
    $('dash').classList.remove('hidden');
    $('sign-out').classList.remove('hidden');
    $('signed-in-as').textContent = state.session?.user?.email || '';
    $('today-label').textContent = 'Today in WIB: ' + state.today;
    $('hotd-day').value = state.today;
  }

  async function checkAdmin() {
    if (!client || !state.session) return false;
    const { data, error } = await client.rpc('is_hadeeth_admin');
    if (!error && data === true) return true;
    // Before the migration lands the RPC is missing. The console remains
    // readable for configured operators; writes fail closed in RLS.
    if (error && /function|schema cache|does not exist/i.test(error.message)) {
      return (window.ADMIN_EMAILS || []).includes(state.session.user.email);
    }
    return false;
  }

  async function tableExists(name) {
    if (!client) return false;
    const { error } = await client.from(name).select('*', { head: true, count: 'exact' }).limit(1);
    return !error;
  }

  async function loadBooks() {
    if (!window.HadeethAPI) return;
    state.books = await window.HadeethAPI.getBooks() || [];
    state.poolSize = state.books.filter((b) => {
      const g = String(b.grade_summary || '');
      return g.includes('صحيح') && !g.includes('Varies') && Number(b.total_hadiths) > 0;
    }).length;
    const sel = $('hotd-book');
    sel.innerHTML = state.books.map((b) =>
      `<option value="${esc(b.id)}">${esc(b.title_id || b.title_en || b.id)} (${esc(b.id)})</option>`
    ).join('');
  }

  async function loadSettings() {
    if (!state.tables.settings) return;
    const { data } = await client.from('hotd_settings')
      .select('auto_rotate').eq('singleton', true).maybeSingle();
    if (data) state.autoRotate = !!data.auto_rotate;
    renderToggle();
  }

  function renderToggle() {
    const btn = $('toggle-auto');
    const knob = $('toggle-knob');
    btn.setAttribute('aria-checked', String(state.autoRotate));
    btn.style.background = state.autoRotate ? '#1B5E20' : '#9ca3af';
    knob.style.transform = state.autoRotate ? 'translateX(24px)' : 'translateX(0)';
  }

  async function loadStats() {
    $('stat-books').textContent = state.poolSize || '—';
    $('stat-auto').textContent = state.tables.settings ? (state.autoRotate ? 'On' : 'Off') : 'Local';
    if (!state.tables.overrides) return;
    const { count } = await client.from('hotd_overrides')
      .select('*', { head: true, count: 'exact' }).gte('day', state.today);
    $('stat-overrides').textContent = count == null ? '—' : count;
  }

  async function loadOverrides() {
    if (!state.tables.overrides) return;
    const { data, error } = await client.from('hotd_overrides')
      .select('day,book_id,hadith_number,note,created_at')
      .gte('day', state.today)
      .order('day', { ascending: true })
      .limit(60);
    const box = $('override-list');
    if (error) {
      box.innerHTML = `<div class="text-red-600 text-xs">${esc(error.message)}</div>`;
      return;
    }
    if (!data || !data.length) {
      box.innerHTML = '<div class="text-muted text-xs">No pinned days. Auto-rotation handles every day.</div>';
      return;
    }
    box.innerHTML = data.map((o) => `
      <div class="flex items-start justify-between gap-2 border-b border-black/5 dark:border-white/10 pb-2">
        <div>
          <div class="font-semibold">${esc(o.day)}</div>
          <div class="text-xs text-muted">${esc(o.book_id)} #${esc(o.hadith_number)}${o.note ? ' · ' + esc(o.note) : ''}</div>
        </div>
        <button class="text-xs text-red-600 hover:underline" data-remove-day="${esc(o.day)}">Remove</button>
      </div>`).join('');
  }

  async function loadResolution() {
    if (!state.tables.overrides) {
      $('today-resolution').textContent = 'Pins unavailable until the schema is applied. Auto-rotation still runs from CDN data.';
      return;
    }
    const { data, error } = await client.rpc('get_hotd_override', { p_day: state.today });
    if (error) {
      $('today-resolution').textContent = 'Could not read today’s pin: ' + error.message;
      return;
    }
    const row = data?.[0];
    $('today-resolution').textContent = row
      ? `Today: pinned to ${row.book_id} #${row.hadith_number} (${row.note || 'manual'}).`
      : `Today: auto rotation across ${state.poolSize} sahih-pure collections on CDN.`;
  }

  async function detectTables() {
    state.tables.overrides = await tableExists('hotd_overrides');
    state.tables.settings = await tableExists('hotd_settings');
    const missing = Object.entries(state.tables).filter(([, v]) => !v).map(([k]) => k);
    if (missing.length) {
      const el = $('setup-warning');
      el.classList.remove('hidden');
      el.innerHTML = `Pin storage not applied (${esc(missing.join(', '))}). Run <span class="mono">supabase/migrations/20261125000000_mobile_sync_and_hotd.sql</span> in the Supabase SQL editor.`;
    }
  }

  async function preview() {
    const book = $('hotd-book').value;
    const number = $('hotd-number').value.trim();
    const box = $('hotd-preview-box');
    box.classList.remove('hidden');
    if (!book || !number) { box.textContent = 'Pick a book and number first.'; return; }
    box.textContent = 'Loading…';
    const h = window.HadeethAPI
      ? await window.HadeethAPI.getHadith(book, number, 'lidwa').catch(() => null)
      : null;
    if (!h) {
      box.innerHTML = `Could not fetch <span class="mono">${esc(book)} #${esc(number)}</span>. <a class="underline" target="_blank" href="hadith.html?book=${encodeURIComponent(book)}&id=${encodeURIComponent(number)}">Open live page</a>.`;
      return;
    }
    box.innerHTML = `
      <div class="text-xs text-muted mb-1">${esc(book)} #${esc(h.hadith_number || number)} · ${esc(h.grade || 'no grade')}</div>
      <div dir="rtl" class="text-right text-xl leading-loose mb-2" style="font-family:Amiri,serif">${esc(h.text_ar_plain || h.text_ar || '')}</div>
      <div class="text-sm">${esc(h.text_id || h.text_en || '')}</div>
      <a class="underline text-xs" target="_blank" href="hadith.html?book=${encodeURIComponent(book)}&id=${encodeURIComponent(h.hadith_number || number)}">Open live page</a>`;
  }

  async function saveOverride(ev) {
    ev.preventDefault();
    if (!state.session || !state.isAdmin) return;
    const row = {
      day: $('hotd-day').value,
      book_id: $('hotd-book').value,
      hadith_number: $('hotd-number').value.trim(),
      note: $('hotd-note').value.trim(),
      set_by: state.session.user.id
    };
    if (!row.day || !row.book_id || !row.hadith_number) return;
    const { error } = await client.from('hotd_overrides').upsert(row, { onConflict: 'day' });
    if (error) { toast(error.message, 'error'); return; }
    toast(`Pinned ${row.book_id} #${row.hadith_number} for ${row.day}`);
    await loadOverrides();
    await loadStats();
    await loadResolution();
  }

  async function deleteOverride(day) {
    if (!day || !state.isAdmin) return;
    const { error } = await client.from('hotd_overrides').delete().eq('day', day);
    if (error) { toast(error.message, 'error'); return; }
    toast(`Removed pin for ${day}`);
    await loadOverrides();
    await loadStats();
    await loadResolution();
  }

  async function toggleAuto() {
    if (!state.isAdmin || !state.tables.settings) {
      toast('Auto-rotation is client-side until the schema is applied.', 'error');
      return;
    }
    state.autoRotate = !state.autoRotate;
    renderToggle();
    const { error } = await client.from('hotd_settings')
      .update({ auto_rotate: state.autoRotate, updated_at: new Date().toISOString() })
      .eq('singleton', true);
    if (error) { toast(error.message, 'error'); return; }
    toast('Auto-rotation ' + (state.autoRotate ? 'enabled' : 'disabled'));
    await loadStats();
    await loadResolution();
  }

  async function signOut() {
    if (client) await client.auth.signOut();
    window.location.href = 'login.html';
  }

  async function boot() {
    if (!client) {
      showGate('Supabase client failed to load. Check network and js/config.js.');
      return;
    }
    $('google-login').addEventListener('click', async () => {
      const { error } = await client.auth.signInWithOAuth({
        provider: 'google',
        options: { redirectTo: window.location.origin + '/login.html?redirect=admin' }
      });
      if (error) $('gate-msg').textContent = error.message;
    });
    $('password-form').addEventListener('submit', async (ev) => {
      ev.preventDefault();
      const { error } = await client.auth.signInWithPassword({
        email: $('email').value.trim(), password: $('password').value
      });
      if (error) $('gate-msg').textContent = error.message;
      else await afterSession();
    });
    $('sign-out').addEventListener('click', signOut);
    $('hotd-form').addEventListener('submit', saveOverride);
    $('hotd-preview').addEventListener('click', preview);
    $('hotd-delete').addEventListener('click', () => deleteOverride($('hotd-day').value));
    $('toggle-auto').addEventListener('click', toggleAuto);
    $('override-list').addEventListener('click', (ev) => {
      const day = ev.target?.getAttribute?.('data-remove-day');
      if (day) deleteOverride(day);
    });
    client.auth.onAuthStateChange((_event, session) => { if (!session) showGate(); });
    await afterSession();
  }

  async function afterSession() {
    const { data: { session } } = await client.auth.getSession();
    state.session = session;
    if (!session) { showGate(); return; }
    state.isAdmin = await checkAdmin();
    if (!state.isAdmin) {
      showGate('This account is not on the admin allowlist.');
      return;
    }
    showDash();
    await detectTables();
    await loadSettings();
    await loadBooks();
    await loadStats();
    await loadOverrides();
    await loadResolution();
  }

  document.addEventListener('DOMContentLoaded', boot);
})();

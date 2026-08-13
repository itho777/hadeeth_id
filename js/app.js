/**
 * HADEETH.ID — Dynamic App Logic v20260807_8
 * Real-time Supabase RPC search integration, dynamic CDN book/hadith loading, and interactive UI.
 * Bilingual EN/ID language switcher with persistent localStorage state.
 */

function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

// ============================================================
// LANGUAGE SYSTEM
// ============================================================
const UI_I18N = {
  en: {
    nav_books: "Books",
    nav_scholars: "Scholars",
    nav_admin: "Admin",
    hero_title: "Discover Authentic Sources",
    hero_subtitle: "Search through thousands of authenticated Ahadith from the major collections, with detailed chains of narration and scholarly grading.",
    search_placeholder: "Scholarly Search (e.g., 'Intention', 'Sahih Bukhari 1')",
    search_scope_all: "All Books",
    search_mode_semantic: "Semantic (Cloudflare AI)",
    search_mode_keyword: "Keyword (Algolia)",
    search_btn: "Search",
    continue_reading: "CONTINUE READING",
    kutub_tisah_title: "Kutubut Tis'ah",
    view_all_collections: "View All Collections →",
    hadith_of_day_title: "Hadith of the Day",
    read_hadith: "Read Hadith →",
    inspect_chain: "Inspect Chain →",
    digital_library: "Digital Library",
    major_collections_title: "Major Hadith Collections",
    major_collections_sub: "Browse the nine canonical collections (Kutubut Tis'ah) of Hadith literature.",
    filter_kitab_placeholder: "Filter Kitab by title or topic...",
    loading_kitab: "Loading Kitab index...",
    search_within_chapter: "Search within chapter or type keyword...",
    scope_label: "Scope:",
    scope_this_chapter: "This Chapter",
    scope_global: "Global (All Books)",
    translation_label: "Translation:",
    trans_id: "Bahasa Indonesia",
    trans_en: "English",
    show_per_page: "Show per page:",
    prev: "Previous",
    next: "Next",
    scholarly_commentary: "Scholarly Commentary (Sharh)",
    chain_of_narrators: "Chain of Narration (Sanad)",
    full_sanad_graph: "View Full Interactive Sanad Graph →",
    role_sahabi: "Sahabi (Companion)",
    footer_text: "© 2026 HADEETH.ID - Digital Manuscript Preservation"
  },
  id: {
    nav_books: "Kitab",
    nav_scholars: "Perawi & Ulama",
    nav_admin: "Admin",
    hero_title: "Telusuri Sumber-sumber Shahih",
    hero_subtitle: "Cari ribuan hadits shahih dari kitab-kitab utama, lengkap dengan silsilah sanad dan derajat keabsahan ulama.",
    search_placeholder: "Cari Hadits (contoh: 'Niat', 'Shahih Bukhari 1')",
    search_scope_all: "Semua Kitab",
    search_mode_semantic: "Semantik (Cloudflare AI)",
    search_mode_keyword: "Kata Kunci (Algolia)",
    search_btn: "Cari",
    continue_reading: "LANJUTKAN MEMBACA",
    kutub_tisah_title: "Kutubut Tis'ah (9 Kitab Utama)",
    view_all_collections: "Lihat Semua Kitab →",
    hadith_of_day_title: "Hadits Hari Ini",
    read_hadith: "Baca Hadits →",
    inspect_chain: "Lihat Sanad →",
    digital_library: "Perpustakaan Digital",
    major_collections_title: "Koleksi Kitab Hadits Utama",
    major_collections_sub: "Jelajahi sembilan kitab utama (Kutubut Tis'ah) dalam literatur hadits.",
    filter_kitab_placeholder: "Filter Kitab berdasarkan judul atau topik...",
    loading_kitab: "Memuat indeks Kitab...",
    search_within_chapter: "Cari dalam bab ini atau ketik kata kunci...",
    scope_label: "Cakupan:",
    scope_this_chapter: "Kitab Ini",
    scope_global: "Global (Semua Kitab)",
    translation_label: "Terjemahan:",
    trans_id: "Bahasa Indonesia",
    trans_en: "Bahasa Inggris",
    show_per_page: "Tampilkan:",
    prev: "Sebelumnya",
    next: "Selanjutnya",
    scholarly_commentary: "Syarah Hadits",
    chain_of_narrators: "Rantai Perawi (Sanad)",
    full_sanad_graph: "Lihat Grafik Interaktif Sanad Lengkap →",
    role_sahabi: "Sahabat",
    footer_text: "© 2026 HADEETH.ID - Pelestarian Manuskrip Digital"
  }
};

const LangSystem = {
  SUPPORTED: ['en', 'id'],
  get() { return localStorage.getItem('hadeeth_lang') || 'id'; },
  isIdMode() {
    return this.get() === 'id';
  },
  set(lang) {
    if (!this.SUPPORTED.includes(lang)) return;
    localStorage.setItem('hadeeth_lang', lang);
    this.apply(lang);
    window.dispatchEvent(new CustomEvent('hadeeth_lang_change', { detail: { lang } }));
  },
  translateUI(lang) {
    const targetLang = (lang === 'id') ? 'id' : 'en';
    const dict = UI_I18N[targetLang] || UI_I18N.en;

    document.querySelectorAll('[data-i18n]').forEach(el => {
      const key = el.dataset.i18n;
      if (dict[key]) {
        if (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA') {
          if (el.hasAttribute('placeholder')) el.placeholder = dict[key];
        } else {
          el.innerText = dict[key];
        }
      }
    });
  },
  apply(lang) {
    const current = this.SUPPORTED.includes(lang) ? lang : 'id';
    document.documentElement.setAttribute('data-lang', current);
    // Show/hide translation containers
    document.querySelectorAll('[data-lang-en]').forEach(el => {
      el.style.display = (current === 'en') ? '' : 'none';
    });
    document.querySelectorAll('[data-lang-id]').forEach(el => {
      el.style.display = (current === 'id') ? '' : 'none';
    });
    // Translate static UI elements
    this.translateUI(current);
    // Update active button state
    document.querySelectorAll('[data-lang-btn]').forEach(btn => {
      btn.classList.toggle('lang-btn-active', btn.dataset.langBtn === current);
    });
  },
  init() {
    const saved = this.get();
    this.apply(saved);
    document.querySelectorAll('[data-lang-btn]').forEach(btn => {
      btn.addEventListener('click', () => this.set(btn.dataset.langBtn));
    });
  }
};

window.LangSystem = LangSystem;

// ============================================================
// BOOK DATASET CONFIGURATIONS
// Maps each book to its available datasets with honest source labels.
// All datasets are served as linked systems (gaps filled with noted sources).
// ============================================================
const BOOK_DATASETS = {
  // Books with all 3 datasets (Kutub Tis'ah + Nawawi)
  bukhari: [
    { id: 'primary',
      label: 'Darussalam / fawazahmed0', labelId: 'Darussalam / fawazahmed0',
      sources: 'Arabic + EN: fawazahmed0 CDN · ID: Lidwa/Irsyad (matched by number — not native to fawazahmed0)',
      sourcesId: 'Arab + EN: fawazahmed0 CDN · ID: Lidwa/Irsyad (dicocokkan berdasarkan nomor — bukan bawaan fawazahmed0)',
      note: null, noteId: null },
    { id: 'native_ahmedbaset',
      label: 'AhmedBaset', labelId: 'AhmedBaset',
      sources: 'Arabic + EN: AhmedBaset native (7,277 hadiths, 97 kitab)',
      sourcesId: 'Arab + EN: AhmedBaset native (7.277 hadits, 97 kitab)',
      note: 'ID translation sourced from Lidwa/Irsyad, matched by hadith number — may not align perfectly with AhmedBaset narration variant', noteId: 'Terjemahan ID bersumber dari Lidwa/Irsyad, dicocokkan berdasarkan nomor — mungkin tidak sesuai sempurna dengan varian riwayat AhmedBaset' },
    { id: 'native_lidwa',
      label: 'Lidwa / Irsyad', labelId: 'Lidwa / Irsyad',
      sources: 'AR/EN/ID/UR/FR: Lidwa SQL (7,589 entries, 98 kitab groupings)',
      sourcesId: 'AR/EN/ID/UR/FR: SQL Lidwa (7.589 entri, 98 pengelompokan kitab)',
      note: null, noteId: null }
  ],
  muslim: [
    { id: 'primary',
      label: 'Darussalam / fawazahmed0', labelId: 'Darussalam / fawazahmed0',
      sources: 'Arabic + EN: fawazahmed0 CDN · ID: Lidwa/Irsyad (matched by number — not native to fawazahmed0)',
      sourcesId: 'Arab + EN: fawazahmed0 CDN · ID: Lidwa/Irsyad (dicocokkan berdasarkan nomor — bukan bawaan fawazahmed0)',
      note: 'Last ~112 hadiths: known upstream duplication in Arabic text', noteId: '~112 hadits terakhir: duplikasi teks Arab dari sumber upstream' },
    { id: 'native_ahmedbaset',
      label: 'AhmedBaset', labelId: 'AhmedBaset',
      sources: 'Arabic + EN: AhmedBaset native (7,459 hadiths, 56 kitab)',
      sourcesId: 'Arab + EN: AhmedBaset native (7.459 hadits, 56 kitab)',
      note: 'ID translation sourced from Lidwa/Irsyad, matched by hadith number — may not align perfectly with AhmedBaset narration variant', noteId: 'Terjemahan ID bersumber dari Lidwa/Irsyad, dicocokkan berdasarkan nomor — mungkin tidak sesuai sempurna dengan varian riwayat AhmedBaset' },
    { id: 'native_lidwa',
      label: 'Lidwa / Irsyad', labelId: 'Lidwa / Irsyad',
      sources: 'AR/EN/ID: Lidwa SQL — 5,362 entries (groups variant narrations)',
      sourcesId: 'AR/EN/ID: SQL Lidwa — 5.362 entri (mengelompokkan variasi riwayat)',
      note: 'Darussalam numbers 5,363–7,563 have no Lidwa equivalent', noteId: 'Nomor Darussalam 5.363–7.563 tidak memiliki padanan Lidwa' }
  ],
  abudawud: [
    { id: 'primary',
      label: 'Darussalam / fawazahmed0', labelId: 'Darussalam / fawazahmed0',
      sources: 'Arabic + EN: fawazahmed0 CDN · ID: Lidwa/Irsyad (matched by number — not native to fawazahmed0)',
      sourcesId: 'Arab + EN: fawazahmed0 CDN · ID: Lidwa/Irsyad (dicocokkan berdasarkan nomor — bukan bawaan fawazahmed0)',
      note: null, noteId: null },
    { id: 'native_ahmedbaset',
      label: 'AhmedBaset', labelId: 'AhmedBaset',
      sources: 'Arabic + EN: AhmedBaset native (5,274 hadiths, 43 kitab)',
      sourcesId: 'Arab + EN: AhmedBaset native (5.274 hadits, 43 kitab)',
      note: 'ID translation sourced from Lidwa/Irsyad, matched by hadith number — may not align perfectly with AhmedBaset narration variant', noteId: 'Terjemahan ID bersumber dari Lidwa/Irsyad, dicocokkan berdasarkan nomor — mungkin tidak sesuai sempurna dengan varian riwayat AhmedBaset' },
    { id: 'native_lidwa',
      label: 'Lidwa / Irsyad', labelId: 'Lidwa / Irsyad',
      sources: 'AR/EN/ID: Lidwa SQL (5,274 entries, 43 kitab)',
      sourcesId: 'AR/EN/ID: SQL Lidwa (5.274 entri, 43 kitab)',
      note: null, noteId: null }
  ],
  tirmidhi: [
    { id: 'primary',
      label: 'Darussalam / fawazahmed0', labelId: 'Darussalam / fawazahmed0',
      sources: 'Arabic + EN: fawazahmed0 CDN · ID: Lidwa/Irsyad (matched by number — not native to fawazahmed0)',
      sourcesId: 'Arab + EN: fawazahmed0 CDN · ID: Lidwa/Irsyad (dicocokkan berdasarkan nomor — bukan bawaan fawazahmed0)',
      note: null, noteId: null },
    { id: 'native_ahmedbaset',
      label: 'AhmedBaset', labelId: 'AhmedBaset',
      sources: 'Arabic + EN: AhmedBaset native (3,956 hadiths, 49 kitab)',
      sourcesId: 'Arab + EN: AhmedBaset native (3.956 hadits, 49 kitab)',
      note: 'ID translation sourced from Lidwa/Irsyad, matched by hadith number — may not align perfectly with AhmedBaset narration variant', noteId: 'Terjemahan ID bersumber dari Lidwa/Irsyad, dicocokkan berdasarkan nomor — mungkin tidak sesuai sempurna dengan varian riwayat AhmedBaset' },
    { id: 'native_lidwa',
      label: 'Lidwa / Irsyad', labelId: 'Lidwa / Irsyad',
      sources: 'AR/EN/ID: Lidwa SQL (3,956 entries, 49 kitab)',
      sourcesId: 'AR/EN/ID: SQL Lidwa (3.956 entri, 49 kitab)',
      note: null, noteId: null }
  ],
  nasai: [
    { id: 'primary',
      label: 'Darussalam / fawazahmed0', labelId: 'Darussalam / fawazahmed0',
      sources: 'Arabic + EN: fawazahmed0 CDN · ID: Lidwa/Irsyad (matched by number — not native to fawazahmed0)',
      sourcesId: 'Arab + EN: fawazahmed0 CDN · ID: Lidwa/Irsyad (dicocokkan berdasarkan nomor — bukan bawaan fawazahmed0)',
      note: null, noteId: null },
    { id: 'native_ahmedbaset',
      label: 'AhmedBaset', labelId: 'AhmedBaset',
      sources: 'Arabic + EN: AhmedBaset native (5,758 hadiths, 51 kitab)',
      sourcesId: 'Arab + EN: AhmedBaset native (5.758 hadits, 51 kitab)',
      note: 'ID translation sourced from Lidwa/Irsyad, matched by hadith number — may not align perfectly with AhmedBaset narration variant', noteId: 'Terjemahan ID bersumber dari Lidwa/Irsyad, dicocokkan berdasarkan nomor — mungkin tidak sesuai sempurna dengan varian riwayat AhmedBaset' },
    { id: 'native_lidwa',
      label: 'Lidwa / Irsyad', labelId: 'Lidwa / Irsyad',
      sources: 'AR/EN/ID: Lidwa SQL (5,758 entries, 51 kitab)',
      sourcesId: 'AR/EN/ID: SQL Lidwa (5.758 entri, 51 kitab)',
      note: null, noteId: null }
  ],
  ibnmajah: [
    { id: 'primary',
      label: 'Darussalam / fawazahmed0', labelId: 'Darussalam / fawazahmed0',
      sources: 'Arabic + EN: fawazahmed0 CDN · ID: Lidwa/Irsyad (matched by number — not native to fawazahmed0)',
      sourcesId: 'Arab + EN: fawazahmed0 CDN · ID: Lidwa/Irsyad (dicocokkan berdasarkan nomor — bukan bawaan fawazahmed0)',
      note: null, noteId: null },
    { id: 'native_ahmedbaset',
      label: 'AhmedBaset', labelId: 'AhmedBaset',
      sources: 'Arabic + EN: AhmedBaset native (4,341 hadiths, 37 kitab)',
      sourcesId: 'Arab + EN: AhmedBaset native (4.341 hadits, 37 kitab)',
      note: 'ID translation sourced from Lidwa/Irsyad, matched by hadith number — may not align perfectly with AhmedBaset narration variant', noteId: 'Terjemahan ID bersumber dari Lidwa/Irsyad, dicocokkan berdasarkan nomor — mungkin tidak sesuai sempurna dengan varian riwayat AhmedBaset' },
    { id: 'native_lidwa',
      label: 'Lidwa / Irsyad', labelId: 'Lidwa / Irsyad',
      sources: 'AR/EN/ID: Lidwa SQL (4,341 entries, 37 kitab)',
      sourcesId: 'AR/EN/ID: SQL Lidwa (4.341 entri, 37 kitab)',
      note: null, noteId: null }
  ],
  malik: [
    { id: 'primary',
      label: 'Darussalam / fawazahmed0', labelId: 'Darussalam / fawazahmed0',
      sources: 'Arabic + EN: fawazahmed0 CDN · ID: Lidwa/Irsyad (matched by number — not native to fawazahmed0)',
      sourcesId: 'Arab + EN: fawazahmed0 CDN · ID: Lidwa/Irsyad (dicocokkan berdasarkan nomor — bukan bawaan fawazahmed0)',
      note: null, noteId: null },
    { id: 'native_ahmedbaset',
      label: 'AhmedBaset', labelId: 'AhmedBaset',
      sources: 'Arabic + EN: AhmedBaset native (1,858 hadiths, 61 kitab)',
      sourcesId: 'Arab + EN: AhmedBaset native (1.858 hadits, 61 kitab)',
      note: 'ID translation sourced from Lidwa/Irsyad, matched by hadith number — may not align perfectly with AhmedBaset narration variant', noteId: 'Terjemahan ID bersumber dari Lidwa/Irsyad, dicocokkan berdasarkan nomor — mungkin tidak sesuai sempurna dengan varian riwayat AhmedBaset' },
    { id: 'native_lidwa',
      label: 'Lidwa / Irsyad', labelId: 'Lidwa / Irsyad',
      sources: 'AR/EN/ID: Lidwa SQL (1,720 entries — some hadiths grouped)',
      sourcesId: 'AR/EN/ID: SQL Lidwa (1.720 entri — beberapa hadits dikelompokkan)',
      note: null, noteId: null }
  ],
  darimi: [
    { id: 'primary',
      label: 'Darussalam / fawazahmed0', labelId: 'Darussalam / fawazahmed0',
      sources: 'Arabic + EN: fawazahmed0 CDN · ID: Lidwa/Irsyad (matched by number — not native to fawazahmed0)',
      sourcesId: 'Arab + EN: fawazahmed0 CDN · ID: Lidwa/Irsyad (dicocokkan berdasarkan nomor — bukan bawaan fawazahmed0)',
      note: null, noteId: null },
    { id: 'native_ahmedbaset',
      label: 'AhmedBaset', labelId: 'AhmedBaset',
      sources: 'Arabic + EN: AhmedBaset native (3,367 hadiths, 24 kitab)',
      sourcesId: 'Arab + EN: AhmedBaset native (3.367 hadits, 24 kitab)',
      note: 'ID translation sourced from Lidwa/Irsyad, matched by hadith number — may not align perfectly with AhmedBaset narration variant', noteId: 'Terjemahan ID bersumber dari Lidwa/Irsyad, dicocokkan berdasarkan nomor — mungkin tidak sesuai sempurna dengan varian riwayat AhmedBaset' },
    { id: 'native_lidwa',
      label: 'Lidwa / Irsyad', labelId: 'Lidwa / Irsyad',
      sources: 'AR/EN/ID: Lidwa SQL (3,367 entries, 24 kitab)',
      sourcesId: 'AR/EN/ID: SQL Lidwa (3.367 entri, 24 kitab)',
      note: null, noteId: null }
  ],
  ahmad: [
    { id: 'primary',
      label: 'Darussalam / fawazahmed0', labelId: 'Darussalam / fawazahmed0',
      sources: 'Arabic + EN: fawazahmed0 CDN · ID: Lidwa/Irsyad (matched by number — not native to fawazahmed0)',
      sourcesId: 'Arab + EN: fawazahmed0 CDN · ID: Lidwa/Irsyad (dicocokkan berdasarkan nomor — bukan bawaan fawazahmed0)',
      note: null, noteId: null },
    { id: 'native_ahmedbaset',
      label: 'AhmedBaset', labelId: 'AhmedBaset',
      sources: 'Arabic + EN: AhmedBaset native (27,647 hadiths, 90 musnad sections)',
      sourcesId: 'Arab + EN: AhmedBaset native (27.647 hadits, 90 bagian musnad)',
      note: 'ID translation sourced from Lidwa/Irsyad, matched by hadith number — may not align perfectly with AhmedBaset narration variant', noteId: 'Terjemahan ID bersumber dari Lidwa/Irsyad, dicocokkan berdasarkan nomor — mungkin tidak sesuai sempurna dengan varian riwayat AhmedBaset' },
    { id: 'native_lidwa',
      label: 'Lidwa / Irsyad', labelId: 'Lidwa / Irsyad',
      sources: 'AR/EN/ID: Lidwa SQL (27,519 entries, musnad arrangement)',
      sourcesId: 'AR/EN/ID: SQL Lidwa (27.519 entri, susunan musnad)',
      note: null, noteId: null }
  ],
  nawawi: [
    { id: 'primary',
      label: 'Darussalam / fawazahmed0', labelId: 'Darussalam / fawazahmed0',
      sources: 'Arabic + EN: fawazahmed0 CDN · ID: Lidwa/Irsyad (42 hadiths, matched by number — not native to fawazahmed0)',
      sourcesId: 'Arab + EN: fawazahmed0 CDN · ID: Lidwa/Irsyad (42 hadits, dicocokkan berdasarkan nomor — bukan bawaan fawazahmed0)',
      note: null, noteId: null },
    { id: 'native_lidwa',
      label: 'Lidwa / Irsyad', labelId: 'Lidwa / Irsyad',
      sources: 'AR/EN/ID: Lidwa SQL (42 entries)',
      sourcesId: 'AR/EN/ID: SQL Lidwa (42 entri)',
      note: null, noteId: null }
  ]
};

/**
 * Switch to a different dataset version and reload the page.
 * Strips the `dataset` URL param so localStorage controls the active dataset
 * (prevents the URL-baked param from overriding the user's explicit choice).
 * @param {string} datasetId - 'primary' | 'native_ahmedbaset' | 'native_lidwa'
 */
window.__switchDataset = function(datasetId) {
  localStorage.setItem('dataset_version', datasetId);
  // Remove ?dataset param from URL so localStorage wins on reload
  const url = new URL(location.href);
  url.searchParams.delete('dataset');
  location.href = url.toString();
};

/**
 * Render the dataset source banner inside a given container element.
 * Shows which dataset is active as a highlighted pill, others as switch buttons.
 * Notes data sources and any gap-filling transparently.
 * @param {string} bookId - The book identifier
 * @param {string} containerId - ID of the DOM element to render into
 * @param {string} [forceDataset] - Override localStorage (used on hadith-list page via URL param)
 */
function renderDatasetBanner(bookId, containerId, forceDataset) {
  const el = document.getElementById(containerId);
  if (!el) return;

  const dsConfig = BOOK_DATASETS[bookId];
  if (!dsConfig || dsConfig.length <= 1) {
    // No switcher needed for books with only one dataset
    el.style.display = 'none';
    return;
  }

  const currentDs = forceDataset || localStorage.getItem('dataset_version') || 'primary';
  const isId = window.LangSystem && window.LangSystem.isIdMode();

  // Validate: if the selected dataset doesn't exist for this book, fall back to primary
  const activeDs = dsConfig.find(d => d.id === currentDs) || dsConfig[0];
  const activeLabel = isId ? activeDs.labelId : activeDs.label;
  const activeSources = isId ? activeDs.sourcesId : activeDs.sources;
  const activeNote = isId ? activeDs.noteId : activeDs.note;

  const pillsHtml = dsConfig.map(ds => {
    const label = isId ? ds.labelId : ds.label;
    if (ds.id === activeDs.id) {
      return `<span class="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-bold bg-secondary dark:bg-[#10b981] text-white dark:text-black select-none">
        <span class="material-symbols-outlined text-[13px]" style="font-size:13px">check_circle</span>${escapeHtml(label)}
      </span>`;
    }
    return `<button
        onclick="window.__switchDataset('${ds.id}')"
        class="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-semibold border border-outline-variant/40 dark:border-[#334155] text-on-surface-variant dark:text-gray-400 hover:border-secondary dark:hover:border-[#10b981] hover:text-secondary dark:hover:text-[#10b981] bg-surface-container-low dark:bg-[#0f172a] transition-all cursor-pointer">
        <span class="material-symbols-outlined text-[13px]" style="font-size:13px">swap_horiz</span>${escapeHtml(label)}
      </button>`;
  }).join('');

  el.innerHTML = `
    <div class="flex flex-col sm:flex-row sm:items-start gap-3 bg-surface dark:bg-[#1e293b] border border-outline-variant/20 dark:border-[#334155] rounded-xl px-4 py-3 shadow-sm">
      <div class="flex items-center gap-1.5 shrink-0 pt-0.5">
        <span class="material-symbols-outlined text-secondary dark:text-[#10b981]" style="font-size:16px">database</span>
        <span class="text-[11px] font-bold text-on-surface-variant dark:text-gray-400 uppercase tracking-wide whitespace-nowrap">${isId ? 'Sumber Data:' : 'Dataset:'}</span>
      </div>
      <div class="flex flex-col gap-2 flex-1 min-w-0">
        <div class="flex flex-wrap gap-2 items-center">
          ${pillsHtml}
        </div>
        <div class="text-[11px] text-outline dark:text-gray-500 leading-snug">
          <span class="font-semibold text-on-surface-variant dark:text-gray-400">${escapeHtml(activeSources)}</span>
          ${activeNote ? `<span class="block mt-0.5 text-secondary/80 dark:text-[#10b981]/70">⚠ ${escapeHtml(activeNote)}</span>` : ''}
        </div>
      </div>
    </div>
  `;
}

document.addEventListener('DOMContentLoaded', () => {

  // Init language system first
  LangSystem.init();

  // --- Mobile Menu Toggle ---
  const menuBtn = document.getElementById('mobile-menu-btn');
  const mobileMenu = document.getElementById('mobile-menu');
  if (menuBtn && mobileMenu) {
    menuBtn.addEventListener('click', () => {
      mobileMenu.classList.toggle('open');
      const icon = menuBtn.querySelector('[data-menu-icon]');
      if (icon) icon.textContent = mobileMenu.classList.contains('open') ? 'close' : 'menu';
    });
  }

  // --- Mark Active Nav Link ---
  const currentPage = location.pathname.split('/').pop() || 'index.html';
  document.querySelectorAll('[data-nav-page]').forEach(link => {
    if (link.dataset.navPage === currentPage) {
      link.classList.add('nav-link-active');
    }
  });

  // --- Dataset Version Switcher (legacy select, kept for back-compat) ---
  const versionSelect = document.getElementById('dataset-version');
  if (versionSelect) {
    const currentVersion = localStorage.getItem('dataset_version') || 'primary';
    versionSelect.value = currentVersion;
    versionSelect.addEventListener('change', (e) => {
      localStorage.setItem('dataset_version', e.target.value);
      location.reload();
    });
  }

  // --- Initialize Books Rendering ---
  const isIndex = location.pathname.endsWith('index.html') || location.pathname === '/';
  const isBooks = location.pathname.endsWith('books.html');

  if (isIndex || isBooks) {
    window.HadeethAPI.getBooks().then(books => {
      if (isIndex) {
        const grid = document.getElementById('tisah-grid');
        if (grid) renderBookCards(books.slice(0, 9), grid);
      }
      if (isBooks) {
        const sittahGrid = document.getElementById('sittah-grid');
        const tisahGrid = document.getElementById('tisah-grid-books');
        const secondaryGrid = document.getElementById('secondary-grid');
        
        if (sittahGrid) renderBookCards(books.slice(0, 6), sittahGrid);
        if (tisahGrid) renderBookCards(books.slice(6, 9), tisahGrid);
        if (secondaryGrid) renderBookCards(books.slice(9, 17), secondaryGrid);
      }
    });
  }

  function renderBookCards(books, container) {
    container.innerHTML = books.map(book => {
      let dataType = 'other';
      if (['bukhari', 'muslim', 'tirmidhi'].includes(book.id)) dataType = 'jami';
      else if (['abudawud', 'nasai', 'ibnmajah', 'darimi'].includes(book.id)) dataType = 'sunan';
      else if (book.id === 'ahmad') dataType = 'musnad';
      else if (book.id === 'malik') dataType = 'mushannaf';
      else if (['nawawi', 'qudsi', 'shah', 'adab', 'bulugh', 'mishkat', 'riyad', 'shamail'].includes(book.id)) dataType = 'jawami';
      
      const typeLabels = {
        'jami': "Jami'",
        'sunan': "Sunan",
        'musnad': "Musnad",
        'mushannaf': "Mushannaf",
        'jawami': "Jawami'",
        'other': "Kitab"
      };
      const badgeText = typeLabels[dataType] || "Kitab";

      const bgImage = "https://lh3.googleusercontent.com/aida-public/AB6AXuBzqnq_A--Wp1V13r_f7R92bOejF-hct-hQfLCt4I-ftXrUjutMDxGksjJBngltuV29M_PS6AvdazjuLJlDmOd7Nc0ym-BdVhIEfg1h3CN3e8NDd2QVp_B8_BNT7AxfGGUpKlbIo9jptiJBClLqpzNbUikCMt5UMZV8IDKrIv4aNVNiQZzmN3Udc92x21MwHEjAngKlR9CIPHct5ipG9Yv4oAGsvvTUSVRu9IgTeTZEreNg2ilBcz2ztw";
      
      return `
        <a href="kitab.html?book=${book.id}" data-type="${dataType}" class="book-card bg-surface dark:bg-[#1e293b] border border-outline-variant/20 dark:border-[#334155] rounded-xl overflow-hidden hover:shadow-md transition-all flex flex-col cursor-pointer group card-lift">
          <div class="h-32 w-full bg-cover bg-center border-b border-outline-variant/20 dark:border-[#334155] relative"
               style="background-image:url('${bgImage}')">
            <div class="absolute top-2 left-2 bg-blue-700 text-white px-2 py-0.5 rounded font-label-sm text-[10px] uppercase tracking-wider font-bold">${badgeText}</div>
          </div>
          <div class="p-4 flex flex-col gap-1 flex-grow">
            <div class="flex justify-between items-start">
              <h3 class="font-body-md text-body-md font-bold text-primary dark:text-white group-hover:text-secondary dark:group-hover:text-[#10b981] transition-colors">${book.title_en}</h3>
              <span class="font-arabic-body text-lg text-secondary dark:text-[#10b981]" dir="rtl">${book.title_ar}</span>
            </div>
            <p class="text-label-sm font-label-sm text-on-surface-variant dark:text-gray-400">${book.author_en}</p>
            <div class="mt-3 flex items-center justify-between text-label-sm font-label-sm text-outline dark:text-gray-500 border-t border-outline-variant/10 dark:border-[#334155] pt-2 mt-auto">
              <span data-lang-en>${book.total_hadiths.toLocaleString()} Ahadith</span>
              <span data-lang-id style="display:none">${book.total_hadiths.toLocaleString()} Hadits</span>
              <span class="text-secondary dark:text-[#10b981] group-hover:underline cursor-pointer">Explore →</span>
            </div>
          </div>
        </a>
      `;
    }).join('');
    LangSystem.updateDOM();
  }

  // --- Copy & Social Media Share Hadith Handler ---
  document.addEventListener('click', async (e) => {
    const copyBtn = e.target.closest('[data-copy-hadith], [data-copy-share-btn], .btn-copy-share');
    if (!copyBtn) return;

    e.preventDefault();
    e.stopPropagation();

    const isIdMode = (window.LangSystem && window.LangSystem.isIdMode());
    let shareText = '';
    let targetUrl = copyBtn.dataset.shareUrl || window.location.href;

    const cardBox = copyBtn.closest('.bg-surface, .p-6, .p-5, div');
    const title = copyBtn.dataset.hadithTitle || document.querySelector('[data-hadith-title]')?.innerText || cardBox?.querySelector('h3, span.bg-primary')?.innerText || 'hadeeth.id';
    const ar = copyBtn.dataset.copyHadithAr || document.querySelector('[data-arabic-text]')?.innerText || cardBox?.querySelector('p[dir="rtl"]')?.innerText || '';
    const idBody = copyBtn.dataset.copyHadithTextId || document.querySelector('[data-indonesian-text]')?.innerText || cardBox?.querySelector('p.text-sm')?.innerText || '';
    const enBody = copyBtn.dataset.copyHadithTextEn || document.querySelector('[data-english-text]')?.innerText || cardBox?.querySelector('p.text-sm')?.innerText || idBody;
    
    const body = isIdMode ? (idBody || enBody) : (enBody || idBody);
    const transLabel = isIdMode ? 'Terjemahan Indonesia:' : 'English Translation:';
    const rawiElem = document.querySelector('[data-hadith-rawi]');
    const rawi = rawiElem ? rawiElem.innerText.replace(/^(Narrator|Perawi):\s*/i, '') : '';
    const rawiLabel = isIdMode ? 'Perawi:' : 'Narrator:';
    const linkTagline = isIdMode ? 'Baca & Telusuri Sanad Selengkapnya di hadeeth.id:' : 'Read & Inspect Sanad Chain on hadeeth.id:';

    shareText = `[${title}]\n\n${ar ? ar + '\n\n' : ''}${transLabel}\n"${body}"\n\n${rawi ? `${rawiLabel} ${rawi}\n\n` : ''}${linkTagline}\n${targetUrl}`;

    let success = false;

    if (navigator.share) {
      try {
        await navigator.share({
          title: 'hadeeth.id',
          text: shareText,
          url: targetUrl
        });
        success = true;
      } catch (err) {
        // Fallback to clipboard if native share sheet dismissed/unsupported
      }
    }

    if (!success) {
      try {
        if (navigator.clipboard && navigator.clipboard.writeText) {
          await navigator.clipboard.writeText(shareText);
        } else {
          const textarea = document.createElement('textarea');
          textarea.value = shareText;
          textarea.style.position = 'fixed';
          textarea.style.opacity = '0';
          document.body.appendChild(textarea);
          textarea.focus();
          textarea.select();
          document.execCommand('copy');
          document.body.removeChild(textarea);
        }
        
        const originalHtml = copyBtn.innerHTML;
        copyBtn.innerHTML = `<span class="material-symbols-outlined text-[14px]">check</span> ${isIdMode ? 'Tersalin!' : 'Copied!'}`;
        setTimeout(() => copyBtn.innerHTML = originalHtml, 2200);
      } catch (err) {
        console.warn('Clipboard write error:', err);
      }
    }
  });

  // --- Real-time Search Handler ---
  initSearch();

  if (document.getElementById('last-read-card')) {
    loadHomeLastRead();
  }
  if (document.getElementById('hotd-container')) {
    loadHOTD();
  }
  if (document.getElementById('books-grid')) {
    loadBooksGrid();
  }
  if (document.getElementById('hadith-detail-container')) {
    loadHadithDetail();
  }
  if (document.getElementById('chapters-list-container')) {
    loadChaptersList();
  }
  if (document.getElementById('hadith-cards-container')) {
    loadHadithList();
  }
  if (document.getElementById('sanad-nodes-container')) {
    loadSanadChain();
  }

});

/**
 * Load Last Read Hadith from localStorage on Home Page
 */
function loadHomeLastRead() {
  const lastRead = LastReadTracker.get();
  const card = document.getElementById('last-read-card');
  const bookElem = document.getElementById('last-read-book');
  const titleElem = document.getElementById('last-read-title');
  const section = document.getElementById('last-read-section');

  if (!lastRead) {
    // Hide the widget if no history yet
    if (section) section.style.display = 'none';
    return;
  }

  if (section) section.style.display = '';
  if (card) card.href = `hadith.html?book=${lastRead.bookId}&id=${lastRead.hadithId}`;
  if (bookElem) bookElem.innerText = lastRead.bookName;
  if (titleElem) titleElem.innerText = lastRead.hadithTitle || `${lastRead.bookName} Hadith #${lastRead.hadithId}`;
}

/**
 * loadHOTD — Load Hadith of the Day from localStorage (set via admin panel)
 */
async function loadHOTD() {
  const container = document.getElementById('hotd-container');
  if (!container) return;

  // Load config from localStorage (set by admin panel)
  let hotdConfig = null;
  try {
    const raw = localStorage.getItem('hadeeth_hotd');
    if (raw) hotdConfig = JSON.parse(raw);
  } catch (e) {}

  // Default fallback: Bukhari #1
  const bookId = (hotdConfig && hotdConfig.bookId) || 'bukhari';
  const hadithId = (hotdConfig && hotdConfig.hadithId) || '1';

  const bookNames = {
    bukhari: 'Sahih al-Bukhari', muslim: 'Sahih Muslim',
    abudawud: 'Sunan Abu Dawud', tirmidhi: "Jami' at-Tirmidhi",
    nasai: "Sunan an-Nasa'i", ibnmajah: 'Sunan Ibn Majah',
    malik: 'Muwatta Malik', darimi: 'Sunan ad-Darimi',
    ahmad: 'Musnad Ahmad', nawawi: 'Forty Hadith an-Nawawi',
    qudsi: '40 Hadith Qudsi', shah: 'Forty Hadith Shah Waliullah',
    adab: 'Al-Adab Al-Mufrad', bulugh: 'Bulugh al-Maram',
    mishkat: 'Mishkat al-Masabih', riyad: 'Riyad as-Salihin',
    shamail: 'Shamail al-Muhammadiyah'
  };
  const bookName = bookNames[bookId] || bookId;

  // Show loading state
  const hotdBookLabel = document.getElementById('hotd-book-label');
  const hotdChapterLabel = document.getElementById('hotd-chapter-label');
  const hotdArabic = document.getElementById('hotd-arabic');
  const hotdEnglish = document.getElementById('hotd-english');
  const hotdRawi = document.getElementById('hotd-rawi');
  const hotdLink = document.getElementById('hotd-read-link');

  if (hotdBookLabel) hotdBookLabel.textContent = `${bookName} ${hadithId}`;
  if (hotdLink) hotdLink.href = `hadith.html?book=${bookId}&id=${hadithId}`;

  try {
    const [arabicEd, engEd] = await Promise.all([
      window.HadeethAPI.getEdition('ara', bookId),
      window.HadeethAPI.getEdition('eng', bookId)
    ]);

    let textAr = '';
    let textEn = '';
    let rawi = '';

    if (arabicEd && arabicEd.hadiths) {
      const h = arabicEd.hadiths.find(h => (h.hadithnumber ?? h.id) == hadithId);
      if (h) textAr = h.text || '';
    }
    if (engEd && engEd.hadiths) {
      const h = engEd.hadiths.find(h => (h.hadithnumber ?? h.id) == hadithId);
      if (h) {
        textEn = h.text || '';
        rawi = h.narrated_by || h.narrator || '';
      }
    }

    if (hotdArabic) hotdArabic.textContent = textAr || '—';
    if (hotdEnglish) hotdEnglish.textContent = textEn ? `"${textEn.substring(0, 220)}${textEn.length > 220 ? '...' : ''}"` : '—';
    if (hotdRawi && rawi) hotdRawi.textContent = `Narrated by ${rawi}.`;
    if (hotdChapterLabel) hotdChapterLabel.textContent = '';
  } catch (e) {
    console.warn('HOTD load failed:', e);
  }
}

/**
 * Initialize Interactive Live Search
 */
function initSearch() {
  const searchInput = document.getElementById('search-input');
  const searchBtn = document.getElementById('search-btn');
  const resultsContainer = document.getElementById('search-results-container');

  if (!searchInput) return;

  // Create results container if missing
  let resultsDiv = resultsContainer;
  if (!resultsDiv) {
    resultsDiv = document.createElement('div');
    resultsDiv.id = 'search-results-container';
    resultsDiv.className = 'w-full max-w-2xl mt-6 hidden flex flex-col gap-4 text-left';
    const parent = searchInput.closest('section') || searchInput.parentElement;
    parent.appendChild(resultsDiv);
  }

  const performSearch = async () => {
    const query = searchInput.value.trim();
    if (!query) {
      resultsDiv.classList.add('hidden');
      return;
    }

    const bookFilter = document.getElementById('search-kitab-filter')?.value || 'all';

    resultsDiv.classList.remove('hidden');
    resultsDiv.innerHTML = `
      <div class="p-8 text-center bg-surface dark:bg-[#1e293b] rounded-xl border border-outline-variant/20 dark:border-[#334155]">
        <span class="material-symbols-outlined animate-spin text-secondary dark:text-[#10b981] text-3xl">progress_activity</span>
        <p class="mt-2 text-sm font-semibold text-primary dark:text-white">Searching authentic sources...</p>
        <p class="text-xs text-outline dark:text-gray-400 mt-1">Query: "${escapeHtml(query)}" • Filter: ${escapeHtml(bookFilter)}</p>
      </div>
    `;

    resultsDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });

    if (window.HadeethAPI) {
      const results = await window.HadeethAPI.search(query, bookFilter, 20);
      renderSearchResults(results, query, resultsDiv);
    }
  };

  // Trigger on Enter key in input
  searchInput.addEventListener('keyup', (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      performSearch();
    }
  });

  // Trigger on search button click
  if (searchBtn) {
    searchBtn.addEventListener('click', (e) => {
      e.preventDefault();
      performSearch();
    });
  }
}

/**
 * Render Search Results Cards
 */
function renderSearchResults(results, query, container) {
  if (!results || results.length === 0) {
    container.innerHTML = `
      <div class="p-8 text-center bg-surface dark:bg-[#1e293b] rounded-xl border border-outline-variant/20 dark:border-[#334155]">
        <span class="material-symbols-outlined text-outline dark:text-gray-500 text-4xl">search_off</span>
        <h3 class="mt-2 font-bold text-primary dark:text-white">No results found for "${escapeHtml(query)}"</h3>
        <p class="text-xs text-outline dark:text-gray-400 mt-1">Try searching by keyword like 'niat', 'intention', 'revelation', or Hadith number like '1'</p>
      </div>
    `;
    return;
  }

  let html = `
    <div class="flex items-center justify-between px-2 mb-1">
      <span class="text-xs font-bold uppercase tracking-wider text-secondary dark:text-[#10b981]">Found ${results.length} authentic matches</span>
      <span class="text-xs text-outline dark:text-gray-500">Multilingual FTS</span>
    </div>
    <div class="flex flex-col gap-4">
  `;

  results.forEach(res => {
    const arabicText = res.arabic_text || '';
    const englishText = res.primary_translation || res.english_text || '';
    const bookName = res.book_name || (res.book_slug === 'nawawi' ? 'Forty Nawawi' : 'Sahih al-Bukhari');
    const hadithNum = res.hadith_number || res.id;
    const grade = res.grade || 'Sahih';

    html += `
      <div class="bg-surface dark:bg-[#1e293b] border border-outline-variant/20 dark:border-[#334155] rounded-xl p-5 hover:border-secondary/50 dark:hover:border-[#10b981]/50 transition-all shadow-sm flex flex-col gap-3">
        <div class="flex items-center justify-between border-b border-outline-variant/10 dark:border-[#334155] pb-2">
          <div class="flex items-center gap-2">
            <span class="bg-primary dark:bg-[#10b981] text-white dark:text-black text-xs font-bold px-2 py-0.5 rounded">${escapeHtml(bookName)} #${hadithNum}</span>
            <span class="bg-sunan-emerald/10 text-sunan-emerald dark:text-[#10b981] text-xs font-semibold px-2 py-0.5 rounded">${escapeHtml(grade)}</span>
          </div>
          <a href="hadith.html?book=${res.book_slug || 'bukhari'}&id=${hadithNum}" class="text-xs text-secondary dark:text-[#10b981] font-semibold hover:underline flex items-center gap-1">
            View Detail &rarr;
          </a>
        </div>
        ${arabicText ? `<p class="font-arabic-body text-lg text-primary dark:text-white text-right leading-relaxed" dir="rtl">${escapeHtml(arabicText.substring(0, 300))}${arabicText.length > 300 ? '...' : ''}</p>` : ''}
        <p class="text-sm text-on-surface-variant dark:text-gray-300 leading-relaxed">${escapeHtml(englishText.substring(0, 250))}${englishText.length > 250 ? '...' : ''}</p>
      </div>
    `;
  });

  html += `</div>`;
  container.innerHTML = html;
}

/**
 * Load Books Grid Dynamically
 */
async function loadBooksGrid() {
  const container = document.getElementById('books-grid');
  if (!container) return;
  if (container.querySelectorAll('.book-card').length > 0) return;

  const books = await window.HadeethAPI.getBooks();
  if (!books || books.length === 0) return;

  const isIdMode = (window.LangSystem && window.LangSystem.isIdMode());
  let html = '';
  books.forEach(b => {
    const countUnit = isIdMode ? 'Hadits' : 'Ahadith';
    html += `
      <a href="kitab.html?book=${b.id}" class="bg-surface dark:bg-[#1e293b] border border-outline-variant/20 dark:border-[#334155] rounded-xl overflow-hidden hover:shadow-md transition-all flex flex-col cursor-pointer group">
        <div class="p-5 flex flex-col gap-2 flex-grow">
          <div class="flex justify-between items-start">
            <span class="bg-sunan-emerald/10 text-sunan-emerald dark:text-[#10b981] px-2 py-0.5 rounded font-bold text-xs uppercase">${b.grade || 'Sahih'}</span>
            <span class="text-xs text-outline dark:text-gray-400 font-bold">${b.total_hadiths || '—'} ${countUnit}</span>
          </div>
          <h3 class="text-lg font-bold text-primary dark:text-white group-hover:text-secondary dark:group-hover:text-[#10b981] transition-colors mt-1">${escapeHtml(b.name_en)}</h3>
          <p class="font-arabic-body text-base text-secondary dark:text-[#10b981]" dir="rtl">${escapeHtml(b.name_ar || '')}</p>
          <p class="text-xs text-on-surface-variant dark:text-gray-400 mt-1">${escapeHtml(b.author || '')}</p>
        </div>
      </a>
    `;
  });
  container.innerHTML = html;
}

/**
 * TafseerLinker — Automatically hyperlinking Qur'anic references to tafseer.id
 */
const TafseerLinker = {
  surahMap: {
    'al-fatihah': 1, 'fatihah': 1, 'al-baqarah': 2, 'baqarah': 2, 'ali imran': 3, 'an-nisa': 4, 'al-maidah': 5,
    'al-anam': 6, 'al-araf': 7, 'al-anfal': 8, 'at-tawbah': 9, 'yunus': 10, 'hud': 11, 'yusuf': 12, 'ar-rad': 13,
    'ibrahim': 14, 'al-hijr': 15, 'an-nahl': 16, 'al-isra': 17, 'al-kahf': 18, 'maryam': 19, 'taha': 20
  },
  parse(text) {
    if (!text) return '';
    let out = text.replace(/\[Qur['’]an\s+(\d+):(\d+)\]/gi, (match, s, a) => {
      return `<a href="https://tafseer.id/surah/${s}/${a}" target="_blank" rel="noopener" class="text-sunan-emerald dark:text-[#10b981] underline font-semibold hover:opacity-80">${match} ↗</a>`;
    });
    out = out.replace(/(?:QS\.?|Surah)\s+([A-Za-z\-'\s]+|\d+)[:\s]+(\d+)/gi, (match, surah, ayah) => {
      let sNum = parseInt(surah);
      if (isNaN(sNum)) {
        const norm = surah.toLowerCase().trim();
        sNum = this.surahMap[norm] || 2;
      }
      return `<a href="https://tafseer.id/surah/${sNum}/${ayah}" target="_blank" rel="noopener" class="text-sunan-emerald dark:text-[#10b981] underline font-semibold hover:opacity-80">${match} ↗</a>`;
    });
    
    // Process Scholar/Narrator Links
    // Exclude strings that already look like HTML (to avoid messing up the Qur'an links)
    const tempTokens = [];
    out = out.replace(/<a[\s\S]*?<\/a>/g, (m) => {
        tempTokens.push(m);
        return `__HTML_TOKEN_${tempTokens.length - 1}__`;
    });
    
    out = out.replace(/\[(.*?)\]/g, (match, name) => {
      let targetName = name;
      let displayName = name;
      
      if (name.includes('|')) {
        const parts = name.split('|');
        targetName = parts[0].trim();
        displayName = parts[1].trim();
      }
      
      let cleanName = targetName.replace(/[\[\]'"]/g, '').trim();
      cleanName = cleanName.replace(/\s*radliallahu\s+'?anh[ua]m?a?/gi, '').trim();
      
      const urlParams = new URLSearchParams({ name: cleanName });
      return `[<a href="profile-detail.html?${urlParams.toString()}" class="font-semibold text-primary-600 dark:text-primary-400 hover:underline inline-flex items-center gap-0.5" title="View Scholar Profile">
                <span class="inline-block translate-y-[2px] opacity-70">
                   <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path></svg>
                </span>
                ${displayName}
              </a>]`;
    });
    
    out = out.replace(/__HTML_TOKEN_(\d+)__/g, (m, idx) => tempTokens[parseInt(idx)]);
    
    return out;
  }
};

/**
 * LastReadTracker — Persist and retrieve last read Hadith
 */
const LastReadTracker = {
  save(bookId, hadithId, bookName, hadithTitle) {
    const data = { bookId, hadithId, bookName, hadithTitle, timestamp: Date.now() };
    localStorage.setItem('hadeeth_last_read', JSON.stringify(data));
  },
  get() {
    try {
      const raw = localStorage.getItem('hadeeth_last_read');
      return raw ? JSON.parse(raw) : null;
    } catch (e) {
      return null;
    }
  }
};

/**
 * Load Hadith Detail View Dynamic from URL params
 */
async function loadHadithDetail() {
  const params = new URLSearchParams(window.location.search);
  const bookId = params.get('book') || 'bukhari';
  const hadithId = params.get('id') || '1';

  const container = document.getElementById('hadith-detail-container');
  if (!container) return;

  if (!window._hadithDetailLangListenerAttached) {
    window._hadithDetailLangListenerAttached = true;
    window.addEventListener('hadeeth_lang_change', () => {
      if (window.LangSystem) window.LangSystem.apply(window.LangSystem.get());
    });
  }

  const bookNames = {
    bukhari: 'Sahih al-Bukhari',
    muslim: 'Sahih Muslim',
    abudawud: 'Sunan Abu Dawud',
    tirmidhi: "Jami' at-Tirmidhi",
    nasai: "Sunan an-Nasa'i",
    ibnmajah: 'Sunan Ibn Majah',
    malik: 'Muwatta Malik',
    darimi: 'Sunan ad-Darimi',
    ahmad: 'Musnad Ahmad',
    nawawi: "Forty Hadith an-Nawawi",
    qudsi: '40 Hadith Qudsi',
    shah: 'Forty Hadith Shah Waliullah',
    adab: 'Al-Adab Al-Mufrad',
    bulugh: 'Bulugh al-Maram',
    mishkat: 'Mishkat al-Masabih',
    riyad: 'Riyad as-Salihin',
    shamail: 'Shamail al-Muhammadiyah'
  };
  const bookName = bookNames[bookId.toLowerCase()] || bookId.toUpperCase();

  // Update page title dynamically
  document.title = `${bookName} Hadith #${hadithId} - HADEETH.ID`;

  // Save Last Read
  if (window.LastReadTracker) window.LastReadTracker.save(bookId, hadithId, bookName, `${bookName} Hadith #${hadithId}`);

  // Elements
  const bcBook = document.querySelector('[data-breadcrumb-book]');
  const bcCurrentEn = document.querySelector('[data-breadcrumb-current-en]');
  const bcCurrentId = document.querySelector('[data-breadcrumb-current-id]');
  const chapterMetaEn = document.querySelector('[data-hadith-chapter-en]');
  const chapterMetaId = document.querySelector('[data-hadith-chapter-id]');
  const prevBtn = document.getElementById('prev-hadith-btn');
  const nextBtn = document.getElementById('next-hadith-btn');

  const currentNum = parseInt(hadithId) || 1;

  // Fetch Chapter info
  let chapterObj = null;
  try {
    const chapters = await window.HadeethAPI.getChapters(bookId);
    if (chapters && chapters.length > 0) {
      chapterObj = chapters.find(c => (c.hadith_start || 0) <= currentNum && currentNum <= (c.hadith_end || 99999));
    }
  } catch (e) {
    console.warn('Failed to load chapter info for detail breadcrumb:', e);
  }

  if (bcBook) {
    bcBook.innerText = bookName;
    bcBook.href = `kitab.html?book=${bookId}`;
  }

  const titleTextEn = chapterObj ? (chapterObj.title_en || `Hadith #${hadithId}`) : `Hadith #${hadithId}`;
  const titleTextId = chapterObj ? (chapterObj.title_id || titleTextEn) : `Hadits #${hadithId}`;

  if (bcCurrentEn) bcCurrentEn.innerText = titleTextEn;
  if (bcCurrentId) bcCurrentId.innerText = titleTextId;

  const chNum = chapterObj ? (chapterObj.chapter_number || '') : '';
  const enCh = chNum ? `Book ${chNum}: ${titleTextEn}` : bookName;
  const idCh = chNum ? `Bab ${chNum}: ${titleTextId}` : bookName;

  if (chapterMetaEn) chapterMetaEn.innerText = enCh;
  if (chapterMetaId) chapterMetaId.innerText = idCh;

  if (prevBtn) {
    if (currentNum > 1) {
      prevBtn.href = `hadith.html?book=${bookId}&id=${currentNum - 1}`;
      prevBtn.classList.remove('opacity-50', 'pointer-events-none');
    } else {
      prevBtn.href = '#';
      prevBtn.classList.add('opacity-50', 'pointer-events-none');
    }
  }
  if (nextBtn) {
    nextBtn.href = `hadith.html?book=${bookId}&id=${currentNum + 1}`;
  }

  // Fetch from CDN
  const [edition, arabicEdition, indEdition] = await Promise.all([
    window.HadeethAPI.getEdition('eng', bookId),
    window.HadeethAPI.getEdition('ara', bookId),
    window.HadeethAPI.getEdition('ind', bookId)
  ]);

  let hadithTextEn = '';
  let hadithTextAr = '';
  let hadithTextId = '';

  if (edition && edition.hadiths) {
    const found = edition.hadiths.find(h => (h.hadithnumber ?? h.id) == hadithId);
    if (found) hadithTextEn = found.text || '';
  }
  if (arabicEdition && arabicEdition.hadiths) {
    const found = arabicEdition.hadiths.find(h => (h.hadithnumber ?? h.id) == hadithId);
    if (found) hadithTextAr = found.text || '';
  }
  if (indEdition && indEdition.hadiths) {
    const found = indEdition.hadiths.find(h => (h.hadithnumber ?? h.id) == hadithId);
    if (found) hadithTextId = found.terjemah || found.text || '';
  }

  const item = {
    hadith_number: hadithId,
    text_ar: hadithTextAr,
    text_en: hadithTextEn,
    text_id: hadithTextId,
    grade: 'Sahih',
    book_id: bookId
  };

  const textAr = (item.text_ar && item.text_ar.trim()) ? item.text_ar.trim() : '';
  const textEn = (item.text_en && item.text_en.trim()) ? item.text_en.trim() : '';
  const textId = (item.text_id && item.text_id.trim()) ? item.text_id.trim() : '';

  if (arabicElem) arabicElem.innerText = textAr || '—';

  if (indonesianElem) {
    if (textId) {
      indonesianElem.innerHTML = TafseerLinker.parse(textId);
    } else {
      indonesianElem.innerHTML = '<span class="text-xs text-outline dark:text-gray-400 italic">Terjemahan Bahasa Indonesia untuk Hadits ini saat ini belum tersedia. Teks Arab lengkap tersedia di atas.</span>';
    }
  }

  if (englishElem) {
    if (textEn) {
      englishElem.innerHTML = TafseerLinker.parse(textEn);
    } else {
      englishElem.innerHTML = '<span class="text-xs text-outline dark:text-gray-400 italic">English translation for this Hadith is currently unavailable. Full Arabic text is displayed above.</span>';
    }
  }

  if (titleEn) titleEn.innerText = `${bookName} Hadith #${item.hadith_number}`;
  if (titleId) titleId.innerText = `${bookName} Hadits #${item.hadith_number}`;

  if (sanadLink) sanadLink.href = `sanad.html?book=${bookId}&id=${item.hadith_number}`;

  const langSelects = container.querySelectorAll('[data-lang-select]');
  langSelects.forEach(selectElem => {
    selectElem.addEventListener('change', () => {
      const cardBox = selectElem.closest('.p-5');
      const targetP = cardBox ? cardBox.querySelector('p') : null;
      if (!targetP) return;
      const val = selectElem.value;
      if (val === 'en') {
        targetP.innerHTML = textEn ? TafseerLinker.parse(textEn) : '<span class="text-xs text-outline dark:text-gray-400 italic">English translation for this Hadith is currently unavailable. Full Arabic text is displayed above.</span>';
      } else if (val === 'id') {
        targetP.innerHTML = textId ? TafseerLinker.parse(textId) : '<span class="text-xs text-outline dark:text-gray-400 italic">Terjemahan Bahasa Indonesia untuk Hadits ini saat ini belum tersedia. Teks Arab lengkap tersedia di atas.</span>';
      } else if (val === 'ar') {
        targetP.innerText = textAr || '—';
      }

      // Sync Syarah language selector dropdown & update Syarah text!
      if (window.switchSyarahLang) {
        window.switchSyarahLang(val);
      }
    });
  });

  if (sanadPreviewEn || sanadPreviewId || rawiEn || rawiId) {
    let previewNames = [];
    if (item.text_id) {
      const isnadPartId = item.text_id.split(/beliau\s+bersabda\s*:|berfirman\s*:|berkata\s*:|tentang\s+firman\s+Allah|bahwa\s+Rasulullah/i)[0] || item.text_id;
      const brackets = isnadPartId.match(/\[([^\]]+)\]/g);
      if (brackets) {
        const stopWords = new Set([
          'al qur\'an', 'al-qur\'an', 'qur\'an', 'islam', 'nabi', 'rasulullah', 'allah', 'tuhan',
          'pamannya', 'pamanku', 'paman', 'uncle', 'my uncle', 'his uncle',
          'ayahnya', 'ayahku', 'bapaknya', 'bapakku', 'ayah', 'bapak', 'father', 'his father', 'my father',
          'kakeknya', 'kakekku', 'kakek', 'grandfather', 'his grandfather', 'my grandfather',
          'ibunya', 'ibuku', 'ibu', 'mother', 'his mother', 'my mother',
          'saudaranya', 'saudaraku', 'saudara', 'brother', 'his brother', 'my brother',
          'saudari', 'saudarinya', 'sister', 'his sister',
          'anaknya', 'anakku', 'anak', 'son', 'daughter', 'his son', 'his daughter',
          'istrinya', 'istri', 'wife', 'his wife',
          'suaminya', 'suami', 'husband', 'her husband',
          'budaknya', 'budak', 'hamba', 'slave', 'freedman',
          'bibinya', 'bibi', 'aunt', 'his aunt',
          'sepupunya', 'sepupu', 'cousin',
          'mertuanya', 'mertua', 'in-law',
          'keluarganya', 'keluarga', 'family',
          'kerabatnya', 'kerabat', 'kin',
          'sahabat', 'sahabatnya', 'companion', 'companions',
          'beliau', 'mereka', 'seseorang', 'seorang', 'lelaki', 'wanita', 'perempuan',
          'orang', 'orang tua', 'kaum', 'umat', 'jamaah'
        ]);
        brackets.forEach(b => {
          let nameStr = b.replace(/[\[\]]/g, '').trim();
          let name = nameStr;
          if (nameStr.includes('|')) {
            name = nameStr.split('|')[0].trim();
          }
          const norm = name.toLowerCase();
          const cleanNorm = norm.replace(/\s+radliallahu.*$/, '').replace(/\s+semoga allah.*$/, '').trim();
          
          // Dynamic pronoun resolution for Sanad preview
          if (['bapaknya', 'ayahnya', 'his father', 'pamannya', 'kakeknya', 'ibunya'].includes(cleanNorm)) {
            const prevRaw = previewNames.length > 0 ? previewNames[previewNames.length - 1] : '';
            const prevName = prevRaw.toLowerCase().replace(/[\']/g, '');
            
            if (cleanNorm === 'bapaknya' || cleanNorm === 'ayahnya' || cleanNorm === 'his father') {
              const pronounMap = {
                'hisyam': 'Urwah bin Az-Zubair',
                'suhail': 'Abu Shalih',
                'salim': 'Abdullah bin Umar',
                'ibnu thawus': 'Thawus',
                'mutamir': 'Sulaiman At-Taimi',
                'al-mutamir': 'Sulaiman At-Taimi',
                'al mutamir': 'Sulaiman At-Taimi',
                'jafar': 'Muhammad bin Ali',
                'ibnu buraidah': 'Buraidah'
              };
              if (pronounMap[prevName]) {
                name = pronounMap[prevName];
              } else if (prevRaw.includes(' bin ')) {
                name = prevRaw.split(' bin ')[1].trim();
              }
            } else if (cleanNorm === 'pamannya') {
              if (prevName.includes('abbad bin tamim')) name = 'Abdullah bin Zaid';
              if (prevName.includes('ibnu akhi ibnu syihab')) name = 'Ibnu Syihab';
            }
          }
          
          if (name && !stopWords.has(name.toLowerCase()) && !stopWords.has(cleanNorm) && name.length > 2) {
            previewNames.push(name);
          }
        });
      }
    }

    if (previewNames.length > 0) {
      const companionRawi = previewNames[previewNames.length - 1];
      if (sanadPreviewEn) sanadPreviewEn.innerText = previewNames.join(' → ') + ' → Prophet ﷺ';
      if (sanadPreviewId) sanadPreviewId.innerText = previewNames.join(' → ') + ' → Rasulullah ﷺ';
      if (rawiEn) rawiEn.innerText = `Narrator: ${companionRawi}`;
      if (rawiId) rawiId.innerText = `Perawi: ${companionRawi}`;
    } else {
      if (sanadPreviewEn) sanadPreviewEn.innerText = `Inspect Chain for ${bookName} #${item.hadith_number} → Prophet ﷺ`;
      if (sanadPreviewId) sanadPreviewId.innerText = `Periksa Silsilah untuk ${bookName} #${item.hadith_number} → Rasulullah ﷺ`;
      if (rawiEn) rawiEn.innerText = `Narrator: Sahabi (Companion)`;
      if (rawiId) rawiId.innerText = `Perawi: Sahabat`;
    }
  }

  loadHadithSyarah(bookId, item.hadith_number || hadithId);

  if (window.LangSystem) window.LangSystem.apply(window.LangSystem.get());

}

/**
 * Load Hadith List Page Dynamic with Full Filtering, Pagination & Language Switcher
 */
async function loadHadithList() {
  const container = document.getElementById('hadith-cards-container');
  if (!container) return;

  const params = new URLSearchParams(window.location.search);
  const bookId = params.get('book') || 'bukhari';
  const chapterId = params.get('chapter') || '1';
  // Dataset from URL takes precedence on first arrival (set by chapter links),
  // then localStorage. Sync localStorage so the banner reflects the URL param.
  const datasetParam = params.get('dataset');
  if (datasetParam) localStorage.setItem('dataset_version', datasetParam);
  const activeDataset = datasetParam || localStorage.getItem('dataset_version') || 'primary';

  const bookNames = {
    bukhari: 'Sahih al-Bukhari',
    nawawi: 'Forty Nawawi',
    muslim: 'Sahih Muslim',
    abudawud: 'Sunan Abu Dawood',
    tirmidhi: "Jami' al-Tirmidhi",
    nasai: "Sunan an-Nasa'i",
    ibnmajah: 'Sunan Ibn Majah',
    malik: 'Muwatta Malik',
    ahmad: 'Musnad Ahmad',
    darimi: 'Sunan ad-Darimi'
  };
  const bookName = bookNames[bookId.toLowerCase()] || bookId.toUpperCase();

  // Elements
  const bcBook = document.querySelector('[data-list-breadcrumb-book]');
  const bcCurrent = document.querySelector('[data-list-breadcrumb-current]');
  const bookBadge = document.querySelector('[data-list-book-badge]');
  const chMeta = document.querySelector('[data-list-chapter-meta]');
  const countMeta = document.querySelector('[data-list-count-meta]');
  const chTitleEn = document.querySelector('[data-list-chapter-title-en]');
  const chTitleId = document.querySelector('[data-list-chapter-title-id]');
  const chTitleAr = document.querySelector('[data-list-chapter-title-ar]');

  const searchInput = document.getElementById('chapter-search-input');
  const scopeSelect = document.getElementById('search-scope-select');
  const langSelect = document.getElementById('default-lang-select');
  
  // Sync the dropdown with the global language setting ONCE on page load
  if (langSelect && !langSelect.hasAttribute('data-synced-initially')) {
    langSelect.value = LangSystem.get() === 'id' ? 'id' : 'en';
    langSelect.setAttribute('data-synced-initially', 'true');
  }

  const pageSizeSelect = document.getElementById('page-size-select');
  const prevBtn = document.getElementById('prev-page-btn');
  const nextBtn = document.getElementById('next-page-btn');
  const pageIndicator = document.getElementById('page-indicator');

  // Indonesian Chapter Titles Master Mapping Dictionary
  const indonesianChapterTitles = {
    'bukhari_1': 'Permulaan Wahyu',
    'bukhari_2': 'Iman',
    'bukhari_3': 'Ilmu',
    'bukhari_4': 'Wudhu',
    'bukhari_5': 'Mandi',
    'bukhari_6': 'Haid',
    'bukhari_7': 'Tayammum',
    'bukhari_8': 'Shalat',
    'bukhari_9': 'Waktu-Waktu Shalat',
    'bukhari_10': 'Adzan',
    'bukhari_11': 'Shalat Jum\'at',
    'bukhari_12': 'Shalat Khauf',
    'bukhari_13': 'Dua Hari Raya (Idul Fitri & Idul Adha)',
    'bukhari_14': 'Shalat Witir',
    'bukhari_15': 'Istisqa\' (Memohon Hujan)',
    'bukhari_16': 'Gerhana (Kusuf)',
    'bukhari_17': 'Sujud Al-Qur\'an',
    'bukhari_18': 'Qashar Shalat',
    'bukhari_19': 'Tahajjud (Shalat Malam)',
    'bukhari_20': 'Keutamaan Shalat di Makkah & Madinah',
    'bukhari_21': 'Tindakan Saat Shalat',
    'bukhari_22': 'Sujud Sahwi',
    'bukhari_23': 'Jenazah',
    'bukhari_24': 'Zakat',
    'bukhari_25': 'Haji',
    'bukhari_26': 'Umrah',
    'bukhari_27': 'Orang Terhalang Haji',
    'bukhari_28': 'Denda Berburu Saat Ihram',
    'bukhari_29': 'Keutamaan Kota Madinah',
    'bukhari_30': 'Puasa (Shaum)',
    'bukhari_31': 'Shalat Tarawih',
    'bukhari_32': 'Lailatul Qadr',
    'bukhari_33': 'I\'tikaf',
    'bukhari_34': 'Jual Beli (Buyu\')',
    'bukhari_35': 'Jual Beli Salam',
    'bukhari_36': 'Sewa Menyewa (Ijarah)',
    'bukhari_37': 'Hutang Piutang (Hawalah)',
    'bukhari_38': 'Wakalah (Perwakilan)',
    'bukhari_39': 'Bercocok Tanam',
    'bukhari_40': 'Penyiraman & Pengairan',
    'bukhari_41': 'Pinjam Meminjam',
    'bukhari_42': 'Persengketaan',
    'bukhari_43': 'Barang Temuan',
    'bukhari_44': 'Kedzaliman & Perampasan',
    'bukhari_45': 'Syirkah (Kemitraan)',
    'bukhari_46': 'Gadai (Rahn)',
    'bukhari_47': 'Pembebasan Budak',
    'bukhari_48': 'Hibah & Keutamaannya',
    'bukhari_49': 'Persaksian (Syahadat)',
    'bukhari_50': 'Perdamaian (Sulh)',
    'bukhari_51': 'Syarat-Syarat',
    'bukhari_52': 'Wasiat (Washaya)',
    'bukhari_53': 'Jihad & Ekspedisi',
    'bukhari_54': 'Permulaan Penciptaan',
    'bukhari_55': 'Kisah Para Nabi',
    'bukhari_56': 'Keutamaan Para Sahabat (Manaqib)',
    'bukhari_57': 'Peperangan (Maghazi)',
    'bukhari_58': 'Tafsir Al-Qur\'an',
    'bukhari_59': 'Keutamaan Al-Qur\'an',
    'bukhari_60': 'Pernikahan (Nikah)',
    'bukhari_61': 'Perceraian (Thalaq)',
    'bukhari_62': 'Nafkah',
    'bukhari_63': 'Makanan (Ath\'imah)',
    'bukhari_64': 'Aqiqah',
    'bukhari_65': 'Sembelihan & Berburu',
    'bukhari_66': 'Kurban (Udhiyah)',
    'bukhari_67': 'Minuman (Asyribah)',
    'bukhari_68': 'Orang Sakit',
    'bukhari_69': 'Pengobatan (Tibb)',
    'bukhari_70': 'Pakaian (Libas)',
    'bukhari_71': 'Adab (Etika Sopan Santun)',
    'bukhari_72': 'Meminta Izin (Isti\'zan)',
    'bukhari_73': 'Doa & Dzikir',
    'bukhari_74': 'Kelembutan Hati (Riqaq)',
    'bukhari_75': 'Takdir (Qadar)',
    'bukhari_76': 'Sumpah & Nadzar',
    'bukhari_77': 'Tebusan Sumpah',
    'bukhari_78': 'Hukum Waris (Faradh)',
    'bukhari_79': 'Hukuman Pidana Islam (Hudud)',
    'bukhari_80': 'Denda Jiwa (Diyat)',
    'bukhari_81': 'Meminta Taubat Orang Murtad',
    'bukhari_82': 'Pemaksaan (Ikrah)',
    'bukhari_83': 'Trik Hukum (Hiyal)',
    'bukhari_84': 'Tafsir Mimpi',
    'bukhari_85': 'Fitnah Akhir Zaman',
    'bukhari_86': 'Hukum & Keputusan (Ahkam)',
    'bukhari_87': 'Harapan (Tamanni)',
    'bukhari_88': 'Khabar Ahad',
    'bukhari_89': 'Berpegang Teguh pada Al-Qur\'an & Sunnah',
    'bukhari_90': 'Tauhid & Keagungan Allah'
  };

  // Fetch Chapter Metadata if available
  let chapterTitleNameEn = chapterId === '0' ? 'Introduction' : `Chapter ${chapterId}`;
  let chapterTitleNameId = chapterId === '0' ? 'Muqaddimah' : `Kitab ${chapterId}`;
  let chapterTitleNameAr = `باب رقم ${chapterId}`;
  let startHadithNum = null;
  let endHadithNum = null;
  let chapterHadithCount = null;

  try {
    const chapters = await window.HadeethAPI.getChapters(bookId);
    if (chapters && chapters.length > 0) {
      const targetNum = parseInt(chapterId);
      const chInfo = chapters.find(c => c.chapter_number === targetNum)
        || chapters[targetNum - 1]
        || chapters[0];
      if (chInfo) {
        chapterTitleNameEn = chInfo.title_en || chInfo.name_en || chInfo.title || `Chapter ${chapterId}`;
        const bookChKey = `${bookId.toLowerCase()}_${chapterId}`;
        const rawId = indonesianChapterTitles[bookChKey] || chInfo.title_id || chInfo.name_id;
        if (rawId) {
          chapterTitleNameId = rawId;
        } else if (chapterTitleNameEn.includes('(')) {
          chapterTitleNameId = chapterTitleNameEn.replace(/.*?\((.*?)\)/, '$1');
        } else {
          chapterTitleNameId = chapterTitleNameEn;
        }
        chapterTitleNameAr = chInfo.title_ar || chInfo.name_ar || chInfo.arabic || `باب رقم ${chapterId}`;
        startHadithNum = chInfo.hadith_start != null ? chInfo.hadith_start : null;
        endHadithNum = chInfo.hadith_end != null ? chInfo.hadith_end : null;
        chapterHadithCount = chInfo.hadith_count || (endHadithNum && startHadithNum ? (endHadithNum - startHadithNum + 1) : null);
      }
    }
  } catch (err) {
    console.warn('Chapter meta load error:', err);
  }

  // Override title_id if in dictionary
  const bookChKey = `${bookId.toLowerCase()}_${chapterId}`;
  if (indonesianChapterTitles[bookChKey]) {
    chapterTitleNameId = indonesianChapterTitles[bookChKey];
  }

  const isIdLang = (window.LangSystem && window.LangSystem.isIdMode());
  const activeChTitle = isIdLang ? chapterTitleNameId : chapterTitleNameEn;
  const activeChMeta = isIdLang ? (chapterId === '0' ? 'Muqaddimah' : `Kitab ${chapterId}`) : (chapterId === '0' ? 'Introduction' : `Chapter ${chapterId}`);

  const bcCurrentEn = document.querySelector('[data-list-breadcrumb-current-en]');
  const bcCurrentId = document.querySelector('[data-list-breadcrumb-current-id]');
  const chMetaEn = document.querySelector('[data-list-chapter-meta-en]');
  const chMetaId = document.querySelector('[data-list-chapter-meta-id]');
  const countMetaEn = document.querySelector('[data-list-count-meta-en]');
  const countMetaId = document.querySelector('[data-list-count-meta-id]');

  if (bcBook) {
    bcBook.innerText = bookName;
    bcBook.href = `kitab.html?book=${bookId}`;
  }
  if (bcCurrentEn) bcCurrentEn.innerText = chapterTitleNameEn;
  if (bcCurrentId) bcCurrentId.innerText = chapterTitleNameId;
  if (bcCurrent && !bcCurrentEn) bcCurrent.innerText = activeChTitle;

  if (bookBadge) bookBadge.innerText = bookName;
  if (chMetaEn) chMetaEn.innerText = chapterId === '0' ? 'Introduction' : `Chapter ${chapterId}`;
  if (chMetaId) chMetaId.innerText = chapterId === '0' ? 'Muqaddimah' : `Kitab ${chapterId}`;
  if (chMeta && !chMetaEn) chMeta.innerText = activeChMeta;

  if (chTitleEn) chTitleEn.innerText = chapterTitleNameEn;
  if (chTitleId) chTitleId.innerText = chapterTitleNameId;
  if (chTitleAr) chTitleAr.innerText = chapterTitleNameAr;
  LangSystem.apply(LangSystem.get());

  if (!window._hadithListLangListenerAttached) {
    window._hadithListLangListenerAttached = true;
    window.addEventListener('hadeeth_lang_change', () => {
      const langSel = document.getElementById('default-lang-select');
      if (langSel) {
        langSel.value = LangSystem.get() === 'id' ? 'id' : 'en';
      }
      loadHadithList();
    });
  }

  // Render dataset banner on hadith-list page
  renderDatasetBanner(bookId, 'dataset-banner-list', activeDataset);

  // Local state
  let allHadiths = [];
  let filteredHadiths = [];
  let currentPage = 1;
  let pageSize = parseInt(pageSizeSelect ? pageSizeSelect.value : '10') || 10;
  let currentLang = langSelect ? langSelect.value : 'id';
  let searchScope = scopeSelect ? scopeSelect.value : 'chapter';

  // ================================================================
  // BRANCH B — AhmedBaset native hadith loading
  // ================================================================
  if (activeDataset === 'native_ahmedbaset') {
    const abBookMap = { ahmad: 'ahmed' };
    const abBook = abBookMap[bookId] || bookId;
    try {
      const resp = await fetch(`data/sources/ahmedbaset/by_chapter/the_9_books/${abBook}/${chapterId}.json`);
      if (resp.ok) {
        const abChapter = await resp.json();
        const chapTitleEn = abChapter.chapter?.english || `Chapter ${chapterId}`;
        const chapTitleAr = abChapter.chapter?.arabic || '';
        if (chTitleEn) chTitleEn.innerText = chapTitleEn;
        if (chTitleId) chTitleId.innerText = chapTitleEn; // no ID in AhmedBaset
        if (chTitleAr) chTitleAr.innerText = chapTitleAr;
        const bcCurEn = document.querySelector('[data-list-breadcrumb-current-en]');
        const bcCurId = document.querySelector('[data-list-breadcrumb-current-id]');
        if (bcCurEn) bcCurEn.innerText = chapTitleEn;
        if (bcCurId) bcCurId.innerText = chapTitleEn;
        const chMetaEn = document.querySelector('[data-list-chapter-meta-en]');
        const chMetaId = document.querySelector('[data-list-chapter-meta-id]');
        if (chMetaEn) chMetaEn.innerText = `AhmedBaset Kitab ${chapterId}`;
        if (chMetaId) chMetaId.innerText = `AhmedBaset Kitab ${chapterId}`;

        allHadiths = (abChapter.hadiths || []).map(h => ({
          hadith_number: h.idInBook || h.id,
          hadith_id_global: h.id,
          text_ar: h.arabic || '',
          text_en: h.english ? (h.english.narrator ? `${h.english.narrator} ${h.english.text}` : h.english.text || '') : '',
          text_id: '', // no ID in AhmedBaset — will show note
          grade: 'Sahih',
          book_id: bookId,
          _source: 'ahmedbaset',
          _noId: true
        }));

        const countEl = document.querySelector('[data-list-count-meta-en]');
        const countIdEl = document.querySelector('[data-list-count-meta-id]');
        const countFallback = document.querySelector('[data-list-count-meta]');
        const total = allHadiths.length;
        if (countEl) countEl.innerText = `${total} Hadiths in ${bookName} (AhmedBaset Kitab ${chapterId})`;
        if (countIdEl) countIdEl.innerText = `${total} Hadits dalam ${bookName} (AhmedBaset Kitab ${chapterId})`;
        if (countFallback && !countEl) countFallback.innerText = `${total} Hadiths — AhmedBaset Kitab ${chapterId}`;
      }
    } catch(e) {
      console.warn('AhmedBaset chapter hadith load error:', e);
    }

  // ================================================================
  // BRANCH C — Lidwa / Irsyad native hadith loading
  // ================================================================
  } else if (activeDataset === 'native_lidwa') {
    try {
      const resp = await fetch(`data/sources/lidwa/${bookId}.json`);
      if (resp.ok) {
        const lidwaAll = await resp.json();
        const chNum = parseInt(chapterId);
        const chapHadiths = lidwaAll.filter(h => h.chapter_number === chNum);

        // Get chapter title from lidwa-chapters index
        let chapTitleId = `Kitab ${chapterId}`;
        let chapTitleEn = `Chapter ${chapterId}`;
        let chapTitleAr = '';
        try {
          const idxResp = await fetch(`data/lidwa-chapters/${bookId}.json`);
          if (idxResp.ok) {
            const idx = await idxResp.json();
            const ch = (idx.chapters || []).find(c => c.chapter_number === chNum);
            if (ch) {
              chapTitleId = ch.title_id || chapTitleId;
              chapTitleEn = ch.title_en || chapTitleEn;
              chapTitleAr = ch.title_ar || '';
            }
          }
        } catch(e2) { /* ignore */ }

        if (chTitleEn) chTitleEn.innerText = chapTitleEn;
        if (chTitleId) chTitleId.innerText = chapTitleId;
        if (chTitleAr) chTitleAr.innerText = chapTitleAr;
        const bcCurEn2 = document.querySelector('[data-list-breadcrumb-current-en]');
        const bcCurId2 = document.querySelector('[data-list-breadcrumb-current-id]');
        if (bcCurEn2) bcCurEn2.innerText = chapTitleEn;
        if (bcCurId2) bcCurId2.innerText = chapTitleId;
        const chMetaEn2 = document.querySelector('[data-list-chapter-meta-en]');
        const chMetaId2 = document.querySelector('[data-list-chapter-meta-id]');
        if (chMetaEn2) chMetaEn2.innerText = `Lidwa Kitab ${chapterId}`;
        if (chMetaId2) chMetaId2.innerText = `Lidwa Kitab ${chapterId}`;

        allHadiths = chapHadiths.map(h => ({
          hadith_number: h.hadith_number,
          text_ar: h.text_ar || '',
          text_en: h.text_en || '',
          text_id: h.text_id || '',
          text_ur: h.text_ur || '',
          text_fr: h.text_fr || '',
          grade: h.grade || '',
          grade_by: h.grade_by || '',
          book_id: bookId,
          _source: 'lidwa',
          _lidwaRef: h.usc_msa_ref || ''
        }));

        const total = allHadiths.length;
        const firstH = chapHadiths[0];
        const lastH = chapHadiths[chapHadiths.length - 1];
        const rangeStr = firstH && lastH ? `${firstH.hadith_number} – ${lastH.hadith_number}` : '';
        const countEl2 = document.querySelector('[data-list-count-meta-en]');
        const countIdEl2 = document.querySelector('[data-list-count-meta-id]');
        const countFallback2 = document.querySelector('[data-list-count-meta]');
        if (countEl2) countEl2.innerText = `Lidwa Hadith ${rangeStr} • ${total} Hadiths in ${bookName} Kitab ${chapterId}`;
        if (countIdEl2) countIdEl2.innerText = `Lidwa Hadits ${rangeStr} • ${total} Hadits dalam ${bookName} Kitab ${chapterId}`;
        if (countFallback2 && !countEl2) countFallback2.innerText = `${total} Hadits — Lidwa Kitab ${chapterId}`;
      }
    } catch(e) {
      console.warn('Lidwa hadith load error:', e);
    }

  // ================================================================
  // ================================================================
  // BRANCH A — Primary (fawazahmed0 CDN)
  // AR + EN: fawazahmed0 CDN editions
  // ID: Lidwa/Irsyad source data (fawazahmed0 has no ind edition —
  //     ind-*.json files are stripped skeletons kept only as API stubs)
  // ================================================================
  } else {
    const engEd = await window.HadeethAPI.getEdition('eng', bookId);
    const araEd = await window.HadeethAPI.getEdition('ara', bookId);

    // Load Indonesian from Lidwa source data directly (same as Branch C)
    let lidwaIdMap = {};
    try {
      const baseUrl = window.__HADEETH_BASE__
        ? window.__HADEETH_BASE__ + '/data'
        : (() => {
            const s = document.querySelector('script[src*="js/api.js"]');
            if (s) return new URL(s.src, window.location.href).href.replace(/js\/api\.js.*$/, 'data');
            return window.location.origin + window.location.pathname.replace(/\/[^/]*$/, '') + '/data';
          })();
      const lidwaResp = await fetch(`${baseUrl}/sources/lidwa/${bookId}.json`);
      if (lidwaResp.ok) {
        const lidwaData = await lidwaResp.json();
        // Build map: hadith_number → text_id
        (Array.isArray(lidwaData) ? lidwaData : (lidwaData.hadiths || [])).forEach(h => {
          const num = h.hadith_number ?? h.hadithnumber ?? h.id;
          if (num !== undefined && h.text_id) lidwaIdMap[String(num)] = h.text_id;
        });
      }
    } catch (e) {
      console.warn('Lidwa ID source not available for', bookId, e);
    }

    const mainEd = engEd;
    if (mainEd && mainEd.hadiths) {
      const araMap = {};
      const engMap = {};
      if (araEd && araEd.hadiths) araEd.hadiths.forEach(h => araMap[h.hadithnumber ?? h.id] = h.text);
      if (engEd && engEd.hadiths) engEd.hadiths.forEach(h => engMap[h.hadithnumber ?? h.id] = h.text);

      let sourceHadiths = mainEd.hadiths;
      if (startHadithNum != null && endHadithNum != null) {
        sourceHadiths = sourceHadiths.filter(h => {
          const num = parseInt(h.hadithnumber ?? h.id);
          return num >= startHadithNum && num <= endHadithNum;
        });
      }

      allHadiths = sourceHadiths.map(h => {
        const num = h.hadithnumber ?? h.id;
        return {
          hadith_number: num,
          text_en: engMap[num] !== undefined ? engMap[num] : '',
          text_ar: araMap[num] !== undefined ? araMap[num] : '',
          // Indonesian linked live from Lidwa/Irsyad, matched by hadith number
          text_id: lidwaIdMap[String(num)] || '',
          grade: 'Sahih',
          book_id: bookId,
          _source: 'primary'  // marks this for the blue attribution note in renderList
        };
      });
    }
  } // end primary branch

  filteredHadiths = [...allHadiths];
  if (activeDataset === 'primary') {
    if (startHadithNum != null && endHadithNum != null) {
      const count = chapterHadithCount || (endHadithNum - startHadithNum + 1);
      const enText = `Hadith ${startHadithNum} – ${endHadithNum} • ${count} Hadiths in ${bookName} Chapter ${chapterId}`;
      const idText = `Hadits ${startHadithNum} – ${endHadithNum} • ${count} Hadits dalam ${bookName} ${chapterId === '0' ? 'Muqaddimah' : `Kitab ${chapterId}`}`;
      if (countMetaEn) countMetaEn.innerText = enText;
      if (countMetaId) countMetaId.innerText = idText;
      if (countMeta && !countMetaEn) countMeta.innerText = isIdLang ? idText : enText;
    } else {
      const enText = `Total ${allHadiths.length} Hadiths in ${bookName} Chapter ${chapterId}`;
      const idText = `Total ${allHadiths.length} Hadits dalam ${bookName} ${chapterId === '0' ? 'Muqaddimah' : `Kitab ${chapterId}`}`;
      if (countMetaEn) countMetaEn.innerText = enText;
      if (countMetaId) countMetaId.innerText = idText;
      if (countMeta && !countMetaEn) countMeta.innerText = isIdLang ? idText : enText;
    }
  }

  // Render Function
  function renderList() {
    if (!filteredHadiths || filteredHadiths.length === 0) {
      container.innerHTML = `
        <div class="p-8 text-center bg-surface dark:bg-[#1e293b] rounded-xl border border-outline-variant/20 dark:border-[#334155]">
          <span class="material-symbols-outlined text-outline dark:text-gray-500 text-4xl">search_off</span>
          <h3 class="mt-2 font-bold text-primary dark:text-white">${isIdLang ? 'Hadits Tidak Ditemukan' : 'No Hadiths found'}</h3>
          <p class="text-xs text-outline dark:text-gray-400 mt-1">${isIdLang ? 'Coba bersihkan kata kunci pencarian atau ubah lingkup pencarian.' : 'Try clearing your search query or changing search scope.'}</p>
        </div>
      `;
      if (pageIndicator) pageIndicator.innerText = `0 of 0`;
      if (prevBtn) prevBtn.disabled = true;
      if (nextBtn) nextBtn.disabled = true;
      return;
    }

    const totalPages = Math.ceil(filteredHadiths.length / pageSize);
    if (currentPage > totalPages) currentPage = totalPages;
    if (currentPage < 1) currentPage = 1;

    const startIdx = (currentPage - 1) * pageSize;
    const endIdx = Math.min(startIdx + pageSize, filteredHadiths.length);
    const pageItems = filteredHadiths.slice(startIdx, endIdx);

    let html = '';
    pageItems.forEach((item, idx) => {
      const num = item.hadith_number || (startIdx + idx + 1);
      const enText = item.text_en || '';
      const arText = item.text_ar || '';
      const hasId = !!item.text_id;
      const idText = item.text_id || enText;
      const grade = item.grade || 'Sahih';

      const isnadLink = `sanad.html?book=${bookId}&id=${num}`;
      const detailLink = `hadith.html?book=${bookId}&id=${num}`;

      let displayText = '';
      const isAhmedBaset = item._source === 'ahmedbaset';
      const isLidwa = item._source === 'lidwa';
      const isPrimary = !isAhmedBaset && !isLidwa;

      // Indonesian source transparency notes
      // Both primary (fawazahmed0) and AhmedBaset source Indonesian from Lidwa/Irsyad.
      // fawazahmed0 has NO ind edition — our local ind-*.json files are built from Lidwa data.

      // Primary/fawazahmed: subtle blue attribution (ID exists but comes from Lidwa)
      const primaryIdSourceNote = `<div class="mt-2 px-3 py-2 rounded-lg border border-blue-500/20 bg-blue-500/5 text-[11px] text-blue-600 dark:text-blue-400 leading-snug">
        <strong class="font-semibold">Sumber terjemahan Indonesia:</strong> fawazahmed0 CDN tidak memiliki edisi Bahasa Indonesia.
        Teks ini bersumber dari <strong>Lidwa / Irsyad</strong>, dicocokkan berdasarkan nomor hadits.
      </div>`;

      // AhmedBaset: amber warning (may not align to AhmedBaset narration variant)
      const abIdSourceNote = hasId
        ? `<div class="mt-2 px-3 py-2 rounded-lg border border-amber-500/30 bg-amber-500/5 text-[11px] text-amber-600 dark:text-amber-400 leading-snug">
        <strong class="font-semibold">Note — Indonesian translation source:</strong> AhmedBaset does not include Indonesian translations.
        The text below is sourced from <strong>Lidwa / Irsyad</strong>, matched by hadith number.
        It may not correspond perfectly to this AhmedBaset narration variant.
      </div>`
        : `<div class="mt-2 px-3 py-2 rounded-lg border border-amber-500/30 bg-amber-500/5 text-[11px] text-amber-600 dark:text-amber-400 leading-snug">
        <strong class="font-semibold">Note:</strong> AhmedBaset has no Indonesian translation, and no Lidwa match was found for this hadith number.
      </div>`;

      // Grade-by explanation helper
      const gradeByHtml = (gradedBy) => gradedBy
        ? `<p class="text-[11px] text-outline dark:text-gray-500 mt-1">Graded Sahih by: <em>${escapeHtml(gradedBy)}</em> <span class="opacity-60">(grading per Lidwa/Irsyad)</span></p>`
        : '';

      const idUnavailableNote = '<em class="text-outline dark:text-gray-500">(Terjemahan tidak tersedia untuk variasi sanad ini)</em>';

      if (currentLang === 'id') {
        const content = hasId ? escapeHtml(item.text_id) : idUnavailableNote;
        displayText = `<p class="text-sm text-on-surface-variant dark:text-gray-300 leading-relaxed font-body-md"><strong class="text-xs text-secondary dark:text-[#10b981] block mb-1">Terjemahan Indonesia:</strong>${content}</p>`;
        if (isPrimary) displayText += primaryIdSourceNote;
        if (isAhmedBaset) displayText += abIdSourceNote;
        if (isLidwa) displayText += gradeByHtml(item.grade_by);
      } else if (currentLang === 'en') {
        displayText = `<p class="text-sm text-on-surface-variant dark:text-gray-300 leading-relaxed font-body-md"><strong class="text-xs text-sunan-emerald dark:text-[#10b981] block mb-1">English Translation:</strong>${escapeHtml(enText)}</p>`;
        if (isPrimary) displayText += `<p class="text-[11px] text-blue-500/70 dark:text-blue-400/70 mt-1 italic">Switch to <strong>Dual Language</strong> or <strong>Bahasa Indonesia</strong> to view Indonesian — sourced from Lidwa/Irsyad (fawazahmed0 has no ind edition)</p>`;
        if (isAhmedBaset) displayText += `<p class="text-[11px] text-amber-600/80 dark:text-amber-400/70 mt-1 italic">Source: AhmedBaset · Switch to <strong>Dual Language</strong> or <strong>Bahasa Indonesia</strong> to see the Lidwa-sourced Indonesian translation (matched by number — not from AhmedBaset)</p>`;
        if (isLidwa) displayText += gradeByHtml(item.grade_by);
      } else {
        const idContent = hasId ? escapeHtml(item.text_id) : idUnavailableNote;
        const idHtml = `<p class="text-sm text-on-surface-variant dark:text-gray-300 leading-relaxed font-body-md"><strong class="text-xs text-secondary dark:text-[#10b981] block mb-1">Terjemahan Indonesia:</strong>${idContent}</p>`;
        const enHtml = enText ? `<p class="text-xs text-outline dark:text-gray-400 leading-relaxed font-body-md"><strong class="text-xs text-sunan-emerald dark:text-[#10b981] block mb-1">English Translation:</strong>${escapeHtml(enText)}</p>` : '';
        const gradeNote = isLidwa ? gradeByHtml(item.grade_by) : '';
        const sourceNote = isPrimary ? primaryIdSourceNote : (isAhmedBaset ? abIdSourceNote : '');
        displayText = `
          <div class="flex flex-col gap-3 pt-2 border-t border-outline-variant/10 dark:border-[#334155]">
            ${idHtml}${enHtml}${sourceNote}${gradeNote}
          </div>
        `;
      }

      html += `
        <div class="bg-surface dark:bg-[#1e293b] border border-outline-variant/30 dark:border-[#334155] rounded-xl p-6 flex flex-col gap-4 shadow-sm hover:border-secondary/40 dark:hover:border-[#10b981]/40 transition-all">
          <div class="flex justify-between items-center border-b border-outline-variant/20 dark:border-[#334155] pb-3">
            <div class="flex items-center gap-2">
              <span class="bg-primary dark:bg-[#10b981] text-white dark:text-black text-xs font-bold px-2.5 py-0.5 rounded uppercase">${escapeHtml(bookName)} #${num}</span>
              <span class="bg-sunan-emerald/10 text-sunan-emerald dark:text-[#10b981] text-xs font-semibold px-2.5 py-0.5 rounded">${escapeHtml(grade)}</span>
            </div>
            <button data-copy-hadith data-copy-share-btn data-hadith-title="${escapeHtml(bookName)} #${num}" data-copy-hadith-ar="${escapeHtml(arText)}" data-copy-hadith-text-id="${escapeHtml(idText)}" data-copy-hadith-text-en="${escapeHtml(enText)}" data-share-url="${window.location.origin + window.location.pathname.replace('hadith-list.html', '')}${detailLink}" class="btn-copy-share text-xs font-semibold px-2.5 py-1 rounded border border-outline-variant/40 dark:border-[#334155] text-primary dark:text-white hover:bg-surface-container-low dark:hover:bg-[#334155] transition-all flex items-center gap-1.5 cursor-pointer">
              <span class="material-symbols-outlined text-[14px]">share</span>
              <span data-lang-en>Copy / Share</span><span data-lang-id>Salin / Bagikan</span>
            </button>
          </div>

          ${arText ? `<p class="font-arabic-body text-2xl text-primary dark:text-white text-right leading-loose" dir="rtl">${escapeHtml(arText)}</p>` : ''}
          ${displayText}

          <div class="flex justify-between items-center pt-3 border-t border-outline-variant/10 dark:border-[#334155] text-xs">
            <a href="${isnadLink}" class="text-secondary dark:text-[#10b981] font-semibold hover:underline flex items-center gap-1">
              <span class="material-symbols-outlined text-sm">account_tree</span>
              <span data-lang-en>Inspect Sanad Chain</span><span data-lang-id>Telusuri Sanad</span>
            </a>
            <div class="flex items-center gap-2">
              <a href="${detailLink}" class="text-outline dark:text-gray-400 hover:text-primary dark:hover:text-white transition-colors">
                <span data-lang-en>Full Hadith & Commentary &rarr;</span><span data-lang-id>Hadits Selengkapnya & Pensyarahan &rarr;</span>
              </a>
            </div>
          </div>
        </div>
      `;
    });

    let transparencyFooter = '';
    const validBooksWithNote = ['bukhari', 'muslim'];
    
    if (validBooksWithNote.includes(bookId)) {
      const bookNames = {
        'bukhari': 'Sahih al-Bukhari (7,589 hadiths)',
        'muslim': 'Sahih Muslim (7,563 hadiths)'
      };
      const bookNamesId = {
        'bukhari': 'Shahih Bukhari (7.589 hadits)',
        'muslim': 'Shahih Muslim (7.563 hadits)'
      };
      
      transparencyFooter = `
        <div class="mt-8 p-4 bg-surface-variant/30 dark:bg-[#1e293b]/50 border border-outline-variant/40 dark:border-[#334155] rounded-xl text-xs text-outline dark:text-gray-400 text-center">
          <strong class="text-primary dark:text-white block mb-1"><span class="material-symbols-outlined text-sm inline-block align-middle mr-1">verified_user</span>Data Validity Note / Catatan Validitas Data:</strong>
          <span data-lang-en>The Arabic text and numbering for ${bookNames[bookId]} follow the global standard. The Indonesian translations are sourced from the verified Lidwa (Irsyadulibad) dataset and mapped using universal indexing. Hadiths without a direct Indonesian translation in the Lidwa dataset are marked as unavailable.</span><span data-lang-id class="hidden">Penomoran dan teks Arab untuk ${bookNamesId[bookId]} mengikuti standar global. Terjemahan bahasa Indonesia bersumber dari dataset Lidwa (Irsyadulibad) yang terverifikasi dan dipetakan menggunakan indeks universal. Hadits yang tidak memiliki terjemahan langsung dalam dataset Lidwa ditandai sebagai tidak tersedia.</span>
        </div>
      `;
    } else if (bookId === 'darimi') {
      transparencyFooter = `
        <div class="mt-8 p-4 bg-surface-variant/30 dark:bg-[#1e293b]/50 border border-outline-variant/40 dark:border-[#334155] rounded-xl text-xs text-outline dark:text-gray-400 text-center">
          <strong class="text-primary dark:text-white block mb-1"><span class="material-symbols-outlined text-sm inline-block align-middle mr-1">verified_user</span>Data Validity Note / Catatan Validitas Data:</strong>
          <span data-lang-en>Darimi numbering is based on standard structural groupings. Hadiths without a direct Indonesian translation are marked as unavailable.</span><span data-lang-id class="hidden">Penomoran Sunan Ad-Darimi didasarkan pada pengelompokan struktural standar. Hadits yang tidak memiliki terjemahan bahasa Indonesia secara langsung ditandai sebagai tidak tersedia.</span>
        </div>
      `;
    }
    html += transparencyFooter;

    container.innerHTML = html;
    LangSystem.apply(LangSystem.get());

    // Update Pagination UI
    const isId = (window.LangSystem && window.LangSystem.isIdMode());
    if (pageIndicator) {
      pageIndicator.innerText = isId
        ? `Menampilkan ${startIdx + 1}–${endIdx} dari ${filteredHadiths.length} Hadits (Hal ${currentPage} dari ${totalPages})`
        : `Showing ${startIdx + 1}–${endIdx} of ${filteredHadiths.length} Ahadith (Page ${currentPage} of ${totalPages})`;
    }
    if (prevBtn) prevBtn.disabled = (currentPage <= 1);
    if (nextBtn) nextBtn.disabled = (currentPage >= totalPages);

    const jumpInput = document.getElementById('jump-page-input');
    if (jumpInput) {
      jumpInput.min = 1;
      jumpInput.max = totalPages;
      jumpInput.value = currentPage;
      jumpInput.placeholder = currentPage;
    }
  }

  // Filter/Search Logic
  async function performFilter() {
    const q = (searchInput ? searchInput.value : '').trim().toLowerCase();
    searchScope = scopeSelect ? scopeSelect.value : 'chapter';

    if (!q) {
      filteredHadiths = [...allHadiths];
    } else if (searchScope === 'global') {
      if (window.HadeethAPI) {
        const results = await window.HadeethAPI.search(q, 50);
        filteredHadiths = results.map(r => ({
          hadith_number: r.hadith_number || r.id,
          text_en: r.primary_translation || r.english_text || '',
          text_ar: r.arabic_text || '',
          text_id: r.indonesian_text || '',
          grade: r.grade || 'Sahih',
          book_id: r.book_slug || 'bukhari'
        }));
      }
    } else {
      // Chapter filter
      filteredHadiths = allHadiths.filter(h => {
        const numStr = String(h.hadith_number || '');
        const ar = (h.text_ar || '').toLowerCase();
        const en = (h.text_en || '').toLowerCase();
        const id = (h.text_id || '').toLowerCase();
        return numStr === q || ar.includes(q) || en.includes(q) || id.includes(q);
      });
    }

    currentPage = 1;
    renderList();
  }

  // Event Listeners
  if (searchInput) {
    searchInput.addEventListener('keyup', (e) => {
      if (e.key === 'Enter') performFilter();
    });
  }
  if (scopeSelect) scopeSelect.addEventListener('change', performFilter);

  if (langSelect) {
    langSelect.addEventListener('change', () => {
      currentLang = langSelect.value;
      renderList();
    });
  }

  if (pageSizeSelect) {
    pageSizeSelect.addEventListener('change', () => {
      pageSize = parseInt(pageSizeSelect.value) || 10;
      currentPage = 1;
      renderList();
    });
  }

  if (prevBtn) {
    prevBtn.addEventListener('click', () => {
      if (currentPage > 1) {
        currentPage--;
        renderList();
        window.scrollTo({ top: 0, behavior: 'smooth' });
      }
    });
  }

  if (nextBtn) {
    nextBtn.addEventListener('click', () => {
      const totalPages = Math.ceil(filteredHadiths.length / pageSize);
      if (currentPage < totalPages) {
        currentPage++;
        renderList();
        window.scrollTo({ top: 0, behavior: 'smooth' });
      }
    });
  }

  const jumpInput = document.getElementById('jump-page-input');
  const jumpBtn = document.getElementById('jump-page-btn');

  function handleJump() {
    if (!jumpInput) return;
    const target = parseInt(jumpInput.value);
    const totalPages = Math.ceil(filteredHadiths.length / pageSize) || 1;
    if (target && target >= 1 && target <= totalPages) {
      currentPage = target;
      renderList();
      window.scrollTo({ top: 300, behavior: 'smooth' });
    } else if (target > totalPages) {
      currentPage = totalPages;
      renderList();
      window.scrollTo({ top: 300, behavior: 'smooth' });
    }
  }

  if (jumpBtn) jumpBtn.addEventListener('click', handleJump);
  if (jumpInput) {
    jumpInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') handleJump();
    });
  }

  renderList();
}

/**
 * Load Chapters List dynamically for Kitab view across all 9 canonical books
 * Branches based on active dataset: primary | native_ahmedbaset | native_lidwa
 */
async function loadChaptersList() {
  const container = document.getElementById('chapters-list-container');
  if (!container) return;

  const params = new URLSearchParams(window.location.search);
  const bookId = (params.get('book') || 'bukhari').toLowerCase();

  const bookMasterDict = {
    bukhari: {
      name: 'Sahih al-Bukhari',
      ar: 'صحيح البخاري',
      author: 'Imam al-Bukhari',
      authorId: 'rawi_bukhari',
      type: "Jami'",
      badgeClass: 'bg-blue-700 text-white',
      desc: 'Recognized across Islamic scholarship as the supreme Jami collection of Hadith, compiled with unmatched authentication criteria.',
      desc_id: "Diakui oleh seluruh ulama Islam sebagai koleksi Jami' tertinggi dari Hadits, disusun dengan kriteria otentikasi yang tak tertandingi.",
      kitabCount: '📚 97 Kitab',
      hadithCount: '📖 7.563 Hadits',
      authenticity: '⭐️ 100% Sahih',
      datasetInfo: {
        primary:           { kitab: '📚 97 Kitab', hadith: '📖 7.563 Hadits (Darussalam)', numbering: 'Penomoran: Darussalam (1–7563)' },
        native_ahmedbaset: { kitab: '📚 97 Kitab', hadith: '📖 7.277 Hadits (AhmedBaset)', numbering: 'Penomoran: AhmedBaset idInBook (1–7277)' },
        native_lidwa:      { kitab: '📚 98 Kitab', hadith: '📖 7.589 Hadits (Lidwa)', numbering: 'Penomoran: Lidwa / Irsyad (1–7589)' }
      }
    },
    muslim: {
      name: 'Sahih Muslim',
      ar: 'صحيح مسلم',
      author: 'Imam Muslim ibn al-Hajjaj',
      authorId: 'rawi_muslim',
      type: "Jami'",
      badgeClass: 'bg-blue-700 text-white',
      desc: 'Masterpiece Jami collection renowned for strict thematic organization and comprehensive parallel chains of narration (turuq).',
      desc_id: "Koleksi Jami' terbaik yang terkenal dengan organisasi tematik yang ketat dan rantai periwayatan paralel (turuq) yang komprehensif.",
      kitabCount: '📚 57 Kitab',
      hadithCount: '📖 7.563 Hadits',
      authenticity: '⭐️ 100% Sahih',
      datasetInfo: {
        primary:           { kitab: '📚 57 Kitab', hadith: '📖 7.563 Hadits (Darussalam)', numbering: 'Penomoran: Darussalam (1–7563)' },
        native_ahmedbaset: { kitab: '📚 56 Kitab', hadith: '📖 7.459 Hadits (AhmedBaset)', numbering: 'Penomoran: AhmedBaset idInBook (1–7459)' },
        native_lidwa:      { kitab: '📚 —', hadith: '📖 7.563 Hadits (Lidwa)', numbering: 'Penomoran: Lidwa (1–7563) · tidak ada pembagian kitab dari sumber Lidwa' }
      }
    },
    tirmidhi: {
      name: "Jami' al-Tirmidhi",
      ar: 'جامع الترمذي',
      author: "Imam Abu 'Isa al-Tirmidhi",
      authorId: 'rawi_al_tirmidhi',
      type: "Jami'",
      badgeClass: 'bg-blue-700 text-white',
      desc: 'Famous Jami collection featuring explicit grading of narrations (Sahih, Hasan, Gharib) and legal opinions of early jurists.',
      desc_id: "Koleksi Jami' yang terkenal dengan penilaian hadits secara eksplisit (Sahih, Hasan, Gharib) dan pendapat hukum ulama awal.",
      kitabCount: '📚 49 Kitab',
      hadithCount: '📖 3.956 Hadits',
      authenticity: "⭐️ Jami' Tergrading",
      datasetInfo: {
        primary:           { kitab: '📚 49 Kitab', hadith: '📖 3.956 Hadits (Darussalam)', numbering: 'Penomoran: Darussalam (1–3956)' },
        native_ahmedbaset: { kitab: '📚 49 Kitab', hadith: '📖 3.956 Hadits (AhmedBaset)', numbering: 'Penomoran: AhmedBaset idInBook (1–3956)' },
        native_lidwa:      { kitab: '📚 49 Kitab', hadith: '📖 3.956 Hadits (Lidwa)', numbering: 'Penomoran: Lidwa / Irsyad (1–3956)' }
      }
    },
    abudawud: {
      name: 'Sunan Abu Dawood',
      ar: 'سنن أبي داود',
      author: 'Imam Abu Dawood al-Sijistani',
      authorId: 'rawi_abu_dawud',
      type: 'Sunan',
      badgeClass: 'bg-indigo-600 text-white',
      desc: 'Primarily focuses on legal rulings (Ahkam) used as foundational evidence by jurists across Sunni Fiqh schools.',
      desc_id: 'Terutama berfokus pada hukum fiqih (Ahkam) yang digunakan sebagai dalil pokok oleh para ulama Fiqih Sunni.',
      kitabCount: '📚 43 Kitab',
      hadithCount: '📖 5.274 Hadits',
      authenticity: '⭐️ Korpus Sunan',
      datasetInfo: {
        primary:           { kitab: '📚 43 Kitab', hadith: '📖 5.274 Hadits (Darussalam)', numbering: 'Penomoran: Darussalam (1–5274)' },
        native_ahmedbaset: { kitab: '📚 43 Kitab', hadith: '📖 5.274 Hadits (AhmedBaset)', numbering: 'Penomoran: AhmedBaset idInBook (1–5274)' },
        native_lidwa:      { kitab: '📚 43 Kitab', hadith: '📖 5.274 Hadits (Lidwa)', numbering: 'Penomoran: Lidwa / Irsyad (1–5274)' }
      }
    },
    nasai: {
      name: "Sunan an-Nasa'i",
      ar: 'سنن النسائي',
      author: "Imam Ahmad an-Nasa'i",
      authorId: 'rawi_al_nasai',
      type: 'Sunan',
      badgeClass: 'bg-indigo-600 text-white',
      desc: 'Possesses the strictest authentication criteria among the Sunan books, second only to the Sahihain.',
      desc_id: 'Memiliki kriteria otentikasi paling ketat di antara kitab Sunan, hanya di bawah dua kitab Shahih.',
      kitabCount: '📚 52 Kitab',
      hadithCount: '📖 5.758 Hadits',
      authenticity: '⭐️ Otentisitas Tinggi',
      datasetInfo: {
        primary:           { kitab: '📚 52 Kitab', hadith: '📖 5.758 Hadits (Darussalam)', numbering: 'Penomoran: Darussalam (1–5758)' },
        native_ahmedbaset: { kitab: '📚 51 Kitab', hadith: '📖 5.758 Hadits (AhmedBaset)', numbering: 'Penomoran: AhmedBaset idInBook (1–5758)' },
        native_lidwa:      { kitab: '📚 51 Kitab', hadith: '📖 5.758 Hadits (Lidwa)', numbering: 'Penomoran: Lidwa / Irsyad (1–5758)' }
      }
    },
    ibnmajah: {
      name: 'Sunan Ibn Majah',
      ar: 'سنن ابن ماجه',
      author: 'Imam Ibn Majah al-Qazwini',
      authorId: 'rawi_ibn_majah',
      type: 'Sunan',
      badgeClass: 'bg-indigo-600 text-white',
      desc: "Renowned for systematic arrangement and unique narrations (zawa'id) expanding Islamic jurisprudence.",
      desc_id: "Terkenal dengan susunan sistematis dan periwayatan unik (zawa'id) yang memperluas khazanah fiqih Islam.",
      kitabCount: '📚 37 Kitab',
      hadithCount: '📖 4.341 Hadits',
      authenticity: '⭐️ Korpus Sunan',
      datasetInfo: {
        primary:           { kitab: '📚 37 Kitab', hadith: '📖 4.341 Hadits (Darussalam)', numbering: 'Penomoran: Darussalam (1–4341)' },
        native_ahmedbaset: { kitab: '📚 37 Kitab', hadith: '📖 4.341 Hadits (AhmedBaset)', numbering: 'Penomoran: AhmedBaset idInBook (1–4341)' },
        native_lidwa:      { kitab: '📚 37 Kitab', hadith: '📖 4.341 Hadits (Lidwa)', numbering: 'Penomoran: Lidwa / Irsyad (1–4341)' }
      }
    },
    malik: {
      name: 'Muwatta Malik',
      ar: 'موطأ مالك',
      author: 'Imam Malik ibn Anas',
      authorId: 'rawi_malik',
      type: 'Mushannaf',
      badgeClass: 'bg-amber-600 text-white',
      desc: 'The earliest surviving legal Mushannaf text of Islam, combining prophetic Hadiths with judicial rulings of Madinah.',
      desc_id: 'Teks Mushannaf fiqih tertua yang masih ada dalam Islam, menggabungkan Hadits Nabi dengan keputusan hukum ulama Madinah.',
      kitabCount: '📚 56 Kitab',
      hadithCount: '📖 1.720 Hadits',
      authenticity: '⭐️ Imam Hijaz',
      datasetInfo: {
        primary:           { kitab: '📚 56 Kitab', hadith: '📖 1.858 Hadits (Darussalam)', numbering: 'Penomoran: Darussalam (1–1858)' },
        native_ahmedbaset: { kitab: '📚 61 Kitab', hadith: '📖 1.858 Hadits (AhmedBaset)', numbering: 'Penomoran: AhmedBaset idInBook (1–1858) · 61 kitab (5 lebih banyak dari DB primer)' },
        native_lidwa:      { kitab: '📚 56 Kitab', hadith: '📖 1.720 Hadits (Lidwa)', numbering: 'Penomoran: Lidwa / Irsyad (1–1720) · beberapa hadits dikelompokkan' }
      }
    },
    ahmad: {
      name: 'Musnad Ahmad',
      ar: 'مسند أحمد بن حنبل',
      author: 'Imam Ahmad ibn Hanbal',
      authorId: 'rawi_ahmad',
      type: 'Musnad',
      badgeClass: 'bg-purple-700 text-white',
      desc: 'The massive encyclopedic Musnad arranged companion by companion (Sahabi), containing over 27,000 narrations.',
      desc_id: 'Musnad ensiklopedis yang sangat besar, disusun berdasarkan sahabat per sahabat (Sahabi), berisi lebih dari 27.000 riwayat.',
      kitabCount: '📚 Sistem Musnad',
      hadithCount: '📖 27.647 Hadits',
      authenticity: '⭐️ Korpus Ensiklopedis',
      datasetInfo: {
        primary:           { kitab: '📚 7 Bagian Musnad', hadith: '📖 27.647 Hadits (Darussalam)', numbering: 'Penomoran: Darussalam (1–27647)' },
        native_ahmedbaset: { kitab: '📚 8 Bagian Musnad', hadith: '📖 27.647 Hadits (AhmedBaset)', numbering: 'Penomoran: AhmedBaset idInBook (1–27647) · 8 bagian musnad' },
        native_lidwa:      { kitab: '📚 Susunan Musnad', hadith: '📖 27.519 Hadits (Lidwa)', numbering: 'Penomoran: Lidwa / Irsyad (1–27519) · susunan musnad' }
      }
    },
    darimi: {
      name: 'Sunan ad-Darimi',
      ar: 'سنن الدارمي',
      author: 'Imam Abdullah bin Abdul Rahman ad-Darimi',
      authorId: 'rawi_darimi',
      type: 'Sunan',
      badgeClass: 'bg-indigo-600 text-white',
      desc: 'Highly respected Hadith collection with rigorous standards, frequently considered alongside the Kutub al-Sittah.',
      desc_id: 'Koleksi Hadits yang sangat dihormati dengan standar ketat, sering dianggap setara dengan Kutub al-Sittah.',
      kitabCount: '📚 24 Kitab',
      hadithCount: '📖 3.367 Hadits',
      authenticity: '⭐️ Korpus Sunan',
      datasetInfo: {
        primary:           { kitab: '📚 24 Kitab', hadith: '📖 3.367 Hadits (Darussalam)', numbering: 'Penomoran: Darussalam (1–3367)' },
        native_ahmedbaset: { kitab: '📚 24 Kitab', hadith: '📖 3.367 Hadits (AhmedBaset)', numbering: 'Penomoran: AhmedBaset idInBook (1–3367)' },
        native_lidwa:      { kitab: '📚 24 Kitab', hadith: '📖 3.367 Hadits (Lidwa)', numbering: 'Penomoran: Lidwa / Irsyad (1–3367)' }
      }
    },
    nawawi: {
      name: 'Forty Nawawi',
      ar: 'الأربعون النووية',
      author: 'Imam Yahya ibn Sharaf al-Nawawi',
      authorId: 'rawi_nawawi',
      type: "Jawami' al-Kalim",
      badgeClass: 'bg-emerald-700 text-white',
      desc: "Essential collection of 42 foundational narrations encapsulating Jawami' al-Kalim (concise comprehensive prophetic guidance).",
      desc_id: "Koleksi esensial 42 riwayat fondasi yang mencakup Jawami' al-Kalim (bimbingan Nabi yang ringkas dan menyeluruh).",
      kitabCount: '📚 1 Jilid',
      hadithCount: '📖 42 Hadits',
      authenticity: "⭐️ Jawami' al-Kalim",
      datasetInfo: {
        primary:      { kitab: '📚 1 Jilid', hadith: '📖 42 Hadits (Darussalam)', numbering: 'Penomoran: Darussalam (1–42)' },
        native_lidwa: { kitab: '📚 1 Jilid', hadith: '📖 42 Hadits (Lidwa)', numbering: 'Penomoran: Lidwa / Irsyad (1–42)' }
      }
    },
    tabarani_kabir: {
      name: "Al-Mu'jam al-Kabir",
      ar: 'المعجم الكبير للطبراني',
      author: 'Imam Al-Tabarani',
      authorId: 'rawi_tabarani',
      type: "Mu'jam",
      badgeClass: 'bg-blue-700 text-white',
      desc: "Monumental Mu'jam collection arranged according to the names of Companion narrators in alphabetical order.",
      desc_id: "Koleksi Mu'jam monumental yang disusun berdasarkan nama perawi Sahabat secara alfabetis.",
      kitabCount: '📚 25 Jilid',
      hadithCount: '📖 20.000+ Hadits',
      authenticity: '⭐️ Kerangka',
      datasetInfo: { primary: { kitab: '📚 25 Jilid', hadith: '📖 20.000+ Hadits', numbering: 'Dataset dalam pengembangan' } }
    },
    ibn_abi_shaybah: {
      name: 'Musannaf Ibn Abi Shaybah',
      ar: 'مصنف ابن أبي شيبة',
      author: 'Imam Ibn Abi Shaybah',
      authorId: 'rawi_ibn_abi_shaybah',
      type: 'Mushannaf',
      badgeClass: 'bg-amber-600 text-white',
      desc: "Encyclopedic Mushannaf collection preserving Marfu', Mauquf, and Maqtu' traditions ordered by Fiqh topics.",
      desc_id: "Koleksi Mushannaf ensiklopedis yang melestarikan tradisi Marfu', Mauquf, dan Maqtu' berdasarkan topik Fiqih.",
      kitabCount: '📚 37 Kitab',
      hadithCount: '📖 37.000+ Hadits',
      authenticity: '⭐️ Kerangka',
      datasetInfo: { primary: { kitab: '📚 37 Kitab', hadith: '📖 37.000+ Hadits', numbering: 'Dataset dalam pengembangan' } }
    }
  };
    const meta = bookMasterDict[bookId] || {
    name: bookId.toUpperCase(),
    ar: bookId,
    author: 'Author Sheikh',
    authorId: 'rawi_bukhari',
    type: 'Hadith Book',
    badgeClass: 'bg-primary text-white',
    desc: 'Authentic Hadith collection preserved in canonical digital manuscripts.',
    kitabCount: '📚 Index',
    hadithCount: '📖 Canonical Corpus',
    authenticity: '⭐️ Verified'
  };

  // Update DOM Elements
  document.title = `${meta.name} - HADEETH.ID`;
  const bcBook = document.querySelector('[data-breadcrumb-book]');
  const badgeElem = document.querySelector('[data-book-badge]');
  const authorLink = document.querySelector('[data-author-profile-link]');
  const titleElem = document.querySelector('[data-book-title]');
  const descElem = document.querySelector('[data-book-desc]');
  const kitabCountElem = document.querySelector('[data-book-kitab-count]');
  const hadithCountElem = document.querySelector('[data-book-hadith-count]');
  const authElem = document.querySelector('[data-book-authenticity]');
  const arTitleElem = document.querySelector('[data-book-arabic-title]');

  if (bcBook) bcBook.innerText = meta.name;
  if (badgeElem) {
    badgeElem.innerText = meta.type;
    badgeElem.className = `${meta.badgeClass} px-2.5 py-0.5 rounded text-xs font-bold uppercase tracking-wider`;
  }
  if (authorLink) {
    authorLink.href = `profile-detail.html?id=${meta.authorId}`;
    authorLink.innerText = `By ${meta.author} →`;
  }
  if (titleElem) titleElem.innerText = meta.name;

  // Bilingual description
  const descEnElem = document.querySelector('[data-book-desc-en]');
  const descIdElem = document.querySelector('[data-book-desc-id]');
  if (descEnElem) descEnElem.innerText = meta.desc;
  if (descIdElem) descIdElem.innerText = meta.desc_id || meta.desc;
  // Legacy fallback (if old [data-book-desc] still present)
  if (descElem) descElem.innerText = meta.desc;

  if (authElem) authElem.innerText = meta.authenticity;
  if (arTitleElem) arTitleElem.innerText = meta.ar;

  // Render dataset banner BEFORE chapter listing
  renderDatasetBanner(bookId, 'dataset-banner');

  const activeDataset = localStorage.getItem('dataset_version') || 'primary';

  // Validate dataset availability for this book
  const dsConfig = BOOK_DATASETS[bookId] || [];
  const validDs = dsConfig.find(d => d.id === activeDataset);
  const resolvedDataset = validDs ? activeDataset : 'primary';

  // Apply dataset-specific counts to info card
  const dsInfo = (meta.datasetInfo || {})[resolvedDataset] || (meta.datasetInfo || {}).primary || {};
  if (kitabCountElem) kitabCountElem.innerText = dsInfo.kitab || meta.kitabCount;
  if (hadithCountElem) hadithCountElem.innerText = dsInfo.hadith || meta.hadithCount;
  const datasetInfoElem = document.querySelector('[data-book-dataset-info]');
  if (datasetInfoElem && dsInfo.numbering) {
    datasetInfoElem.innerText = dsInfo.numbering;
    datasetInfoElem.style.display = '';
  }

  // ================================================================
  // BRANCH A — Primary (Darussalam / fawazahmed0)
  // Reads from data/chapters/<book>.json (pre-indexed)
  // ================================================================
  if (resolvedDataset === 'primary') {
    let chapters = await window.HadeethAPI.getChapters(bookId);

    // Default Chapter Skeletons for Books without pre-generated JSON files
    if (!chapters || chapters.length === 0) {
      if (bookId === 'muslim') {
        chapters = [
          { chapter_number: 1, name_en: 'Belief (Kitab al-Iman)', name_ar: 'كتاب الإيمان', hadith_range: 'Hadith 1 – 222' },
          { chapter_number: 2, name_en: 'Purification (Kitab al-Taharah)', name_ar: 'كتاب الطهارة', hadith_range: 'Hadith 223 – 376' },
          { chapter_number: 3, name_en: 'Menstruation (Kitab al-Hayd)', name_ar: 'كتاب الحيض', hadith_range: 'Hadith 377 – 511' },
          { chapter_number: 4, name_en: 'Prayer (Kitab al-Salah)', name_ar: 'كتاب الصلاة', hadith_range: 'Hadith 512 – 1160' },
          { chapter_number: 5, name_en: 'Zakat (Kitab al-Zakat)', name_ar: 'كتاب الزكاة', hadith_range: 'Hadith 1161 – 1438' },
          { chapter_number: 6, name_en: 'Fasting (Kitab al-Siyam)', name_ar: 'كتاب الصيام', hadith_range: 'Hadith 1439 – 1660' },
          { chapter_number: 7, name_en: 'Pilgrimage (Kitab al-Hajj)', name_ar: 'كتاب الحج', hadith_range: 'Hadith 1661 – 1912' },
          { chapter_number: 8, name_en: 'Marriage (Kitab al-Nikah)', name_ar: 'كتاب النكاح', hadith_range: 'Hadith 1913 – 2120' }
        ];
      } else if (bookId === 'abudawud') {
        chapters = [
          { chapter_number: 1, name_en: 'Purification (Kitab al-Taharah)', name_ar: 'كتاب الطهارة', hadith_range: 'Hadith 1 – 390' },
          { chapter_number: 2, name_en: 'Prayer (Kitab al-Salah)', name_ar: 'كتاب الصلاة', hadith_range: 'Hadith 391 – 1555' },
          { chapter_number: 3, name_en: 'Zakat (Kitab al-Zakat)', name_ar: 'كتاب الزكاة', hadith_range: 'Hadith 1556 – 1700' },
          { chapter_number: 4, name_en: 'Commercial Transactions (Kitab al-Buyu)', name_ar: 'كتاب البيوع', hadith_range: 'Hadith 3326 – 3415' }
        ];
      } else if (bookId === 'tirmidhi') {
        chapters = [
          { chapter_number: 1, name_en: 'Purification (Kitab al-Taharah)', name_ar: 'كتاب الطهارة', hadith_range: 'Hadith 1 – 148' },
          { chapter_number: 2, name_en: 'Prayer (Kitab al-Salah)', name_ar: 'كتاب الصلاة', hadith_range: 'Hadith 149 – 451' },
          { chapter_number: 3, name_en: 'Zakat (Kitab al-Zakat)', name_ar: 'كتاب الزكاة', hadith_range: 'Hadith 617 – 681' }
        ];
      } else if (bookId === 'nasai') {
        chapters = [
          { chapter_number: 1, name_en: 'Purification (Kitab al-Taharah)', name_ar: 'كتاب الطهارة', hadith_range: 'Hadith 1 – 324' },
          { chapter_number: 2, name_en: 'Water (Kitab al-Miyaah)', name_ar: 'كتاب المياه', hadith_range: 'Hadith 325 – 347' },
          { chapter_number: 3, name_en: 'Prayer (Kitab al-Salah)', name_ar: 'كتاب الصلاة', hadith_range: 'Hadith 494 – 1432' }
        ];
      } else if (bookId === 'ibnmajah') {
        chapters = [
          { chapter_number: 1, name_en: 'Sunnah & Creed (Kitab al-Muqaddimah)', name_ar: 'المقدمة', hadith_range: 'Hadith 1 – 266' },
          { chapter_number: 2, name_en: 'Purification (Kitab al-Taharah)', name_ar: 'كتاب الطهارة', hadith_range: 'Hadith 267 – 666' }
        ];
      } else if (bookId === 'malik') {
        chapters = [
          { chapter_number: 1, name_en: 'Prayer Times (Kitab Wuqut al-Salah)', name_ar: 'وقوت الصلاة', hadith_range: 'Hadith 1 – 31' },
          { chapter_number: 2, name_en: 'Purity (Kitab al-Taharah)', name_ar: 'كتاب الطهارة', hadith_range: 'Hadith 32 – 146' }
        ];
      } else if (bookId === 'darimi') {
        chapters = [
          { chapter_number: 1, name_en: 'Muqaddimah (Introduction)', name_ar: 'المقدمة', hadith_range: 'Hadith 1 – 649' },
          { chapter_number: 2, name_en: 'Purification (Taharah)', name_ar: 'كتاب الطهارة', hadith_range: 'Hadith 650 – 1159' },
          { chapter_number: 3, name_en: 'Prayer (Salah)', name_ar: 'كتاب الصلاة', hadith_range: 'Hadith 1160 – 1578' },
          { chapter_number: 4, name_en: 'Charity (Zakat)', name_ar: 'كتاب الزكاة', hadith_range: 'Hadith 1579 – 1637' },
          { chapter_number: 5, name_en: 'Fasting (Sawm)', name_ar: 'كتاب الصوم', hadith_range: 'Hadith 1638 – 1735' },
          { chapter_number: 6, name_en: 'Pilgrimage (Manasik)', name_ar: 'كتاب المناسك', hadith_range: 'Hadith 1736 – 1888' },
          { chapter_number: 7, name_en: 'Sacrifices (Adahi)', name_ar: 'كتاب الأضاحي', hadith_range: 'Hadith 1889 – 1943' },
          { chapter_number: 8, name_en: 'Hunting (Sayd)', name_ar: 'كتاب الصيد', hadith_range: 'Hadith 1944 – 1959' },
          { chapter_number: 9, name_en: "Food (At'imah)", name_ar: 'كتاب الأطعمة', hadith_range: 'Hadith 1960 – 2022' },
          { chapter_number: 10, name_en: 'Drinks (Ashribah)', name_ar: 'كتاب الأشربة', hadith_range: 'Hadith 2023 – 2071' },
          { chapter_number: 11, name_en: "Dreams (Ru'ya)", name_ar: 'كتاب الرؤيا', hadith_range: 'Hadith 2072 – 2098' },
          { chapter_number: 12, name_en: 'Marriage (Nikah)', name_ar: 'كتاب النكاح', hadith_range: 'Hadith 2099 – 2190' },
          { chapter_number: 13, name_en: 'Divorce (Talaq)', name_ar: 'كتاب الطلاق', hadith_range: 'Hadith 2191 – 2222' },
          { chapter_number: 14, name_en: 'Punishments (Hudud)', name_ar: 'كتاب الحدود', hadith_range: 'Hadith 2223 – 2255' },
          { chapter_number: 15, name_en: 'Vows and Oaths (Nudhur)', name_ar: 'كتاب النذور والأيمان', hadith_range: 'Hadith 2256 – 2273' },
          { chapter_number: 16, name_en: 'Blood Money (Diyat)', name_ar: 'كتاب الديات', hadith_range: 'Hadith 2274 – 2311' },
          { chapter_number: 17, name_en: 'Jihad', name_ar: 'كتاب الجهاد', hadith_range: 'Hadith 2312 – 2359' },
          { chapter_number: 18, name_en: 'Expeditions (Siyar)', name_ar: 'كتاب السير', hadith_range: 'Hadith 2360 – 2450' },
          { chapter_number: 19, name_en: "Trade (Buyu')", name_ar: 'كتاب البيوع', hadith_range: 'Hadith 2451 – 2547' },
          { chapter_number: 20, name_en: "Permission (Isti'dhan)", name_ar: 'كتاب الاستئذان', hadith_range: 'Hadith 2548 – 2622' },
          { chapter_number: 21, name_en: 'Heart-Melting Traditions (Riqaq)', name_ar: 'كتاب الرقاق', hadith_range: 'Hadith 2623 – 2759' },
          { chapter_number: 22, name_en: "Inheritance (Fara'id)", name_ar: 'كتاب الفرائض', hadith_range: 'Hadith 2760 – 3084' },
          { chapter_number: 23, name_en: 'Wills (Wasiyyah)', name_ar: 'كتاب الوصايا', hadith_range: 'Hadith 3085 – 3210' },
          { chapter_number: 24, name_en: "Virtues of Qur'an (Fada'il al-Qur'an)", name_ar: 'كتاب فضائل القرآن', hadith_range: 'Hadith 3211 – 3367' }
        ];
      } else if (bookId === 'ahmad') {
        chapters = [
          { chapter_number: 1, name_en: 'Musnad of 10 Promised Companions', name_ar: 'مسند العشرة المبشرين بالجنة', hadith_range: 'Hadith 1 – 1380' },
          { chapter_number: 2, name_en: 'Musnad of Ahl al-Bayt', name_ar: 'مسند أهل البيت', hadith_range: 'Hadith 1381 – 3500' }
        ];
      } else {
        chapters = [
          { chapter_number: 1, name_en: `${meta.name} - Chapter 1`, name_ar: 'الفصل الأول', hadith_range: 'Chapter Index' }
        ];
      }
    }

    let html = '';
    chapters.forEach((ch, idx) => {
      const chNum = ch.chapter_number !== undefined && ch.chapter_number !== null && ch.chapter_number !== '' ? ch.chapter_number : (idx + 1);
      const titleEn = ch.title_en || ch.name_en || ch.title || `Chapter ${chNum}`;
      const titleId = ch.title_id || ch.name_id || titleEn;
      const titleAr = ch.title_ar || ch.name_ar || ch.arabic || '';
      const hadithRange = ch.hadith_range
        || (ch.hadith_start != null ? `Hadith ${ch.hadith_start} – ${ch.hadith_end}` : `Chapter ${chNum}`);
      const hadithCount = ch.hadith_count != null ? ch.hadith_count
        : (ch.hadith_end && ch.hadith_start ? (ch.hadith_end - ch.hadith_start + 1) : '');

      html += `
        <a href="hadith-list.html?book=${bookId}&chapter=${chNum}" class="group bg-surface dark:bg-[#1e293b] border border-outline-variant/20 dark:border-[#334155] hover:border-secondary dark:hover:border-[#10b981] rounded-xl p-5 transition-all flex justify-between items-center card-lift">
          <div class="flex gap-4 items-center">
            <div class="w-10 h-10 rounded-full bg-secondary/10 dark:bg-[#10b981]/10 text-secondary dark:text-[#10b981] font-bold text-sm flex items-center justify-center flex-shrink-0">${chNum === 0 || chNum === '0' ? 'M' : chNum}</div>
            <div class="flex flex-col gap-0.5">
              <span class="text-xs text-outline dark:text-gray-400 font-semibold">${escapeHtml(hadithRange)}${hadithCount ? ` &bull; ${hadithCount} hadiths` : ''}</span>
              <h3 class="font-bold text-base text-primary dark:text-white group-hover:text-secondary dark:group-hover:text-[#10b981]" data-lang-en>${escapeHtml(titleEn)}</h3>
              <h3 class="font-bold text-base text-primary dark:text-white group-hover:text-secondary dark:group-hover:text-[#10b981]" data-lang-id style="display:none">${escapeHtml(titleId)}</h3>
              ${titleAr ? `<span class="text-xs text-on-surface-variant dark:text-gray-400 font-arabic-body" dir="rtl">${escapeHtml(titleAr)}</span>` : ''}
            </div>
          </div>
          <span class="material-symbols-outlined text-outline dark:text-gray-400 group-hover:text-primary dark:group-hover:text-white">arrow_forward</span>
        </a>
      `;
    });
    container.innerHTML = html;
    LangSystem.apply(LangSystem.get());

  // ================================================================
  // BRANCH B — AhmedBaset (native Arabic + EN, no ID)
  // Reads from data/sources/ahmedbaset/by_book/the_9_books/<book>.json
  // ================================================================
  } else if (resolvedDataset === 'native_ahmedbaset') {
    const abBookMap = { ahmad: 'ahmed' };
    const abBook = abBookMap[bookId] || bookId;
    let abData = null;
    try {
      const resp = await fetch(`data/sources/ahmedbaset/by_book/the_9_books/${abBook}.json`);
      if (resp.ok) abData = await resp.json();
    } catch(e) { console.warn('AhmedBaset fetch error:', e); }

    if (!abData || !abData.chapters) {
      container.innerHTML = `<div class="col-span-2 py-12 text-center text-outline dark:text-gray-400">
        <span class="material-symbols-outlined text-4xl block mb-2">info</span>
        <p>AhmedBaset chapter data not available for <strong>${bookId}</strong>.</p>
      </div>`;
    } else {
      // Build hadith count per chapter from hadiths array
      const chCounts = {};
      (abData.hadiths || []).forEach(h => {
        chCounts[h.chapterId] = (chCounts[h.chapterId] || 0) + 1;
      });

      let html = '';
      abData.chapters.forEach((ch, idx) => {
        const chNum = ch.id;
        const titleEn = ch.english || `Chapter ${chNum}`;
        const titleAr = ch.arabic || '';
        const count = chCounts[chNum] || 0;

        html += `
          <a href="hadith-list.html?book=${bookId}&chapter=${chNum}&dataset=native_ahmedbaset" class="group bg-surface dark:bg-[#1e293b] border border-outline-variant/20 dark:border-[#334155] hover:border-secondary dark:hover:border-[#10b981] rounded-xl p-5 transition-all flex justify-between items-center card-lift">
            <div class="flex gap-4 items-center">
              <div class="w-10 h-10 rounded-full bg-secondary/10 dark:bg-[#10b981]/10 text-secondary dark:text-[#10b981] font-bold text-sm flex items-center justify-center flex-shrink-0">${chNum}</div>
              <div class="flex flex-col gap-0.5">
                <span class="text-xs text-outline dark:text-gray-400 font-semibold">AhmedBaset Kitab ${chNum}${count ? ` &bull; ${count} hadiths` : ''}</span>
                <h3 class="font-bold text-base text-primary dark:text-white group-hover:text-secondary dark:group-hover:text-[#10b981]">${escapeHtml(titleEn)}</h3>
                ${titleAr ? `<span class="text-xs text-on-surface-variant dark:text-gray-400 font-arabic-body" dir="rtl">${escapeHtml(titleAr)}</span>` : ''}
              </div>
            </div>
            <span class="material-symbols-outlined text-outline dark:text-gray-400 group-hover:text-primary dark:group-hover:text-white">arrow_forward</span>
          </a>
        `;
      });
      container.innerHTML = html;
    }
    LangSystem.apply(LangSystem.get());

  // ================================================================
  // BRANCH C — Lidwa / Irsyad (native ID + AR, EN from AhmedBaset where matched)
  // Reads from data/lidwa-chapters/<book>.json (pre-built index)
  // ================================================================
  } else if (resolvedDataset === 'native_lidwa') {
    let lidwaIndex = null;
    try {
      const resp = await fetch(`data/lidwa-chapters/${bookId}.json`);
      if (resp.ok) lidwaIndex = await resp.json();
    } catch(e) { console.warn('Lidwa chapter index fetch error:', e); }

    if (!lidwaIndex || !lidwaIndex.chapters || lidwaIndex.chapters.length === 0) {
      container.innerHTML = `<div class="col-span-2 py-12 text-center text-outline dark:text-gray-400">
        <span class="material-symbols-outlined text-4xl block mb-2">info</span>
        <p>Lidwa chapter data not available for <strong>${bookId}</strong>.</p>
      </div>`;
    } else {
      const enSource = lidwaIndex.title_en_source || 'AhmedBaset';
      const idSource = lidwaIndex.title_id_source || 'Lidwa / Irsyad';
      const showEnNote = !enSource.toLowerCase().includes('lidwa');

      let html = '';
      lidwaIndex.chapters.forEach((ch, idx) => {
        const chNum = ch.chapter_number !== undefined ? ch.chapter_number : (idx + 1);
        const titleId = ch.title_id || `Kitab ${chNum}`;
        const titleEn = ch.title_en || titleId;
        const titleAr = ch.title_ar || '';
        const hadithRange = ch.hadith_start != null
          ? `Hadits ${ch.hadith_start} – ${ch.hadith_end}`
          : `Kitab ${chNum}`;
        const hadithCount = ch.hadith_count || (ch.hadith_end && ch.hadith_start ? ch.hadith_end - ch.hadith_start + 1 : '');

        html += `
          <a href="hadith-list.html?book=${bookId}&chapter=${chNum}&dataset=native_lidwa" class="group bg-surface dark:bg-[#1e293b] border border-outline-variant/20 dark:border-[#334155] hover:border-secondary dark:hover:border-[#10b981] rounded-xl p-5 transition-all flex justify-between items-center card-lift">
            <div class="flex gap-4 items-center">
              <div class="w-10 h-10 rounded-full bg-secondary/10 dark:bg-[#10b981]/10 text-secondary dark:text-[#10b981] font-bold text-sm flex items-center justify-center flex-shrink-0">${chNum === 0 || chNum === '0' ? 'M' : chNum}</div>
              <div class="flex flex-col gap-0.5">
                <span class="text-xs text-outline dark:text-gray-400 font-semibold">Lidwa ${hadithRange}${hadithCount ? ` &bull; ${hadithCount} hadits` : ''}</span>
                <h3 class="font-bold text-base text-primary dark:text-white group-hover:text-secondary dark:group-hover:text-[#10b981]" data-lang-en>${escapeHtml(titleEn)}</h3>
                <h3 class="font-bold text-base text-primary dark:text-white group-hover:text-secondary dark:group-hover:text-[#10b981]" data-lang-id style="display:none">${escapeHtml(titleId)}</h3>
                ${titleAr ? `<span class="text-xs text-on-surface-variant dark:text-gray-400 font-arabic-body" dir="rtl">${escapeHtml(titleAr)}</span>` : ''}
                ${showEnNote ? `<span class="text-[10px] text-outline/60 dark:text-gray-600 italic">EN/AR title from ${escapeHtml(enSource)}</span>` : ''}
              </div>
            </div>
            <span class="material-symbols-outlined text-outline dark:text-gray-400 group-hover:text-primary dark:group-hover:text-white">arrow_forward</span>
          </a>
        `;
      });
      container.innerHTML = html;
    }
    LangSystem.apply(LangSystem.get());
  }


  // Chapter filter input listener — live search
  const filterInput = document.getElementById('chapter-filter-input');
  if (filterInput) {
    filterInput.addEventListener('input', (e) => {
      const q = e.target.value.toLowerCase().trim();
      container.querySelectorAll('a').forEach(card => {
        const matches = !q || card.innerText.toLowerCase().includes(q);
        card.style.display = matches ? '' : 'none';
      });
      // Show "no results" if all hidden
      let noResults = container.querySelector('.no-results-msg');
      const visible = container.querySelectorAll('a:not([style*="none"])').length;
      if (!visible && q) {
        if (!noResults) {
          noResults = document.createElement('div');
          noResults.className = 'no-results-msg col-span-2 py-6 text-center text-outline dark:text-gray-400 text-sm';
          container.appendChild(noResults);
        }
        noResults.textContent = `No kitab matching "${q}"`;
      } else if (noResults) {
        noResults.remove();
      }
    });
  }
}

/**
 * Load list of Hadith cards dynamically for Hadith List view
 */
async function loadHadithCardsList() {
  const container = document.getElementById('hadith-cards-container');
  if (!container) return;

  const params = new URLSearchParams(window.location.search);
  const bookId = params.get('book') || 'bukhari';
  const chapterId = params.get('chapter') || '1';

  const bookNames = {
    bukhari: 'Sahih al-Bukhari',
    nawawi: 'Forty Nawawi',
    muslim: 'Sahih Muslim',
    abudawud: 'Sunan Abu Dawood',
    tirmidhi: "Jami' al-Tirmidhi",
    nasai: "Sunan an-Nasa'i",
    ibnmajah: 'Sunan Ibn Majah',
    malik: 'Muwatta Malik',
    ahmad: 'Musnad Ahmad'
  };
  const bookName = bookNames[bookId.toLowerCase()] || bookId.toUpperCase();

  const isIdLang = (window.LangSystem && window.LangSystem.isIdMode());

  // Update Breadcrumbs & Chapter Titles
  const listBcBook = document.querySelector('[data-list-breadcrumb-book]');
  const listBcCurrent = document.querySelector('[data-list-breadcrumb-current]');
  const chapterMeta = document.querySelector('[data-list-chapter-meta]');
  const chapterTitleEn = document.querySelector('[data-list-chapter-title-en]');
  const chapterTitleId = document.querySelector('[data-list-chapter-title-id]');
  const chapterTitleAr = document.querySelector('[data-list-chapter-title-ar]');
  const countMeta = document.querySelector('[data-list-count-meta]');

  if (listBcBook) {
    listBcBook.innerText = bookName;
    listBcBook.href = `kitab.html?book=${bookId}`;
  }

  let enTitle = `Chapter ${chapterId}`;
  let idTitle = chapterId === '0' ? 'Muqaddimah' : `Kitab ${chapterId}`;
  let arTitle = '';

  let startNum = '';
  let endNum = '';
  // Fetch chapter title info
  const chapters = await window.HadeethAPI.getChapters(bookId);
  if (chapters && chapters.length >= parseInt(chapterId)) {
    const chInfo = chapters[parseInt(chapterId) - 1];
    enTitle = chInfo.title_en || chInfo.name_en || enTitle;
    idTitle = chInfo.title_id || chInfo.name_id || enTitle;
    arTitle = chInfo.title_ar || chInfo.name_ar || '';

    startNum = chInfo.hadith_start || '';
    endNum = chInfo.hadith_end || '';
    const hCount = chInfo.hadith_count || (endNum && startNum ? (endNum - startNum + 1) : '');

    if (countMeta) {
      countMeta.innerText = isIdLang
        ? `Hadits ${startNum} - ${endNum} • ${hCount} Hadits dalam ${bookName} ${chapterId === '0' ? 'Muqaddimah' : `Kitab ${chapterId}`}`
        : `Hadith ${startNum} - ${endNum} • ${hCount} Hadiths in ${bookName} Chapter ${chapterId}`;
    }
  }

  if (listBcCurrent) listBcCurrent.innerText = isIdLang ? idTitle : enTitle;
  if (chapterMeta) chapterMeta.innerText = isIdLang ? (chapterId === '0' ? 'Muqaddimah' : `Kitab ${chapterId}`) : (chapterId === '0' ? 'Introduction' : `Chapter ${chapterId}`);
  if (chapterTitleEn) chapterTitleEn.innerText = enTitle;
  if (chapterTitleId) chapterTitleId.innerText = idTitle;
  if (chapterTitleAr) chapterTitleAr.innerText = arTitle;

  container.innerHTML = `
    <div class="p-8 text-center bg-surface dark:bg-[#1e293b] rounded-xl border border-outline-variant/20 dark:border-[#334155]">
      <span class="material-symbols-outlined animate-spin text-secondary dark:text-[#10b981] text-3xl">progress_activity</span>
      <p class="mt-2 text-sm text-outline dark:text-gray-400">${isIdLang ? `Memuat daftar hadits untuk ${escapeHtml(bookName)} ${chapterId === '0' ? 'Muqaddimah' : `Kitab ${chapterId}`}...` : `Loading authentic Hadith list for ${escapeHtml(bookName)} ${chapterId === '0' ? 'Introduction' : `Chapter ${chapterId}`}...`}</p>
    </div>
  `;

  const langSelectVal = document.getElementById('default-lang-select')?.value || (isIdLang ? 'id' : 'en');

  // Fetch English + Arabic from fawazahmed0 CDN; Indonesian from Lidwa source directly
  const [engEdition, araEdition] = await Promise.all([
    window.HadeethAPI.getEdition('eng', bookId).catch(() => null),
    window.HadeethAPI.getEdition('ara', bookId).catch(() => null)
  ]);

  // Load Indonesian live from Lidwa/Irsyad source data
  let indMap = {};
  try {
    const baseUrl = window.__HADEETH_BASE__
      ? window.__HADEETH_BASE__ + '/data'
      : (() => {
          const s = document.querySelector('script[src*="js/api.js"]');
          if (s) return new URL(s.src, window.location.href).href.replace(/js\/api\.js.*$/, 'data');
          return window.location.origin + window.location.pathname.replace(/\/[^/]*$/, '') + '/data';
        })();
    const lResp = await fetch(`${baseUrl}/sources/lidwa/${bookId}.json`);
    if (lResp.ok) {
      const lData = await lResp.json();
      (Array.isArray(lData) ? lData : (lData.hadiths || [])).forEach(h => {
        const num = h.hadith_number ?? h.hadithnumber ?? h.id;
        if (num !== undefined && h.text_id) indMap[String(num)] = h.text_id;
      });
    }
  } catch (e) {
    console.warn('Lidwa ID not available for detail page', bookId, e);
  }

  if (!engEdition || !engEdition.hadiths) {
    container.innerHTML = `
      <div class="p-8 text-center bg-surface dark:bg-[#1e293b] rounded-xl border border-outline-variant/20 dark:border-[#334155]">
        <p class="text-sm text-outline dark:text-gray-400">${isIdLang ? `Tidak ada hadits ditemukan untuk ${escapeHtml(bookId)}.` : `No Hadiths found for ${escapeHtml(bookId)}.`}</p>
      </div>
    `;
    return;
  }

  // Map Arabic hadith texts by hadithnumber
  const arabicMap = {};
  if (araEdition && araEdition.hadiths) {
    araEdition.hadiths.forEach(h => {
      arabicMap[h.hadithnumber] = h.text;
    });
  }

  const baseHadiths = engEdition.hadiths;
  
  // Actually filter by chapter ranges!
  let listHadiths = baseHadiths;
  // Use chapter range if we successfully extracted it from getChapters
  if (typeof startNum !== 'undefined' && startNum !== '' && endNum !== '') {
    listHadiths = baseHadiths.filter(h => h.hadithnumber >= parseInt(startNum) && h.hadithnumber <= parseInt(endNum));
  } else {
    // Fallback to first 100 if we couldn't parse chapter ranges
    listHadiths = baseHadiths.slice(0, 100);
  }

  let html = '';
  listHadiths.forEach(h => {
    const num = h.hadithnumber;
    const engText = h.text || '';
    const araText = arabicMap[num] || '';
    const indText = indMap[String(num)] || '';

    let transHtml = '';
    if (langSelectVal === 'both') {
      transHtml = `
        <div class="flex flex-col gap-3 border-t border-outline-variant/10 dark:border-[#334155] pt-3">
          ${indText ? `
            <div>
              <span class="text-[11px] uppercase font-bold text-sunan-emerald dark:text-[#10b981] block mb-1">Terjemahan Indonesia:</span>
              <p class="text-sm text-on-surface-variant dark:text-gray-300 leading-relaxed font-sans">${escapeHtml(indText)}</p>
            </div>
          ` : ''}
          ${engText ? `
            <div>
              <span class="text-[11px] uppercase font-bold text-secondary dark:text-gray-400 block mb-1">English Translation:</span>
              <p class="text-sm text-on-surface-variant dark:text-gray-300 leading-relaxed font-sans">${escapeHtml(engText)}</p>
            </div>
          ` : ''}
        </div>
      `;
    } else if (langSelectVal === 'id') {
      const textToUse = indText || engText;
      transHtml = `<p class="text-sm text-on-surface-variant dark:text-gray-300 leading-relaxed font-sans">${escapeHtml(textToUse)}</p>`;
    } else {
      const textToUse = engText || indText;
      transHtml = `<p class="text-sm text-on-surface-variant dark:text-gray-300 leading-relaxed font-sans">${escapeHtml(textToUse)}</p>`;
    }

    html += `
      <div class="bg-surface dark:bg-[#1e293b] border border-outline-variant/20 dark:border-[#334155] rounded-xl p-6 flex flex-col gap-4 shadow-sm hadith-accent border-l-primary dark:border-l-[#10b981]">
        <div class="flex justify-between items-center border-b border-outline-variant/10 dark:border-[#334155] pb-3">
          <div class="flex items-center gap-2">
            <span class="bg-primary dark:bg-[#10b981] text-white dark:text-black text-xs font-bold px-2.5 py-0.5 rounded">${isIdLang ? `Hadits #${num}` : `Hadith #${num}`}</span>
            <span class="bg-sunan-emerald/10 text-sunan-emerald dark:text-[#10b981] text-xs font-semibold px-2 py-0.5 rounded">${isIdLang ? 'Shahih' : 'Sahih'}</span>
          </div>
          <button type="button" data-copy-share-btn data-book="${bookId}" data-id="${num}" data-hadith-title="${escapeHtml(bookName)} #${num}" class="border border-outline-variant/30 dark:border-[#334155] hover:border-secondary dark:hover:border-[#10b981] text-xs font-semibold text-primary dark:text-white px-3 py-1 rounded-lg transition-colors flex items-center gap-1.5 cursor-pointer">
            <span class="material-symbols-outlined text-sm">share</span>
            <span>${isIdLang ? 'Salin / Bagikan' : 'Copy / Share'}</span>
          </button>
        </div>
        ${araText ? `<p class="font-arabic-body text-xl text-primary dark:text-white text-right leading-loose" dir="rtl">${escapeHtml(araText)}</p>` : ''}
        ${transHtml}
        <div class="flex justify-between items-center pt-3 border-t border-outline-variant/10 dark:border-[#334155]">
          <a href="hadith.html?book=${bookId}&id=${num}" class="text-xs font-bold text-primary dark:text-[#10b981] hover:underline flex items-center gap-1">
            ${isIdLang ? 'Hadits Selengkapnya & Pensyarahan &rarr;' : 'Full Hadith & Commentary &rarr;'}
          </a>
          <a href="sanad.html?book=${bookId}&id=${num}" class="text-xs font-semibold text-secondary dark:text-gray-400 hover:underline flex items-center gap-1">
            <span class="material-symbols-outlined text-[16px]">account_tree</span> ${isIdLang ? 'Telusuri Sanad' : 'Inspect Sanad Chain'}
          </a>
        </div>
      </div>
    `;
  });

  container.innerHTML = html;
  LangSystem.apply(LangSystem.get());

  const langSelect = document.getElementById('default-lang-select');
  if (langSelect && !langSelect._langSelectBound) {
    langSelect._langSelectBound = true;
    langSelect.addEventListener('change', () => {
      loadHadithCardsList();
    });
  }

  if (!window._hadithCardsLangListenerAttached) {
    window._hadithCardsLangListenerAttached = true;
    window.addEventListener('hadeeth_lang_change', () => {
      loadHadithCardsList();
    });
  }
}

/**
 * Load Sanad Transmission Chain dynamically
 */
/**
 * Helper to transliterate Arabic narrator names into clean Latin script
 */
function transliterateArabicName(ar) {
  if (!ar) return 'Scholar / Transmitter';

  const clean = ar.replace(/[\u064B-\u0652]/g, '').trim();

  const dict = {
    'عبد الله': 'Abdullah', 'عبد الرحمن': 'Abdurrahman', 'عبد العزيز': 'Abdul Aziz',
    'عبد المجيد': 'Abdul Majid', 'عبد الملك': 'Abdul Malik', 'عبد الرزاق': 'Abdul Razzaq',
    'أبو': 'Abu', 'أبي': 'Abu', 'أبا': 'Abu', 'أم': 'Umm', 'ابن': 'ibn', 'بن': 'bin', 'بنت': 'bint',
    'صالح': 'Salih', 'دينار': 'Dinar', 'بلال': 'Bilal', 'سليمان': 'Sulaiman',
    'العقدي': 'al-Aqadi', 'عامر': 'Amir', 'محمد': 'Muhammad', 'أحمد': 'Ahmad',
    'علي': 'Ali', 'حسين': 'Husayn', 'حسن': 'Hasan', 'عثمان': 'Uthman',
    'سعيد': 'Sa\'id', 'مسلم': 'Muslim', 'إبراهيم': 'Ibrahim', 'يحيى': 'Yahya',
    'شعيب': 'Shu\'ayb', 'مالك': 'Malik', 'حميد': 'Humayd', 'ثابت': 'Thabit',
    'قتادة': 'Qatadah', 'أيوب': 'Ayyub', 'نافع': 'Nafi\'', 'مسدد': 'Musaddad',
    'يزيد': 'Yazid', 'عبيد الله': 'Ubaydullah', 'هشام': 'Hisham', 'موسى': 'Musa',
    'جبير': 'Jubair', 'عوانة': 'Awanah', 'إسماعيل': 'Ismail', 'عباس': 'Abbas',
    'عائشة': 'Aisha', 'عطاء': 'Ata\'', 'مجاهد': 'Mujahid', 'الزهري': 'al-Zuhri'
  };

  const words = clean.split(/\s+/);
  const translated = words.map(w => dict[w] || w);
  return translated.join(' ');
}

async function loadSanadChain() {
  const container = document.getElementById('sanad-nodes-container');
  if (!container) return;

  const params = new URLSearchParams(window.location.search);
  const bookId = params.get('book') || 'bukhari';
  const hadithNum = params.get('id') || '1';
  const hadithId = `${bookId}_${hadithNum}`;

  const bookNames = {
    bukhari: 'Sahih al-Bukhari',
    nawawi: 'Forty Nawawi',
    muslim: 'Sahih Muslim',
    abudawud: 'Sunan Abu Dawood',
    tirmidhi: "Jami' al-Tirmidhi",
    nasai: "Sunan an-Nasa'i",
    ibnmajah: 'Sunan Ibn Majah',
    malik: 'Muwatta Malik',
    ahmad: 'Musnad Ahmad',
    darimi: 'Sunan ad-Darimi'
  };
  const bookName = bookNames[bookId.toLowerCase()] || bookId.toUpperCase();
  const isIdLang = (window.LangSystem && window.LangSystem.isIdMode());

  const hadithUrl = `hadith.html?book=${encodeURIComponent(bookId)}&id=${encodeURIComponent(hadithNum)}`;
  const backBtn = document.getElementById('back-to-hadith-btn');
  if (backBtn) backBtn.href = hadithUrl;
  const titleLink = document.getElementById('sanad-title-link');
  if (titleLink) titleLink.href = hadithUrl;

  const titleEn = document.querySelector('#sanad-title [data-lang-en]');
  const titleId = document.querySelector('#sanad-title [data-lang-id]');
  const subEn = document.querySelector('#sanad-subtitle [data-lang-en]');
  const subId = document.querySelector('#sanad-subtitle [data-lang-id]');

  if (titleEn) titleEn.innerText = `Sanad: ${bookName} ${hadithNum}`;
  if (titleId) titleId.innerText = `Sanad: ${bookName} Hadits #${hadithNum}`;
  if (subEn) subEn.innerText = `Chain of narrators (الإسناد) for ${bookName} Hadith #${hadithNum} tracing back to the Messenger of Allah ﷺ.`;
  if (subId) subId.innerText = `Silsilah perawi (الإسناد) untuk ${bookName} Hadits #${hadithNum} yang bersambung sampai ke Rasulullah ﷺ.`;

  let dbNarrators = [];
  try {
    const primaryId = await window.HadeethAPI.getPrimaryAnchorId(bookId, hadithNum);
    const res = await fetch(`data/hadiths/${bookId}/${primaryId}.json`);
    if (res.ok) {
      const data = await res.json();
      dbNarrators = data.sanad || [];
    }
  } catch (err) {
    console.warn('Local sanad fetch error:', err);
  }

  let narrators = [];

  // Master Rawi Dictionary with complete 3-name separation (Arabic script, EN Latin, ID Latin)
  const rawiDict = [
    { rawi_id: 'rawi_ali_bin_al_madini', en: "'Ali bin 'Abdillah al-Madini", id: "Ali bin Abdullah al-Madini", ar: "علي بن عبد الله المديني", roleEn: "Direct Sheikh of Bukhari • Grade: Hafiz Hujjah", roleId: "GURU LANGSUNG BUKHARI • DERAJAT: HAFIZH HUJJAH", kunyah: "Abu al-Hasan", residence: "Basra / Baghdad", death_ah: "234 AH (849 CE)", counts: "Bukhari: 303", remarks: "Ibn Hajar: Amir al-Mu'minin fi al-Hadith | Imam al-Bukhari: I never felt small before anyone except Ali ibn al-Madini" },
    { rawi_id: 'rawi_abdullah_bin_dinar', en: "Abdullah bin Dinar", id: "Abdullah bin Dinar", ar: "عبد الله بن دينار", roleEn: "Transmitter (Rawi) • Grade: Thiqah", roleId: "PERAWI (RAWI) • DERAJAT: TSIQAH", kunyah: "Abu Abdullah", residence: "Madinah", death_ah: "127 AH (745 CE)", counts: "Bukhari: 180 | Muslim: 160", remarks: "Ibn Hajar: Thiqah Mutqin | Imam al-Bukhari: Thiqah" },
    { rawi_id: 'rawi_ismail_bin_jafar', en: "Isma'il bin Ja'far", id: "Ismail bin Ja'far al-Madani", ar: "إسماعيل بن جعفر", roleEn: "Transmitter (Rawi) • Grade: Thiqah", roleId: "PERAWI (RAWI) • DERAJAT: TSIQAH", kunyah: "Abu Ishaq", residence: "Madinah / Baghdad", death_ah: "180 AH (796 CE)", counts: "Bukhari: 210 | Muslim: 190", remarks: "Ibn Hajar: Thiqah Thabt | Yahya bin Ma'in: Thiqah" },
    { rawi_id: 'rawi_sulaiman_bin_harb', en: "Sulaiman bin Harb", id: "Sulaiman bin Harb al-Azdi", ar: "سليمان بن حرب", roleEn: "Direct Sheikh of Bukhari • Grade: Thiqah", roleId: "GURU LANGSUNG BUKHARI • DERAJAT: TSIQAH", kunyah: "Abu Ayyub", residence: "Basra / Makkah", death_ah: "224 AH (839 CE)", counts: "Bukhari: 145", remarks: "Ibn Hajar: Thiqah Imam Hafiz | Ahmad bin Hanbal: Thiqah Thabt" },
    { rawi_id: 'rawi_atho_bin_yasar', en: "Atho' bin Yasar", id: "Atha bin Yasar", ar: "عطاء بن يسار", roleEn: "Tabi'i (Successor) • Grade: Thiqah", roleId: "TABI'IN • DERAJAT: TSIQAH", kunyah: "Abu Muhammad", residence: "Madinah", death_ah: "103 AH (721 CE)", counts: "Bukhari: 110 | Muslim: 95", remarks: "Ibn Hajar: Thiqah Fadil | Al-Dhahabi: Min A'immat al-Madinah" },
    { rawi_id: 'rawi_hilal_bin_ali', en: "Hilal bin Ali", id: "Hilal bin Ali bin Osama", ar: "هلال بن علي", roleEn: "Transmitter (Rawi) • Grade: Thiqah", roleId: "PERAWI (RAWI) • DERAJAT: TSIQAH", kunyah: "Abu Maimunah", residence: "Madinah", death_ah: "120 AH (738 CE)", counts: "Bukhari & Muslim", remarks: "Ibn Hajar: Thiqah | Ibn Ma'in: La Ba'sa Bihi" },
    { rawi_id: 'rawi_aisha_bint_abi_bakr', en: "'Aisha bint Abi Bakr", id: "Aisyah binti Abu Bakar ash-Shiddiq", ar: "عائشة بنت أبي بكر", roleEn: "Sahabi (Companion) • Grade: Thiqah", roleId: "SAHABAT NABI • DERAJAT: TSIQAH", kunyah: "Umm Abdillah", residence: "Madinah", death_ah: "58 AH (678 CE)", counts: "Bukhari: 2420 | Muslim: 2210", remarks: "Ibn Hajar: Al-Faqiha Al-Hafiz | Al-Dhahabi: Ummu al-Mu'minin" },
    { rawi_id: 'rawi_umar_ibn_al_khattab', en: "'Umar bin Al-Khattab", id: "Umar bin al-Khaththab", ar: "عمر بن الخطاب", roleEn: "Sahabi (Companion) • Grade: Thiqah", roleId: "SAHABAT NABI • DERAJAT: TSIQAH", kunyah: "Abu Hafsh", residence: "Madinah", death_ah: "23 AH (644 CE)", counts: "Bukhari: 537 | Muslim: 450", remarks: "Ibn Hajar: Amir al-Mu'minin Al-Farooq | Al-Dhahabi: Al-Imam Al-Adl" },
    { rawi_id: 'rawi_abu_hurairah', en: "Abu Hurairah", id: "Abu Hurairah radliallahu 'anhu", ar: "أبو هريرة", roleEn: "Sahabi (Companion) • Grade: Thiqah", roleId: "SAHABAT NABI • DERAJAT: TSIQAH", kunyah: "Abu Hurairah", residence: "Madinah / Bahrain", death_ah: "57 AH (678 CE)", counts: "Bukhari: 5374 | Muslim: 4000", remarks: "Ibn Hajar: Sayyid al-Huffaz | Al-Dhahabi: Al-Hafiz Al-Adl" },
    { rawi_id: 'rawi_ibn_umar', en: "Ibnu 'Umar", id: "Ibnu Umar", ar: "عبد الله بن عمر", roleEn: "Sahabi (Companion) • Grade: Thiqah", roleId: "SAHABAT NABI • DERAJAT: TSIQAH", kunyah: "Abu Abdurrahman", residence: "Madinah", death_ah: "73 AH (693 CE)", counts: "Bukhari: 2630 | Muslim: 1800", remarks: "Ibn Hajar: Al-Faqih Al-Muttabi' | Ibn Ma'in: Thiqah Thabt" },
    { rawi_id: 'rawi_ibn_abbas', en: "'Abdullah bin 'Abbas", id: "Abdullah bin Abbas", ar: "عبد الله بن عباس", roleEn: "Sahabi (Companion) • Grade: Thiqah", roleId: "SAHABAT NABI • DERAJAT: TSIQAH", kunyah: "Abu al-Abbas", residence: "Makkah / Ta'if", death_ah: "68 AH (687 CE)", counts: "Bukhari: 1660 | Muslim: 1200", remarks: "Ibn Hajar: Hibr al-Ummah wa Tarjuman al-Qur'an" },
    { rawi_id: 'rawi_anas_bin_malik', en: "Anas bin Malik", id: "Anas bin Malik al-Anshari", ar: "أنس بن مالك", roleEn: "Sahabi (Companion) • Grade: Thiqah", roleId: "SAHABAT NABI • DERAJAT: TSIQAH", kunyah: "Abu Hamzah", residence: "Basra", death_ah: "93 AH (712 CE)", counts: "Bukhari: 2286 | Muslim: 1800", remarks: "Ibn Hajar: Khadim Rasulillahi ﷺ" },
    { rawi_id: 'rawi_abdurrahman_bin_al_qasim', en: "'Abdurrahman bin Al-Qasim", id: "Abdurrahman bin al-Qasim bin Muhammad", ar: "عبد الرحمن بن القاسم", roleEn: "Transmitter (Rawi) • Grade: Thiqah", roleId: "PERAWI (RAWI) • DERAJAT: TSIQAH", kunyah: "Abu al-Qasim", residence: "Madinah", death_ah: "126 AH (744 CE)", counts: "Bukhari & Muslim", remarks: "Ibn Hajar: Thiqah Faqih | Imam Malik: Min Afdal Ahl al-Madinah" },
    { rawi_id: 'rawi_abdullah_bin_yusuf', en: "'Abdullah bin Yusuf at-Tinnisi", id: "Abdullah bin Yusuf at-Tinnisi", ar: "عبد الله بن يوسف التنيسي", roleEn: "Direct Sheikh of Bukhari • Grade: Thiqah", roleId: "GURU LANGSUNG BUKHARI • DERAJAT: TSIQAH", kunyah: "Abu Muhammad", residence: "Tinnis / Damascus", death_ah: "218 AH (833 CE)", counts: "Bukhari: 215", remarks: "Ibn Hajar: Thiqah Mutqin | Yahya bin Ma'in: Thiqah" },
    { rawi_id: 'rawi_ikrimah_bin_khalid', en: "'Ikrimah bin Khalid", id: "Ikrimah bin Khalid", ar: "عكرمة بن خالد", roleEn: "Transmitter (Rawi) • Grade: Thiqah", roleId: "PERAWI (RAWI) • DERAJAT: TSIQAH", kunyah: "Abu Abdullah", residence: "Kufah / Basra", death_ah: "2nd Century AH", counts: "Bukhari & Muslim", remarks: "Ibn Hajar: Thiqah (Verified Transmitter)" },
    { rawi_id: 'rawi_hanzalah_bin_abu_sufyan', en: "Hanzhalah bin Abu Sufyan", id: "Hanzhalah bin Abu Sufyan", ar: "حنظلة بن أبي سفيان", roleEn: "Transmitter (Rawi) • Grade: Thiqah", roleId: "PERAWI (RAWI) • DERAJAT: TSIQAH", kunyah: "Abu Abdullah", residence: "Kufah / Basra", death_ah: "2nd Century AH", counts: "Bukhari & Muslim", remarks: "Ibn Hajar: Thiqah (Verified Transmitter)" },
    { rawi_id: 'rawi_malik_bin_anas', en: "Imam Malik bin Anas", id: "Imam Malik bin Anas", ar: "مالك بن أنس", roleEn: "Imam of Madinah • Grade: Hafiz", roleId: "IMAM MADINAH • DERAJAT: HAFIZH", kunyah: "Abu Abdillah", residence: "Madinah", death_ah: "179 AH (795 CE)", counts: "Muwatta: 1720 | Bukhari: 850", remarks: "Ibn Hajar: Al-Imam Al-Hafiz | Al-Dhahabi: Sayyid al-Fuqaha" },
    { rawi_id: 'rawi_said_bin_jubair', en: "Sa'id bin Jubair", id: "Sa'id bin Jubair", ar: "سعيد بن جبير", roleEn: "Tabi'i (Successor) • Grade: Thiqah", roleId: "TABI'IN • DERAJAT: TSIQAH", kunyah: "Abu Abdillah", residence: "Kufah", death_ah: "95 AH (714 CE)", counts: "Bukhari: 140 | Muslim: 120", remarks: "Ibn Hajar: Thiqah Thabt Imam | Sufyan: A'lam al-Tabi'in" },
    { rawi_id: 'rawi_sufyan_al_thawri', en: "Sufyan bin 'Uyaynah", id: "Sufyan bin Uyainah", ar: "سفيان بن عيينة", roleEn: "Transmitter (Rawi) • Grade: Hafiz", roleId: "PERAWI (RAWI) • DERAJAT: HAFIZH", kunyah: "Abu Muhammad", residence: "Makkah / Kufah", death_ah: "198 AH (814 CE)", counts: "Bukhari: 650 | Muslim: 580", remarks: "Ibn Hajar: Thiqah Hafiz Faqih | Ibn Ma'in: Thabt" },
    { rawi_id: 'rawi_yahya_bin_said', en: "Yahya bin Sa'id al-Ansari", id: "Yahya bin Sa'id al-Anshari", ar: "يحيى بن سعيد الأنصاري", roleEn: "Transmitter (Rawi) • Grade: Thiqah", roleId: "PERAWI (RAWI) • DERAJAT: TSIQAH", kunyah: "Abu Sa'id", residence: "Madinah / Iraq", death_ah: "143 AH (760 CE)", counts: "Bukhari: 210 | Muslim: 190", remarks: "Ibn Hajar: Thiqah Thabt | Ahmad bin Hanbal: Imam Hujjah" },
    { rawi_id: 'rawi_al_humaydi', en: "'Abdullah bin al-Zubayr al-Humaydi", id: "Abdullah bin az-Zubair al-Humaidi", ar: "عبد الله بن الزبير الحميدي", roleEn: "Direct Sheikh of Bukhari • Grade: Thiqah", roleId: "GURU LANGSUNG BUKHARI • DERAJAT: TSIQAH", kunyah: "Abu Bakr", residence: "Makkah / Madinah", death_ah: "219 AH (834 CE)", counts: "Bukhari: 75 | Muslim: 45", remarks: "Ibn Hajar: Thiqah Hafiz | Imam al-Bukhari: Imam fi al-Hadith" },
    { rawi_id: 'rawi_muhammad_bin_ibrahim', en: "Muhammad bin Ibrahim al-Taymi", id: "Muhammad bin Ibrahim at-Taimi", ar: "محمد بن إبراهيم التيمي", roleEn: "Tabi' al-Tabi'in • Grade: Thiqah", roleId: "TABI'UT TABI'IN • DERAJAT: TSIQAH", kunyah: "Abu Abdillah", residence: "Madinah", death_ah: "120 AH (738 CE)", counts: "Bukhari: 110 | Muslim: 95", remarks: "Ibn Hajar: Thiqah Mutqin | Ibn Ma'in: Thiqah" },
    { rawi_id: 'rawi_alqama_bin_waqqas', en: "'Alqama bin Waqqas al-Laythi", id: "Alqamah bin Waqqash al-Laitsi", ar: "علقمة بن وقاص الليثي", roleEn: "Tabi'i (Successor) • Grade: Thiqah", roleId: "TABI'IN • DERAJAT: TSIQAH", kunyah: "Abu Abdullah", residence: "Madinah", death_ah: "85 AH (704 CE)", counts: "Bukhari: 48 | Muslim: 40", remarks: "Ibn Hajar: Thiqah | Al-Dhahabi: Min Kibar al-Tabi'in" },
    { rawi_id: 'rawi_al_araj', en: "Al-A'raj", id: "Al-A'raj (Abdurrahman bin Hormuz)", ar: "الأعرج", roleEn: "Tabi'i (Successor) • Grade: Thiqah", roleId: "TABI'IN • DERAJAT: TSIQAH", kunyah: "Abu Dawood", residence: "Madinah / Alexandria", death_ah: "117 AH (735 CE)", counts: "Bukhari: 180 | Muslim: 150", remarks: "Ibn Hajar: Thiqah Mutqin | Al-Dhahabi: Imam al-Qura' wa al-Muhaddithin" },
    { rawi_id: 'rawi_abu_az_zanad', en: "Abu Az-Zanad", id: "Abu Az-Zanad (Abdullah bin Zakwan)", ar: "أبو الزناد", roleEn: "Transmitter (Rawi) • Grade: Thiqah", roleId: "PERAWI (RAWI) • DERAJAT: TSIQAH", kunyah: "Abu Abdurrahman", residence: "Madinah / Baghdad", death_ah: "130 AH (748 CE)", counts: "Bukhari: 220 | Muslim: 180", remarks: "Ibn Hajar: Thiqah Thabt Faqih | Sufyan: Amir al-Mu'minin fi al-Hadith" }
  ];

  // If DB returned structured chain from hadith_rijal with 3+ narrators, use it!
  if (dbNarrators && dbNarrators.length > 0) {
    narrators = dbNarrators.map((r, idx) => {
      const matchDict = rawiDict.find(d => d.rawi_id === r.rawi_id);
      
      const enName = matchDict ? matchDict.en : (r.name_id || 'Transmitter');
      const idName = r.name_id || (matchDict ? matchDict.id : 'Perawi');
      const isFirst = (idx === 0) || (matchDict && matchDict.roleEn.includes('Sahabi'));

      return {
        rawi_id: r.rawi_id,
        name: enName + (isFirst && !enName.includes('رضي الله') ? ' (رضي الله عنه)' : ''),
        name_id: idName,
        roleEn: matchDict ? (matchDict.roleEn || matchDict.role) : (isFirst ? 'SAHABI (COMPANION) • GRADE: THIQAH' : 'TRANSMITTER (RAWI) • GRADE: THIQAH'),
        roleId: matchDict ? (matchDict.roleId || matchDict.role) : (isFirst ? 'SAHABAT NABI • DERAJAT: TSIQAH' : 'PERAWI (RAWI) • DERAJAT: TSIQAH'),
        ar: getArabicScriptForRawi(r.name_ar || (matchDict ? matchDict.ar : r.name_id)),
        kunyah: matchDict ? matchDict.kunyah : (isFirst ? 'Abu Abdillah' : 'Abu Abdullah'),
        residence: matchDict ? matchDict.residence : (isFirst ? 'Madinah' : 'Kufah / Basra'),
        death_ah: matchDict ? matchDict.death_ah : (isFirst ? 'Early Era' : 'Abad ke-2 H'),
        counts: matchDict ? matchDict.counts : 'Bukhari & Muslim',
        remarks: matchDict ? matchDict.remarks : 'Ibn Hajar: Thiqah'
      };
    });
  }

  // Fallback defaults if no narrators extracted
  if (narrators.length === 0) {
    narrators = [
      { rawi_id: null, name: "Sanad tidak terdeteksi", name_id: "Sanad tidak terdeteksi", roleEn: "UNKNOWN", roleId: "TIDAK DIKETAHUI", ar: "غير معروف", kunyah: "-", residence: "-", death_ah: "-", counts: "-", remarks: "Sistem belum mendeteksi teks sanad" }
    ];
  }

  const countText = document.getElementById('sanad-count-text');
  if (countText) {
    countText.innerHTML = `
      <span data-lang-en>${narrators.length} Narrators</span>
      <span data-lang-id style="display:none">${narrators.length} Perawi</span>
    `;
  }

  let html = `
    <div class="sanad-line"></div>

    <!-- Source: Prophet Muhammad -->
    <div class="sanad-node relative z-10 bg-gradient-to-r from-sunan-emerald to-emerald-800 text-white rounded-xl p-5 shadow-sm border border-emerald-600">
      <div class="absolute -left-11 top-6 w-6 h-6 rounded-full bg-sunan-emerald border-2 border-white dark:border-ink-black flex items-center justify-center text-white text-[10px]">ﷺ</div>
      <div class="flex justify-between items-center">
        <div>
          <span class="text-[10px] uppercase font-bold tracking-widest text-emerald-200">
            <span data-lang-en>SOURCE OF REVELATION</span>
            <span data-lang-id style="display:none">SUMBER WAHYU</span>
          </span>
          <h3 class="font-bold text-lg">
            <span data-lang-en>The Prophet Muhammad ﷺ</span>
            <span data-lang-id style="display:none">Nabi Muhammad ﷺ</span>
          </h3>
        </div>
        <span class="font-arabic-body text-xl" dir="rtl">محمد رسول الله ﷺ</span>
      </div>
    </div>
  `;

  // Render Narrators from Companion down to Direct Sheikh of Author
  narrators.forEach((nr, idx) => {
    let rawiSlug = nr.rawi_id;
    if (!rawiSlug && nr.name) {
      const cleanName = nr.name.replace(/\(.*?\)/g, '').replace(/[^a-zA-Z0-9\s]/g, '').trim().toLowerCase().replace(/\s+/g, '_');
      rawiSlug = `rawi_${cleanName}`;
    }
    const profileUrl = `profile-detail.html?id=${encodeURIComponent(rawiSlug || 'rawi_abu_hurairah')}`;

    const roleEn = nr.roleEn || nr.role || 'TRANSMITTER (RAWI) • GRADE: THIQAH';
    const roleId = nr.roleId || nr.role || 'PERAWI (RAWI) • DERAJAT: TSIQAH';
    const nameEn = nr.name || 'Transmitter';
    const nameId = nr.name_id || getIndonesianRawiName(nameEn, nr.rawi_id, nr.ar);
    const displayArName = getArabicScriptForRawi(nr.ar || nr.name_id || nr.name);

    html += `
      <div class="sanad-node relative z-10 bg-surface dark:bg-[#1e293b] border border-outline-variant/30 dark:border-[#334155] rounded-xl p-5 shadow-sm hover:border-sunan-emerald/50 transition-colors flex flex-col gap-3">
        <div class="absolute -left-11 top-6 w-6 h-6 rounded-full bg-secondary text-white border-2 border-white dark:border-ink-black flex items-center justify-center text-[10px]">${idx + 1}</div>
        
        <div class="flex justify-between items-start border-b border-outline-variant/20 dark:border-[#334155] pb-3">
          <div>
            <span class="text-[10px] uppercase font-bold text-sunan-emerald dark:text-[#10b981]">
              <span data-lang-en>${escapeHtml(roleEn)}</span>
              <span data-lang-id style="display:none">${escapeHtml(roleId)}</span>
            </span>
            <a href="${profileUrl}" class="font-bold text-base text-primary dark:text-white hover:text-sunan-emerald dark:hover:text-[#10b981] hover:underline flex items-center gap-1 mt-0.5">
              <span data-lang-en>${escapeHtml(nameEn)}</span>
              <span data-lang-id style="display:none">${escapeHtml(nameId)}</span>
              <span class="material-symbols-outlined text-xs">open_in_new</span>
            </a>
          </div>
          <span class="font-arabic-body text-lg text-secondary dark:text-[#10b981]" dir="rtl">${escapeHtml(displayArName)}</span>
        </div>

        <div class="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs">
          <div>
            <span class="text-outline dark:text-gray-400 block text-[10px] uppercase font-bold">KUNYAH:</span>
            <span class="font-semibold text-primary dark:text-white">${escapeHtml(nr.kunyah || 'Abu Abdullah')}</span>
          </div>
          <div>
            <span class="text-outline dark:text-gray-400 block text-[10px] uppercase font-bold">
              <span data-lang-en>SETTLED IN:</span>
              <span data-lang-id style="display:none">DOMISILI:</span>
            </span>
            <span class="font-semibold text-primary dark:text-white">${escapeHtml(nr.residence || 'Madinah')}</span>
          </div>
          <div>
            <span class="text-outline dark:text-gray-400 block text-[10px] uppercase font-bold">
              <span data-lang-en>WAFAT (DIED):</span>
              <span data-lang-id style="display:none">WAFAT:</span>
            </span>
            <span class="font-semibold text-primary dark:text-white">${escapeHtml(nr.death_ah || 'Abad ke-1 H')}</span>
          </div>
          <div>
            <span class="text-outline dark:text-gray-400 block text-[10px] uppercase font-bold">
              <span data-lang-en>TOTAL HADITHS:</span>
              <span data-lang-id style="display:none">TOTAL HADITS:</span>
            </span>
            <span class="font-semibold text-sunan-emerald dark:text-[#10b981]">${escapeHtml(nr.counts || 'Bukhari & Muslim')}</span>
          </div>
        </div>

        ${nr.remarks ? `
          <div class="mt-2 pt-2 border-t border-outline-variant/10 dark:border-[#334155] text-xs text-on-surface-variant dark:text-gray-300 italic">
            <span class="font-bold text-secondary dark:text-[#10b981] not-italic text-[10px] uppercase block mb-0.5">
              <span data-lang-en>SCHOLAR REMARKS (JARH WA TA'DIL):</span>
              <span data-lang-id style="display:none">CATATAN ULAMA (JARH WA TA'DIL):</span>
            </span>
            "${escapeHtml(nr.remarks)}"
          </div>
        ` : ''}
      </div>
    `;
  });

  // Final Node: Collector & Author
  const authorNamesEn = {
    bukhari: 'Imam al-Bukhari',
    muslim: 'Imam Muslim',
    abudawud: 'Imam Abu Dawood',
    tirmidhi: 'Imam at-Tirmidhi',
    nasai: 'Imam an-Nasa\'i',
    ibnmajah: 'Imam Ibn Majah',
    malik: 'Imam Malik bin Anas',
    ahmad: 'Imam Ahmad bin Hanbal',
    darimi: 'Imam Abdullah bin Abdul Rahman ad-Darimi'
  };

  const authorNamesId = {
    bukhari: 'Imam al-Bukhari',
    muslim: 'Imam Muslim',
    abudawud: 'Imam Abu Daud',
    tirmidhi: 'Imam at-Tirmidzi',
    nasai: 'Imam an-Nasa\'i',
    ibnmajah: 'Imam Ibn Majah',
    malik: 'Imam Malik bin Anas',
    ahmad: 'Imam Ahmad bin Hanbal',
    darimi: 'Imam Abdullah bin Abdul Rahman ad-Darimi'
  };

  const authorNameEn = authorNamesEn[bookId.toLowerCase()] || 'Imam al-Bukhari';
  const authorNameId = authorNamesId[bookId.toLowerCase()] || 'Imam al-Bukhari';

  const authorIdMap = { 'bukhari': 'rawi_al_bukhari', 'muslim': 'rawi_muslim_ibn_hajjaj', 'abudawud': 'rawi_abu_dawud', 'tirmidhi': 'rawi_al_tirmidhi', 'nasai': 'rawi_al_nasai', 'ibnmajah': 'rawi_ibn_majah', 'malik': 'rawi_malik_bin_anas', 'ahmad': 'rawi_ahmad', 'darimi': 'rawi_darimi' };
  const authorProfileUrl = authorIdMap[bookId] ? `profile-detail.html?id=${authorIdMap[bookId]}` : `profile-detail.html?id=rawi_al_bukhari`;

  html += `
    <div class="sanad-node relative z-10 bg-primary text-white dark:bg-[#0f172a] border border-primary dark:border-[#334155] rounded-xl p-5 shadow-sm">
      <div class="absolute -left-11 top-6 w-6 h-6 rounded-full bg-primary border-2 border-white dark:border-ink-black flex items-center justify-center text-[10px]">📚</div>
      <div class="flex justify-between items-center">
        <div>
          <span class="text-[10px] uppercase font-bold tracking-widest text-[#10b981]">
            <span data-lang-en>COLLECTOR & AUTHOR</span>
            <span data-lang-id style="display:none">KOLEKTOR & PENULIS</span>
          </span>
          <a href="${authorProfileUrl}" class="font-bold text-lg hover:underline flex items-center gap-1 text-white">
            <span data-lang-en>${escapeHtml(authorNameEn)}</span>
            <span data-lang-id style="display:none">${escapeHtml(authorNameId)}</span>
            <span class="material-symbols-outlined text-xs">open_in_new</span>
          </a>
          <p class="text-xs text-gray-300">
            <span data-lang-en>Preserved in Authentic Canonical Corpus</span>
            <span data-lang-id style="display:none">Tercatat dalam Koleksi Kitab Shahih Utama</span>
          </p>
        </div>
      </div>
    </div>
  `;
  container.innerHTML = html;
  LangSystem.apply(LangSystem.get());

  if (!window._sanadLangListenerAttached) {
    window._sanadLangListenerAttached = true;
    window.addEventListener('hadeeth_lang_change', () => {
      LangSystem.apply(LangSystem.get());
    });
  }
}

function normalizeRawiNameKey(str) {
  return (str || '')
    .toLowerCase()
    .replace(/['`’\u2019]/g, '')
    .replace(/[-_]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
}

/**
 * Helper to get clean Indonesian Latin name for Rawi/Scholar
 */
function getIndonesianRawiName(name, rawiId, arName) {
  if (!name && !arName) return 'Perawi Hadits';
  const clean = (name || '').trim();
  const lower = clean.toLowerCase();

  if (rawiId === 'rawi_aisha_bint_abi_bakr' || rawiId === 'rawi_aisha' || lower.includes('aisha') || lower.includes('aisyah')) {
    return 'Aisyah binti Abu Bakar ash-Shiddiq';
  }
  if (rawiId === 'rawi_abdurrahman_bin_al_qasim' || (lower.includes('abdurrahman') && lower.includes('qasim'))) {
    return 'Abdurrahman bin al-Qasim bin Muhammad';
  }
  if (rawiId === 'rawi_abdullah_bin_yusuf' || lower === 'abdullah bin yusuf') {
    return 'Abdullah bin Yusuf at-Tinnisi';
  }
  if (rawiId === 'rawi_malik_bin_anas' || lower === 'malik bin anas' || lower === 'imam malik') {
    return 'Imam Malik bin Anas';
  }
  if (rawiId === 'rawi_umar_ibn_al_khattab' || lower === 'umar' || lower === 'umar bin al-khattab') {
    return 'Umar bin al-Khaththab';
  }
  if (rawiId === 'rawi_abu_hurairah' || lower.includes('abu hurairah')) {
    return 'Abu Hurairah radliallahu \'anhu';
  }
  if (lower.includes('al-humaydi') || lower.includes('humaidi')) {
    return 'Abdullah bin az-Zubair al-Humaidi';
  }
  if (lower.includes('sufyan') && lower.includes('uyaynah')) {
    return 'Sufyan bin Uyainah';
  }
  if (lower.includes('yahya') && lower.includes('said')) {
    return 'Yahya bin Sa\'id al-Anshari';
  }
  if (lower.includes('muhammad') && lower.includes('ibrahim')) {
    return 'Muhammad bin Ibrahim at-Taimi';
  }
  if (lower.includes('alqama')) {
    return 'Alqamah bin Waqqash al-Laitsi';
  }

  return clean
    .replace(/^'/, '')
    .replace(/\s+'/, ' ')
    .replace(/bint\s+/gi, 'binti ')
    .replace(/bin\s+al-khattab/gi, 'bin al-Khaththab')
    .replace(/al-ansari/gi, 'al-Anshari')
    .replace(/al-laythi/gi, 'al-Laitsi')
    .replace(/al-humaydi/gi, 'al-Humaidi')
    .replace(/\(رضي الله عنها\)/gi, '')
    .replace(/\(رضي الله عنه\)/gi, '')
    .trim();
}

/**
 * Helper to get true Arabic script name for Rawi/Scholar
 */
function getArabicScriptForRawi(latinOrAr) {
  if (!latinOrAr) return 'أحد الرواة';

  let rawStr = typeof latinOrAr === 'string' ? latinOrAr : (latinOrAr.ar || latinOrAr.name_ar || latinOrAr.name || '');

  // 1. If raw text contains pure Arabic script and ZERO Latin characters, return it immediately!
  if (/[\u0600-\u06FF]/.test(rawStr) && !/[a-zA-Z]/.test(rawStr)) {
    return rawStr.trim();
  }

  const normKey = normalizeRawiNameKey(rawStr);

  const map = {
    "umar bin al khaththab": "عمر بن الخطاب",
    "umar bin al khattab": "عمر بن الخطاب",
    "umar bin al-khattab": "عمر بن الخطاب",
    "umar bin al-khaththab": "عمر بن الخطاب",
    "alqamah bin waqash al laitsi": "علقمة بن وقاص الليثي",
    "alqamah bin waqqash al laitsi": "علقمة بن وقاص الليثي",
    "alqama bin waqqas al laythi": "علقمة بن وقاص الليثي",
    "alqama bin waqqas": "علقمة بن وقاص الليثي",
    "alqamah bin waqqas": "علقمة بن وقاص الليثي",
    "alqamah bin waqqash": "علقمة بن وقاص الليثي",
    "al humaidi abdullah bin az zubair": "عبد الله بن الزبير الحميدي",
    "abdullah bin az-zubair al-humaydi": "عبد الله بن الزبير الحميدي",
    "al-humaydi": "الحميدي",
    "al humaydi": "الحميدي",
    "qutaibah bin said": "قتيبة بن سعيد",
    "qutaibah bin sa'id": "قتيبة بن سعيد",
    "qutaybah bin said": "قتيبة بن سعيد",
    "abdullah bin dinar": "عبد الله بن دينار",
    "ismail bin jafar": "إسماعيل بن جعفر",
    "ismail bin ja'far": "إسماعيل بن جعفر",
    "sulaiman bin harb": "سليمان بن حرب",
    "atho bin yasar": "عطاء بن يسار",
    "atho' bin yasar": "عطاء بن يسار",
    "ata bin yasar": "عطاء بن يسار",
    "ata' bin yasar": "عطاء بن يسار",
    "hilal bin ali": "هلال بن علي",
    "hilal bin abi maimunah": "هلال بن علي بن أسامة",
    "aisyah": "عائشة بنت أبي بكر",
    "aisha": "عائشة بنت أبي بكر",
    "hafsyah": "حفصة",
    "hafshah": "حفصة",
    "ma'mar": "معمر",
    "mamar": "معمر",
    "abdur razaq": "عبد الرزاق",
    "abdur razaaq": "عبد الرزاق",
    "abdurrazaq": "عبد الرزاق",
    "mahmud": "محمود",
    "hisyam": "هشام",
    "salim": "سالم",
    "abdullah bin muhammad": "عبد الله بن محمد",
    "az zuhriy": "الزهري",
    "az-zuhriy": "الزهري",
    "az zuhri": "الزهري",
    "ibnu syihab": "ابن شهاب",
    "ibnu syihab az-zuhri": "ابن شهاب الزهري",
    "abdurrahman bin al qasim": "عبد الرحمن بن القاسم",
    "abdurrahman bin al-qasim": "عبد الرحمن بن القاسم",
    "abdurrahman bin qasim": "عبد الرحمن بن القاسم",
    "abdullah bin yusuf": "عبد الله بن يوسف التنيسي",
    "al-tinnisi": "عبد الله بن يوسف التنيسي",
    "yusuf": "عبد الله بن يوسف التنيسي",
    "al qasim": "القاسم بن محمد بن أبي بكر",
    "al-qasim": "القاسم بن محمد بن أبي بكر",
    "qasim": "القاسم بن محمد بن أبي بكر",
    "al a'raj": "الأعرج",
    "al-a'raj": "الأعرج",
    "al araj": "الأعرج",
    "abu az zanad": "أبو الزناد",
    "abu az-zanad": "أبو الزناد",
    "abu zanad": "أبو الزناد",
    "abu hurairah": "أبو هريرة",
    "abu huraira": "أبو هريرة",
    "sufyan bin 'uyaynah": "سفيان بن عيينة",
    "sufyan bin uyainah": "سفيان بن عيينة",
    "yahya bin sa'id": "يحيى بن سعيد الأنصاري",
    "muhammad bin ibrahim": "محمد بن إبراهيم التيمي",
    "aisha bint abi bakr": "عائشة بنت أبي بكر",
    "aisyah binti abu bakar": "عائشة بنت أبي بكر",
    "ibn umar": "عبد الله بن عمر",
    "ibnu umar": "عبد الله بن عمر",
    "ibn abbas": "عبد الله بن عباس",
    "anas bin malik": "أنس بن مالك",
    "ikrimah": "عكرمة بن خالد",
    "hanzhalah": "حنظلة بن أبي سفيان",
    "malik bin anas": "مالك بن أنس",
    "imam malik": "مالك بن أنس",
    "sa'id bin jubair": "سعيد بن جبير",
    "nafi'": "نافع مولي ابن عمر",
    "nafi": "نافع",
    "salim": "سالم بن عبد الله",
    "urwah": "عروة بن الزبير",
    "abu salama": "أبو سلمة بن عبد الرحمن",
    "amr bin dinar": "عمرو بن دينار",
    "amru bin dinar": "عمرو بن دينار",
    "al-zuhri": "ابن شهاب الزهري",
    "az-zuhri": "ابن شهاب الزهري",
    "zuhri": "ابن شهاب الزهري"
  };

  for (const [k, v] of Object.entries(map)) {
    const kNorm = normalizeRawiNameKey(k);
    if (normKey.includes(kNorm) || kNorm.includes(normKey)) return v;
  }

  // Word-by-word Arabic Transliteration engine for unmapped narrators
  const wordMap = {
    'khaththab': 'الخطاب',
    'khattab': 'الخطاب',
    'alqamah': 'علقمة',
    'alqama': 'علقمة',
    'waqqash': 'وقاص',
    'waqash': 'وقاص',
    'waqqas': 'وقاص',
    'laitsi': 'الليثي',
    'laythi': 'الليثي',
    'qutaibah': 'قتيبة',
    'qutaybah': 'قتيبة',
    'bin': 'بن',
    'bint': 'بنت',
    'binti': 'بنت',
    'ibn': 'ابن',
    'ibnu': 'ابن',
    'abu': 'أبو',
    'abi': 'أبي',
    'umm': 'أم',
    'ummu': 'أم',
    'al': 'ال',
    'muhammad': 'محمد',
    'ahmad': 'أحمد',
    'abdullah': 'عبد الله',
    'abdurrahman': 'عبد الرحمن',
    'ali': 'علي',
    'umar': 'عمر',
    'usman': 'عثمان',
    'uthman': 'عثمان',
    'aisyah': 'عائشة',
    'aisha': 'عائشة',
    'fatimah': 'فاطمة',
    'hassan': 'الحسن',
    'hussein': 'الحسين',
    'hussain': 'الحسين',
    'saad': 'سعد',
    'said': 'سعيد',
    'sa\'id': 'سعيد',
    'zayd': 'زيد',
    'zaid': 'زيد',
    'khalid': 'خالد',
    'tariq': 'طارق',
    'jabir': 'جابر',
    'salman': 'سلمان',
    'bilal': 'بلال',
    'muadh': 'معاذ',
    'suhayb': 'صهيب',
    'yasser': 'ياسر',
    'yasar': 'يسار',
    'amr': 'عمرو',
    'amru': 'عمرو',
    'dinar': 'دينار',
    'ismail': 'إسماعيل',
    'jafar': 'جعفر',
    'ja\'far': 'جعفر',
    'sulaiman': 'سليمان',
    'harb': 'حرب',
    'atho': 'عطاء',
    'ata': 'عطاء',
    'hilal': 'هلال',
    'qasim': 'القاسم',
    'tinnisi': 'التنيسي',
    'humaydi': 'الحميدي',
    'humaidi': 'الحميدي',
    'ansari': 'الأنصاري',
    'anshari': 'الأنصاري',
    'zuhri': 'الزهري',
    'malik': 'مالك',
    'sufyan': 'سفيان',
    'yahya': 'يحيى',
    'urwah': 'عروة',
    'nafi': 'نافع',
    'salim': 'سالم',
    'tawus': 'طاووس',
    'ikrimah': 'عكرمة',
    'katir': 'كثير',
    'kathir': 'كثير',
    'hisham': 'هشام',
    'musab': 'مصعب',
    'bukhari': 'البخاري',
    'muslim': 'مسلم'
  };

  const clean = rawStr.replace(/\(.*?\)/g, '').replace(/[^a-zA-Z\s]/g, '').trim();
  const words = clean.split(/\s+/);
  const arWords = words.map(w => {
    const lw = w.toLowerCase().replace(/[^a-z]/g, '');
    return wordMap[lw] || w;
  });

  const converted = arWords.join(' ');
  // Purge any remaining Latin characters!
  const arPurged = converted.replace(/[a-zA-Z0-9\(\)\'\`’\-\._]/g, '').trim().replace(/\s+/g, ' ');
  if (/[\u0600-\u06FF]/.test(arPurged) && arPurged.length > 1) {
    return arPurged;
  }

  return 'أحد الرواة';
}

/**
 * Helper to sanitize HTML strings
 */
function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

// ── Multi-Source & Multi-Language Syarah Engine ──
window.activeSyarahData = null;
window.activeSyarahSource = 'enc';
window.activeSyarahLang = 'id';

window.switchSyarahSource = function(srcCode) {
  window.activeSyarahSource = srcCode;
  renderSyarahUI();
};

window.switchSyarahLang = function(langCode) {
  window.activeSyarahLang = langCode;
  renderSyarahUI();
};

function renderSyarahUI() {
  const btnEnc = document.getElementById('syarah-tab-enc');
  const btnFath = document.getElementById('syarah-tab-fath');
  const btnNawawi = document.getElementById('syarah-tab-nawawi');
  const langSelect = document.getElementById('syarah-lang-select');
  const expText = document.getElementById('syarah-explanation-text');
  const benefitsList = document.getElementById('syarah-benefits-list');

  if (!expText) return;

  const activeClass = "px-3.5 py-1.5 rounded-lg text-xs font-bold transition-all cursor-pointer bg-primary dark:bg-[#10b981] text-white dark:text-black shadow-sm";
  const inactiveClass = "px-3.5 py-1.5 rounded-lg text-xs font-medium text-outline dark:text-gray-400 hover:text-primary dark:hover:text-white transition-all cursor-pointer";

  const src = window.activeSyarahSource || 'enc';
  const lang = window.activeSyarahLang || ((window.LangSystem && window.LangSystem.isIdMode()) ? 'id' : 'en');

  if (btnEnc) btnEnc.className = (src === 'enc') ? activeClass : inactiveClass;
  if (btnFath) btnFath.className = (src === 'fath') ? activeClass : inactiveClass;
  if (btnNawawi) btnNawawi.className = (src === 'nawawi') ? activeClass : inactiveClass;
  if (langSelect && langSelect.value !== lang) langSelect.value = lang;

  const data = window.activeSyarahData;
  if (!data) {
    expText.innerText = (lang === 'id') ? "Syarah sedang dimuat..." : "Loading commentary...";
    return;
  }

  let textExp = '';
  let benefits = [];

  if (src === 'fath') {
    textExp = data[`explanation_fath_${lang}`] || (lang === 'ar' ? data.explanation_fath_ar : (lang === 'id' ? data.explanation_fath_id : data.explanation_fath_en));
    benefits = data[`benefits_fath_${lang}`] || (lang === 'ar' ? data.benefits_fath_ar : (lang === 'id' ? data.benefits_fath_id : data.benefits_fath_en)) || [];
    if (!textExp) {
      if (lang === 'id') {
        textExp = '<span class="text-outline dark:text-gray-400 italic">Syarah Fathul Bari (Ibnu Hajar al-\'Asqalani) belum tersedia untuk nomor hadits ini dalam basis data.</span>';
      } else if (lang === 'ar') {
        textExp = '<span class="text-outline dark:text-gray-400 italic" dir="rtl">شرح فتح الباري للحافظ ابن حجر غير متوفر لهذا الحديث حالياً.</span>';
      } else {
        textExp = '<span class="text-outline dark:text-gray-400 italic">Sharh Fath al-Bari (Ibn Hajar al-\'Asqalani) is not yet available for this Hadith in the database.</span>';
      }
    }
  } else if (src === 'nawawi') {
    textExp = data[`explanation_nawawi_${lang}`] || (lang === 'ar' ? data.explanation_nawawi_ar : (lang === 'id' ? data.explanation_nawawi_id : data.explanation_nawawi_en));
    benefits = data[`benefits_nawawi_${lang}`] || (lang === 'ar' ? data.benefits_nawawi_ar : (lang === 'id' ? data.benefits_nawawi_id : data.benefits_nawawi_en)) || [];
    if (!textExp) {
      if (lang === 'id') {
        textExp = '<span class="text-outline dark:text-gray-400 italic">Syarah Sahih Muslim (Imam an-Nawawi) belum tersedia untuk nomor hadits ini dalam basis data.</span>';
      } else if (lang === 'ar') {
        textExp = '<span class="text-outline dark:text-gray-400 italic" dir="rtl">شرح صحيح مسلم للإمام النووي غير متوفر لهذا الحديث حالياً.</span>';
      } else {
        textExp = '<span class="text-outline dark:text-gray-400 italic">Sharh Sahih Muslim (Al-Nawawi) is not yet available for this Hadith in the database.</span>';
      }
    }
  } else {
    textExp = data[`explanation_${lang}`] || data.explanation_id || data.explanation_en;
    benefits = data[`benefits_${lang}`] || data.benefits_id || data.benefits_en || [];
    if (!textExp) {
      if (lang === 'id') {
        textExp = '<span class="text-outline dark:text-gray-400 italic">Syarah ringkas belum tersedia untuk nomor hadits ini.</span>';
      } else if (lang === 'ar') {
        textExp = '<span class="text-outline dark:text-gray-400 italic" dir="rtl">الشرح المختصر غير متوفر لهذا الحديث حالياً.</span>';
      } else {
        textExp = '<span class="text-outline dark:text-gray-400 italic">Concise commentary is not available for this Hadith.</span>';
      }
    }
  }

  expText.innerHTML = textExp;

  if (benefitsList) {
    if (benefits && benefits.length > 0) {
      benefitsList.parentElement.style.display = 'flex';
      benefitsList.innerHTML = benefits.map(b => `<li>${escapeHtml(String(b).replace(/^\d+[\-\.]\s*/, ''))}</li>`).join('');
    } else {
      benefitsList.parentElement.style.display = 'none';
    }
  }

  if (window.LangSystem) window.LangSystem.apply(window.LangSystem.get());
}

async function loadHadithSyarah(bookId, hadithNum) {
  const hadithId = `${bookId}_${hadithNum}`;
  let commentaryData = null;

  // Default Syarah language to current active site language (id or en)
  const currentSiteLang = (window.LangSystem && window.LangSystem.get()) ? window.LangSystem.get() : ((window.LangSystem && window.LangSystem.isIdMode()) ? 'id' : 'en');
  window.activeSyarahLang = currentSiteLang;

  // Default Syarah source based on book
  if (bookId === 'bukhari') {
    window.activeSyarahSource = 'fath';
  } else if (bookId === 'nawawi') {
    window.activeSyarahSource = 'nawawi';
  } else {
    window.activeSyarahSource = 'enc';
  }

  try {
    const primaryId = await window.HadeethAPI.getPrimaryAnchorId(bookId, hadithNum);
    const resolvedHadithId = `${bookId}_${primaryId}`;
    const res = await fetch(`data/commentaries/${resolvedHadithId}.json`);
    if (res && res.ok) {
      commentaryData = await res.json();
    }
  } catch (e) {}

  if (!commentaryData && typeof process !== 'undefined' && process.versions && process.versions.node) {
    try {
      const fs = require('fs');
      const path = require('path');
      const fp = path.resolve(process.cwd(), 'data', 'commentaries', `${hadithId}.json`);
      if (fs.existsSync(fp)) {
        commentaryData = JSON.parse(fs.readFileSync(fp, 'utf8'));
      }
    } catch (e) {}
  }

  if (!commentaryData) {
    commentaryData = {
      hadith_id: hadithId,
      book_id: bookId,
      hadith_number: hadithNum,
      explanation_id: "",
      explanation_en: "",
      benefits_id: [],
      benefits_en: []
    };
  }

  window.activeSyarahData = commentaryData;
  renderSyarahUI();

  // Listen for global site language changes and sync Syarah default language
  if (!window._syarahLangListenerAttached) {
    window._syarahLangListenerAttached = true;
    window.addEventListener('hadeeth_lang_change', (e) => {
      const newLang = (e && e.detail) ? e.detail : (window.LangSystem ? window.LangSystem.get() : 'id');
      window.activeSyarahLang = newLang;
      renderSyarahUI();
    });
  }
}


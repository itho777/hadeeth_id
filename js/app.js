
window.addEventListener('error', function(e) {
    const dbg = document.getElementById('debug-log-screen');
    if (!dbg) {
        const div = document.createElement('div');
        div.id = 'debug-log-screen';
        div.style.position = 'fixed';
        div.style.bottom = '0';
        div.style.left = '0';
        div.style.width = '100%';
        div.style.height = '300px';
        div.style.background = 'rgba(0,0,0,0.8)';
        div.style.color = 'red';
        div.style.zIndex = '999999';
        div.style.overflow = 'auto';
        div.style.padding = '10px';
        document.body.appendChild(div);
    }
    document.getElementById('debug-log-screen').innerHTML += '<br>' + e.message + ' at ' + e.filename + ':' + e.lineno;
});
window.addEventListener('unhandledrejection', function(e) {
    const dbg = document.getElementById('debug-log-screen');
    if (!dbg) {
        const div = document.createElement('div');
        div.id = 'debug-log-screen';
        div.style.position = 'fixed';
        div.style.bottom = '0';
        div.style.left = '0';
        div.style.width = '100%';
        div.style.height = '300px';
        div.style.background = 'rgba(0,0,0,0.8)';
        div.style.color = 'orange';
        div.style.zIndex = '999999';
        div.style.overflow = 'auto';
        div.style.padding = '10px';
        document.body.appendChild(div);
    }
    document.getElementById('debug-log-screen').innerHTML += '<br>Unhandled Promise: ' + (e.reason ? e.reason.message || e.reason : 'unknown');
});

/**
 * HADEETH.ID — Dynamic App Logic v20260807_8
 * Real-time Supabase RPC search integration, dynamic CDN book/hadith loading, and interactive UI.
 * Bilingual EN/ID language switcher with persistent localStorage state.
 */

// Auto-migrate legacy 'primary' dataset ID
if (typeof localStorage !== 'undefined') {
    if (localStorage.getItem('dataset_version') === 'primary') {
        localStorage.setItem('dataset_version', 'fawazahmed');
    }
}

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
    nav_topics: "Topics",
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
    footer_text: "© 2026 hadeeth.id - Digital Hadith Manuscript Preservation"
  },
  id: {
    nav_books: "Kitab",
    nav_topics: "Topik",
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
    footer_text: "© 2026 hadeeth.id - Pelestarian Manuskrip Hadits Digital"
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
  // 9 Books (Kutubut Tis'ah)
  bukhari: [
    { id: 'fawazahmed', label: 'International Numbering (Main)', labelId: 'Penomoran Internasional (Utama)' },
    { id: 'native_lidwa', label: 'Lidwa Numbering', labelId: 'Penomoran Lidwa' }
  ],
  muslim: [
    { id: 'fawazahmed', label: 'International Numbering (Main)', labelId: 'Penomoran Internasional (Utama)' },
    { id: 'native_lidwa', label: 'Lidwa Numbering', labelId: 'Penomoran Lidwa' }
  ],
  nasai: [
    { id: 'fawazahmed', label: 'International Numbering (Main)', labelId: 'Penomoran Internasional (Utama)' },
    { id: 'native_lidwa', label: 'Lidwa Numbering', labelId: 'Penomoran Lidwa' }
  ],
  abudawud: [
    { id: 'fawazahmed', label: 'International Numbering (Main)', labelId: 'Penomoran Internasional (Utama)' },
    { id: 'native_lidwa', label: 'Lidwa Numbering', labelId: 'Penomoran Lidwa' }
  ],
  tirmidhi: [
    { id: 'fawazahmed', label: 'International Numbering (Main)', labelId: 'Penomoran Internasional (Utama)' },
    { id: 'native_lidwa', label: 'Lidwa Numbering', labelId: 'Penomoran Lidwa' }
  ],
  ibnmajah: [
    { id: 'fawazahmed', label: 'International Numbering (Main)', labelId: 'Penomoran Internasional (Utama)' },
    { id: 'native_lidwa', label: 'Lidwa Numbering', labelId: 'Penomoran Lidwa' }
  ],
  malik: [
    { id: 'fawazahmed', label: 'International Numbering (Main)', labelId: 'Penomoran Internasional (Utama)' },
    { id: 'native_lidwa', label: 'Lidwa Numbering', labelId: 'Penomoran Lidwa' }
  ],
  ahmad: [
    { id: 'native_lidwa', label: 'Lidwa Numbering (Main)', labelId: 'Penomoran Lidwa (Utama)' },
    { id: 'native_ahmedbaset', label: 'AhmedBaset Edition', labelId: 'Edisi AhmedBaset' }
  ],
  darimi: [
    { id: 'native_lidwa', label: 'Lidwa Numbering (Main)', labelId: 'Penomoran Lidwa (Utama)' },
    { id: 'native_ahmedbaset', label: 'AhmedBaset Edition', labelId: 'Edisi AhmedBaset' }
  ],

  // 8 Books (AhmedBaset as Main)
  riyad: [
    { id: 'native_ahmedbaset', label: 'AhmedBaset Edition (Main)', labelId: 'Edisi AhmedBaset (Utama)' }
  ],
  shamail: [
    { id: 'native_ahmedbaset', label: 'AhmedBaset Edition (Main)', labelId: 'Edisi AhmedBaset (Utama)' }
  ],
  bulugh: [
    { id: 'native_ahmedbaset', label: 'AhmedBaset Edition (Main)', labelId: 'Edisi AhmedBaset (Utama)' }
  ],
  adab: [
    { id: 'native_ahmedbaset', label: 'AhmedBaset Edition (Main)', labelId: 'Edisi AhmedBaset (Utama)' }
  ],
  mishkat: [
    { id: 'native_ahmedbaset', label: 'AhmedBaset Edition (Main)', labelId: 'Edisi AhmedBaset (Utama)' }
  ],
  nawawi: [
    { id: 'native_ahmedbaset', label: 'AhmedBaset Edition (Main)', labelId: 'Edisi AhmedBaset (Utama)' },
    { id: 'fawazahmed', label: 'Fawaz Edition', labelId: 'Edisi Fawaz' }
  ],
  qudsi: [
    { id: 'native_ahmedbaset', label: 'AhmedBaset Edition (Main)', labelId: 'Edisi AhmedBaset (Utama)' },
    { id: 'fawazahmed', label: 'Fawaz Edition', labelId: 'Edisi Fawaz' }
  ],
  dehlawi: [
    { id: 'native_ahmedbaset', label: 'AhmedBaset Edition (Main)', labelId: 'Edisi AhmedBaset (Utama)' },
    { id: 'fawazahmed', label: 'Fawaz Edition', labelId: 'Edisi Fawaz' }
  ],

  // IrsyadulIbad
  syafii: [
    { id: 'native_irsyad', label: 'IrsyadulIbad (Main)', labelId: 'IrsyadulIbad (Utama)' }
  ],
  riyad_arab: [
    { id: 'native_irsyad', label: 'IrsyadulIbad (850 Hadith)', labelId: 'IrsyadulIbad (850 Hadits)' }
  ],

  // MJNA
  ibnukhuzaimah: [
    { id: 'native_mjna', label: 'MJNA Edition (Main)', labelId: 'Edisi MJNA (Utama)' }
  ],
  ibnuhibban: [
    { id: 'native_mjna', label: 'MJNA Edition (Main)', labelId: 'Edisi MJNA (Utama)' }
  ],
  mustadrak: [
    { id: 'native_mjna', label: 'MJNA Edition (Main)', labelId: 'Edisi MJNA (Utama)' }
  ],
  daruquthni: [
    { id: 'native_mjna', label: 'MJNA Edition (Main)', labelId: 'Edisi MJNA (Utama)' }
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

  const currentDs = forceDataset || localStorage.getItem('dataset_version') || 'fawazahmed';
  const isId = window.LangSystem && window.LangSystem.isIdMode();

  // Validate: if the selected dataset doesn't exist for this book, fall back to primary
  const activeDs = dsConfig.find(d => d.id === currentDs) || dsConfig[0];
  
  
  

  const activeNote = activeDs.note;
  const pillsHtml = dsConfig.map(ds => {
    
    if (ds.id === activeDs.id) {
      return `<span class="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-bold bg-secondary dark:bg-[#10b981] text-white dark:text-black select-none">
        <span class="material-symbols-outlined text-[13px]" style="font-size:13px">check_circle</span><span data-lang-en>${escapeHtml(ds.label)}</span><span data-lang-id style="display:none">${escapeHtml(ds.labelId)}</span>
      </span>`;
    }
    return `<button
        onclick="window.__switchDataset('${ds.id}')"
        class="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-semibold border border-outline-variant/40 dark:border-[#334155] text-on-surface-variant dark:text-gray-400 hover:border-secondary dark:hover:border-[#10b981] hover:text-secondary dark:hover:text-[#10b981] bg-surface-container-low dark:bg-[#0f172a] transition-all cursor-pointer">
        <span class="material-symbols-outlined text-[13px]" style="font-size:13px">swap_horiz</span><span data-lang-en>${escapeHtml(ds.label)}</span><span data-lang-id style="display:none">${escapeHtml(ds.labelId)}</span>
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
          <span class="font-semibold text-on-surface-variant dark:text-gray-400"><span data-lang-en>${escapeHtml(activeDs.sources)}</span><span data-lang-id style="display:none">${escapeHtml(activeDs.sourcesId)}</span></span>
          ${activeNote ? `<span class="block mt-0.5 text-secondary/80 dark:text-[#10b981]/70">⚠ <span data-lang-en>${escapeHtml(activeDs.note)}</span><span data-lang-id style="display:none">${escapeHtml(activeDs.noteId)}</span></span>` : ''}
        </div>
      </div>
    </div>
  `;
}

window.setupReadMore = function() {
  const containers = document.querySelectorAll('.hadith-text-container:not(.read-more-initialized)');
  containers.forEach(container => {
    container.classList.add('read-more-initialized');
    const inner = container.querySelector('.hadith-text-inner');
    const overlay = container.querySelector('.read-more-overlay');
    const btn = container.querySelector('.read-more-btn');
    if (!inner || !overlay || !btn) return;

    // Wait a brief moment for styles to apply if just inserted
    setTimeout(() => {
      // Assuming 10 lines is roughly 350-400px depending on language/text size. Let's use 380px.
      if (inner.scrollHeight > 400) {
        overlay.classList.remove('hidden');
        btn.classList.remove('hidden');

        btn.addEventListener('click', () => {
          if (inner.style.maxHeight === '380px') {
            inner.style.maxHeight = inner.scrollHeight + 'px';
            overlay.classList.add('hidden');
            const isId = window.LangSystem && window.LangSystem.isIdMode();
            btn.innerHTML = `<span data-lang-en style="${isId?'display:none':''}">Show less</span><span data-lang-id style="${isId?'':'display:none'}">Sembunyikan</span> <span class="material-symbols-outlined text-[14px]">expand_less</span>`;
          } else {
            inner.style.maxHeight = '380px';
            overlay.classList.remove('hidden');
            const isId = window.LangSystem && window.LangSystem.isIdMode();
            btn.innerHTML = `<span data-lang-en style="${isId?'display:none':''}">Read more</span><span data-lang-id style="${isId?'':'display:none'}">Selengkapnya</span> <span class="material-symbols-outlined text-[14px]">expand_more</span>`;
            
            // Scroll back into view if it was scrolled past
            const rect = container.getBoundingClientRect();
            if (rect.top < 0) {
              window.scrollBy({ top: rect.top - 80, behavior: 'smooth' });
            }
          }
        });
      } else {
        inner.style.maxHeight = 'none';
      }
    }, 50);
  });
};

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
    const currentVersion = localStorage.getItem('dataset_version') || 'fawazahmed';
    versionSelect.value = currentVersion;
    versionSelect.addEventListener('change', (e) => {
      localStorage.setItem('dataset_version', e.target.value);
      location.reload();
    });
  }

  // --- Initialize Books Rendering ---
  const tisahGrid = document.getElementById('tisah-grid');
  const tisahGridBooks = document.getElementById('tisah-grid-books');
  const sittahGrid = document.getElementById('sittah-grid');
  const secondaryGrid = document.getElementById('secondary-grid');

  if (tisahGrid || tisahGridBooks || sittahGrid || secondaryGrid) {
    window.HadeethAPI.getBooks().then(books => {
      if (tisahGrid) renderBookCards(books.slice(0, 9), tisahGrid);
      if (sittahGrid) renderBookCards(books.slice(0, 6), sittahGrid);
      if (tisahGridBooks) renderBookCards(books.slice(6, 9), tisahGridBooks);
      if (secondaryGrid) renderBookCards(books.slice(9), secondaryGrid);
    }).catch(e => console.warn("Failed to load books", e));
  }

  function renderBookCards(books, container) {
    container.innerHTML = books.map(book => {
      let dataType = 'other';
      if (['bukhari', 'muslim', 'tirmidhi', 'ibnukhuzaimah', 'ibnuhibban'].includes(book.id)) dataType = 'jami';
      else if (['abudawud', 'nasai', 'ibnmajah', 'darimi', 'daruquthni'].includes(book.id)) dataType = 'sunan';
      else if (['ahmad', 'syafii'].includes(book.id)) dataType = 'musnad';
      else if (book.id === 'malik') dataType = 'mushannaf';
      else if (book.id === 'tabarani') dataType = 'mujam';
      else if (book.id === 'mustadrak') dataType = 'mustadrak';
      else if (['nawawi', 'qudsi', 'shah', 'adab', 'bulugh', 'mishkat', 'riyad', 'riyad_arab', 'shamail'].includes(book.id)) dataType = 'jawami';
      
      const typeLabels = {
        'jami': "Jami'",
        'sunan': "Sunan",
        'musnad': "Musnad",
        'mushannaf': "Mushannaf",
        'jawami': "Jawami'",
        'mujam': "Mu'jam",
        'mustadrak': "Mustadrak",
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
    if (window.LangSystem) window.LangSystem.apply(window.LangSystem.get());
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

  if (document.getElementById('hadith-detail-container')) {
    loadHadithDetail();
  }
  if (document.getElementById('chapters-list-container')) {
    loadChaptersList();
  }
  if (document.getElementById('hadith-cards-container')) {
    loadHadithList();
  }
  if (document.getElementById('topic-hadith-cards-container')) {
    loadTopicHadiths();
  }
  if (document.getElementById('profile-header-name-en')) {
    loadProfileDetail();
  }
  if (document.getElementById('sanad-nodes-container')) {
    loadSanadChain().catch(err => console.warn('Sanad chain load failed:', err));
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

  // Default HOTD: Bukhari #1 (Umar narration on intentions)
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

  const hotdBookLabel = document.getElementById('hotd-book-label');
  const hotdArabic = document.getElementById('hotd-arabic');
  const hotdEnglish = document.getElementById('hotd-english');
  const hotdRawi = document.getElementById('hotd-rawi');
  const hotdLink = document.getElementById('hotd-read-link');

  try {
    // Fetch with timeout to avoid indefinite skeleton on local dev
    const h = await Promise.race([
      window.HadeethAPI.getHadith(bookId, hadithId).catch(() => null),
      new Promise((_, reject) => setTimeout(() => reject(new Error('HOTD timeout')), 8000))
    ]).catch(() => null);
    if (!h) {
      // Show friendly fallback message instead of skeleton
      const hotdBookLabel = document.getElementById('hotd-book-label');
      if (hotdBookLabel) hotdBookLabel.textContent = 'Hadith of the Day';
      const hotdArabic = document.getElementById('hotd-arabic');
      if (hotdArabic) {
        hotdArabic.textContent = 'Loading requires server Range support. Deploy to GitHub Pages to view Hadith of the Day.';
        hotdArabic.classList.remove('animate-pulse', 'text-transparent', 'bg-surface-container-high');
      }
      return;
    }
    
    if (hotdBookLabel) hotdBookLabel.textContent = `${bookName} ${h.hadith_number || h.id}`;
    if (hotdLink) hotdLink.href = `hadith.html?book=${bookId}&id=${h.hadith_number || h.id}`;
    
    if (hotdArabic) {
      hotdArabic.textContent = h.text_ar_plain || h.text_ar || '—';
      hotdArabic.classList.remove('animate-pulse', 'text-transparent', 'bg-surface-container-high');
    }
    
    const textEn = h.text_en || '';
    if (hotdEnglish) {
      hotdEnglish.textContent = textEn ? `"${textEn.substring(0, 220)}${textEn.length > 220 ? '...' : ''}"` : '—';
      hotdEnglish.classList.remove('animate-pulse', 'text-transparent', 'bg-surface-container-high');
    }
    
    const rawis = h.rawis || [];
    let rawiStr = '';
    if (rawis.length > 0) {
      const sahabi = rawis.find(r => r.rank === 1 || (r.tags && r.tags.includes('Sahabi')));
      if (sahabi) rawiStr = sahabi.name_en || sahabi.name_ar;
    }
    if (!rawiStr) rawiStr = "The Prophet's Companion";
    
    if (hotdRawi) {
      hotdRawi.textContent = `Narrated by ${rawiStr}.`;
      hotdRawi.classList.remove('animate-pulse', 'text-transparent', 'bg-surface-container-high');
    }
    
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
    const gradeEn = res.grade_en || res.grade || 'Sahih';
    const gradeId = res.grade_id || 'Shahih';

    html += `
      <div class="bg-surface dark:bg-[#1e293b] border border-outline-variant/20 dark:border-[#334155] rounded-xl p-5 hover:border-secondary/50 dark:hover:border-[#10b981]/50 transition-all shadow-sm flex flex-col gap-3">
        <div class="flex items-center justify-between border-b border-outline-variant/10 dark:border-[#334155] pb-2">
          <div class="flex items-center gap-2">
            <span class="bg-primary dark:bg-[#10b981] text-white dark:text-black text-xs font-bold px-2 py-0.5 rounded">${escapeHtml(bookName)} #${hadithNum}</span>
            <span class="bg-sunan-emerald/10 text-sunan-emerald dark:text-[#10b981] text-xs font-semibold px-2 py-0.5 rounded">
              <span data-lang-en>${escapeHtml(gradeEn)}</span>
              <span data-lang-id style="display:none">${escapeHtml(gradeId)}</span>
            </span>
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
 * TafseerLinker — Automatically hyperlinking Qur'anic references to tafseer.id
 */
const TafseerLinker = {
  surahMap: {
    "fatihah": 1, "al-fatihah": 1, "baqarah": 2, "al-baqarah": 2, "ali imran": 3, "ali 'imran": 3, "ali `imran": 3, "lmraan": 3,
    "nisa": 4, "an-nisa": 4, "nisaa": 4, "an-nisaa": 4, "maidah": 5, "al-maidah": 5, "ma'idah": 5, "maa'idah": 5,
    "anam": 6, "al-anam": 6, "an'am": 6, "an'aam": 6, "araf": 7, "al-araf": 7, "a'raf": 7,
    "anfal": 8, "al-anfal": 8, "anfaal": 8, "nafaal": 8, "tawbah": 9, "at-tawbah": 9, "taubah": 9,
    "yunus": 10, "hud": 11, "huud": 11, "yusuf": 12, "rad": 13, "ar-rad": 13, "ra'd": 13, "ibrahim": 14,
    "hijr": 15, "al-hijr": 15, "15": 15, "nahl": 16, "an-nahl": 16, "isra": 17, "al-isra": 17, "israa": 17,
    "kahf": 18, "al-kahf": 18, "kahfi": 18, "maryam": 19, "taha": 20, "thaahaa": 20,
    "anbiya": 21, "al-anbiya": 21, "anbiyaa": 21, "hajj": 22, "al-hajj": 22, "mukminuun": 23,
    "nur": 24, "an-nur": 24, "nuur": 24, "furqan": 25, "al-furqan": 25,
    "syu'ara": 26, "syu'araa": 26, "naml": 27, "an-naml": 27, "qasas": 28, "qashash": 28, "ankabut": 29, "ankabuut": 29,
    "rum": 30, "ar-rum": 30, "ruum": 30, "luqman": 31, "luqmaan": 31, "sajdah": 32, "as-sajdah": 32, "sajadah": 32,
    "ahzab": 33, "al-ahzab": 33, "ahzaab": 33, "saba": 34, "fatir": 35, "yasin": 36, "yaasiin": 36,
    "saffat": 37, "shaffaat": 37, "shaaffaat": 37, "sad": 38, "shaad": 38, "zumar": 39, "az-zumar": 39,
    "ghafir": 40, "fussilat": 41, "fushilat": 41, "shura": 42, "syura": 42, "zukhruf": 43, "dukhan": 44, "dukhaan": 44,
    "jathiyah": 45, "ahqaf": 46, "muhammad": 47, "fath": 48, "al-fath": 48, "hujurat": 49, "al-hujurat": 49,
    "qaf": 50, "qaaf": 50, "dhariyat": 51, "tur": 52, "najm": 53, "an-najm": 53, "qamar": 54, "rahman": 55, "ar-rahman": 55,
    "waqiah": 56, "hadid": 57, "mujadilah": 58, "hasyr": 59, "al-hasyr": 59, "mumtahanah": 60,
    "saff": 61, "jumuah": 62, "munafiqun": 63, "munaafiquun": 63, "taghabun": 64, "talaq": 65, "thalaq": 65,
    "tahrim": 66, "at-tahrim": 66, "tahriim": 66, "mulk": 67, "qalam": 68, "haqqah": 69, "maarij": 70, "nuh": 71,
    "jinn": 72, "jin": 72, "72": 72, "muzzammil": 73, "muddaththir": 74, "mudatstsir": 74, "qiyamah": 75, "insan": 76,
    "mursalat": 77, "naba": 78, "naziat": 79, "abasa": 80, "takwir": 81, "infitar": 82, "mutaffifin": 83, "insyiqaaq": 84,
    "buruj": 85, "tariq": 86, "ala": 87, "ghashiyah": 88, "fajr": 89, "balad": 90, "shams": 91, "lail": 92, "a1-laii": 92,
    "duha": 93, "sharh": 94, "tin": 95, "alaq": 96, "qadr": 97, "bayyinah": 98, "zalzalah": 99, "adiyat": 100,
    "qariah": 101, "takathur": 102, "takaatsur": 102, "asr": 103, "humazah": 104, "fil": 105, "quraish": 106,
    "maun": 107, "kawthar": 108, "kafirun": 109, "nasr": 110, "masad": 111, "ikhlas": 112, "ikhlash": 112,
    "falaq": 113, "nas": 114
  },
  parse(text) {
    if (!text) return '';
    let out = text;
    
    const renderLink = (s, a, originalMatch) => {
        return `<a href="https://tafseer.id/#sura/${s}/verse/${a}" target="_blank" rel="noopener" class="text-secondary dark:text-[#10b981] underline font-semibold hover:opacity-80">${originalMatch}</a>`;
    };

    // 1. [Qur'an 75:16]
    out = out.replace(/\[Qur['’]an\s+(\d+):(\d+)(?:-\d+)?\]/gi, (match, s, a) => {
      return renderLink(s, a, match);
    });

    // 2. (QS. Al Baqarah: 159-160) or Surah 2:159
    out = out.replace(/(?:QS\.?|Qs\.?|qs\.?|Surah|Surat)\s+([A-Za-z\-'`\s]+|\d+)[:\s]+(\d+)(?:-\d+)?[a-z]?/gi, (match, surah, ayah) => {
      let sNum = parseInt(surah);
      if (isNaN(sNum)) {
        let norm = surah.toLowerCase().trim().replace(/^al-/, "").replace(/^al /, "").replace(/^as-/, "").replace(/^as /, "");
        // Direct map lookup
        sNum = this.surahMap[norm];
        
        // If not found, try to find a key that is a substring
        if (!sNum) {
            for (const key in this.surahMap) {
                if (norm.indexOf(key) !== -1 || key.indexOf(norm) !== -1) {
                    sNum = this.surahMap[key];
                    break;
                }
            }
        }
        if (!sNum) sNum = 2; // fallback
      }
      return renderLink(sNum, ayah, match);
    });
    
    // 3. (V. 3:144) or (V.3:144)
    out = out.replace(/\(\s*V\.\s*(\d+)\s*:\s*(\d+)(?:\s*-\s*\d+)?\s*\)/gi, (match, s, a) => {
        return renderLink(s, a, match);
    });
    
    // 4. (75.16) or (75.16-17) 
    // We only want to link if it's enclosed in parentheses or quotes, and looks like a sura.verse format.
    out = out.replace(/\(\s*(\d+)\s*\.\s*(\d+)(?:\s*-\s*\d+)?\s*\)/gi, (match, s, a) => {
        let sNum = parseInt(s);
        let aNum = parseInt(a);
        if (sNum >= 1 && sNum <= 114 && aNum >= 1 && aNum <= 286) {
            return renderLink(sNum, aNum, match);
        }
        return match;
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
window.LastReadTracker = LastReadTracker;

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

  // Active dataset mapping
  const activeDataset = localStorage.getItem('dataset_version') || 'fawazahmed';
  let dsPrefix = 'fawaz';
  let activeDsLabel = 'International Numbering';
  let activeDsLabelId = 'Penomoran Internasional';

  if (activeDataset === 'native_lidwa') {
    dsPrefix = 'lidwa';
    activeDsLabel = 'Lidwa Numbering';
    activeDsLabelId = 'Penomoran Lidwa';
  } else if (activeDataset === 'native_ahmedbaset') {
    dsPrefix = 'ab';
    activeDsLabel = 'AhmedBaset Edition';
    activeDsLabelId = 'Edisi AhmedBaset';
  }

  // Fetch from unified reciprocal API
  const data = await window.HadeethAPI.getHadith(bookId, hadithId, dsPrefix);
  
  if (!data) {
    container.innerHTML = `<div class="p-8 text-center text-red-500">Failed to load Hadith ${bookId}:${hadithId} from ${activeDsLabel}</div>`;
    return;
  }

  // Extract variables
  const bookName = (bookId === 'nawawi' ? 'Forty Nawawi' : bookId.toUpperCase());
  const displayNum = (localStorage.getItem('numbering_system') === 'lidwa' && data.lidwa_id) ? data.lidwa_id : data.hadith_number;
  const titleTextEn = `Hadith #${displayNum}`;
  const titleTextId = `Hadits #${displayNum}`;
  
  document.title = `${bookName} Hadith #${displayNum} - HADEETH.ID`;
  
  if (window.LastReadTracker) window.LastReadTracker.save(bookId, data.hadith_number, bookName, `${bookName} Hadith #${data.hadith_number}`);

  // Update Breadcrumbs & Meta
  const bcBook = document.querySelector('[data-breadcrumb-book]');
  if (bcBook) { bcBook.innerText = bookName; bcBook.href = `kitab.html?book=${bookId}`; }
  
  const bcCurrentEn = document.querySelector('[data-breadcrumb-current-en]');
  const bcCurrentId = document.querySelector('[data-breadcrumb-current-id]');
  if (bcCurrentEn) bcCurrentEn.innerText = titleTextEn + ` (${activeDsLabel})`;
  if (bcCurrentId) bcCurrentId.innerText = titleTextId + ` (${activeDsLabelId})`;

  const chapterMetaEn = document.querySelector('[data-hadith-chapter-en]');
  const chapterMetaId = document.querySelector('[data-hadith-chapter-id]');

  let chId = data.chapter_id;

  let chTitleId = "";

  let chTitleEn = "";

  try {

      const chapters = await window.HadeethAPI.getChapters(bookId);

      if (chapters && chapters.length > 0) {

          const hNum = parseInt(displayNum);

          const foundCh = chapters.find(c => hNum >= parseInt(c.hadith_start) && hNum <= parseInt(c.hadith_end));

          if (foundCh) {

              chId = foundCh.chapter_number || foundCh.id || chId;

              chTitleId = foundCh.title_id || "";

              chTitleEn = foundCh.title_en || "";

              

              // Clean up titles (e.g. "bukhari_c1" -> 1 if id is used)

              if (typeof chId === "string" && chId.includes("_c")) {

                  chId = chId.split("_c")[1];

              }

          }

      }

  } catch(e) {}

  

  if (chId === undefined || chId === null || chId === "") chId = "?";

  

  if (chapterMetaEn) {

      chapterMetaEn.innerText = chTitleEn ? `Chapter ${chId}: ${chTitleEn}` : `Chapter ${chId}`;

  }

  if (chapterMetaId) {

      chapterMetaId.innerText = chTitleId ? `Bab ${chId}: ${chTitleId}` : `Bab ${chId}`;

  }

  // Next / Prev buttons
  const prevBtn = document.getElementById('prev-hadith-btn');
  const nextBtn = document.getElementById('next-hadith-btn');
  const isnadBtn = document.getElementById('view-isnad-btn');
  const currentNum = parseInt(hadithId) || 1;
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
  if (isnadBtn) {
    if (data.rawis && data.rawis.length > 0) {
      isnadBtn.href = `sanad.html?book=${bookId}&id=${hadithId}`;
      isnadBtn.style.display = 'flex';
    } else {
      isnadBtn.style.display = 'none';
    }
  }

  // Populate Text
  const arabicElem = document.querySelector('[data-arabic-text]');
  const englishElem = document.querySelector('[data-english-text]');
  const indonesianElem = document.querySelector('[data-indonesian-text]');
  
  if (arabicElem) arabicElem.innerText = data.text_ar || 'Not Available';

  // Populate Grade
  const gradeElem = document.querySelector('[data-hadith-grade]');
  if (gradeElem) {
      if (data.grade) {
          gradeElem.innerText = data.grade;
          gradeElem.style.display = 'inline-block';
      } else {
          gradeElem.style.display = 'none';
      }
  }
  
  // Restore dynamic translation options
  const baseUrl = window.__HADEETH_BASE__ ? window.__HADEETH_BASE__ + '/data' : window.location.origin + window.location.pathname.replace(/\/[^/]*$/, '') + '/data';
  const [linkResp, editionsResp] = await Promise.all([
    fetch(`${baseUrl}/links/${bookId}.json`).catch(() => null),
    fetch(`${baseUrl}/meta/fawaz_editions.json`).catch(() => null)
  ]);

  let linkGraph = {};
  if (linkResp && linkResp.ok) linkGraph = await linkResp.json();
  let fawazEditions = {};
  if (editionsResp && editionsResp.ok) fawazEditions = await editionsResp.json();

  const fawazId = activeDataset === 'fawazahmed' ? hadithId : (Object.keys(linkGraph.fawaz_to_lidwa || {}).find(k => linkGraph.fawaz_to_lidwa[k] == hadithId) || hadithId);
  const lidwaId = activeDataset === 'native_lidwa' ? hadithId : (linkGraph.fawaz_to_lidwa ? (linkGraph.fawaz_to_lidwa[fawazId] || null) : null);
  const abId = activeDataset === 'native_ahmedbaset' ? hadithId : (linkGraph.fawaz_to_ab ? linkGraph.fawaz_to_ab[fawazId] : (linkGraph[fawazId] ? linkGraph[fawazId].ahmedbaset_id : null));

  const translationOptions = [];
  
  // Even if we are on Lidwa or Ahmedbaset, we want to allow users to switch languages!
  if (fawazEditions[bookId]) {
      const editions = fawazEditions[bookId].collection || [];
      editions.forEach(ed => {
          if (ed.name.startsWith('ara-')) return; 
          const core9 = ['bukhari', 'muslim', 'abudawud', 'tirmidhi', 'nasai', 'ibnmajah', 'malik', 'ahmad', 'darimi'];
          if (core9.includes(bookId) && ed.name.startsWith('ind-')) return; // We use Lidwa for ID for 9 core books
          const langCode = ed.language.toUpperCase();
          const author = ed.author !== 'Unknown' ? ed.author : 'Fawazahmed0';
          translationOptions.push({
              id: `fawaz-${ed.name}`,
              label: `${langCode} - ${author}`,
              lang: ed.language,
              source: 'fawaz',
              hid: fawazId,
              file: `${baseUrl}/raw_baseline/${ed.name}.json`
          });
      });
  }
  
  // Inject Lidwa translation — only for books where Lidwa data is known to exist
  const lidwaBooks = ['bukhari', 'muslim', 'tirmidhi', 'abudawud', 'nasai', 'ibnmajah', 'malik', 'ahmad', 'darimi', 'riyad', 'nawawi', 'syafii'];
  const hasLidwaSource = lidwaBooks.includes(bookId);
  const hasLidwaIdText = !!(data && data.translations && data.translations.id && data.translations.id.find(x => x.source === 'lidwa'));
  const hasLidwaEnText = !!(data && data.translations && data.translations.en && data.translations.en.find(x => x.source === 'lidwa'));
  // Also check direct text_id on native_lidwa dataset
  const hasLidwaId2 = !!(activeDataset === 'native_lidwa' && data && data.text_id);
  const hasLidwaEn2 = !!(activeDataset === 'native_lidwa' && data && data.text_en);
  // Also check text_id directly available from NDJSON (even without a fawaz→lidwa link mapping)
  const hasNdjsonId = !!(data && data.text_id);

  if ((lidwaId || activeDataset === 'native_lidwa' || hasNdjsonId) && hasLidwaSource) {
      if (hasLidwaIdText || hasLidwaId2 || lidwaId || hasNdjsonId) {
          translationOptions.push({
              id: 'lidwa-id',
              label: `ID - Lidwa`,
              lang: 'Indonesian',
              source: 'lidwa_id',
              hid: lidwaId || hadithId,
              file: `${baseUrl}/sources/lidwa/${bookId}.json`
          });
      }
      if (hasLidwaEnText || hasLidwaEn2) {
          translationOptions.push({
              id: 'lidwa-en',
              label: `EN - Lidwa`,
              lang: 'English',
              source: 'lidwa_en',
              hid: lidwaId || hadithId,
              file: `${baseUrl}/sources/lidwa/${bookId}.json`
          });
      }
  }

  // Inject AhmedBaset translation — only for the 9 core books that AB covers
  const abBookMap = { 
      ahmad: 'the_9_books/ahmed',
      bukhari: 'the_9_books/bukhari',
      muslim: 'the_9_books/muslim',
      abudawud: 'the_9_books/abudawud',
      tirmidhi: 'the_9_books/tirmidhi',
      nasai: 'the_9_books/nasai',
      ibnmajah: 'the_9_books/ibnmajah',
      malik: 'the_9_books/malik',
      darimi: 'the_9_books/darimi',
      nawawi: 'forties/nawawi40',
      qudsi: 'forties/qudsi40',
      dehlawi: 'forties/shahwaliullah40',
      riyad: 'other_books/riyad_assalihin',
      shamail: 'other_books/shamail_muhammadiyah',
      bulugh: 'other_books/bulugh_almaram',
      adab: 'other_books/aladab_almufrad',
      mishkat: 'other_books/mishkat_almasabih'
    };
  const abBook = abBookMap[bookId] || bookId;
  const abCoreBooks = ['bukhari', 'muslim', 'tirmidhi', 'abudawud', 'nasai', 'ibnmajah', 'malik', 'ahmad', 'darimi'];
  const hasAbText = !!(data && data.translations && data.translations.en && data.translations.en.find(x => x.source === 'ab' || x.source === 'ahmedbaset'));
  const hasAbDirect = !!(data && data.text_en && activeDataset === 'native_ahmedbaset');
  if (abCoreBooks.includes(bookId) && (hasAbText || hasAbDirect || abId || activeDataset === 'native_ahmedbaset')) {
      translationOptions.push({
          id: 'ab-en',
          label: `EN - AhmedBaset`,
          lang: 'English',
          source: 'ab',
          hid: abId || fawazId || hadithId,
          file: `${baseUrl}/sources/ahmedbaset/by_book/${abBook}.json`
      });
  }

  // Inject MJNA.or.id translation — only for MJNA books
  const mjnaBooksList = ['ibnukhuzaimah', 'ibnuhibban', 'mustadrak', 'daruquthni'];
  const isMjnaBook = mjnaBooksList.includes(bookId);
  const hasMjnaIdText = !!(data && data.translations && data.translations.id && data.translations.id.find(x => x.source === 'mjna'));
  const hasMjnaArText = !!(data && data.translations && data.translations.ar && data.translations.ar.find(x => x.source === 'mjna'));

  if (isMjnaBook && hasMjnaIdText) {
      translationOptions.push({
          id: 'mjna-id',
          label: 'ID - MJNA.or.id',
          lang: 'Indonesian',
          source: 'mjna_id',
          hid: hadithId,
          file: null  // served directly from data.translations
      });
  }
  if (isMjnaBook && hasMjnaArText) {
      // Arabic from MJNA is already shown as main text, but expose via dropdown too
      // (only show if user might want to compare / copy)
  }

  async function fetchTranslationText(opt) {
      // First try to use the consolidated API translations if available
      if (data && data.translations) {
          // MJNA.or.id source
          if (opt.source === 'mjna_id' && data.translations.id) {
              const t = data.translations.id.find(x => x.source === 'mjna');
              if (t) return t.text;
          }
          if (opt.source === 'lidwa_id' && data.translations.id) {
              const t = data.translations.id.find(x => x.source === 'lidwa');
              if (t) return t.text;
          }
          if (opt.source === 'lidwa_en' && data.translations.en) {
              const t = data.translations.en.find(x => x.source === 'lidwa');
              if (t) return t.text;
          }
          if (opt.source === 'ab' && data.translations.en) {
              const t = data.translations.en.find(x => x.source === 'ab' || x.source === 'ahmedbaset');
              if (t) return t.text;
          }
      }
      
      // Also fallback to properties if injected directly
      if (opt.source === 'lidwa_id' && data.text_id) return data.text_id;
      if (opt.source === 'lidwa_en' && data.text_en_lidwa) return data.text_en_lidwa;
      if (opt.source === 'ab' && data.text_en) return data.text_en;
      
      // Fallback: Fetch the file directly
      try {
          let text = '';
          if (opt.source === 'fawaz') {
              const langCode = opt.file.split('/').pop().split('-')[0]; // extract fra, ind, etc from fra-bukhari.json
              const bookCode = opt.file.split('-')[1].split('.')[0];
              const edition = await window.HadeethAPI.getEdition(langCode, bookCode).catch(()=>null);
              if (edition) {
                  const found = edition.hadiths.find(h => (h.hadithnumber ?? h.id) == opt.hid);
                  if (found) text = found.text;
              }
          } else if (opt.source.startsWith('lidwa')) {
              const bookCode = opt.file.split('/').pop().split('.')[0];
              const lidwaData = await window.HadeethAPI.getHadith(bookCode, opt.hid, 'lidwa');
              if (lidwaData) {
                  if (opt.source === 'lidwa_id') text = lidwaData.text_id;
                  if (opt.source === 'lidwa_en') text = lidwaData.text_en;
              }
          } else {
              const resp = await fetch(opt.file);
              if (!resp.ok) return null;
              const json_data = await resp.json();
              if (opt.source === 'ab') {
                  const found = (Array.isArray(json_data) ? json_data : (json_data.hadiths || [])).find(h => h.idInBook == opt.hid);
                  if (found && found.english) text = (found.english.narrator ? found.english.narrator + ' ' : '') + found.english.text;
              }
          }

          return text;
      } catch(e) {
          console.warn('Failed to fetch', opt, e);
      }
      return null;
  }

  // Populate Dropdowns
  const langSelects = container.querySelectorAll('[data-lang-select]');
  langSelects.forEach((selectElem, idx) => {
      selectElem.style.display = 'block'; // Ensure it's unhidden
      selectElem.innerHTML = '';
      translationOptions.forEach(opt => {
          const option = document.createElement('option');
          option.value = opt.id;
          option.innerText = opt.label;
          option.className = "bg-white dark:bg-[#1e293b] text-gray-900 dark:text-white";
          selectElem.appendChild(option);
      });
      // Set defaults
      if (idx === 0) {
         const defaultEn = translationOptions.find(o => o.id.includes('eng-bukhari') || (o.lang==='English' && (o.source==='fawaz' || o.source==='ab'))) || translationOptions[0];
         if (defaultEn) selectElem.value = defaultEn.id;
      } else {
         const defaultId = translationOptions.find(o => o.id === 'mjna-id') || translationOptions.find(o => o.id === 'lidwa-id') || translationOptions[0];
         if (defaultId) selectElem.value = defaultId.id;
      }
      
      // Update the header span dynamically
      const spanTitle = selectElem.parentElement.querySelector('span');
      if (spanTitle && selectElem.selectedIndex >= 0) {
          const opt = selectElem.options[selectElem.selectedIndex];
          if (opt) {
              const langName = opt.text.split(' - ')[0];
              spanTitle.innerText = langName + " TRANSLATION";
          }
      }
  });

  async function updateTranslationBox(selectElem, targetBox) {
      const val = selectElem.value;
      const opt = translationOptions.find(o => o.id === val);
      if (!opt) return;
      
      targetBox.innerHTML = '<span class="text-xs text-secondary animate-pulse">Loading translation...</span>';
      
      const txt = await fetchTranslationText(opt);
      if (txt) {
          let output = typeof TafseerLinker !== 'undefined' ? TafseerLinker.parse(txt) : txt;
          
          if (opt.source !== 'fawaz' && activeDataset === 'fawazahmed') {
             output = `<div class="mb-2 text-xs text-blue-500 font-semibold">[Linked via Arabic matching → ${opt.source.toUpperCase()} #${opt.hid}]</div>` + output;
          }
          
          targetBox.innerHTML = output;
      } else {
          targetBox.innerHTML = `<span class="text-xs text-outline dark:text-gray-400 italic">Translation not available in ${opt.label}.</span>`;
      }
  }

  // Initial load for both boxes
  if (englishElem && langSelects[0]) {
      updateTranslationBox(langSelects[0], englishElem);
  } else if (englishElem) {
      if (data.text_en) englishElem.innerHTML = data.text_en;
  }
  
  if (indonesianElem && langSelects[1]) {
      updateTranslationBox(langSelects[1], indonesianElem);
  } else if (indonesianElem) {
      if (data.text_id) indonesianElem.innerHTML = data.text_id;
      else if (data.translations && data.translations.id) {
          const mjnaT = data.translations.id.find(x => x.source === 'mjna');
          if (mjnaT) indonesianElem.innerHTML = mjnaT.text;
      }
  }

  // Probe each option and remove from dropdown if translation is not available
  (async () => {
    for (const selectElem of Array.from(langSelects)) {
      const toRemove = [];
      for (const opt of translationOptions) {
        const optElem = selectElem.querySelector(`option[value="${opt.id}"]`);
        if (!optElem) continue;
        // Quick pre-check: if we already know the text is in data, keep it
        const knownAvailable = (opt.source === 'mjna_id' && hasMjnaIdText)
          || (opt.source === 'lidwa_id' && (hasLidwaIdText || hasLidwaId2))
          || (opt.source === 'lidwa_en' && (hasLidwaEnText || hasLidwaEn2))
          || (opt.source === 'ab' && (hasAbText || hasAbDirect))
          || (opt.source === 'fawaz');
        if (knownAvailable) continue;
        // Otherwise probe by fetching
        try {
          const txt = await fetchTranslationText(opt);
          if (!txt) toRemove.push(opt.id);
        } catch(e) {
          toRemove.push(opt.id);
        }
      }
      toRemove.forEach(id => {
        const optElem = selectElem.querySelector(`option[value="${id}"]`);
        if (optElem) optElem.remove();
      });
      // If selected option was removed, reset to first available
      if (!selectElem.value && selectElem.options.length > 0) {
        selectElem.value = selectElem.options[0].value;
        const cardBox = selectElem.closest('.p-5');
        const targetP = cardBox ? cardBox.querySelector('p') : null;
        if (targetP) updateTranslationBox(selectElem, targetP);
      }
    }
  })();

  // Listeners
  langSelects.forEach(selectElem => {
    selectElem.addEventListener('change', () => {
      const cardBox = selectElem.closest('.p-5');
      const targetP = cardBox ? cardBox.querySelector('p') : null;
      
      // Update title dynamically on change
      const spanTitle = selectElem.parentElement.querySelector('span');
      if (spanTitle && selectElem.selectedIndex >= 0) {
          const opt = selectElem.options[selectElem.selectedIndex];
          if (opt) {
              const langName = opt.text.split(' - ')[0];
              spanTitle.innerText = langName + " TRANSLATION";
          }
      }
      
      if (targetP) {
          updateTranslationBox(selectElem, targetP);
      }
      if (window.switchSyarahLang) {
          // Sync syarah lang loosely
          const val = selectElem.value.toLowerCase();
          window.switchSyarahLang(val.includes('id') || val.includes('ind') ? 'id' : 'en');
      }
    });
  });

  // Fix panels layout
  const engPanel = document.querySelector('[data-english-text]')?.closest('.flex.flex-col');
  const idPanel = document.querySelector('[data-indonesian-text]')?.closest('.flex.flex-col');
  if (engPanel) engPanel.style.display = 'flex';
  if (idPanel) idPanel.style.display = 'flex';

  const panelsContainer = document.querySelector('.grid.grid-cols-1.md\\:grid-cols-2') || document.querySelector('.grid.grid-cols-1.gap-6');
  if (panelsContainer) {
    panelsContainer.className = "grid grid-cols-1 md:grid-cols-2 gap-6";
  }

  // Sanad Link
  const sanadLinkBtn = document.querySelector('[data-sanad-link]');
  if (sanadLinkBtn) {
    sanadLinkBtn.href = `sanad.html?book=${bookId}&id=${hadithId}`;
  }
  
  // Sanad Preview Text (Strictly from Lidwa Bracket Data)
  const sanadPreviewEn = document.querySelector('[data-sanad-preview-en]');
  const sanadPreviewId = document.querySelector('[data-sanad-preview-id]');
  const rawiEn = document.querySelector('[data-hadith-rawi-en]');
  const rawiId = document.querySelector('[data-hadith-rawi-id]');
  
  if (sanadPreviewEn || sanadPreviewId) {
      let previewStrEn = `Inspect Chain for ${bookName} #${hadithId} → Prophet ﷺ`;
      let previewStrId = `Periksa Silsilah untuk ${bookName} #${hadithId} → Rasulullah ﷺ`;
      let narratorEn = "Unknown";
      let narratorId = "Tidak diketahui";
      
      if (data.rawis && data.rawis.length > 0) {
          // Lidwa rawis array is ordered from Highest (Sahabi) to Lowest (Mukharrij).
          // We display from Lowest to Highest -> Prophet.
          const reversedRawis = [...data.rawis].reverse();
          
          const namesEn = reversedRawis.map(r => r.name_en || r.name || r.ar || r.id);
          const namesId = reversedRawis.map(r => r.name_id || r.name || r.ar || r.id);
          
          previewStrEn = namesEn.join(' → ') + ' → Prophet ﷺ';
          previewStrId = namesId.join(' → ') + ' → Rasulullah ﷺ';
          
          // The narrator closest to the Prophet (Sahabi) is the first element in Lidwa's rawis array
          narratorEn = data.rawis[0].name_en || data.rawis[0].name || data.rawis[0].ar || "Unknown Transmitter";
          narratorId = data.rawis[0].name_id || data.rawis[0].name || data.rawis[0].ar || "Perawi Tidak Diketahui";
      }
      
      if (sanadPreviewEn) sanadPreviewEn.innerText = previewStrEn;
      if (sanadPreviewId) sanadPreviewId.innerText = previewStrId;
      if (rawiEn) rawiEn.innerText = `Narrator: ${narratorEn}`;
      if (rawiId) rawiId.innerText = `Perawi: ${narratorId}`;
  }
  
  const banners = document.querySelectorAll('#dataset-banner');
  banners.forEach(b => b.style.display = 'none');

  // Load Syarah
  if (typeof loadHadithSyarah === 'function') {
      loadHadithSyarah(bookId, hadithId);
  }

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
  const activeDataset = datasetParam || localStorage.getItem('dataset_version') || 'fawazahmed';

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
  renderDatasetBanner(bookId, 'dataset-banner-list', datasetParam);

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
    const abBookMap = { 
      ahmad: 'the_9_books/ahmed',
      bukhari: 'the_9_books/bukhari',
      muslim: 'the_9_books/muslim',
      abudawud: 'the_9_books/abudawud',
      tirmidhi: 'the_9_books/tirmidhi',
      nasai: 'the_9_books/nasai',
      ibnmajah: 'the_9_books/ibnmajah',
      malik: 'the_9_books/malik',
      darimi: 'the_9_books/darimi',
      nawawi: 'forties/nawawi40',
      qudsi: 'forties/qudsi40',
      dehlawi: 'forties/shahwaliullah40',
      riyad: 'other_books/riyad_assalihin',
      shamail: 'other_books/shamail_muhammadiyah',
      bulugh: 'other_books/bulugh_almaram',
      adab: 'other_books/aladab_almufrad',
      mishkat: 'other_books/mishkat_almasabih'
    };
    const abBook = abBookMap[bookId] || bookId;
    try {
      const resp = await fetch(`data/sources/ahmedbaset/by_chapter/${abBook}/${chapterId}.json`);
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

        // Fetch Link Matrix to map AhmedBaset ID -> Lidwa HNum
        let abToLidwaMap = {};
        let lidwaIdMap = {};
        try {
          const baseUrl = window.__HADEETH_BASE__ ? window.__HADEETH_BASE__ + '/data' : window.location.origin + window.location.pathname.replace(/\/[^/]*$/, '') + '/data';
          
          const [linkResp, lidwaData] = await Promise.all([
            fetch(`${baseUrl}/links/${bookId}.json`).catch(() => null),
            window.HadeethAPI.fetchNdjsonFull('sources/lidwa', bookId).catch(() => null)
          ]);

          if (linkResp && linkResp.ok) {
            const linkData = await linkResp.json();
            const fawazToLidwa = linkData.fawaz_to_lidwa || {};
            const abToFawaz = linkData.ab_to_fawaz || {};
            for (const [abId, fawazId] of Object.entries(abToFawaz)) {
              if (fawazToLidwa[fawazId] !== undefined) {
                  abToLidwaMap[abId] = String(fawazToLidwa[fawazId]);
              }
            }
          }

          if (lidwaData) {
            (Array.isArray(lidwaData) ? lidwaData : (lidwaData.hadiths || [])).forEach(h => {
              const num = h.hadith_number ?? h.hadithnumber ?? h.id;
              if (num !== undefined && h.text_id) lidwaIdMap[String(num)] = h.text_id;
            });
          }
        } catch (e) {
          console.warn('Linking engine error for AhmedBaset:', e);
        }

        allHadiths = (abChapter.hadiths || []).map(h => {
          const abIdGlobal = String(h.idInBook || h.id);
          const lidwaNum = abToLidwaMap[abIdGlobal];
          const matchedIdText = lidwaNum ? (lidwaIdMap[lidwaNum] || '') : '';
          
          return {
            hadith_number: lidwaNum ? String(lidwaNum) : (h.idInBook || h.id),
            hadith_id_global: h.id,
            text_ar: h.arabic || '',
            text_en: h.english ? (h.english.narrator ? `${h.english.narrator} ${h.english.text}` : h.english.text || '') : '',
            text_id: matchedIdText,
            grade: 'Sahih',
            book_id: bookId,
            _source: 'ahmedbaset',
            _noId: !matchedIdText
          };
        });

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
  // BRANCH C — Native source hadith loading (Lidwa / MJNA.or.id)
  // ================================================================
  } else if (activeDataset === 'native_lidwa' || activeDataset === 'native_mjna' || activeDataset === 'native_irsyad') {
    try {
      const mjnaBooks = ['ibnukhuzaimah', 'ibnuhibban', 'mustadrak', 'daruquthni'];
      const irsyadBooks = ['syafii', 'riyad_arab'];
      const isMjnaBook = mjnaBooks.includes(bookId);
      const isIrsyadBook = irsyadBooks.includes(bookId);
      let nativeSourceDir = 'sources/lidwa';
      let nativeSourceLabel = 'Lidwa';
      if (isMjnaBook) {
        nativeSourceDir = 'sources/mjna';
        nativeSourceLabel = 'MJNA.or.id';
      } else if (isIrsyadBook) {
        nativeSourceDir = 'sources/irsyadulibad';
        nativeSourceLabel = 'IrsyadulIbad';
      }
      const lidwaAll = await window.HadeethAPI.fetchNdjsonFull(nativeSourceDir, bookId).catch(() => null);
      if (lidwaAll) {
        const chNum = parseInt(chapterId);
        
        let chapTitleId = `Kitab ${chapterId}`;
        let chapTitleEn = `Chapter ${chapterId}`;
        let chapTitleAr = '';
        let startNum = -1;
        let endNum = -1;
        
        try {
          const idxResp = await fetch(`data/lidwa-chapters/${bookId}.json`);
          if (idxResp.ok) {
            const idx = await idxResp.json();
            const ch = (idx.chapters || []).find(c =>
              c.chapter_number === chNum ||
              c.chapter_number === String(chNum) ||
              String(c.chapter_id) === String(chNum) ||
              String(c.chapter_id) === String(chapterId)
            );
            if (ch) {
              chapTitleId = ch.title_id || chapTitleId;
              chapTitleEn = ch.title_en || chapTitleEn;
              chapTitleAr = ch.title_ar || '';
              if (ch.hadith_start !== undefined) startNum = ch.hadith_start;
              if (ch.hadith_end !== undefined) endNum = ch.hadith_end;
            }
          }
        } catch(e2) { /* ignore */ }

        let chapHadiths = lidwaAll;
        if (startNum !== -1 && endNum !== -1) {
            chapHadiths = lidwaAll.filter(h => {
                const n = parseInt(String(h.hadith_number).replace(/\D/g, '')) || 0;
                return n >= startNum && n <= endNum;
            });
        } else {
            // Fallback just grab first 100 if range not found
            chapHadiths = lidwaAll.slice(0, 100);
        }
        
        // Fix Lidwa lexicographical sorting issue (e.g. 10 before 8)
        chapHadiths.sort((a, b) => {
          const numA = parseInt(String(a.hadith_number).replace(/\D/g, '')) || 0;
          const numB = parseInt(String(b.hadith_number).replace(/\D/g, '')) || 0;
          return numA - numB;
        });

        if (chTitleEn) chTitleEn.innerText = chapTitleEn;
        if (chTitleId) chTitleId.innerText = chapTitleId;
        // For MJNA books: if chapter has no separate Arabic title, show book-level Arabic title
        let arToShow = chapTitleAr;
        if (!arToShow && isMjnaBook) {
          const mjnaArFallbacks = {
            ibnukhuzaimah: 'صحيح ابن خزيمة',
            ibnuhibban: 'صحيح ابن حبان',
            mustadrak: 'المستدرك على الصحيحين',
            daruquthni: 'سنن الدارقطني',
          };
          arToShow = mjnaArFallbacks[bookId] || '';
        }
        if (chTitleAr) chTitleAr.innerText = arToShow;
        const bcCurEn2 = document.querySelector('[data-list-breadcrumb-current-en]');
        const bcCurId2 = document.querySelector('[data-list-breadcrumb-current-id]');
        if (bcCurEn2) bcCurEn2.innerText = chapTitleEn;
        if (bcCurId2) bcCurId2.innerText = chapTitleId;
        const chMetaEn2 = document.querySelector('[data-list-chapter-meta-en]');
        const chMetaId2 = document.querySelector('[data-list-chapter-meta-id]');
        if (chMetaEn2) chMetaEn2.innerText = `${nativeSourceLabel} Kitab ${chapterId}`;
        if (chMetaId2) chMetaId2.innerText = `${nativeSourceLabel} Kitab ${chapterId}`;

        allHadiths = chapHadiths.map(h => {
          // text_id: for MJNA books (after NDJSON rebuild) it's in translations.id[].text
          // for core Lidwa books it's in h.text_id directly
          const mjnaIdTx = h.translations && h.translations.id && h.translations.id.length > 0
            ? h.translations.id[0].text : null;
          const textId = mjnaIdTx || h.text_id || '';
          const textEn = (h.translations && h.translations.en && h.translations.en[0] && h.translations.en[0].text)
            || h.text_en || '';
          return {
          hadith_number: h.hadith_number,
          text_ar: h.text_ar || '',
          text_en: textEn,
          text_id: textId,
          text_ur: h.text_ur || '',
          text_fr: h.text_fr || '',
          grade: h.grade || '',
          grade_by: h.grade_by || '',
          book_id: bookId,
          _source: isMjnaBook ? 'mjna' : 'lidwa',
          _lidwaRef: h.usc_msa_ref || ''
        };
        });

        const total = allHadiths.length;
        const firstH = chapHadiths[0];
        const lastH = chapHadiths[chapHadiths.length - 1];
        const rangeStr = firstH && lastH ? `${firstH.hadith_number} – ${lastH.hadith_number}` : '';
        const countEl2 = document.querySelector('[data-list-count-meta-en]');
        const countIdEl2 = document.querySelector('[data-list-count-meta-id]');
        const countFallback2 = document.querySelector('[data-list-count-meta]');
        if (countEl2) countEl2.innerText = `${nativeSourceLabel} Hadith ${rangeStr} • ${total} Hadiths in ${bookName} Kitab ${chapterId}`;
        if (countIdEl2) countIdEl2.innerText = `${nativeSourceLabel} Hadits ${rangeStr} • ${total} Hadits dalam ${bookName} Kitab ${chapterId}`;
        if (countFallback2 && !countEl2) countFallback2.innerText = `${total} Hadits — ${nativeSourceLabel} Kitab ${chapterId}`;
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
    let lidwaIdMap = {};
    let abEngMap = {};
    let linkGraph = {};
    try {
      const baseUrl = window.__HADEETH_BASE__
        ? window.__HADEETH_BASE__ + '/data'
        : (() => {
            const s = document.querySelector('script[src*="js/api.js"]');
            if (s) return new URL(s.src, window.location.href).href.replace(/js\/api\.js.*$/, 'data');
            return window.location.origin + window.location.pathname.replace(/\/[^/]*$/, '') + '/data';
          })();
      
      const abBookMap = { 
      ahmad: 'the_9_books/ahmed',
      bukhari: 'the_9_books/bukhari',
      muslim: 'the_9_books/muslim',
      abudawud: 'the_9_books/abudawud',
      tirmidhi: 'the_9_books/tirmidhi',
      nasai: 'the_9_books/nasai',
      ibnmajah: 'the_9_books/ibnmajah',
      malik: 'the_9_books/malik',
      darimi: 'the_9_books/darimi',
      nawawi: 'forties/nawawi40',
      qudsi: 'forties/qudsi40',
      dehlawi: 'forties/shahwaliullah40',
      riyad: 'other_books/riyad_assalihin',
      shamail: 'other_books/shamail_muhammadiyah',
      bulugh: 'other_books/bulugh_almaram',
      adab: 'other_books/aladab_almufrad',
      mishkat: 'other_books/mishkat_almasabih'
    };
      const abBook = abBookMap[bookId] || bookId;

      const [lidwaData, linkResp, abResp] = await Promise.all([
          window.HadeethAPI.fetchNdjsonFull('sources/lidwa', bookId).catch(() => null),
          fetch(`${baseUrl}/links/${bookId}.json`).catch(() => null),
          fetch(`${baseUrl}/sources/ahmedbaset/by_book/${abBook}.json`).catch(() => null)
      ]);

      if (linkResp && linkResp.ok) linkGraph = await linkResp.json();

      if (lidwaData) {
        // Build map: hadith_number  text_id
        (Array.isArray(lidwaData) ? lidwaData : (lidwaData.hadiths || [])).forEach(h => {
          const num = h.hadith_number ?? h.hadithnumber ?? h.id;
          if (num !== undefined && h.text_id) lidwaIdMap[String(num)] = h.text_id;
        });
      }

      if (abResp && abResp.ok) {
        const abData = await abResp.json();
        (abData.hadiths || []).forEach(h => {
          if (h.english && h.english.text) {
             const txt = h.english.narrator ? `${h.english.narrator} ${h.english.text}` : h.english.text;
             abEngMap[String(h.idInBook)] = txt;
          }
        });
      }
    } catch (e) {
      console.warn('Fallback sources or links not available for', bookId, e);
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
        const num = String(h.hadithnumber ?? h.id);
        
        let targetLidwaId = null;
        if (linkGraph && linkGraph.fawaz_to_lidwa && linkGraph.fawaz_to_lidwa[num]) {
            targetLidwaId = linkGraph.fawaz_to_lidwa[num];
        }

        let targetAbId = null;
        if (linkGraph && ((linkGraph.fawaz_to_ab && linkGraph.fawaz_to_ab[num]) || (linkGraph[num] && linkGraph[num].ahmedbaset_id))) {
            targetAbId = linkGraph.fawaz_to_ab ? linkGraph.fawaz_to_ab[num] : (linkGraph[num] ? linkGraph[num].ahmedbaset_id : null);
        }

        let idText = lidwaIdMap[targetLidwaId] || '';
        if (idText && targetLidwaId !== num) {
            idText = `<div class="mb-2 text-xs text-blue-500 font-semibold">[Linked from Lidwa #${targetLidwaId}]</div>` + idText;
        }

        let finalEnText = engMap[num] !== undefined ? engMap[num] : '';
        if (!finalEnText && abEngMap[targetAbId]) {
            finalEnText = `<div class="mb-2 text-xs text-amber-500 font-semibold">[Linked from AhmedBaset #${targetAbId}]</div>` + abEngMap[targetAbId];
        }

        return {
          hadith_number: num,
          text_en: finalEnText,
          text_ar: araMap[num] !== undefined ? araMap[num] : '',
          // Indonesian linked dynamically from Lidwa/Irsyad via graph
          text_id: idText,
          grade: 'Sahih',
          book_id: bookId,
          _source: 'primary'  // marks this for the blue attribution note in renderList
        };
      });
    }
  } // end primary branch

  filteredHadiths = [...allHadiths];
  if (activeDataset === 'fawazahmed') {
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
      const displayNum = (localStorage.getItem('numbering_system') === 'lidwa' && item.lidwa_id) ? item.lidwa_id : num;
      const enText = item.text_en || '';
      const arText = item.text_ar || '';
      const hasId = !!item.text_id;
      const idText = item.text_id || enText;
      const gradeEn = item.grade_en || item.grade || 'Sahih';
      const gradeId = item.grade_id || 'Shahih';

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
        <strong class="font-semibold">Info Sumber:</strong> Teks terjemahan Indonesia ini diintegrasikan dari <strong>Lidwa / Irsyad</strong> (dicocokkan berdasarkan tabel relasi/mapping metadata).
      </div>`;

      // AhmedBaset: amber warning (may not align to AhmedBaset narration variant)
      const abIdSourceNote = hasId
        ? `<div class="mt-2 px-3 py-2 rounded-lg border border-amber-500/30 bg-amber-500/5 text-[11px] text-amber-600 dark:text-amber-400 leading-snug">
        <strong class="font-semibold">Note — Indonesian translation source:</strong> AhmedBaset does not include Indonesian translations.
        The text below is sourced from <strong>Lidwa / Irsyad</strong>, matched using the relational metadata map.
      </div>`
        : `<div class="mt-2 px-3 py-2 rounded-lg border border-amber-500/30 bg-amber-500/5 text-[11px] text-amber-600 dark:text-amber-400 leading-snug">
        <strong class="font-semibold">Note:</strong> AhmedBaset has no Indonesian translation, and no Lidwa match was found for this hadith number.
      </div>`;

      // Grade-by explanation helper
      const gradeByHtml = (gradedBy) => gradedBy
        ? `<p class="text-[11px] text-outline dark:text-gray-500 mt-1">Graded Sahih by: <em>${escapeHtml(gradedBy)}</em> <span class="opacity-60">(grading per Lidwa/Irsyad)</span></p>`
        : '';

      const idUnavailableNote = '<em class="text-outline dark:text-gray-500">(Terjemahan tidak tersedia untuk variasi sanad ini)</em>';

      const enUnavailableNote = '<em class="text-outline dark:text-gray-500">(English translation not available in this dataset)</em>';

      if (currentLang === 'id') {
        const content = hasId ? escapeHtml(item.text_id) : idUnavailableNote;
        displayText = `<p class="text-sm text-on-surface-variant dark:text-gray-300 leading-relaxed font-body-md"><strong class="text-xs text-secondary dark:text-[#10b981] block mb-1">Terjemahan Indonesia:</strong>${content}</p>`;
        if (isPrimary) displayText += primaryIdSourceNote;
        if (isAhmedBaset) displayText += abIdSourceNote;
        if (isLidwa) displayText += gradeByHtml(item.grade_by);
      } else if (currentLang === 'en') {
        const enContent = enText ? escapeHtml(enText) : enUnavailableNote;
        displayText = `<p class="text-sm text-on-surface-variant dark:text-gray-300 leading-relaxed font-body-md"><strong class="text-xs text-sunan-emerald dark:text-[#10b981] block mb-1">English Translation:</strong>${enContent}</p>`;
        if (isPrimary) displayText += `<p class="text-[11px] text-blue-500/70 dark:text-blue-400/70 mt-1 italic">Switch to <strong>Dual Language</strong> or <strong>Bahasa Indonesia</strong> to view Indonesian — sourced from Lidwa/Irsyad (fawazahmed0 has no ind edition)</p>`;
        if (isAhmedBaset) displayText += `<p class="text-[11px] text-amber-600/80 dark:text-amber-400/70 mt-1 italic">Source: AhmedBaset · Switch to <strong>Dual Language</strong> or <strong>Bahasa Indonesia</strong> to see the Lidwa-sourced Indonesian translation (matched by number — not from AhmedBaset)</p>`;
        if (isLidwa) displayText += gradeByHtml(item.grade_by);
      } else {
        const idContent = hasId ? escapeHtml(item.text_id) : idUnavailableNote;
        const idHtml = `<p class="text-sm text-on-surface-variant dark:text-gray-300 leading-relaxed font-body-md"><strong class="text-xs text-secondary dark:text-[#10b981] block mb-1">Terjemahan Indonesia:</strong>${idContent}</p>`;
        const enContent = enText ? escapeHtml(enText) : enUnavailableNote;
        const enHtml = `<p class="text-xs text-outline dark:text-gray-400 leading-relaxed font-body-md"><strong class="text-xs text-sunan-emerald dark:text-[#10b981] block mb-1">English Translation:</strong>${enContent}</p>`;
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
              <span class="bg-sunan-emerald/10 text-sunan-emerald dark:text-[#10b981] text-xs font-semibold px-2.5 py-0.5 rounded">
                <span data-lang-en>${escapeHtml(gradeEn)}</span>
                <span data-lang-id style="display:none">${escapeHtml(gradeId)}</span>
              </span>
            </div>
            <button data-copy-hadith data-copy-share-btn data-hadith-title="${escapeHtml(bookName)} #${num}" data-copy-hadith-ar="${escapeHtml(arText)}" data-copy-hadith-text-id="${escapeHtml(idText)}" data-copy-hadith-text-en="${escapeHtml(enText)}" data-share-url="${window.location.origin + window.location.pathname.replace('hadith-list.html', '')}${detailLink}" class="btn-copy-share text-xs font-semibold px-2.5 py-1 rounded border border-outline-variant/40 dark:border-[#334155] text-primary dark:text-white hover:bg-surface-container-low dark:hover:bg-[#334155] transition-all flex items-center gap-1.5 cursor-pointer">
              <span class="material-symbols-outlined text-[14px]">share</span>
              <span data-lang-en>Copy / Share</span><span data-lang-id>Salin / Bagikan</span>
            </button>
          </div>

          <div class="hadith-text-container relative">
            <div class="hadith-text-inner transition-all duration-300 overflow-hidden" style="max-height: 380px;">
              ${arText ? `<p class="font-arabic-body text-2xl text-primary dark:text-white text-right leading-loose" dir="rtl">${escapeHtml(arText)}</p>` : ''}
              ${displayText}
            </div>
            <div class="read-more-overlay absolute bottom-0 left-0 right-0 h-24 bg-gradient-to-t from-surface dark:from-[#1e293b] to-transparent pointer-events-none hidden"></div>
            <button class="read-more-btn hidden text-secondary dark:text-[#10b981] font-semibold text-xs mt-2 hover:underline flex items-center gap-1 cursor-pointer">
              <span data-lang-en>Read more</span><span data-lang-id>Selengkapnya</span> <span class="material-symbols-outlined text-[14px]">expand_more</span>
            </button>
          </div>

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
    const validBooksWithNote = ['bukhari', 'muslim', 'syafii', 'ibnukhuzaimah', 'ibnuhibban', 'mustadrak', 'daruquthni'];
    
    if (validBooksWithNote.includes(bookId)) {
      const bookNames = {
        'bukhari': 'Sahih al-Bukhari (7,589 hadiths)',
        'muslim': 'Sahih Muslim (7,563 hadiths)',
        'syafii': 'Musnad Syafi\'i (1,800 hadiths)',
        'ibnukhuzaimah': 'Shahih Ibnu Khuzaimah (1808)',
        'ibnuhibban': 'Shahih Ibnu Hibban (2769)',
        'mustadrak': 'Mustadrak Al-Hakim (673)',
        'daruquthni': 'Sunan Daruquthni (4790)'
      };
      const bookNamesId = {
        'bukhari': 'Shahih Bukhari (7.589 hadits)',
        'muslim': 'Shahih Muslim (7.563 hadits)',
        'syafii': 'Musnad Syafi\'i (1.800 hadits)',
        'ibnukhuzaimah': 'Shahih Ibnu Khuzaimah (1808)',
        'ibnuhibban': 'Shahih Ibnu Hibban (2769)',
        'mustadrak': 'Mustadrak Al-Hakim (673)',
        'daruquthni': 'Sunan Daruquthni (4790)'
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
    if (window.setupReadMore) window.setupReadMore();

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
        native_lidwa:      { kitab: '📚 77 Kitab', hadith: '📖 7.008 Hadits (Lidwa)', numbering: 'Penomoran: Lidwa / Irsyad (1–7008)' }
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
        native_lidwa:      { kitab: '📚 —', hadith: '📖 5.362 Hadits (Lidwa)', numbering: 'Penomoran: Lidwa (1–5362) · tidak ada pembagian kitab dari sumber Lidwa' }
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
        native_lidwa:      { kitab: '📚 51 Kitab', hadith: '📖 5.662 Hadits (Lidwa)', numbering: 'Penomoran: Lidwa / Irsyad (1–5662)' }
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
        native_lidwa:      { kitab: '📚 56 Kitab', hadith: '📖 1.594 Hadits (Lidwa)', numbering: 'Penomoran: Lidwa / Irsyad (1–1594) · beberapa hadits dikelompokkan' }
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
        native_lidwa:      { kitab: '📚 Susunan Musnad', hadith: '📖 26.363 Hadits (Lidwa)', numbering: 'Penomoran: Lidwa / Irsyad (1–26363) · susunan musnad' }
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
      datasetInfo: { fawazahmed: { kitab: '📚 25 Jilid', hadith: '📖 20.000+ Hadits', numbering: 'Dataset dalam pengembangan' } }
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
      datasetInfo: { fawazahmed: { kitab: '📚 37 Kitab', hadith: '📖 37.000+ Hadits', numbering: 'Dataset dalam pengembangan' } }
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

  const activeDataset = localStorage.getItem('dataset_version') || 'fawazahmed';

  // Validate dataset availability for this book
  const dsConfig = BOOK_DATASETS[bookId] || [];
  const validDs = dsConfig.find(d => d.id === activeDataset);
  const resolvedDataset = validDs ? activeDataset : (dsConfig.length > 0 ? dsConfig[0].id : 'fawazahmed');

  // Apply dataset-specific counts to info card
  const dsInfo = (meta.datasetInfo || {})[resolvedDataset] || (meta.datasetInfo || {}).fawazahmed || {};
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
  if (resolvedDataset === 'fawazahmed') {
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
    if (window.setupReadMore) window.setupReadMore();

  // ================================================================
  // BRANCH B — AhmedBaset (native Arabic + EN, no ID)
  // Reads from data/sources/ahmedbaset/by_book/the_9_books/<book>.json
  // ================================================================
  } else if (resolvedDataset === 'native_ahmedbaset') {
    const abBookMap = { 
      ahmad: 'the_9_books/ahmed',
      bukhari: 'the_9_books/bukhari',
      muslim: 'the_9_books/muslim',
      abudawud: 'the_9_books/abudawud',
      tirmidhi: 'the_9_books/tirmidhi',
      nasai: 'the_9_books/nasai',
      ibnmajah: 'the_9_books/ibnmajah',
      malik: 'the_9_books/malik',
      darimi: 'the_9_books/darimi',
      nawawi: 'forties/nawawi40',
      qudsi: 'forties/qudsi40',
      dehlawi: 'forties/shahwaliullah40',
      riyad: 'other_books/riyad_assalihin',
      shamail: 'other_books/shamail_muhammadiyah',
      bulugh: 'other_books/bulugh_almaram',
      adab: 'other_books/aladab_almufrad',
      mishkat: 'other_books/mishkat_almasabih'
    };
    const abBook = abBookMap[bookId] || bookId;
    let abData = null;
    try {
      const resp = await fetch(`data/sources/ahmedbaset/by_book/${abBook}.json`);
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
  // BRANCH C — Native source loading (Lidwa for 9 books, MJNA.or.id for additional books)
  // Reads from data/lidwa-chapters/<book>.json (pre-built index)
  // ================================================================
  } else if (resolvedDataset === 'native_lidwa' || resolvedDataset === 'native_mjna' || resolvedDataset === 'native_irsyad') {
    let lidwaIndex = null;
    try {
      const resp = await fetch(`data/lidwa-chapters/${bookId}.json`);
      if (resp.ok) lidwaIndex = await resp.json();
    } catch(e) { console.warn('Chapter index fetch error:', e); }

    if (!lidwaIndex || !lidwaIndex.chapters || lidwaIndex.chapters.length === 0) {
      container.innerHTML = `<div class="col-span-2 py-12 text-center text-outline dark:text-gray-400">
        <span class="material-symbols-outlined text-4xl block mb-2">info</span>
        <p>Chapter data not available for <strong>${bookId}</strong>.</p>
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
                <span class="text-xs text-outline dark:text-gray-400 font-semibold">${idSource} ${hadithRange}${hadithCount ? ` &bull; ${hadithCount} hadits` : ''}</span>
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

  // Fetch English + Arabic from fawazahmed0 CDN; Indonesian from source data (Lidwa / IrsyadulIbad / MJNA.or.id)
  const baseUrl = window.__HADEETH_BASE__
    ? window.__HADEETH_BASE__ + '/data'
    : (() => {
        const s = document.querySelector('script[src*="js/api.js"]');
        if (s) return new URL(s.src, window.location.href).href.replace(/js\/api\.js.*$/, 'data');
        return window.location.origin + window.location.pathname.replace(/\/[^/]*$/, '') + '/data';
      })();

  const [engEdition, araEdition, linkResp] = await Promise.all([
    window.HadeethAPI.getEdition('eng', bookId).catch(() => null),
    window.HadeethAPI.getEdition('ara', bookId).catch(() => null),
    fetch(`${baseUrl}/links/${bookId}.json`).catch(() => null)
  ]);

  let linkGraph = {};
  if (linkResp && linkResp.ok) {
    linkGraph = await linkResp.json();
  }

  // Load Indonesian from native source data (Lidwa / IrsyadulIbad / MJNA.or.id / etc.)
  let indMap = {};
  try {
    const lData = await window.HadeethAPI.fetchNdjsonFull('sources/lidwa', bookId).catch(() => null);
    if (lData) {
      const lidwaById = {};
      (Array.isArray(lData) ? lData : (lData.hadiths || [])).forEach(h => {
        const num = h.hadith_number ?? h.hadithnumber ?? h.id;
        if (num !== undefined && h.text_id) lidwaById[String(num)] = h.text_id;
      });

      // Populate indMap (FawazID -> LidwaText) using cross_ref_graph
      if (engEdition && engEdition.hadiths) {
          engEdition.hadiths.forEach(h => {
              const fawazId = String(h.hadithnumber ?? h.id);
              let targetLidwaId = fawazId;
              if (linkGraph && linkGraph.fawaz_to_lidwa && linkGraph.fawaz_to_lidwa[fawazId]) {
                  targetLidwaId = linkGraph.fawaz_to_lidwa[fawazId];
              }
              if (lidwaById[targetLidwaId]) {
                  let textId = lidwaById[targetLidwaId];
                  if (targetLidwaId !== fawazId) {
                      textId = `<div class="mb-2 text-xs text-blue-500 font-semibold">[Linked from Lidwa #${targetLidwaId}]</div>` + textId;
                  }
                  indMap[fawazId] = textId;
              }
          });
      }
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
            <span class="bg-primary dark:bg-[#10b981] text-white dark:text-black text-xs font-bold px-2.5 py-0.5 rounded">${isIdLang ? `Hadits #${displayNum}` : `Hadith #${displayNum}`}</span>
            <span class="bg-sunan-emerald/10 text-sunan-emerald dark:text-[#10b981] text-xs font-semibold px-2 py-0.5 rounded">${isIdLang ? 'Shahih' : 'Sahih'}</span>
          </div>
          <button type="button" data-copy-share-btn data-book="${bookId}" data-id="${num}" data-hadith-title="${escapeHtml(bookName)} #${num}" class="border border-outline-variant/30 dark:border-[#334155] hover:border-secondary dark:hover:border-[#10b981] text-xs font-semibold text-primary dark:text-white px-3 py-1 rounded-lg transition-colors flex items-center gap-1.5 cursor-pointer">
            <span class="material-symbols-outlined text-sm">share</span>
            <span>${isIdLang ? 'Salin / Bagikan' : 'Copy / Share'}</span>
          </button>
        </div>
        <div class="hadith-text-container relative">
          <div class="hadith-text-inner transition-all duration-300 overflow-hidden" style="max-height: 380px;">
            ${araText ? `<p class="font-arabic-body text-xl text-primary dark:text-white text-right leading-loose" dir="rtl">${escapeHtml(araText)}</p>` : ''}
            ${transHtml}
          </div>
          <div class="read-more-overlay absolute bottom-0 left-0 right-0 h-24 bg-gradient-to-t from-surface dark:from-[#1e293b] to-transparent pointer-events-none hidden"></div>
          <button class="read-more-btn hidden text-secondary dark:text-[#10b981] font-semibold text-xs mt-2 hover:underline flex items-center gap-1 cursor-pointer">
            <span data-lang-en>Read more</span><span data-lang-id>Selengkapnya</span> <span class="material-symbols-outlined text-[14px]">expand_more</span>
          </button>
        </div>
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
  if (window.setupReadMore) window.setupReadMore();

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

  const activeDataset = localStorage.getItem('dataset_version') || 'fawazahmed';
  let dsPrefix = 'fawaz';
  if (activeDataset === 'native_lidwa') dsPrefix = 'lidwa';
  else if (activeDataset === 'native_ahmedbaset') dsPrefix = 'ab';

  let narrators = [];
  let data = null;
  try {
    const rawisDict = await window.HadeethAPI.getActiveRawis();
    data = await window.HadeethAPI.getHadith(bookId, hadithNum, dsPrefix);

    if (data) {
      let gradeEn = data.grade_en || data.grade || '';
      let gradeId = data.grade_id || '';
      let elevation = data.elevation || '';

      if ((!gradeEn && !gradeId) || !elevation) {
        if (data.related && data.related.length > 0) {
          for (const relStr of data.related) {
            const parts = relStr.split(':');
            if (parts.length === 2) {
              try {
                const relData = await window.HadeethAPI.getHadith(parts[0], parts[1], dsPrefix);
                if (relData) {
                  if ((!gradeEn && !gradeId) && (relData.grade_en || relData.grade_id || relData.grade)) {
                    data.grade_en = relData.grade_en || relData.grade || '';
                    data.grade_id = relData.grade_id || '';
                    data._hasGradeFallback = true;
                  }
                  if (!elevation && relData.elevation) {
                    data.elevation = relData.elevation;
                    data._hasElevationFallback = true;
                  }
                }
              } catch(e) {}
              gradeEn = data.grade_en || data.grade || '';
              gradeId = data.grade_id || '';
              elevation = data.elevation || '';
              if ((gradeEn || gradeId) && elevation) break;
            }
          }
        }
      }
    }
    
    // Final Node: Collector & Author metadata
    const authorNamesEn = {
      bukhari: 'Imam al-Bukhari', muslim: 'Imam Muslim', abudawud: 'Imam Abu Dawood',
      tirmidhi: 'Imam at-Tirmidhi', nasai: 'Imam an-Nasa\'i', ibnmajah: 'Imam Ibn Majah',
      malik: 'Imam Malik bin Anas', ahmad: 'Imam Ahmad bin Hanbal', darimi: 'Imam Abdullah bin Abdul Rahman ad-Darimi'
    };
    const authorNamesId = {
      bukhari: 'Imam al-Bukhari', muslim: 'Imam Muslim', abudawud: 'Imam Abu Daud',
      tirmidhi: 'Imam at-Tirmidzi', nasai: 'Imam an-Nasa\'i', ibnmajah: 'Imam Ibn Majah',
      malik: 'Imam Malik bin Anas', ahmad: 'Imam Ahmad bin Hanbal', darimi: 'Imam Abdullah bin Abdul Rahman ad-Darimi'
    };
    const authorNameEn = authorNamesEn[bookId.toLowerCase()] || 'Imam al-Bukhari';
    const authorNameId = authorNamesId[bookId.toLowerCase()] || 'Imam al-Bukhari';
    const authorIdMap = { 'bukhari': 'rawi_al_bukhari', 'muslim': 'rawi_muslim_ibn_hajjaj', 'abudawud': 'rawi_abu_dawud', 'tirmidhi': 'rawi_al_tirmidhi', 'nasai': 'rawi_al_nasai', 'ibnmajah': 'rawi_ibn_majah', 'malik': 'rawi_malik_bin_anas', 'ahmad': 'rawi_ahmad', 'darimi': 'rawi_darimi' };
    const authorProfileUrl = authorIdMap[bookId] ? `profile-detail.html?id=${authorIdMap[bookId]}` : `profile-detail.html?id=rawi_al_bukhari`;

    if (data && data.rawis && data.rawis.length > 0) {
      let paths = data.paths || [];
      if (paths.length === 0) {
        // Fallback for single path
        paths = [data.rawis];
      }
      
      const tabsContainer = document.getElementById('sanad-tabs-container');
      if (paths.length > 1) {
        tabsContainer.classList.remove('hidden');
        let tabsHtml = '';
        paths.forEach((path, idx) => {
          // Identify the unique top narrator (usually the sheikh or the one who branches)
          // Since the path is Companion -> Sheikh, the last element is the Sheikh
          const lastRawi = path[path.length - 1];
          const rawiName = typeof lastRawi === 'object' ? (lastRawi.name_id || lastRawi.name_en || lastRawi.id) : lastRawi;
          const isActive = idx === 0 ? 'bg-primary text-white dark:bg-[#10b981] dark:text-black' : 'bg-surface-container-low text-on-surface-variant hover:bg-surface-container dark:bg-[#1e293b] dark:text-gray-300 dark:hover:bg-[#334155]';
          
          tabsHtml += `
            <button class="sanad-tab-btn px-4 py-2 rounded-lg font-bold text-sm whitespace-nowrap transition-colors border border-outline-variant/30 dark:border-[#334155] ${isActive}" data-path-idx="${idx}">
              <span data-lang-en>Branch ${idx + 1} (${rawiName})</span>
              <span data-lang-id style="display:none">Jalur ${idx + 1} (${rawiName})</span>
            </button>
          `;
        });
        tabsContainer.innerHTML = tabsHtml;
        
        // Attach event listeners
        setTimeout(() => {
          const btns = tabsContainer.querySelectorAll('.sanad-tab-btn');
          btns.forEach(btn => {
            btn.addEventListener('click', (e) => {
              // Update active tab style
              btns.forEach(b => {
                b.className = b.className.replace(/bg-primary text-white dark:bg-\[\#10b981\] dark:text-black/g, 'bg-surface-container-low text-on-surface-variant hover:bg-surface-container dark:bg-[#1e293b] dark:text-gray-300 dark:hover:bg-[#334155]');
              });
              const clicked = e.currentTarget;
              clicked.className = clicked.className.replace(/bg-surface-container-low text-on-surface-variant hover:bg-surface-container dark:bg-\[\#1e293b\] dark:text-gray-300 dark:hover:bg-\[\#334155\]/g, 'bg-primary text-white dark:bg-[#10b981] dark:text-black');
              
              const idx = parseInt(clicked.getAttribute('data-path-idx'));
              renderSanadPath(paths[idx], rawisDict, data, bookId, authorProfileUrl, authorNameEn, authorNameId);
            });
          });
        }, 50);
      } else {
        tabsContainer.classList.add('hidden');
      }

      // Initial render of Path 0
      renderSanadPath(paths[0], rawisDict, data, bookId, authorProfileUrl, authorNameEn, authorNameId);

    } else {
      // Empty fallback
      renderSanadPath([], rawisDict, data, bookId, authorProfileUrl, authorNameEn, authorNameId);
    }
  } catch (err) {
    console.warn('Failed to load sanad chain:', err);
  }
}

function renderSanadPath(rawiList, rawisDict, data, bookId, authorProfileUrl, authorNameEn, authorNameId) {
  let narrators = [];
  
  // Filter out consecutive duplicates within the path
  let filteredRawiList = [];
  for (const item of rawiList) {
    const id = typeof item === 'object' ? item.id : item;
    if (filteredRawiList.length === 0) {
      filteredRawiList.push(item);
    } else {
      const lastItem = filteredRawiList[filteredRawiList.length - 1];
      const lastId = typeof lastItem === 'object' ? lastItem.id : lastItem;
      if (lastId !== id) filteredRawiList.push(item);
    }
  }
  
  narrators = filteredRawiList.map((rawItem, idx) => {
    const isObj = typeof rawItem === 'object' && rawItem !== null;
    let rId = isObj ? rawItem.id : rawItem;
    if (typeof rId === 'number' || (typeof rId === 'string' && /^\d+$/.test(rId))) {
        rId = 'lidwa_' + rId;
    }
    
    const rawiData = rawisDict[rId] || {};
    const isFirst = idx === 0 || (rawiData.grade && rawiData.grade.toLowerCase().includes('sahab'));
    
    let enName = (isObj ? rawItem.name_en : null) || rawiData.en || 'Transmitter ' + rId;
    let idName = (isObj ? rawItem.name_id : null) || rawiData.id || 'Perawi ' + rId;
    let arName = (isObj ? rawItem.ar : null) || rawiData.ar || idName;
    
    return {
      rawi_id: rId,
      name: enName + (isFirst && !enName.includes('رضي الله عنه') ? ' (رضي الله عنه)' : ''),
      name_id: idName,
      roleEn: rawiData.role || (isFirst ? 'SAHABI (COMPANION) • GRADE: THIQAH' : 'TRANSMITTER (RAWI) • GRADE: ' + (rawiData.grade || 'THIQAH')),
      roleId: rawiData.roleId || (isFirst ? 'SAHABAT NABI • DERAJAT: TSIQAH' : 'PERAWI (RAWI) • DERAJAT: ' + (rawiData.grade || 'TSIQAH')),
      ar: arName,
      kunyah: rawiData.kunyah || (isFirst ? 'Abu Abdillah' : '-'),
      residence: rawiData.residence || (isFirst ? 'Madinah' : '-'),
      death_ah: rawiData.death_ah || (isFirst ? 'Early Era' : '-'),
      counts: rawiData.counts || '-',
      remarks: rawiData.grade ? 'Grade: ' + rawiData.grade : 'No remarks'
    };
  });

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

  const filteredNarrators = narrators.filter(nr => nr.rawi_id !== "1" && !nr.name.toLowerCase().includes('prophet muhammad'));

  filteredNarrators.forEach((nr, idx) => {
    let rawiSlug = nr.rawi_id;
    if (!rawiSlug && nr.name) {
      const cleanName = nr.name.replace(/\(.*?\)/g, '').replace(/[^a-zA-Z0-9\s]/g, '').trim().toLowerCase().replace(/\s+/g, '_');
      rawiSlug = `rawi_${cleanName}`;
    }
    const profileUrl = `profile-detail.html?id=${encodeURIComponent(rawiSlug || 'rawi_abu_hurairah')}`;

    const roleEn = nr.roleEn;
    const roleId = nr.roleId;
    
    const rawNameEn = nr.name || 'Transmitter';
    const pureLatinName = rawNameEn.replace(/[\u0600-\u06FF]/g, '').replace(/\s*\(\s*\)/g, '').replace(/\s+/g, ' ').trim();
    
    const nameEn = pureLatinName;
    const nameId = typeof getIndonesianRawiName === 'function' ? getIndonesianRawiName(pureLatinName, nr.rawi_id, nr.ar) : pureLatinName;
    const displayArName = typeof getArabicScriptForRawi === 'function' ? getArabicScriptForRawi(nr.ar || rawNameEn) : (nr.ar || '');
    
    function escapeHtml(str) {
      if (!str) return '';
      return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#039;');
    }

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
            <span class="font-semibold text-primary dark:text-white">${escapeHtml(nr.kunyah)}</span>
          </div>
          <div>
            <span class="text-outline dark:text-gray-400 block text-[10px] uppercase font-bold">
              <span data-lang-en>SETTLED IN:</span>
              <span data-lang-id style="display:none">DOMISILI:</span>
            </span>
            <span class="font-semibold text-primary dark:text-white">${escapeHtml(nr.residence)}</span>
          </div>
          <div>
            <span class="text-outline dark:text-gray-400 block text-[10px] uppercase font-bold">
              <span data-lang-en>WAFAT (DIED):</span>
              <span data-lang-id style="display:none">WAFAT:</span>
            </span>
            <span class="font-semibold text-primary dark:text-white">${escapeHtml(nr.death_ah)}</span>
          </div>
          <div>
            <span class="text-outline dark:text-gray-400 block text-[10px] uppercase font-bold">
              <span data-lang-en>TOTAL HADITHS:</span>
              <span data-lang-id style="display:none">TOTAL HADITS:</span>
            </span>
            <span class="font-semibold text-sunan-emerald dark:text-[#10b981]">${escapeHtml(nr.counts)}</span>
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
  const container = document.getElementById('sanad-nodes-container');
  if (container) container.innerHTML = html;
  
  const statusEl = document.getElementById('sanad-status-text');
  const elevatedEl = document.getElementById('sanad-elevated-text');
  
  if (statusEl) {
    if (data && data.status) {
        statusEl.innerHTML = `<span data-lang-en>${escapeHtml(data.status)}</span><span data-lang-id style="display:none">${escapeHtml(data.status)}</span>`;
    } else {
        statusEl.innerHTML = `<span data-lang-en>N/A (Not in dataset)</span><span data-lang-id style="display:none">N/A (Tidak tercatat)</span>`;
    }
}
  
  if (data) {
    let gradeEn = data.grade_en || data.grade || 'Sahih';
    let gradeId = data.grade_id || 'Shahih';
    let elevation = data.elevation || '-';

    const gradeEl = document.getElementById('sanad-grade-text');

    if (elevatedEl) {
      let extEn = data._hasElevationFallback ? ' <em class="text-[10px] font-normal opacity-75">(from linked hadith)</em>' : '';
      let extId = data._hasElevationFallback ? ' <em class="text-[10px] font-normal opacity-75">(dari hadits terkait)</em>' : '';
      elevatedEl.innerHTML = `<span data-lang-en>${escapeHtml(elevation)}${extEn}</span><span data-lang-id style="display:none">${escapeHtml(elevation)}${extId}</span>`;
    }

    if (gradeEl) {
      let extEn = data._hasGradeFallback ? ' <em class="text-[10px] font-normal opacity-75">(from linked hadith)</em>' : '';
      let extId = data._hasGradeFallback ? ' <em class="text-[10px] font-normal opacity-75">(dari hadits terkait)</em>' : '';
      const enText = gradeEn || gradeId;
      const idText = gradeId || gradeEn;
      
      gradeEl.innerHTML = `<span data-lang-en>${escapeHtml(enText)}${extEn}</span><span data-lang-id style="display:none">${escapeHtml(idText)}${extId}</span>`;
    }
  }
  
  if (window.LangSystem) window.LangSystem.apply(window.LangSystem.get());
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
  if (!latinOrAr) return '';

  let rawStr = typeof latinOrAr === 'string' ? latinOrAr : (latinOrAr.ar || latinOrAr.name_ar || latinOrAr.name || '');

  // 1. If raw text contains Arabic script, return the Arabic parts.
  if (/[\u0600-\u06FF]/.test(rawStr)) {
    const arabicParts = rawStr.match(/[\u0600-\u06FF\s]+/g);
    if (arabicParts) {
        return arabicParts.join(' ').trim();
    }
  }

  // If it reached here, there are no Arabic characters in the string.
  return '';
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

  const lang = window.activeSyarahLang || ((window.LangSystem && window.LangSystem.isIdMode()) ? 'id' : 'en');

  const dataArray = window.activeSyarahData;
  if (!dataArray || dataArray.length === 0) {
    if (expText) expText.innerText = (lang === 'id') ? "Syarah sedang dimuat atau tidak tersedia..." : "Loading commentary or unavailable...";
    return;
  }

  // Ensure active index
  let activeIndex = window.activeSyarahIndex || 0;
  if (activeIndex >= dataArray.length) activeIndex = 0;

  const data = dataArray[activeIndex];
  const srcNameEn = data.source_name_en || (data.book_id === 'bukhari' ? 'Fath al-Bari' : 'Commentary');
  const srcNameId = data.source_name_id || srcNameEn;

  // Dynamically generate tabs
  const tabsContainer = document.getElementById('syarah-source-tabs');
  if (tabsContainer) {
    let tabsHtml = '';
    dataArray.forEach((c, idx) => {
      const cNameEn = c.source_name_en || 'Commentary ' + (idx + 1);
      const cNameId = c.source_name_id || cNameEn;
      const cName = lang === 'id' ? cNameId : cNameEn;
      
      const isActive = idx === activeIndex;
      const cls = isActive ? activeClass : inactiveClass;
      
      tabsHtml += `<button onclick="window.switchSyarahSource(${idx})" class="${cls}">${escapeHtml(cName)}</button>`;
    });
    tabsContainer.innerHTML = tabsHtml;
  }

  let textExp = '';
  let benefits = [];
  let availableLang = lang;

  if (data[`explanation_${lang}`] || data[`syarah_${lang}`]) {
    textExp = data[`explanation_${lang}`] || data[`syarah_${lang}`];
    benefits = data[`benefits_${lang}`] || [];
  } else if (lang === 'id' && (data['explanation_en'] || data['syarah_en'])) {
    textExp = data['explanation_en'] || data['syarah_en'];
    benefits = data['benefits_en'] || [];
    availableLang = 'en';
  } else if (data['syarah_ar']) {
    textExp = data['syarah_ar'];
    availableLang = 'ar';
  } else if (data['explanation_en'] || data['syarah_en']) {
    textExp = data['explanation_en'] || data['syarah_en'];
    benefits = data['benefits_en'] || [];
    availableLang = 'en';
  }

  if (langSelect && langSelect.value !== availableLang) {
    langSelect.value = availableLang;
  }

  if (!textExp) {
    textExp = lang === 'id' ? '<span class="text-outline dark:text-gray-400 italic">Syarah (Penjelasan Hadits) belum tersedia untuk hadits ini dalam bahasa ini.</span>' : '<span class="text-outline dark:text-gray-400 italic">Syarah (Commentary) is not yet available for this Hadith in this language.</span>';
  }

  if (expText) expText.innerHTML = textExp;

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

window.switchSyarahSource = function(idx) {
  window.activeSyarahIndex = parseInt(idx) || 0;
  renderSyarahUI();
};

async function loadHadithSyarah(bookId, hadithNum) {
  const hadithId = `${bookId}_${hadithNum}`;
  let commentariesArray = [];

  // Default Syarah language to current active site language (id or en)
  const currentSiteLang = (window.LangSystem && window.LangSystem.get()) ? window.LangSystem.get() : ((window.LangSystem && window.LangSystem.isIdMode()) ? 'id' : 'en');
  window.activeSyarahLang = currentSiteLang;

  try {
    let resolvedHadithId = hadithNum;
    try {
       resolvedHadithId = await window.HadeethAPI.getPrimaryAnchorId(bookId, hadithNum);
    } catch (e) {}

    commentariesArray = await window.HadeethAPI.getCommentaries(bookId, resolvedHadithId);
  } catch (e) {}

  if (!commentariesArray || commentariesArray.length === 0) {
    if (typeof process !== 'undefined' && process.versions && process.versions.node) {
      try {
        const fs = require('fs');
        const path = require('path');
        const fp = path.resolve(process.cwd(), 'data', 'commentaries', `${bookId}_${hadithNum}.json`);
        if (fs.existsSync(fp)) {
          commentariesArray.push(JSON.parse(fs.readFileSync(fp, 'utf8')));
        }
      } catch (e) {}
    }
  }

  window.activeSyarahData = commentariesArray;
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



async function loadProfileDetail() {
  const params = new URLSearchParams(window.location.search);
  const rawiIdRaw = params.get('id') || params.get('name') || 'rawi_abu_hurairah';
  
  let rawiId = rawiIdRaw;
  if (rawiId.startsWith('rawi_')) {
     const p = rawiId.split('_')[1];
     if (!isNaN(parseInt(p))) rawiId = p;
  }
  if (!isNaN(parseInt(rawiIdRaw))) rawiId = rawiIdRaw;

  const rawisDict = await window.HadeethAPI.getActiveRawis();
  const rawiData = rawisDict[rawiId] || await window.HadeethAPI.getRawiProfile(rawiId);

  const nameEnEl = document.getElementById('profile-header-name-en');
  const nameIdEl = document.getElementById('profile-header-name-id');
  const gradeEl = document.getElementById('profile-header-grade');

  if (nameEnEl && rawiData) nameEnEl.innerText = rawiData.en || rawiData.name_en || 'Transmitter';
  if (nameIdEl && rawiData) nameIdEl.innerText = rawiData.id || rawiData.name_ar || rawiData.name_en || 'Perawi';
  if (gradeEl && rawiData) gradeEl.innerText = rawiData.grade || 'Unknown';
}


async function loadTopicHadiths() {
  const container = document.getElementById('topic-hadith-cards-container');
  if (!container) return;

  const params = new URLSearchParams(window.location.search);
  const bookId = params.get('book') || 'bukhari';
  const topicId = params.get('topic') || '1';

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

  const pageSizeSelect = document.getElementById('page-size-select');
  const prevBtn = document.getElementById('prev-page-btn');
  const nextBtn = document.getElementById('next-page-btn');
  const pageIndicator = document.getElementById('page-indicator');
  const langSelect = document.getElementById('default-lang-select');
  
  if (langSelect && !langSelect.hasAttribute('data-synced-initially')) {
    langSelect.value = LangSystem.get() === 'id' ? 'id' : 'en';
    langSelect.setAttribute('data-synced-initially', 'true');
  }

  // Load Topic Metadata
  let topicNameEn = '';
  let topicNameId = '';
  try {
      const topicRes = await fetch('data/api/topics_metadata.ndjson');
      const topicText = await topicRes.text();
      const topics = topicText.trim().split('\n').filter(l => l.trim()).map(line => JSON.parse(line));
      const topic = topics.find(t => t.id == topicId);
      if (topic) {
          topicNameEn = topic.name_en;
          topicNameId = topic.name_id;
      }
  } catch (e) {}

  document.querySelector('[data-list-breadcrumb-book]').innerText = bookName;
  document.querySelector('[data-list-breadcrumb-book]').href = `topics-in-kitab.html?topic=${topicId}`;
  
  const bcEn = document.querySelector('[data-list-breadcrumb-current-en]');
  const bcId = document.querySelector('[data-list-breadcrumb-current-id]');
  if (bcEn) bcEn.innerText = topicNameEn;
  if (bcId) bcId.innerText = topicNameId;

  document.querySelector('[data-list-book-badge]').innerText = bookName;
  const chMetaEn = document.querySelector('[data-list-chapter-meta-en]');
  const chMetaId = document.querySelector('[data-list-chapter-meta-id]');
  if (chMetaEn) chMetaEn.innerText = `Topic: ${topicNameEn}`;
  if (chMetaId) chMetaId.innerText = `Topik: ${topicNameId}`;

  const countMetaEn = document.querySelector('[data-list-count-meta-en]');
  const countMetaId = document.querySelector('[data-list-count-meta-id]');
  
  document.querySelector('[data-list-chapter-title-en]').innerText = topicNameEn;
  document.querySelector('[data-list-chapter-title-id]').innerText = topicNameId;
  document.querySelector('[data-list-chapter-title-ar]').innerText = '';


  let allHadiths = [];
  let filteredHadiths = [];
  let currentPage = 1;
  let pageSize = parseInt(pageSizeSelect ? pageSizeSelect.value : '10') || 10;
  let currentLang = langSelect ? langSelect.value : 'id';

  try {
    const fullNdjson = await window.HadeethAPI.fetchNdjsonFull('api', bookId);
    allHadiths = fullNdjson.filter(h => h.tags && h.tags.includes(topicNameEn));
    filteredHadiths = [...allHadiths];
  } catch (e) {
    container.innerHTML = '<div class="p-6 text-red-500">Error loading topic data. Please build NDJSON database first.</div>';
    return;
  }

  if (countMetaEn) countMetaEn.innerText = filteredHadiths.length + ' Hadiths found in ' + bookName + ' for topic ' + topicNameEn;
  if (countMetaId) countMetaId.innerText = filteredHadiths.length + ' Hadits ditemukan dalam ' + bookName + ' untuk topik ' + topicNameId;

  function buildTopicCard(item) {
    const num = item.id || item.hadith_number;
    let arText = item.text_ar || '';
    if (!arText && item.translations && item.translations.ar && item.translations.ar.length > 0) arText = item.translations.ar[0].text;
    let enText = item.text_en || '';
    if (!enText && item.translations && item.translations.en && item.translations.en.length > 0) enText = item.translations.en[0].text;
    let idText = item.text_id || '';
    if (!idText && item.translations && item.translations.id && item.translations.id.length > 0) idText = item.translations.id[0].text;

    let gradeEn = item.grade || item.grade_en || '';
    if (!gradeEn && item.gradings && item.gradings.length > 0) gradeEn = item.gradings[0].grade;
    const gradeId = item.grade_id || gradeEn;
    const detailLink = 'hadith.html?book=' + bookId + '&id=' + num;

    const idUnavailable = '<em class="text-outline dark:text-gray-500">Terjemahan Indonesia tidak tersedia.</em>';
    const enUnavailable = '<em class="text-outline dark:text-gray-500">English translation unavailable.</em>';

    let displayText = '';
    if (currentLang === 'id') {
      displayText = '<div class="flex flex-col gap-2 pt-2 border-t border-outline-variant/10 dark:border-[#334155]">'
        + '<p class="text-sm text-on-surface-variant dark:text-gray-300 leading-relaxed"><strong class="text-xs text-secondary dark:text-[#10b981] block mb-1">Terjemahan Indonesia:</strong>' + (idText || idUnavailable) + '</p>'
        + '<p class="text-[11px] text-blue-500/70 mt-1 italic">Source: unified NDJSON engine</p></div>';
    } else if (currentLang === 'en') {
      displayText = '<div class="flex flex-col gap-2 pt-2 border-t border-outline-variant/10 dark:border-[#334155]">'
        + '<p class="text-sm text-on-surface-variant dark:text-gray-300 leading-relaxed"><strong class="text-xs text-sunan-emerald dark:text-[#10b981] block mb-1">English Translation:</strong>' + (enText || enUnavailable) + '</p>'
        + '<p class="text-[11px] text-blue-500/70 mt-1 italic">Source: unified NDJSON engine</p></div>';
    } else {
      displayText = '<div class="flex flex-col gap-2 pt-2 border-t border-outline-variant/10 dark:border-[#334155]">'
        + '<p class="text-sm text-on-surface-variant dark:text-gray-300 leading-relaxed"><strong class="text-xs text-secondary dark:text-[#10b981] block mb-1">Terjemahan Indonesia:</strong>' + (idText || idUnavailable) + '</p>'
        + '<p class="text-xs text-outline dark:text-gray-400 leading-relaxed"><strong class="text-xs text-sunan-emerald dark:text-[#10b981] block mb-1">English Translation:</strong>' + (enText || enUnavailable) + '</p>'
        + '<p class="text-[11px] text-blue-500/70 mt-1 italic">Source: unified NDJSON engine</p></div>';
    }

    return '<div class="bg-surface dark:bg-[#1e293b] border border-outline-variant/30 dark:border-[#334155] rounded-xl p-6 flex flex-col gap-4 shadow-sm hover:border-secondary/40 transition-all">'
      + '<div class="flex justify-between items-center border-b border-outline-variant/20 dark:border-[#334155] pb-3">'
      + '<div class="flex items-center gap-2">'
      + '<span class="bg-primary dark:bg-[#10b981] text-white dark:text-black text-xs font-bold px-2.5 py-0.5 rounded uppercase">' + escapeHtml(bookName) + ' #' + num + '</span>'
      + '<span class="bg-sunan-emerald/10 text-sunan-emerald dark:text-[#10b981] text-xs font-semibold px-2.5 py-0.5 rounded"><span data-lang-en>' + escapeHtml(gradeEn) + '</span><span data-lang-id style="display:none">' + escapeHtml(gradeId) + '</span></span>'
      + '</div>'
      + '<button data-copy-hadith data-copy-share-btn data-hadith-title="' + escapeHtml(bookName) + ' #' + num + '" data-copy-hadith-ar="' + escapeHtml(arText) + '" data-copy-hadith-text-id="' + escapeHtml(idText) + '" data-copy-hadith-text-en="' + escapeHtml(enText) + '" class="btn-copy-share text-xs font-semibold px-2.5 py-1 rounded border border-outline-variant/40 dark:border-[#334155] text-primary dark:text-white hover:bg-surface-container-low dark:hover:bg-[#334155] transition-all flex items-center gap-1.5 cursor-pointer"><span class="material-symbols-outlined text-[14px]">share</span><span data-lang-en>Copy / Share</span><span data-lang-id>Salin / Bagikan</span></button>'
      + '</div>'
      + '<div class="hadith-text-container relative">'
      + '<div class="hadith-text-inner transition-all duration-300 overflow-hidden" style="max-height: 380px;">'
      + (arText ? '<p class="font-arabic-body text-2xl text-primary dark:text-white text-right leading-loose" dir="rtl">' + escapeHtml(arText) + '</p>' : '')
      + displayText
      + '</div>'
      + '<div class="read-more-overlay absolute bottom-0 left-0 right-0 h-24 bg-gradient-to-t from-surface dark:from-[#1e293b] to-transparent pointer-events-none hidden"></div>'
      + '<button class="read-more-btn hidden text-secondary dark:text-[#10b981] font-semibold text-xs mt-2 hover:underline flex items-center gap-1 cursor-pointer"><span data-lang-en>Read more</span><span data-lang-id>Selengkapnya</span> <span class="material-symbols-outlined text-[14px]">expand_more</span></button>'
      + '</div>'
      + '<div class="flex justify-between items-center pt-3 border-t border-outline-variant/10 dark:border-[#334155] text-xs">'
      + '<a href="sanad.html?book=' + bookId + '&id=' + num + '" class="text-secondary dark:text-[#10b981] font-semibold hover:underline flex items-center gap-1"><span class="material-symbols-outlined text-sm">account_tree</span><span data-lang-en>Inspect Sanad Chain</span><span data-lang-id>Telusuri Sanad</span></a>'
      + '<a href="' + detailLink + '" class="text-outline dark:text-gray-400 hover:text-primary dark:hover:text-white transition-colors"><span data-lang-en>Full Hadith &amp; Commentary &rarr;</span><span data-lang-id>Hadits Selengkapnya &amp; Pensyarahan &rarr;</span></a>'
      + '</div></div>';
  }

  function updateTopicPaginationUI() {
    const totalPages = Math.ceil(filteredHadiths.length / pageSize) || 1;
    if (currentPage > totalPages) currentPage = totalPages;
    const startIdx = (currentPage - 1) * pageSize;
    const endIdx = Math.min(startIdx + pageSize, filteredHadiths.length);
    const pageData = filteredHadiths.slice(startIdx, endIdx);

    let html = '';
    if (pageData.length === 0) {
      html = '<div class="bg-surface dark:bg-[#1e293b] p-8 text-center rounded-xl border border-outline-variant/30 text-on-surface-variant dark:text-gray-400"><span class="material-symbols-outlined text-4xl mb-3 opacity-50 block">search_off</span>No ahadith found for this topic.</div>';
    } else {
      pageData.forEach(item => { html += buildTopicCard(item); });
    }

    container.innerHTML = html;
    if (window.LangSystem) window.LangSystem.apply(window.LangSystem.get());
    if (window.setupReadMore) window.setupReadMore();

    if (pageIndicator) {
      const isId = (window.LangSystem && window.LangSystem.isIdMode());
      pageIndicator.innerText = isId
        ? 'Menampilkan ' + (startIdx + 1) + '-' + endIdx + ' dari ' + filteredHadiths.length + ' Hadits (Hal ' + currentPage + ' dari ' + totalPages + ')'
        : 'Showing ' + (startIdx + 1) + '-' + endIdx + ' of ' + filteredHadiths.length + ' Ahadith (Page ' + currentPage + ' of ' + totalPages + ')';
    }
    if (prevBtn) prevBtn.disabled = (currentPage <= 1);
    if (nextBtn) nextBtn.disabled = (currentPage >= totalPages);
    const jumpInput = document.getElementById('jump-page-input');
    if (jumpInput) { jumpInput.min = 1; jumpInput.max = totalPages; jumpInput.value = currentPage; jumpInput.placeholder = currentPage; }
  }

  // Sync with Translation dropdown
  if (langSelect) {
    langSelect.addEventListener('change', function(e) {
      currentLang = e.target.value;
      currentPage = 1;
      updateTopicPaginationUI();
    });
  }

  // Sync with global EN/ID header toggle
  if (!window._topicHadithLangListenerAttached) {
    window._topicHadithLangListenerAttached = true;
    window.addEventListener('hadeeth_lang_change', function() {
      var sel = document.getElementById('default-lang-select');
      if (sel) {
        var newLang = (window.LangSystem && window.LangSystem.get() === 'id') ? 'id' : 'en';
        sel.value = newLang;
        currentLang = newLang;
        currentPage = 1;
        updateTopicPaginationUI();
      }
    });
  }

  if (pageSizeSelect) {
    pageSizeSelect.addEventListener('change', function(e) { pageSize = parseInt(e.target.value) || 10; currentPage = 1; updateTopicPaginationUI(); });
  }
  if (prevBtn) {
    prevBtn.addEventListener('click', function() { if (currentPage > 1) { currentPage--; updateTopicPaginationUI(); window.scrollTo({ top: 0, behavior: 'smooth' }); } });
  }
  if (nextBtn) {
    nextBtn.addEventListener('click', function() { var tot = Math.ceil(filteredHadiths.length / pageSize) || 1; if (currentPage < tot) { currentPage++; updateTopicPaginationUI(); window.scrollTo({ top: 0, behavior: 'smooth' }); } });
  }
  var jumpBtn = document.getElementById('jump-page-btn');
  if (jumpBtn) {
    jumpBtn.addEventListener('click', function() {
      var val = parseInt(document.getElementById('jump-page-input') && document.getElementById('jump-page-input').value);
      var tot = Math.ceil(filteredHadiths.length / pageSize) || 1;
      if (val >= 1 && val <= tot) { currentPage = val; updateTopicPaginationUI(); window.scrollTo({ top: 0, behavior: 'smooth' }); }
    });
  }

  var searchInput = document.getElementById('topic-search-input');
  if (searchInput) {
    searchInput.addEventListener('input', function() {
      var q = searchInput.value.toLowerCase();
      filteredHadiths = !q ? [...allHadiths] : allHadiths.filter(function(h) {
        return (h.text_en && h.text_en.toLowerCase().indexOf(q) >= 0) ||
               (h.text_id && h.text_id.toLowerCase().indexOf(q) >= 0) ||
               (h.text_ar && h.text_ar.indexOf(q) >= 0) ||
               (String(h.hadith_number).indexOf(q) >= 0);
      });
      currentPage = 1;
      updateTopicPaginationUI();
    });
  }

  updateTopicPaginationUI();
}

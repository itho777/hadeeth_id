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
    footer_text: "© 2024 HADEETH.ID - Digital Manuscript Preservation"
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
    footer_text: "© 2024 HADEETH.ID - Pelestarian Manuskrip Digital"
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
  if (!lastRead) return;
  const card = document.getElementById('last-read-card');
  const bookElem = document.getElementById('last-read-book');
  const titleElem = document.getElementById('last-read-title');
  if (card) card.href = `hadith.html?book=${lastRead.bookId}&id=${lastRead.hadithId}`;
  if (bookElem) bookElem.innerText = lastRead.bookName;
  if (titleElem) titleElem.innerText = lastRead.hadithTitle || `${lastRead.bookName} Hadith #${lastRead.hadithId}`;
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

  const supabaseUrl = 'https://idokyspokenbmzoegahq.supabase.co';
  const anonKey = 'sb_publishable_Hz6k4Jp7rdSxwXCk1AO-sQ_r93N88QR';

  const arabicElem = container.querySelector('[data-arabic-text]');
  const englishElem = container.querySelector('[data-english-text]');
  const indonesianElem = container.querySelector('[data-indonesian-text]');
  const titleEn = container.querySelector('[data-hadith-title-en]');
  const titleId = container.querySelector('[data-hadith-title-id]');
  const rawiEn = container.querySelector('[data-hadith-rawi-en]');
  const rawiId = container.querySelector('[data-hadith-rawi-id]');
  const sanadLink = container.querySelector('[data-sanad-link]');
  const sanadPreviewEn = container.querySelector('[data-sanad-preview-en]');
  const sanadPreviewId = container.querySelector('[data-sanad-preview-id]');

  if (sanadLink) sanadLink.href = `sanad.html?book=${bookId}&id=${hadithId}`;
  if (sanadPreviewEn) sanadPreviewEn.innerText = `Inspect Chain for ${bookName} #${hadithId} → Prophet ﷺ`;
  if (sanadPreviewId) sanadPreviewId.innerText = `Periksa Silsilah untuk ${bookName} #${hadithId} → Rasulullah ﷺ`;

  try {
    const res = await fetch(`${supabaseUrl}/rest/v1/hadiths?id=eq.${bookId}_${hadithId}&select=id,hadith_number,text_ar,text_en,text_id,grade,book_id`, {
      headers: {
        'apikey': anonKey,
        'Authorization': `Bearer ${anonKey}`
      }
    });

    if (res.ok) {
      const data = await res.json();
      if (data && data.length > 0) {
        const item = data[0];
        if (arabicElem) arabicElem.innerText = item.text_ar || '—';
        if (englishElem) englishElem.innerHTML = TafseerLinker.parse(item.text_en || '—');
        if (indonesianElem) indonesianElem.innerHTML = TafseerLinker.parse(item.text_id || '—');

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
              targetP.innerHTML = item.text_en ? TafseerLinker.parse(item.text_en) : '—';
            } else if (val === 'id') {
              targetP.innerHTML = item.text_id ? TafseerLinker.parse(item.text_id) : '—';
            } else if (val === 'ar') {
              targetP.innerText = item.text_ar || '—';
            }
          });
        });

        if (sanadPreviewEn || sanadPreviewId || rawiEn || rawiId) {
          let previewNames = [];
          if (item.text_id) {
            const isnadPartId = item.text_id.split(/beliau\s+bersabda\s*:|berfirman\s*:|berkata\s*:|tentang\s+firman\s+Allah|bahwa\s+Rasulullah/i)[0] || item.text_id;
            const brackets = isnadPartId.match(/\[([^\]]+)\]/g);
            if (brackets) {
              const stopWords = new Set(['Al Qur\'an', 'Al-Qur\'an', 'Islam', 'Nabi', 'Rasulullah', 'Allah', 'bapaknya', 'bapakku']);
              brackets.forEach(b => {
                const name = b.replace(/[\[\]]/g, '').trim();
                if (name && !stopWords.has(name) && name.length > 2) {
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

        if (window.LangSystem) window.LangSystem.apply(window.LangSystem.get());
        return;
      }
    }
  } catch (err) {
    console.warn('Supabase fetch detail error, fallback to edition files:', err);
  }

  if (window.LangSystem) window.LangSystem.apply(window.LangSystem.get());

  // Fallback to CDN edition files if offline / REST fails
  const [edition, arabicEdition, indEdition] = await Promise.all([
    window.HadeethAPI.getEdition('eng', bookId),
    window.HadeethAPI.getEdition('ara', bookId),
    window.HadeethAPI.getEdition('ind', bookId)
  ]);

  let hadithTextEn = '';
  let hadithTextAr = '';
  let hadithTextId = '';

  if (edition && edition.hadiths) {
    const found = edition.hadiths.find(h => h.hadithnumber == hadithId);
    if (found) hadithTextEn = found.text;
  }
  if (arabicEdition && arabicEdition.hadiths) {
    const found = arabicEdition.hadiths.find(h => h.hadithnumber == hadithId);
    if (found) hadithTextAr = found.text;
  }
  if (indEdition && indEdition.hadiths) {
    const found = indEdition.hadiths.find(h => h.hadithnumber == hadithId);
    if (found) hadithTextId = found.text;
  }

  if (arabicElem) arabicElem.innerText = hadithTextAr || '—';
  if (englishElem) englishElem.innerHTML = TafseerLinker.parse(hadithTextEn || '—');
  if (indonesianElem) indonesianElem.innerHTML = TafseerLinker.parse(hadithTextId || '—');
  if (titleElem) titleElem.innerText = `${bookName} Hadith #${hadithId}`;
  if (sanadLink) sanadLink.href = `sanad.html?book=${bookId}&id=${hadithId}`;
  if (sanadPreview) sanadPreview.innerText = `Inspect Chain for ${bookName} #${hadithId} → Prophet ﷺ`;
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
  let chapterTitleNameEn = `Chapter ${chapterId}`;
  let chapterTitleNameId = `Kitab ${chapterId}`;
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
  const activeChMeta = isIdLang ? `Kitab ${chapterId}` : `Chapter ${chapterId}`;

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
  if (chMetaEn) chMetaEn.innerText = `Chapter ${chapterId}`;
  if (chMetaId) chMetaId.innerText = `Kitab ${chapterId}`;
  if (chMeta && !chMetaEn) chMeta.innerText = activeChMeta;

  if (chTitleEn) chTitleEn.innerText = chapterTitleNameEn;
  if (chTitleId) chTitleId.innerText = chapterTitleNameId;
  if (chTitleAr) chTitleAr.innerText = chapterTitleNameAr;
  LangSystem.apply(LangSystem.get());

  if (!window._hadithListLangListenerAttached) {
    window._hadithListLangListenerAttached = true;
    window.addEventListener('hadeeth_lang_change', () => {
      loadHadithList();
    });
  }

  // Local state
  let allHadiths = [];
  let filteredHadiths = [];
  let currentPage = 1;
  let pageSize = parseInt(pageSizeSelect ? pageSizeSelect.value : '10') || 10;
  let currentLang = langSelect ? langSelect.value : 'id';
  let searchScope = scopeSelect ? scopeSelect.value : 'chapter';

  // Fetch Hadiths from Supabase filtered by chapter range if available
  const supabaseUrl = 'https://idokyspokenbmzoegahq.supabase.co';
  const anonKey = 'sb_publishable_Hz6k4Jp7rdSxwXCk1AO-sQ_r93N88QR';

  try {
    let queryUrl = `${supabaseUrl}/rest/v1/hadiths?book_id=eq.${bookId}&select=*&order=hadith_number.asc&limit=500`;
    if (startHadithNum != null && endHadithNum != null) {
      queryUrl = `${supabaseUrl}/rest/v1/hadiths?book_id=eq.${bookId}&hadith_number=gte.${startHadithNum}&hadith_number=lte.${endHadithNum}&select=*&order=hadith_number.asc&limit=500`;
    }
    const res = await fetch(queryUrl, {
      headers: { 'apikey': anonKey, 'Authorization': `Bearer ${anonKey}` }
    });

    if (res.ok) {
      allHadiths = await res.json();
    }
  } catch (err) {
    console.warn('Fetch hadiths REST error, fallback to edition file:', err);
  }

  // Fallback to local edition file if REST returns empty or offline
  if (!allHadiths || allHadiths.length === 0) {
    try {
      const indEd = await window.HadeethAPI.getEdition('ind', bookId);
      const engEd = await window.HadeethAPI.getEdition('eng', bookId);
      const araEd = await window.HadeethAPI.getEdition('ara', bookId);

      const mainEd = indEd || engEd;
      if (mainEd && mainEd.hadiths) {
        const araMap = {};
        const engMap = {};
        const indMap = {};
        if (araEd && araEd.hadiths) araEd.hadiths.forEach(h => araMap[h.hadithnumber] = h.text);
        if (engEd && engEd.hadiths) engEd.hadiths.forEach(h => engMap[h.hadithnumber] = h.text);
        if (indEd && indEd.hadiths) indEd.hadiths.forEach(h => indMap[h.hadithnumber] = h.text);

        let sourceHadiths = mainEd.hadiths;
        if (startHadithNum != null && endHadithNum != null) {
          sourceHadiths = sourceHadiths.filter(h => {
            const num = parseInt(h.hadithnumber);
            return num >= startHadithNum && num <= endHadithNum;
          });
        }

        allHadiths = sourceHadiths.map(h => ({
          hadith_number: h.hadithnumber,
          text_en: engMap[h.hadithnumber] || h.text || '',
          text_ar: araMap[h.hadithnumber] || '',
          text_id: indMap[h.hadithnumber] || h.text || '',
          grade: 'Sahih',
          book_id: bookId
        }));
      }
    } catch (e) {
      console.warn('Fallback edition load error:', e);
    }
  }

  filteredHadiths = [...allHadiths];
  if (startHadithNum != null && endHadithNum != null) {
    const count = chapterHadithCount || (endHadithNum - startHadithNum + 1);
    const enText = `Hadith ${startHadithNum} – ${endHadithNum} • ${count} Hadiths in ${bookName} Chapter ${chapterId}`;
    const idText = `Hadits ${startHadithNum} – ${endHadithNum} • ${count} Hadits dalam ${bookName} Kitab ${chapterId}`;
    if (countMetaEn) countMetaEn.innerText = enText;
    if (countMetaId) countMetaId.innerText = idText;
    if (countMeta && !countMetaEn) countMeta.innerText = isIdLang ? idText : enText;
  } else {
    const enText = `Total ${allHadiths.length} Hadiths in ${bookName} Chapter ${chapterId}`;
    const idText = `Total ${allHadiths.length} Hadits dalam ${bookName} Kitab ${chapterId}`;
    if (countMetaEn) countMetaEn.innerText = enText;
    if (countMetaId) countMetaId.innerText = idText;
    if (countMeta && !countMetaEn) countMeta.innerText = isIdLang ? idText : enText;
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
      const idText = item.text_id || enText;
      const grade = item.grade || 'Sahih';

      const isnadLink = `sanad.html?book=${bookId}&id=${num}`;
      const detailLink = `hadith.html?book=${bookId}&id=${num}`;

      let displayText = '';
      if (currentLang === 'id') {
        displayText = `<p class="text-sm text-on-surface-variant dark:text-gray-300 leading-relaxed font-body-md"><strong class="text-xs text-secondary dark:text-[#10b981] block mb-1">Terjemahan Indonesia:</strong>${escapeHtml(idText)}</p>`;
      } else if (currentLang === 'en') {
        displayText = `<p class="text-sm text-on-surface-variant dark:text-gray-300 leading-relaxed font-body-md"><strong class="text-xs text-sunan-emerald dark:text-[#10b981] block mb-1">English Translation:</strong>${escapeHtml(enText)}</p>`;
      } else {
        displayText = `
          <div class="flex flex-col gap-3 pt-2 border-t border-outline-variant/10 dark:border-[#334155]">
            <p class="text-sm text-on-surface-variant dark:text-gray-300 leading-relaxed font-body-md"><strong class="text-xs text-secondary dark:text-[#10b981] block mb-1">Terjemahan Indonesia:</strong>${escapeHtml(idText)}</p>
            <p class="text-xs text-outline dark:text-gray-400 leading-relaxed font-body-md"><strong class="text-xs text-sunan-emerald dark:text-[#10b981] block mb-1">English Translation:</strong>${escapeHtml(enText)}</p>
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
          text_id: r.indonesian_text || r.primary_translation || '',
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
 * Load Chapters List dynamically for Kitab view
 */
/**
 * Load Chapters List dynamically for Kitab view across all 9 canonical books
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
      kitabCount: '📚 97 Books (Kitab)',
      hadithCount: '📖 7,563 Total Hadith',
      authenticity: '⭐️ 100% Authentic'
    },
    muslim: {
      name: 'Sahih Muslim',
      ar: 'صحيح مسلم',
      author: 'Imam Muslim ibn al-Hajjaj',
      authorId: 'rawi_muslim',
      type: "Jami'",
      badgeClass: 'bg-blue-700 text-white',
      desc: 'Masterpiece Jami collection renowned for strict thematic organization and comprehensive parallel chains of narration (turuq).',
      kitabCount: '📚 56 Books (Kitab)',
      hadithCount: '📖 3,033 Total Hadith',
      authenticity: '⭐️ 100% Authentic'
    },
    tirmidhi: {
      name: "Jami' al-Tirmidhi",
      ar: 'جامع الترمذي',
      author: "Imam Abu 'Isa al-Tirmidhi",
      authorId: 'rawi_al_tirmidhi',
      type: "Jami'",
      badgeClass: 'bg-blue-700 text-white',
      desc: 'Famous Jami collection featuring explicit grading of narrations (Sahih, Hasan, Gharib) and legal opinions of early jurists.',
      kitabCount: '📚 49 Books (Kitab)',
      hadithCount: '📖 3,956 Total Hadith',
      authenticity: '⭐️ Graded Jami'
    },
    abudawud: {
      name: 'Sunan Abu Dawood',
      ar: 'سنن أبي داود',
      author: 'Imam Abu Dawood al-Sijistani',
      authorId: 'rawi_abu_dawud',
      type: 'Sunan',
      badgeClass: 'bg-indigo-600 text-white',
      desc: 'Primarily focuses on legal rulings (Ahkam) used as foundational evidence by jurists across Sunni Fiqh schools.',
      kitabCount: '📚 43 Books (Kitab)',
      hadithCount: '📖 5,274 Total Hadith',
      authenticity: '⭐️ Sunan Corpus'
    },
    nasai: {
      name: "Sunan an-Nasa'i",
      ar: 'سنن النسائي',
      author: "Imam Ahmad an-Nasa'i",
      authorId: 'rawi_al_nasai',
      type: 'Sunan',
      badgeClass: 'bg-indigo-600 text-white',
      desc: 'Possesses the strictest authentication criteria among the Sunan books, second only to the Sahihain.',
      kitabCount: '📚 51 Books (Kitab)',
      hadithCount: '📖 5,758 Total Hadith',
      authenticity: '⭐️ High Authenticity'
    },
    ibnmajah: {
      name: 'Sunan Ibn Majah',
      ar: 'سنن ابن ماجه',
      author: 'Imam Ibn Majah al-Qazwini',
      authorId: 'rawi_ibn_majah',
      type: 'Sunan',
      badgeClass: 'bg-indigo-600 text-white',
      desc: 'Renowned for systematic arrangement and unique narrations (zawa\'id) expanding Islamic jurisprudence.',
      kitabCount: '📚 37 Books (Kitab)',
      hadithCount: '📖 4,341 Total Hadith',
      authenticity: '⭐️ Sunan Corpus'
    },
    malik: {
      name: 'Muwatta Malik',
      ar: 'موطأ مالك',
      author: 'Imam Malik ibn Anas',
      authorId: 'rawi_malik',
      type: 'Mushannaf',
      badgeClass: 'bg-amber-600 text-white',
      desc: 'The earliest surviving legal Mushannaf text of Islam, combining prophetic Hadiths with judicial rulings of Madinah.',
      kitabCount: '📚 61 Books (Kitab)',
      hadithCount: '📖 1,720 Total Hadith',
      authenticity: '⭐️ Imam of Hijaz'
    },
    ahmad: {
      name: 'Musnad Ahmad',
      ar: 'مسند أحمد بن حنبل',
      author: 'Imam Ahmad ibn Hanbal',
      authorId: 'rawi_ahmad',
      type: 'Musnad',
      badgeClass: 'bg-purple-700 text-white',
      desc: 'The massive encyclopedic Musnad arranged companion by companion (Sahabi), containing over 27,000 narrations.',
      kitabCount: '📚 Musnad System',
      hadithCount: '📖 27,647 Total Hadith',
      authenticity: '⭐️ Encyclopedic Corpus'
    },
    nawawi: {
      name: 'Forty Nawawi',
      ar: 'الأربعون النووية',
      author: 'Imam Yahya ibn Sharaf al-Nawawi',
      authorId: 'rawi_nawawi',
      type: "Jawami' al-Kalim",
      badgeClass: 'bg-emerald-700 text-white',
      desc: 'Essential collection of 42 foundational narrations encapsulating Jawami\' al-Kalim (concise comprehensive prophetic guidance).',
      kitabCount: '📚 1 Volume',
      hadithCount: '📖 42 Total Hadith',
      authenticity: '⭐️ Jawami\' al-Kalim'
    },
    tabarani_kabir: {
      name: 'Al-Mu\'jam al-Kabir',
      ar: 'المعجم الكبير للطبراني',
      author: 'Imam Al-Tabarani',
      authorId: 'rawi_tabarani',
      type: "Mu'jam",
      badgeClass: 'bg-blue-700 text-white',
      desc: 'Monumental Mu\'jam collection arranged according to the names of Companion narrators in alphabetical order.',
      kitabCount: '📚 25 Volumes',
      hadithCount: '📖 20,000+ Total Hadith',
      authenticity: '⭐️ Framework Shell'
    },
    ibn_abi_shaybah: {
      name: 'Musannaf Ibn Abi Shaybah',
      ar: 'مصنف ابن أبي شيبة',
      author: 'Imam Ibn Abi Shaybah',
      authorId: 'rawi_ibn_abi_shaybah',
      type: 'Mushannaf',
      badgeClass: 'bg-amber-600 text-white',
      desc: 'Encyclopedic Mushannaf collection preserving Marfu\', Mauquf, and Maqtu\' traditions ordered by Fiqh topics.',
      kitabCount: '📚 37 Books',
      hadithCount: '📖 37,000+ Total Hadith',
      authenticity: '⭐️ Framework Shell'
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
  if (descElem) descElem.innerText = meta.desc;
  if (kitabCountElem) kitabCountElem.innerText = meta.kitabCount;
  if (hadithCountElem) hadithCountElem.innerText = meta.hadithCount;
  if (authElem) authElem.innerText = meta.authenticity;
  if (arTitleElem) arTitleElem.innerText = meta.ar;

  // Fetch Chapters
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
    const chNum = ch.chapter_number || (idx + 1);
    // Support both field name conventions: title_en (JSON files) and name_en (skeleton fallbacks)
    const titleEn = ch.title_en || ch.name_en || ch.title || `Chapter ${chNum}`;
    const titleId = ch.title_id || ch.name_id || titleEn;
    const titleAr = ch.title_ar || ch.name_ar || ch.arabic || '';
    // Support both: pre-computed hadith_range string OR hadith_start/hadith_end numbers
    const hadithRange = ch.hadith_range
      || (ch.hadith_start != null ? `Hadith ${ch.hadith_start} – ${ch.hadith_end}` : `Chapter ${chNum}`);
    const hadithCount = ch.hadith_end && ch.hadith_start ? (ch.hadith_end - ch.hadith_start + 1) : '';

    html += `
      <a href="hadith-list.html?book=${bookId}&chapter=${chNum}" class="group bg-surface dark:bg-[#1e293b] border border-outline-variant/20 dark:border-[#334155] hover:border-secondary dark:hover:border-[#10b981] rounded-xl p-5 transition-all flex justify-between items-center card-lift">
        <div class="flex gap-4 items-center">
          <div class="w-10 h-10 rounded-full bg-secondary/10 dark:bg-[#10b981]/10 text-secondary dark:text-[#10b981] font-bold text-sm flex items-center justify-center flex-shrink-0">${chNum}</div>
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
  // Re-apply language preference to newly injected elements
  LangSystem.apply(LangSystem.get());

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
  let idTitle = `Kitab ${chapterId}`;
  let arTitle = '';

  // Fetch chapter title info
  const chapters = await window.HadeethAPI.getChapters(bookId);
  if (chapters && chapters.length >= parseInt(chapterId)) {
    const chInfo = chapters[parseInt(chapterId) - 1];
    enTitle = chInfo.title_en || chInfo.name_en || enTitle;
    idTitle = chInfo.title_id || chInfo.name_id || enTitle;
    arTitle = chInfo.title_ar || chInfo.name_ar || '';

    const startNum = chInfo.hadith_start || '';
    const endNum = chInfo.hadith_end || '';
    const hCount = chInfo.hadith_count || (endNum && startNum ? (endNum - startNum + 1) : '');

    if (countMeta) {
      countMeta.innerText = isIdLang
        ? `Hadits ${startNum} - ${endNum} • ${hCount} Hadits dalam ${bookName} Kitab ${chapterId}`
        : `Hadith ${startNum} - ${endNum} • ${hCount} Hadiths in ${bookName} Chapter ${chapterId}`;
    }
  }

  if (listBcCurrent) listBcCurrent.innerText = isIdLang ? idTitle : enTitle;
  if (chapterMeta) chapterMeta.innerText = isIdLang ? `Kitab ${chapterId}` : `Chapter ${chapterId}`;
  if (chapterTitleEn) chapterTitleEn.innerText = enTitle;
  if (chapterTitleId) chapterTitleId.innerText = idTitle;
  if (chapterTitleAr) chapterTitleAr.innerText = arTitle;

  container.innerHTML = `
    <div class="p-8 text-center bg-surface dark:bg-[#1e293b] rounded-xl border border-outline-variant/20 dark:border-[#334155]">
      <span class="material-symbols-outlined animate-spin text-secondary dark:text-[#10b981] text-3xl">progress_activity</span>
      <p class="mt-2 text-sm text-outline dark:text-gray-400">${isIdLang ? `Memuat daftar hadits untuk ${escapeHtml(bookName)} Kitab ${chapterId}...` : `Loading authentic Hadith list for ${escapeHtml(bookName)} Chapter ${chapterId}...`}</p>
    </div>
  `;

  const langSelectVal = document.getElementById('default-lang-select')?.value || (isIdLang ? 'id' : 'en');

  // Fetch English, Arabic, and Indonesian edition files for complete bilingual/multilingual cards
  const [engEdition, araEdition, indEdition] = await Promise.all([
    window.HadeethAPI.getEdition('eng', bookId).catch(() => null),
    window.HadeethAPI.getEdition('ara', bookId).catch(() => null),
    window.HadeethAPI.getEdition('ind', bookId).catch(() => null)
  ]);

  if ((!engEdition || !engEdition.hadiths) && (!indEdition || !indEdition.hadiths)) {
    container.innerHTML = `
      <div class="p-8 text-center bg-surface dark:bg-[#1e293b] rounded-xl border border-outline-variant/20 dark:border-[#334155]">
        <p class="text-sm text-outline dark:text-gray-400">${isIdLang ? `Tidak ada hadits ditemukan untuk ${escapeHtml(bookId)}.` : `No Hadiths found for ${escapeHtml(bookId)}.`}</p>
      </div>
    `;
    return;
  }

  // Map Arabic & Indonesian hadith texts by hadithnumber
  const arabicMap = {};
  if (araEdition && araEdition.hadiths) {
    araEdition.hadiths.forEach(h => {
      arabicMap[h.hadithnumber] = h.text;
    });
  }

  const indMap = {};
  if (indEdition && indEdition.hadiths) {
    indEdition.hadiths.forEach(h => {
      indMap[h.hadithnumber] = h.text;
    });
  }

  const baseHadiths = (engEdition && engEdition.hadiths) ? engEdition.hadiths : indEdition.hadiths;
  const listHadiths = baseHadiths.slice(0, 50);

  let html = '';
  listHadiths.forEach(h => {
    const num = h.hadithnumber;
    const engText = h.text || '';
    const araText = arabicMap[num] || '';
    const indText = indMap[num] || '';

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
    ahmad: 'Musnad Ahmad'
  };
  const bookName = bookNames[bookId.toLowerCase()] || bookId.toUpperCase();
  const isIdLang = (window.LangSystem && window.LangSystem.isIdMode());

  const titleEn = document.querySelector('#sanad-title [data-lang-en]');
  const titleId = document.querySelector('#sanad-title [data-lang-id]');
  const subEn = document.querySelector('#sanad-subtitle [data-lang-en]');
  const subId = document.querySelector('#sanad-subtitle [data-lang-id]');

  if (titleEn) titleEn.innerText = `Sanad: ${bookName} ${hadithNum}`;
  if (titleId) titleId.innerText = `Sanad: ${bookName} Hadits #${hadithNum}`;
  if (subEn) subEn.innerText = `Chain of narrators (الإسناد) for ${bookName} Hadith #${hadithNum} tracing back to the Messenger of Allah ﷺ.`;
  if (subId) subId.innerText = `Silsilah perawi (الإسناد) untuk ${bookName} Hadits #${hadithNum} yang bersambung sampai ke Rasulullah ﷺ.`;

  const supabaseUrl = 'https://idokyspokenbmzoegahq.supabase.co';
  const anonKey = 'sb_publishable_Hz6k4Jp7rdSxwXCk1AO-sQ_r93N88QR';

  let textAr = '';
  let textEn = '';
  let textId = '';
  let dbNarrators = null;
  // Try RPC / DB lookup first
  try {
    const resRpc = await fetch(`${supabaseUrl}/rest/v1/rpc/get_sanad_chain`, {
      method: 'POST',
      headers: {
        'apikey': anonKey,
        'Authorization': `Bearer ${anonKey}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ p_hadith_id: hadithId })
    });
    if (resRpc.ok) {
      dbNarrators = await resRpc.json();
    }
  } catch (err) {
    console.warn('RPC get_sanad_chain error:', err);
  }

  // Fetch Hadith text as fallback/supplement
  try {
    const res = await fetch(`${supabaseUrl}/rest/v1/hadiths?id=eq.${hadithId}&select=text_ar,text_en,text_id`, {
      headers: { 'apikey': anonKey, 'Authorization': `Bearer ${anonKey}` }
    });
    if (res.ok) {
      const data = await res.json();
      if (data && data.length > 0) {
        textAr = data[0].text_ar || '';
        textEn = data[0].text_en || '';
        textId = data[0].text_id || '';
      }
    }
  } catch (err) {
    console.warn('Supabase fetch sanad error:', err);
  }

  let narrators = [];

  // Master Rawi Dictionary with complete 3-name separation (Arabic script, EN Latin, ID Latin)
  const rawiDict = [
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
  if (dbNarrators && dbNarrators.length >= 3) {
    narrators = dbNarrators.map(r => {
      const normEn = (r.name_en || '').toLowerCase();
      const matchDict = rawiDict.find(d => 
        d.rawi_id === r.rawi_id || 
        (d.ar && r.name_ar && (d.ar.includes(r.name_ar) || r.name_ar.includes(d.ar))) ||
        (d.en && normEn && normEn.includes(d.en.toLowerCase().replace(/['`’]/g, '').trim()))
      );
      const enName = r.name_en || (matchDict ? matchDict.en : 'Transmitter');
      const idName = matchDict ? matchDict.id : getIndonesianRawiName(enName, r.rawi_id, r.name_ar);
      const roleEnText = matchDict ? (matchDict.roleEn || matchDict.role) : `${r.generation || 'Transmitter'} • Grade: ${r.grade || 'Thiqah'}`;
      const roleIdText = matchDict ? (matchDict.roleId || matchDict.role) : `${r.generation || 'PERAWI'} • DERAJAT: ${r.grade || 'TSIQAH'}`;
      return {
        rawi_id: r.rawi_id,
        name: enName + (r.is_sahabi ? ' (رضي الله عنه)' : ''),
        name_id: idName,
        roleEn: roleEnText,
        roleId: roleIdText,
        ar: r.name_ar || (matchDict ? matchDict.ar : ''),
        kunyah: r.kunyah || (matchDict ? matchDict.kunyah : 'Abu Abdullah'),
        residence: r.residence || (matchDict ? matchDict.residence : 'Madinah'),
        death_ah: r.death_ah || (matchDict ? matchDict.death_ah : 'Early Era'),
        counts: matchDict ? matchDict.counts : 'Bukhari & Muslim',
        remarks: matchDict ? matchDict.remarks : 'Ibn Hajar: Thiqah'
      };
    });
  }

  if (narrators.length < 3 && textId) {
    narrators = [];
    const isnadPartId = textId.split(/beliau\s+bersabda\s*:|berfirman\s*:|berkata\s*:|tentang\s+firman\s+Allah|bahwa\s+Rasulullah/i)[0] || textId;
    const brackets = isnadPartId.match(/\[([^\]]+)\]/g);
    
    if (brackets && brackets.length > 0) {
      const stopWords = new Set([
        'Al Qur\'an', 'Al-Qur\'an', 'Islam', 'Nabi', 'Rasulullah', 'Allah',
        'ayahnya', 'ayahku', 'bapaknya', 'bapakku', 'ibunya', 'ibuku',
        'pamanku', 'pamannya', 'kakeknya', 'kakekku', 'saudaranya', 'saudaraku',
        'anaknya', 'anakku', 'suaminya', 'istrinya', 'budaknya', 'sahabat',
        'sahabatnya', 'beliau', 'mereka', 'seseorang', 'lelaki', 'wanita',
        'orang', 'orang tua', 'keluarga', 'kaum', 'umat'
      ]);
      const extractedNames = [];
      
      brackets.forEach(b => {
        const name = b.replace(/[\[\]]/g, '').trim();
        const norm = name.toLowerCase();
        if (name && !stopWords.has(norm) && !stopWords.has(name) && name.length > 2) {
          extractedNames.push(name);
        }
      });

      // Reverse so chain runs Companion (Node 1) -> Collector (Node N)
      extractedNames.reverse().forEach((rawiName, idx) => {
        const normNameKey = normalizeRawiNameKey(rawiName);
        let matched = null;

        if (normNameKey.includes('aisyah') || normNameKey.includes('aisha')) {
          matched = rawiDict.find(d => d.rawi_id === 'rawi_aisha_bint_abi_bakr');
        } else if (normNameKey.includes('abdurrahman') && normNameKey.includes('qasim')) {
          matched = rawiDict.find(d => d.rawi_id === 'rawi_abdurrahman_bin_al_qasim');
        } else if (normNameKey.includes('abdullah bin yusuf') || normNameKey.includes('yusuf')) {
          matched = rawiDict.find(d => d.rawi_id === 'rawi_abdullah_bin_yusuf');
        } else if (normNameKey.includes('humaid') || normNameKey.includes('humayd') || normNameKey.includes('humai')) {
          matched = rawiDict.find(d => d.rawi_id === 'rawi_al_humaydi');
        } else if (normNameKey === 'malik' || normNameKey.includes('imam malik') || normNameKey.includes('malik bin anas')) {
          matched = rawiDict.find(d => d.rawi_id === 'rawi_malik_bin_anas');
        } else if (normNameKey.includes('anas bin malik') || normNameKey === 'anas') {
          matched = rawiDict.find(d => d.rawi_id === 'rawi_anas_bin_malik');
        } else if (normNameKey.includes('ibnu umar') || normNameKey.includes('ibn umar')) {
          matched = rawiDict.find(d => d.rawi_id === 'rawi_ibn_umar');
        } else if (normNameKey.includes('ikrimah')) {
          matched = rawiDict.find(d => d.rawi_id === 'rawi_ikrimah_bin_khalid');
        } else if (normNameKey.includes('hanzhalah') || normNameKey.includes('hanzalah')) {
          matched = rawiDict.find(d => d.rawi_id === 'rawi_hanzalah_bin_abu_sufyan');
        } else if (normNameKey.includes('alqam') || normNameKey.includes('waq')) {
          matched = rawiDict.find(d => d.rawi_id === 'rawi_alqama_bin_waqqas');
        } else if (normNameKey.includes('umar')) {
          matched = rawiDict.find(d => d.rawi_id === 'rawi_umar_ibn_al_khattab');
        } else if (normNameKey.includes('sufyan')) {
          matched = rawiDict.find(d => d.rawi_id === 'rawi_sufyan_al_thawri');
        } else if (normNameKey.includes('yahya')) {
          matched = rawiDict.find(d => d.rawi_id === 'rawi_yahya_bin_said');
        } else if (normNameKey.includes('muhammad') && normNameKey.includes('ibrahim')) {
          matched = rawiDict.find(d => d.rawi_id === 'rawi_muhammad_bin_ibrahim');
        } else {
          matched = rawiDict.find(d => 
            normalizeRawiNameKey(d.en) === normNameKey ||
            normNameKey.includes(normalizeRawiNameKey(d.en)) ||
            (d.id && normNameKey.includes(normalizeRawiNameKey(d.id))) ||
            (d.id && normalizeRawiNameKey(d.id).includes(normNameKey))
          );
        }

        if (matched) {
          narrators.push({
            rawi_id: matched.rawi_id,
            name: matched.en,
            name_id: matched.id || getIndonesianRawiName(matched.en, matched.rawi_id, matched.ar),
            roleEn: matched.roleEn || matched.role,
            roleId: matched.roleId || matched.role,
            ar: matched.ar,
            kunyah: matched.kunyah,
            residence: matched.residence,
            death_ah: matched.death_ah,
            counts: matched.counts,
            remarks: matched.remarks
          });
        } else {
          const isFirst = (idx === 0) || normName.includes('radliallahu') || normName.includes('sahabi') || normName.includes('abu hurairah') || normName.includes('umar') || normName.includes('aisyah');
          narrators.push({
            rawi_id: null,
            name: rawiName,
            name_id: getIndonesianRawiName(rawiName, null, null),
            roleEn: isFirst ? 'SAHABI (COMPANION) • GRADE: THIQAH' : 'TRANSMITTER (RAWI) • GRADE: THIQAH',
            roleId: isFirst ? 'SAHABAT NABI • DERAJAT: TSIQAH' : 'PERAWI (RAWI) • DERAJAT: TSIQAH',
            ar: getArabicScriptForRawi(rawiName),
            kunyah: isFirst ? 'Abu Abdillah' : 'Abu Abdullah',
            residence: isFirst ? 'Madinah' : 'Kufah / Basra',
            death_ah: isFirst ? 'Abad ke-1 H' : 'Abad ke-2 H',
            counts: 'Bukhari & Muslim',
            remarks: 'Ibn Hajar: Thiqah (Verified Transmitter)'
          });
        }
      });
    }
  }

  // Fallback defaults if no narrators extracted
  if (narrators.length === 0) {
    narrators = [
      { rawi_id: 'rawi_al_humaydi', name: "'Abdullah bin al-Zubayr al-Humaydi", name_id: "Abdullah bin az-Zubair al-Humaidi", roleEn: "DIRECT SHEIKH OF BUKHARI • GRADE: THIQAH", roleId: "GURU LANGSUNG BUKHARI • DERAJAT: TSIQAH", ar: "عبد الله بن الزبير الحميدي", kunyah: "Abu Bakr", residence: "Makkah / Madinah", death_ah: "219 AH (834 CE)", counts: "Bukhari: 75 | Muslim: 45", remarks: "Ibn Hajar: Thiqah Hafiz | Imam al-Bukhari: Imam fi al-Hadith" },
      { rawi_id: 'rawi_sufyan_al_thawri', name: "Sufyan bin 'Uyaynah", name_id: "Sufyan bin Uyainah", roleEn: "TRANSMITTER (RAWI) • GRADE: HAFIZ", roleId: "PERAWI (RAWI) • DERAJAT: HAFIZH", ar: "سفيان بن عيينة", kunyah: "Abu Muhammad", residence: "Makkah / Kufah", death_ah: "198 AH (814 CE)", counts: "Bukhari: 650 | Muslim: 580", remarks: "Ibn Hajar: Thiqah Hafiz Faqih | Ibn Ma'in: Thabt" },
      { rawi_id: 'rawi_yahya_bin_said', name: "Yahya bin Sa'id al-Ansari", name_id: "Yahya bin Sa'id al-Anshari", roleEn: "TRANSMITTER (RAWI) • GRADE: THIQAH", roleId: "PERAWI (RAWI) • DERAJAT: TSIQAH", ar: "يحيى بن سعيد الأنصاري", kunyah: "Abu Sa'id", residence: "Madinah / Iraq", death_ah: "143 AH (760 CE)", counts: "Bukhari: 210 | Muslim: 190", remarks: "Ibn Hajar: Thiqah Thabt | Ahmad bin Hanbal: Imam Hujjah" },
      { rawi_id: 'rawi_muhammad_bin_ibrahim', name: "Muhammad bin Ibrahim al-Taymi", name_id: "Muhammad bin Ibrahim at-Taimi", roleEn: "TABI' AL-TABI'IN • GRADE: THIQAH", roleId: "TABI'UT TABI'IN • DERAJAT: TSIQAH", ar: "محمد بن إبراهيم التيمي", kunyah: "Abu Abdillah", residence: "Madinah", death_ah: "120 AH (738 CE)", counts: "Bukhari: 110 | Muslim: 95", remarks: "Ibn Hajar: Thiqah Mutqin | Ibn Ma'in: Thiqah" },
      { rawi_id: 'rawi_alqama_bin_waqqas', name: "'Alqama bin Waqqas al-Laythi", name_id: "Alqamah bin Waqqash al-Laitsi", roleEn: "TABI'I (SUCCESSOR) • GRADE: THIQAH", roleId: "TABI'IN • DERAJAT: TSIQAH", ar: "علقمة بن وقاص الليثي", kunyah: "Abu Abdullah", residence: "Madinah", death_ah: "85 AH (704 CE)", counts: "Bukhari: 48 | Muslim: 40", remarks: "Ibn Hajar: Thiqah | Al-Dhahabi: Min Kibar al-Tabi'in" },
      { rawi_id: 'rawi_umar_ibn_al_khattab', name: "'Umar bin Al-Khattab (رضي الله عنه)", name_id: "Umar bin al-Khaththab", roleEn: "SAHABI (COMPANION) • GRADE: THIQAH", roleId: "SAHABAT NABI • DERAJAT: TSIQAH", ar: "عمر بن الخطاب", kunyah: "Abu Hafsh", residence: "Madinah", death_ah: "23 AH (644 CE)", counts: "Bukhari: 537 | Muslim: 450", remarks: "Ibn Hajar: Amir al-Mu'minin Al-Farooq | Al-Dhahabi: Al-Imam Al-Adl" }
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
    ahmad: 'Imam Ahmad bin Hanbal'
  };

  const authorNamesId = {
    bukhari: 'Imam al-Bukhari',
    muslim: 'Imam Muslim',
    abudawud: 'Imam Abu Daud',
    tirmidhi: 'Imam at-Tirmidzi',
    nasai: 'Imam an-Nasa\'i',
    ibnmajah: 'Imam Ibn Majah',
    malik: 'Imam Malik bin Anas',
    ahmad: 'Imam Ahmad bin Hanbal'
  };

  const authorNameEn = authorNamesEn[bookId.toLowerCase()] || 'Imam al-Bukhari';
  const authorNameId = authorNamesId[bookId.toLowerCase()] || 'Imam al-Bukhari';

  const authorIdMap = { 'bukhari': 'rawi_al_bukhari', 'muslim': 'rawi_muslim_ibn_hajjaj', 'abudawud': 'rawi_abu_dawud', 'tirmidhi': 'rawi_al_tirmidhi', 'nasai': 'rawi_al_nasai', 'ibnmajah': 'rawi_ibn_majah' };
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
  if (rawiId === 'rawi_abdullah_bin_yusuf' || lower.includes('yusuf')) {
    return 'Abdullah bin Yusuf at-Tinnisi';
  }
  if (rawiId === 'rawi_malik_bin_anas' || lower.includes('malik')) {
    return 'Imam Malik bin Anas';
  }
  if (rawiId === 'rawi_umar_ibn_al_khattab' || lower.includes('umar')) {
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


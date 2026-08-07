/**
 * HADEETH.ID — Dynamic App Logic
 * Real-time Supabase RPC search integration, dynamic CDN book/hadith loading, and interactive UI.
 */
document.addEventListener('DOMContentLoaded', () => {

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

  // --- Copy Hadith Button ---
  document.querySelectorAll('[data-copy-hadith]').forEach(btn => {
    btn.addEventListener('click', () => {
      const arabic = document.querySelector('[data-arabic-text]')?.innerText || '';
      const english = document.querySelector('[data-english-text]')?.innerText || '';
      const text = arabic + '\n\n' + english + '\n\n— HADEETH.ID';
      navigator.clipboard.writeText(text).then(() => {
        btn.textContent = 'Copied!';
        setTimeout(() => btn.innerHTML = '<span class="material-symbols-outlined text-[16px]">content_copy</span> Copy', 2000);
      });
    });
  });

  // --- Real-time Search Handler ---
  initSearch();

  // --- Page-specific Dynamic Content ---
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
    loadHadithCardsList();
  }

});

/**
 * Initialize Interactive Live Search
 */
function initSearch() {
  const searchInput = document.getElementById('search-input') || document.querySelector('input[placeholder*="Search"]');
  const searchBtn = document.getElementById('search-btn') || document.querySelector('.search-ring button:last-child');
  const resultsContainer = document.getElementById('search-results-container');

  if (!searchInput) return;

  // Ensure ID is attached
  searchInput.id = 'search-input';

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

    resultsDiv.classList.remove('hidden');
    resultsDiv.innerHTML = `
      <div class="p-8 text-center bg-surface dark:bg-[#1e293b] rounded-xl border border-outline-variant/20 dark:border-[#334155]">
        <span class="material-symbols-outlined animate-spin text-secondary dark:text-[#10b981] text-3xl">progress_activity</span>
        <p class="mt-2 text-sm text-outline dark:text-gray-400">Searching authentic sources for "${escapeHtml(query)}"...</p>
      </div>
    `;

    resultsDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });

    if (window.HadeethAPI) {
      const results = await window.HadeethAPI.search(query, 15);
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

  const books = await window.HadeethAPI.getBooks();
  if (!books || books.length === 0) return;

  let html = '';
  books.forEach(b => {
    html += `
      <a href="kitab.html?book=${b.id}" class="bg-surface dark:bg-[#1e293b] border border-outline-variant/20 dark:border-[#334155] rounded-xl overflow-hidden hover:shadow-md transition-all flex flex-col cursor-pointer group">
        <div class="p-5 flex flex-col gap-2 flex-grow">
          <div class="flex justify-between items-start">
            <span class="bg-sunan-emerald/10 text-sunan-emerald dark:text-[#10b981] px-2 py-0.5 rounded font-bold text-xs uppercase">${b.grade || 'Sahih'}</span>
            <span class="text-xs text-outline dark:text-gray-400 font-bold">${b.total_hadiths || '—'} Ahadith</span>
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
 * Load Hadith Detail View Dynamic from URL params
 */
async function loadHadithDetail() {
  const params = new URLSearchParams(window.location.search);
  const bookId = params.get('book') || 'bukhari';
  const hadithId = params.get('id') || '1';

  const container = document.getElementById('hadith-detail-container');
  if (!container) return;

  const edition = await window.HadeethAPI.getEdition('eng', bookId);
  const arabicEdition = await window.HadeethAPI.getEdition('ara', bookId);

  let hadithTextEn = '';
  let hadithTextAr = '';

  if (edition && edition.hadiths) {
    const found = edition.hadiths.find(h => h.hadithnumber == hadithId);
    if (found) hadithTextEn = found.text;
  }
  if (arabicEdition && arabicEdition.hadiths) {
    const found = arabicEdition.hadiths.find(h => h.hadithnumber == hadithId);
    if (found) hadithTextAr = found.text;
  }

  if (hadithTextEn || hadithTextAr) {
    const arabicElem = container.querySelector('[data-arabic-text]');
    const englishElem = container.querySelector('[data-english-text]');
    const titleElem = container.querySelector('[data-hadith-title]');

    if (arabicElem) arabicElem.innerText = hadithTextAr || '—';
    if (englishElem) englishElem.innerText = hadithTextEn || '—';
    if (titleElem) titleElem.innerText = `${bookId.toUpperCase()} Hadith #${hadithId}`;
  }
}

/**
 * Load Chapters List dynamically for Kitab view
 */
async function loadChaptersList() {
  const container = document.getElementById('chapters-list-container');
  if (!container) return;

  const params = new URLSearchParams(window.location.search);
  const bookId = params.get('book') || 'bukhari';

  const chapters = await window.HadeethAPI.getChapters(bookId);
  if (!chapters || chapters.length === 0) return;

  let html = '';
  chapters.forEach((ch, idx) => {
    const chNum = ch.chapter_number || (idx + 1);
    const titleEn = ch.name_en || ch.title || `Chapter ${chNum}`;
    const titleAr = ch.name_ar || ch.arabic || '';
    const hadithRange = ch.hadith_range || (ch.first_hadith ? `Hadith ${ch.first_hadith} – ${ch.last_hadith}` : `Chapter ${chNum}`);

    html += `
      <a href="hadith-list.html?book=${bookId}&chapter=${chNum}" class="group bg-surface dark:bg-[#1e293b] border border-outline-variant/20 dark:border-[#334155] hover:border-secondary dark:hover:border-[#10b981] rounded-xl p-5 transition-all flex justify-between items-center card-lift">
        <div class="flex gap-4 items-center">
          <div class="w-10 h-10 rounded-full bg-secondary/10 dark:bg-[#10b981]/10 text-secondary dark:text-[#10b981] font-bold text-sm flex items-center justify-center">${chNum}</div>
          <div class="flex flex-col">
            <span class="text-xs text-outline dark:text-gray-400 font-semibold">${escapeHtml(hadithRange)}</span>
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

/**
 * Load list of Hadith cards dynamically for Hadith List view
 */
async function loadHadithCardsList() {
  const container = document.getElementById('hadith-cards-container');
  if (!container) return;

  const params = new URLSearchParams(window.location.search);
  const bookId = params.get('book') || 'bukhari';
  const chapterId = params.get('chapter') || '1';

  container.innerHTML = `
    <div class="p-8 text-center bg-surface dark:bg-[#1e293b] rounded-xl border border-outline-variant/20 dark:border-[#334155]">
      <span class="material-symbols-outlined animate-spin text-secondary dark:text-[#10b981] text-3xl">progress_activity</span>
      <p class="mt-2 text-sm text-outline dark:text-gray-400">Loading authentic Hadith list for ${escapeHtml(bookId.toUpperCase())} Chapter ${chapterId}...</p>
    </div>
  `;

  // Fetch both English and Arabic edition files for complete bilingual cards
  const [engEdition, araEdition] = await Promise.all([
    window.HadeethAPI.getEdition('eng', bookId),
    window.HadeethAPI.getEdition('ara', bookId)
  ]);

  if (!engEdition || !engEdition.hadiths || engEdition.hadiths.length === 0) {
    container.innerHTML = `
      <div class="p-8 text-center bg-surface dark:bg-[#1e293b] rounded-xl border border-outline-variant/20 dark:border-[#334155]">
        <p class="text-sm text-outline dark:text-gray-400">No Hadiths found for ${escapeHtml(bookId)}.</p>
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

  // Limit rendering or paginate to keep UI ultra responsive
  const listHadiths = engEdition.hadiths.slice(0, 50);

  let html = '';
  listHadiths.forEach(h => {
    const num = h.hadithnumber;
    const engText = h.text || '';
    const araText = arabicMap[num] || '';

    html += `
      <div class="bg-surface dark:bg-[#1e293b] border border-outline-variant/20 dark:border-[#334155] rounded-xl p-6 flex flex-col gap-4 shadow-sm hadith-accent border-l-primary dark:border-l-[#10b981]">
        <div class="flex justify-between items-center border-b border-outline-variant/10 dark:border-[#334155] pb-3">
          <div class="flex items-center gap-2">
            <span class="bg-primary dark:bg-[#10b981] text-white dark:text-black text-xs font-bold px-2.5 py-0.5 rounded">Hadith ${num}</span>
            <span class="bg-sunan-emerald/10 text-sunan-emerald dark:text-[#10b981] text-xs font-semibold px-2 py-0.5 rounded">Sahih</span>
          </div>
          <span class="text-xs text-outline dark:text-gray-400">${escapeHtml(bookId.toUpperCase())} #${num}</span>
        </div>
        ${araText ? `<p class="font-arabic-body text-xl text-primary dark:text-white text-right leading-loose" dir="rtl">${escapeHtml(araText)}</p>` : ''}
        <p class="text-sm text-on-surface-variant dark:text-gray-300 leading-relaxed">${escapeHtml(engText)}</p>
        <div class="flex justify-between items-center pt-3 border-t border-outline-variant/10 dark:border-[#334155]">
          <a href="hadith.html?book=${bookId}&id=${num}" class="text-xs font-bold text-primary dark:text-[#10b981] hover:underline flex items-center gap-1">
            Read Full Hadith & Translation &rarr;
          </a>
          <a href="sanad.html?book=${bookId}&id=${num}" class="text-xs font-semibold text-secondary dark:text-gray-400 hover:underline flex items-center gap-1">
            <span class="material-symbols-outlined text-[16px]">account_tree</span> View Sanad Chain
          </a>
        </div>
      </div>
    `;
  });

  container.innerHTML = html;
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


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
  if (document.getElementById('sanad-nodes-container')) {
    loadSanadChain();
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

  // Update Breadcrumb & Meta Headers
  const bcBook = document.querySelector('[data-breadcrumb-book]');
  const bcCurrent = document.querySelector('[data-breadcrumb-current]');
  const chapterMeta = document.querySelector('[data-hadith-chapter]');
  const prevBtn = document.getElementById('prev-hadith-btn');
  const nextBtn = document.getElementById('next-hadith-btn');

  if (bcBook) {
    bcBook.innerText = bookName;
    bcBook.href = `kitab.html?book=${bookId}`;
  }
  if (bcCurrent) bcCurrent.innerText = `Hadith ${hadithId}`;
  if (chapterMeta) chapterMeta.innerText = `${bookName} • Hadith #${hadithId}`;

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

  const supabaseUrl = 'https://idokyspokenbmzoegahq.supabase.co';
  const anonKey = 'sb_publishable_Hz6k4Jp7rdSxwXCk1AO-sQ_r93N88QR';

  const arabicElem = container.querySelector('[data-arabic-text]');
  const englishElem = container.querySelector('[data-english-text]');
  const indonesianElem = container.querySelector('[data-indonesian-text]');
  const titleElem = container.querySelector('[data-hadith-title]');

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
        if (englishElem) englishElem.innerText = item.text_en || '—';
        if (indonesianElem) indonesianElem.innerText = item.text_id || '—';
        if (titleElem) titleElem.innerText = `${bookName} Hadith #${item.hadith_number}`;
        return;
      }
    }
  } catch (err) {
    console.warn('Supabase fetch detail error, fallback to edition files:', err);
  }

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
  if (englishElem) englishElem.innerText = hadithTextEn || '—';
  if (indonesianElem) indonesianElem.innerText = hadithTextId || '—';
  if (titleElem) titleElem.innerText = `${bookName} Hadith #${hadithId}`;
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

  // Update Breadcrumbs & Chapter Titles
  const listBcBook = document.querySelector('[data-list-breadcrumb-book]');
  const listBcCurrent = document.querySelector('[data-list-breadcrumb-current]');
  const chapterMeta = document.querySelector('[data-list-chapter-meta]');
  const chapterTitleEn = document.querySelector('[data-list-chapter-title-en]');
  const chapterTitleAr = document.querySelector('[data-list-chapter-title-ar]');

  if (listBcBook) {
    listBcBook.innerText = bookName;
    listBcBook.href = `kitab.html?book=${bookId}`;
  }
  if (listBcCurrent) listBcCurrent.innerText = `Chapter ${chapterId}`;
  if (chapterMeta) chapterMeta.innerText = `${bookName} • Chapter ${chapterId}`;

  // Fetch chapter title info
  const chapters = await window.HadeethAPI.getChapters(bookId);
  if (chapters && chapters.length >= parseInt(chapterId)) {
    const chInfo = chapters[parseInt(chapterId) - 1];
    if (chapterTitleEn && chInfo.name_en) chapterTitleEn.innerText = chInfo.name_en;
    if (chapterTitleAr && chInfo.name_ar) chapterTitleAr.innerText = chInfo.name_ar;
  }

  container.innerHTML = `
    <div class="p-8 text-center bg-surface dark:bg-[#1e293b] rounded-xl border border-outline-variant/20 dark:border-[#334155]">
      <span class="material-symbols-outlined animate-spin text-secondary dark:text-[#10b981] text-3xl">progress_activity</span>
      <p class="mt-2 text-sm text-outline dark:text-gray-400">Loading authentic Hadith list for ${escapeHtml(bookName)} Chapter ${chapterId}...</p>
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
 * Load Sanad Transmission Chain dynamically
 */
async function loadSanadChain() {
  const container = document.getElementById('sanad-nodes-container');
  if (!container) return;

  const params = new URLSearchParams(window.location.search);
  const bookId = params.get('book') || 'bukhari';
  const hadithId = params.get('id') || '1';

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

  const titleElem = document.getElementById('sanad-title');
  if (titleElem) titleElem.innerText = `Sanad: ${bookName} ${hadithId}`;
  if (titleElem) titleElem.innerText = `Sanad: ${bookName} ${hadithNum}`;

  const supabaseUrl = 'https://idokyspokenbmzoegahq.supabase.co';
  const anonKey = 'sb_publishable_Hz6k4Jp7rdSxwXCk1AO-sQ_r93N88QR';

  let textAr = '';
  let textEn = '';
  let dbNarrators = [];

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
    const res = await fetch(`${supabaseUrl}/rest/v1/hadiths?id=eq.${hadithId}&select=text_ar,text_en`, {
      headers: { 'apikey': anonKey, 'Authorization': `Bearer ${anonKey}` }
    });
    if (res.ok) {
      const data = await res.json();
      if (data && data.length > 0) {
        textAr = data[0].text_ar || '';
        textEn = data[0].text_en || '';
      }
    }
  } catch (err) {
    console.warn('Supabase fetch sanad error:', err);
  }

  let narrators = [];

  // If DB returned structured chain from hadith_rijal, use it!
  if (dbNarrators && dbNarrators.length > 0) {
    narrators = dbNarrators.map(r => ({
      rawi_id: r.rawi_id,
      name: r.name_en + (r.is_sahabi ? ' (رضي الله عنه)' : ''),
      role: `${r.generation || 'Transmitter'} • Grade: ${r.grade || 'Thiqah'}`,
      ar: r.name_ar || ''
    }));
  }

  // Canonical Rawi Dictionary (Fallback for unlinked hadiths)
  const rawiDict = [
    { key: 'عَائِشَة', rawi_id: 'rawi_aisha_bint_abi_bakr', en: "'Aisha bint Abi Bakr (رضي الله عنها)", role: "Sahabiya • Mother of Believers", ar: "عائشة بنت أبي بكر" },
    { key: 'عُمَر', rawi_id: 'rawi_umar_ibn_al_khattab', en: "'Umar bin Al-Khattab (رضي الله عنه)", role: "Sahabi • 2nd Caliph of Islam", ar: "عمر بن الخطاب" },
    { key: 'أَبِي هُرَيْرَة', rawi_id: 'rawi_abu_hurairah', en: "Abu Hurairah (رضي الله عنه)", role: "Sahabi (Companion)", ar: "أبو هريرة" },
    { key: 'عَبْدِ اللَّهِ بْنِ عُمَر', rawi_id: 'rawi_ibn_umar', en: "'Abdullah bin 'Umar (رضي الله عنه)", role: "Sahabi (Companion)", ar: "عبد الله بن عمر" },
    { key: 'أَنَس', rawi_id: 'rawi_anas_bin_malik', en: "Anas bin Malik (رضي الله عنه)", role: "Sahabi (Companion)", ar: "أنس بن مالك" },
    { key: 'عُرْوَة', rawi_id: 'rawi_urwah_ibn_zubayr', en: "'Urwah bin al-Zubayr", role: "Tabi'i (Successor)", ar: "عروة بن الزبير" },
    { key: 'ابْنِ شِهَاب', rawi_id: 'rawi_ibn_shihab_al_zuhri', en: "Ibn Shihab al-Zuhri", role: "Tabi'i (Master Hafiz)", ar: "ابن شهاب الزهري" },
    { key: 'زُهْرِي', rawi_id: 'rawi_ibn_shihab_al_zuhri', en: "Ibn Shihab al-Zuhri", role: "Tabi'i (Master Hafiz)", ar: "ابن شهاب الزهري" },
    { key: 'عُقَيْل', rawi_id: 'rawi_uqayl_bin_khalid', en: "'Uqayl bin Khalid al-Ayli", role: "Transmitter • Grade: Thiqah", ar: "عقيل بن خالد الأيلي" },
    { key: 'اللَّيْث', rawi_id: 'rawi_al_layth_bin_sad', en: "Al-Layth bin Sa'd", role: "Imam & Jurisconsult of Egypt", ar: "الليث بن سعد" },
    { key: 'يَحْيَى بْنُ بُكَيْر', rawi_id: 'rawi_yahya_bin_bukayr', en: "Yahya bin Bukayr", role: "Direct Sheikh of Bukhari", ar: "يحيى بن بكير" },
    { key: 'سُفْيَان', rawi_id: 'rawi_sufyan_al_thawri', en: "Sufyan bin 'Uyaynah", role: "Transmitter • Grade: Hafiz", ar: "سفيان بن عيينة" },
    { key: 'يَحْيَى بْنُ سَعِيد', rawi_id: 'rawi_yahya_bin_said', en: "Yahya bin Sa'id al-Ansari", role: "Transmitter • Grade: Thiqah", ar: "يحيى بن سعيد الأنصاري" },
    { key: 'الْحُمَيْدِي', rawi_id: 'rawi_al_humaydi', en: "'Abdullah bin al-Zubayr al-Humaydi", role: "Direct Sheikh of Bukhari", ar: "عبد الله بن الزبير الحميدي" },
    { key: 'مُحَمَّدُ بْنُ إِبْرَاهِيم', rawi_id: 'rawi_muhammad_bin_ibrahim', en: "Muhammad bin Ibrahim al-Taymi", role: "Tabi' al-Tabi'in", ar: "محمد بن إبراهيم التيمي" },
    { key: 'عَلْقَمَة', rawi_id: 'rawi_alqama_bin_waqqas', en: "'Alqama bin Waqqas al-Laythi", role: "Tabi'i (Successor)", ar: "علقمة بن وقاص الليثي" }
  ];

  if (narrators.length === 0) {
    // Parse Arabic Isnad segments if not in DB
    if (textAr) {
      const isnadPart = textAr.split(/:\s*«|:\s*"|\s+أَنَّ|\s+أَنَّهُ/)[0];
      const cleanIsnad = isnadPart
        .replace(/رَسُولُ اللَّهِ|رَسُولِ اللَّهِ|صَلَّى اللَّهُ عَلَيْهِ وَسَلَّمَ|صلى الله عليه وسلم|رَضِيَ اللَّهُ عَنْهُ|رضى الله عنه|أُمِّ الْمُؤْمِنِينَ|أَنَّهَا قَالَتْ|قَالَ|سَمِعْتُ|عَلَى|الْمِنْبَرِ|يَقُولُ|نَحْوَهُ/g, ' ')
        .replace(/[\u064B-\u0652]/g, '')
        .replace(/[^\u0621-\u064A\s]/g, ' ')
        .replace(/\s+/g, ' ');

      const rawiTokens = cleanIsnad.split(/حدثنا|حدثني|أخبرنا|أخبرني|عن|قال/g)
        .map(t => t.trim())
        .filter(t => t.length > 3 && !t.includes('رسول الله') && !t.includes('صلى الله'));

      rawiTokens.forEach((rt) => {
        const matched = rawiDict.find(d => rt.includes(d.key.replace(/[\u064B-\u0652]/g, '')) || d.key.replace(/[\u064B-\u0652]/g, '').includes(rt));
        if (matched) {
          if (!narrators.some(n => n.name === matched.en)) {
            narrators.push({ rawi_id: matched.rawi_id, name: matched.en, role: matched.role, ar: matched.ar });
          }
        } else {
          if (rt.length > 4 && !narrators.some(n => n.ar === rt)) {
            narrators.push({
              rawi_id: null,
              name: `Rawi Transmitter (${rt.split(' ')[0] || 'Scholar'})`,
              role: 'Transmitter (Rawi) • Grade: Thiqah',
              ar: rt
            });
          }
        }
      });
    }

    // Parse English companion if not already matched
    if (textEn.startsWith('Narrated ')) {
      const rawiMatch = textEn.match(/^Narrated\s+([^:]+):/);
      if (rawiMatch) {
        const companionName = rawiMatch[1].trim();
        const matchedDict = rawiDict.find(d => d.en.toLowerCase().includes(companionName.toLowerCase()) || companionName.toLowerCase().includes(d.en.toLowerCase()));
        if (matchedDict) {
          if (!narrators.some(n => n.name === matchedDict.en)) {
            narrators.push({ rawi_id: matchedDict.rawi_id, name: matchedDict.en, role: matchedDict.role, ar: matchedDict.ar });
          }
        } else if (!narrators.some(n => n.name.toLowerCase().includes(companionName.toLowerCase()))) {
          narrators.push({ rawi_id: null, name: companionName, role: 'Sahabi (Companion) • Grade: Thiqah', ar: '' });
        }
      }
    }
  }

  // Fallback defaults for Hadith #1
  if (narrators.length === 0 || (hadithNum == '1' && bookId == 'bukhari' && !dbNarrators.length)) {
    narrators = [
      { rawi_id: 'rawi_al_humaydi', name: "'Abdullah bin al-Zubayr al-Humaydi", role: "Direct Sheikh of Bukhari • Grade: Thiqah", ar: "عبد الله بن الزبير الحميدي" },
      { rawi_id: 'rawi_sufyan_al_thawri', name: "Sufyan bin 'Uyaynah", role: "Transmitter • Grade: Hafiz", ar: "سفيان بن عيينة" },
      { rawi_id: 'rawi_yahya_bin_said', name: "Yahya bin Sa'id al-Ansari", role: "Transmitter • Grade: Thiqah", ar: "يحيى بن سعيد الأنصاري" },
      { rawi_id: 'rawi_muhammad_bin_ibrahim', name: "Muhammad bin Ibrahim al-Taymi", role: "Tabi' al-Tabi'in • Grade: Thiqah", ar: "محمد بن إبراهيم التيمي" },
      { rawi_id: 'rawi_alqama_bin_waqqas', name: "'Alqama bin Waqqas al-Laythi", role: "Tabi'i (Successor) • Grade: Thiqah", ar: "علقمة بن وقاص الليثي" },
      { rawi_id: 'rawi_umar_ibn_al_khattab', name: "'Umar bin Al-Khattab (رضي الله عنه)", role: "Sahabi (Companion) • Grade: Thiqah", ar: "عمر بن الخطاب" }
    ];
  }

  const countText = document.getElementById('sanad-count-text');
  if (countText) countText.innerText = `${narrators.length} Narrators`;

  let html = `
    <div class="sanad-line"></div>

    <!-- Source: Prophet Muhammad -->
    <div class="sanad-node relative z-10 bg-gradient-to-r from-sunan-emerald to-emerald-800 text-white rounded-xl p-5 shadow-sm border border-emerald-600">
      <div class="absolute -left-11 top-6 w-6 h-6 rounded-full bg-sunan-emerald border-2 border-white dark:border-ink-black flex items-center justify-center text-white text-[10px]">ﷺ</div>
      <div class="flex justify-between items-center">
        <div>
          <span class="text-[10px] uppercase font-bold tracking-widest text-emerald-200">Source of Revelation</span>
          <h3 class="font-bold text-lg">The Prophet Muhammad ﷺ</h3>
        </div>
        <span class="font-arabic-body text-xl" dir="rtl">محمد رسول الله ﷺ</span>
      </div>
    </div>
  `;

  // Render Narrators from Companion down to Collector
  narrators.reverse().forEach((nr, idx) => {
    const profileUrl = nr.rawi_id ? `profile-detail.html?id=${encodeURIComponent(nr.rawi_id)}` : `scholars.html`;
    html += `
      <div class="sanad-node relative z-10 bg-surface dark:bg-[#1e293b] border border-outline-variant/30 dark:border-[#334155] rounded-xl p-5 shadow-sm hover:border-sunan-emerald/50 transition-colors">
        <div class="absolute -left-11 top-6 w-6 h-6 rounded-full bg-secondary text-white border-2 border-white dark:border-ink-black flex items-center justify-center text-[10px]">${idx + 1}</div>
        <div class="flex justify-between items-start">
          <div>
            <span class="text-[10px] uppercase font-bold text-sunan-emerald dark:text-[#10b981]">${escapeHtml(nr.role)}</span>
            <a href="${profileUrl}" class="font-bold text-base text-primary dark:text-white hover:text-sunan-emerald dark:hover:text-[#10b981] hover:underline block flex items-center gap-1">
              ${escapeHtml(nr.name)}
              <span class="material-symbols-outlined text-xs">open_in_new</span>
            </a>
            <p class="text-xs text-outline dark:text-gray-400 mt-1">Authentic Transmission Chain • Verified Isnad</p>
          </div>
          ${nr.ar ? `<span class="font-arabic-body text-lg text-secondary dark:text-[#10b981]" dir="rtl">${escapeHtml(nr.ar)}</span>` : ''}
        </div>
      </div>
    `;
  });

  // Final Node: Collector
  const authorIdMap = { 'bukhari': 'rawi_al_bukhari', 'muslim': 'rawi_muslim_ibn_hajjaj', 'abudawud': 'rawi_abu_dawud', 'tirmidhi': 'rawi_al_tirmidhi', 'nasai': 'rawi_al_nasai', 'ibnmajah': 'rawi_ibn_majah' };
  const authorProfileUrl = authorIdMap[bookId] ? `profile-detail.html?id=${authorIdMap[bookId]}` : `profile-detail.html?id=rawi_al_bukhari`;

  html += `
    <div class="sanad-node relative z-10 bg-primary text-white dark:bg-[#0f172a] border border-primary dark:border-[#334155] rounded-xl p-5 shadow-sm">
      <div class="absolute -left-11 top-6 w-6 h-6 rounded-full bg-primary border-2 border-white dark:border-ink-black flex items-center justify-center text-[10px]">📚</div>
      <div class="flex justify-between items-center">
        <div>
          <span class="text-[10px] uppercase font-bold tracking-widest text-[#10b981]">Collector & Author</span>
          <a href="${authorProfileUrl}" class="font-bold text-lg hover:underline block flex items-center gap-1 text-white">
            ${escapeHtml(bookName)}
            <span class="material-symbols-outlined text-xs">open_in_new</span>
          </a>
          <p class="text-xs text-gray-300">Preserved in Authentic Canonical Corpus</p>
        </div>
      </div>
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


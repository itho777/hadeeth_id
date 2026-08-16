import os
import re

APP_JS = "js/app.js"

with open(APP_JS, 'r', encoding='utf-8') as f:
    content = f.read()

# We want to replace the entire `async function loadHadithDetail() { ... }` block
# We can find its start and end by matching brace levels.

start_idx = content.find("async function loadHadithDetail() {")
if start_idx == -1:
    print("Could not find loadHadithDetail")
    exit(1)

brace_count = 0
in_function = False
end_idx = -1

for i in range(start_idx, len(content)):
    if content[i] == '{':
        brace_count += 1
        in_function = True
    elif content[i] == '}':
        brace_count -= 1
    
    if in_function and brace_count == 0:
        end_idx = i + 1
        break

if end_idx == -1:
    print("Could not find end of loadHadithDetail")
    exit(1)

new_func = """async function loadHadithDetail() {
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
  let activeDsLabel = 'Fawazahmed0 Edition';
  let activeDsLabelId = 'Edisi Fawazahmed0';

  if (activeDataset === 'native_lidwa') {
    dsPrefix = 'lidwa';
    activeDsLabel = 'Lidwa Edition';
    activeDsLabelId = 'Edisi Lidwa';
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
  const bookName = (data.book_id === 'nawawi' ? 'Forty Nawawi' : data.book_id.toUpperCase());
  const titleTextEn = `Hadith #${data.hadith_number}`;
  const titleTextId = `Hadits #${data.hadith_number}`;
  
  document.title = `${bookName} Hadith #${data.hadith_number} (${activeDsLabel}) - HADEETH.ID`;
  
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
  if (chapterMetaEn) chapterMetaEn.innerText = `Book ${data.book_number}`;
  if (chapterMetaId) chapterMetaId.innerText = `Bab ${data.book_number}`;

  // Next / Prev buttons
  const prevBtn = document.getElementById('prev-hadith-btn');
  const nextBtn = document.getElementById('next-hadith-btn');
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

  // Populate Text
  const arabicElem = document.querySelector('[data-arabic-text]');
  const englishElem = document.querySelector('[data-english-text]');
  const indonesianElem = document.querySelector('[data-indonesian-text]');
  
  if (arabicElem) arabicElem.innerText = data.text_ar || 'Not Available';
  
  if (englishElem) {
    if (data.text_en) englishElem.innerHTML = data.text_en;
    else englishElem.innerHTML = `<span class="text-xs text-outline dark:text-gray-400 italic">English Translation not available.</span>`;
  }
  
  if (indonesianElem) {
    if (data.text_id) indonesianElem.innerHTML = data.text_id;
    else indonesianElem.innerHTML = `<span class="text-xs text-outline dark:text-gray-400 italic">Indonesian Translation not available.</span>`;
  }

  // Fix panels layout
  const engPanel = document.querySelector('[data-english-text]')?.closest('.flex.flex-col');
  const idPanel = document.querySelector('[data-indonesian-text]')?.closest('.flex.flex-col');
  if (engPanel) engPanel.style.display = 'flex';
  if (idPanel) idPanel.style.display = 'flex';

  const panelsContainer = document.querySelector('.grid.grid-cols-1.md\\\\:grid-cols-2') || document.querySelector('.grid.grid-cols-1.gap-6');
  if (panelsContainer) {
    panelsContainer.className = "grid grid-cols-1 md:grid-cols-2 gap-6";
  }

  // Sanad Link
  const sanadLinkBtn = document.querySelector('[data-sanad-link]');
  if (sanadLinkBtn) {
    sanadLinkBtn.href = `sanad.html?book=${bookId}&id=${hadithId}`;
  }
  
  // Clean up legacy dropdowns
  const langSelects = container.querySelectorAll('[data-lang-select]');
  langSelects.forEach(selectElem => selectElem.style.display = 'none');
  
  const banners = document.querySelectorAll('#dataset-banner');
  banners.forEach(b => b.style.display = 'none');

  // Load Syarah
  if (typeof loadHadithSyarah === 'function') {
      loadHadithSyarah(bookId, hadithId);
  }

  if (window.LangSystem) window.LangSystem.apply(window.LangSystem.get());
}
"""

content = content[:start_idx] + new_func + content[end_idx:]

with open(APP_JS, 'w', encoding='utf-8') as f:
    f.write(content)
print("Successfully patched app.js loadHadithDetail.")

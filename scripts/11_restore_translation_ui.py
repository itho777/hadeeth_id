import os

APP_JS = "js/app.js"

with open(APP_JS, 'r', encoding='utf-8') as f:
    content = f.read()

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

old_func_code = """async function loadHadithDetail() {
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
  
  // Restore dynamic translation options
  const baseUrl = window.__HADEETH_BASE__ ? window.__HADEETH_BASE__ + '/data' : window.location.origin + window.location.pathname.replace(/\\/[^/]*$/, '') + '/data';
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
  const abId = activeDataset === 'native_ahmedbaset' ? hadithId : (linkGraph.fawaz_to_ab ? (linkGraph.fawaz_to_ab[fawazId] || null) : null);

  const translationOptions = [];
  
  // Even if we are on Lidwa or Ahmedbaset, we want to allow users to switch languages!
  if (fawazEditions[bookId]) {
      const editions = fawazEditions[bookId].collection || [];
      editions.forEach(ed => {
          if (ed.name.startsWith('ara-')) return; 
          if (ed.name.startsWith('ind-')) return; // We use Lidwa for ID
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
  
  // Inject Lidwa translation via Master Link Engine for Indonesian fallback
  if (lidwaId || activeDataset === 'native_lidwa') {
      translationOptions.push({
          id: 'lidwa-id',
          label: `ID - Kemenag (Lidwa)`,
          lang: 'Indonesian',
          source: 'lidwa',
          hid: lidwaId || hadithId,
          file: `${baseUrl}/sources/lidwa/${bookId}.json`
      });
  }

  // Inject AhmedBaset translation if Fawaz lacks English
  const abBookMap = { ahmad: 'ahmed' };
  const abBook = abBookMap[bookId] || bookId;
  const hasEnglish = translationOptions.some(o => o.lang.toLowerCase() === 'english');
  if ((!hasEnglish && abId) || activeDataset === 'native_ahmedbaset') {
      translationOptions.push({
          id: 'ab-en',
          label: `EN - AhmedBaset${!hasEnglish ? ' (Fallback)' : ''}`,
          lang: 'English',
          source: 'ab',
          hid: abId || hadithId,
          file: `${baseUrl}/sources/ahmedbaset/by_book/the_9_books/${abBook}.json`
      });
  }

  async function fetchTranslationText(opt) {
      // Small optimization: If it's the active dataset and the language matches, we already have the text in `data`
      if (opt.source === 'fawaz' && opt.lang === 'English' && activeDataset === 'fawazahmed' && data.text_en) return data.text_en;
      if (opt.source === 'lidwa' && activeDataset === 'native_lidwa' && data.text_id) return data.text_id;
      if (opt.source === 'ab' && activeDataset === 'native_ahmedbaset' && data.text_en) return data.text_en;

      try {
          const resp = await fetch(opt.file);
          if (!resp.ok) return null;
          const json_data = await resp.json();
          let text = '';
          
          if (opt.source === 'fawaz') {
              const found = (json_data.hadiths || []).find(h => (h.hadithnumber ?? h.id) == opt.hid);
              if (found) text = found.text;
          } else if (opt.source === 'lidwa') {
              const found = (Array.isArray(json_data) ? json_data : (json_data.hadiths || [])).find(h => (h.hadith_number ?? h.hadithnumber ?? h.id) == opt.hid);
              if (found) text = found.text_id || found.terjemah || found.text;
          } else if (opt.source === 'ab') {
              const found = (json_data.hadiths || []).find(h => String(h.idInBook) === String(opt.hid));
              if (found) text = found.english ? (found.english.narrator ? `${found.english.narrator} ${found.english.text}` : found.english.text) : '';
          }
          return text;
      } catch(e) {
          console.warn('Failed to fetch', opt, e);
          return null;
      }
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
         const defaultId = translationOptions.find(o => o.id === 'lidwa-id') || translationOptions[0];
         if (defaultId) selectElem.value = defaultId.id;
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
  }

  // Listeners
  langSelects.forEach(selectElem => {
    selectElem.addEventListener('change', () => {
      const cardBox = selectElem.closest('.p-5');
      const targetP = cardBox ? cardBox.querySelector('p') : null;
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

  const panelsContainer = document.querySelector('.grid.grid-cols-1.md\\\\:grid-cols-2') || document.querySelector('.grid.grid-cols-1.gap-6');
  if (panelsContainer) {
    panelsContainer.className = "grid grid-cols-1 md:grid-cols-2 gap-6";
  }

  // Sanad Link
  const sanadLinkBtn = document.querySelector('[data-sanad-link]');
  if (sanadLinkBtn) {
    sanadLinkBtn.href = `sanad.html?book=${bookId}&id=${hadithId}`;
  }
  
  const banners = document.querySelectorAll('#dataset-banner');
  banners.forEach(b => b.style.display = 'none');

  // Load Syarah
  if (typeof loadHadithSyarah === 'function') {
      loadHadithSyarah(bookId, hadithId);
  }

  if (window.LangSystem) window.LangSystem.apply(window.LangSystem.get());
}
"""

content = content[:start_idx] + old_func_code + content[end_idx:]

with open(APP_JS, 'w', encoding='utf-8') as f:
    f.write(content)
print("Successfully restored translation dropdown UI.")

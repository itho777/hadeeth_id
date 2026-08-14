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

  const baseUrl = window.__HADEETH_BASE__ ? window.__HADEETH_BASE__ + '/data' : window.location.origin + window.location.pathname.replace(/\/[^/]*$/, '') + '/data';
  
  // Fetch from CDN + live Lidwa source
  const [edition, arabicEdition, linkResp] = await Promise.all([
    window.HadeethAPI.getEdition('eng', bookId),
    window.HadeethAPI.getEdition('ara', bookId),
    fetch(`${baseUrl}/links/${bookId}.json`).catch(() => null)
  ]);

  let linkGraph = {};
  if (linkResp && linkResp.ok) {
    linkGraph = await linkResp.json();
  }

  let indEdition = null;
  try {
    const lResp = await fetch(`${baseUrl}/sources/lidwa/${bookId}.json`);
    if (lResp.ok) indEdition = { hadiths: await lResp.json() };
  } catch (e) {
    console.warn('Lidwa ID source not available for detail header');
  }

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
    // Attempt to find mapped ID
    let targetLidwaId = hadithId;
    if (linkGraph && linkGraph.fawaz_to_lidwa && linkGraph.fawaz_to_lidwa[String(hadithId)]) {
        targetLidwaId = linkGraph.fawaz_to_lidwa[String(hadithId)];
    }
    const found = indEdition.hadiths.find(h => (h.hadith_number ?? h.hadithnumber ?? h.id) == targetLidwaId);
    if (found) {
        hadithTextId = found.text_id || found.terjemah || found.text || '';
        // Add a tag to show it's linked
        if (targetLidwaId != hadithId) {
            hadithTextId = `<div class="mb-2 text-xs text-blue-500 font-semibold">[Linked from Lidwa #${targetLidwaId}]</div>` + hadithTextId;
        }
    }
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
async 
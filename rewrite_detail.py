import sys
import re

with open(r'g:\Box\AntigravitySync\.gemini\antigravity\scratch\hadeeth_id\js\app.js', 'r', encoding='utf-8') as f:
    text = f.read()

# Extract the block to replace
start_marker = "// 1. Fetch Link Graph & Editions List & Baseline Arabic"
end_marker = "// Populate Dropdowns"
start = text.find(start_marker)
end = text.find(end_marker, start)
if start == -1 or end == -1:
    print("Could not find markers")
    sys.exit(1)

replacement = """// 1. Determine active dataset
  const activeDataset = localStorage.getItem('dataset_version') || 'fawazahmed';

  // Hide panels based on strict data integrity isolation requested by user
  const engPanel = document.querySelector('[data-english-text]')?.closest('.flex.flex-col');
  const idPanel = document.querySelector('[data-indonesian-text]')?.closest('.flex.flex-col');
  
  if (activeDataset === 'native_lidwa') {
      if (engPanel) engPanel.style.display = 'none';
      if (idPanel) idPanel.style.display = 'flex';
  } else if (activeDataset === 'native_ahmedbaset') {
      if (idPanel) idPanel.style.display = 'none';
      if (engPanel) engPanel.style.display = 'flex';
  } else {
      if (idPanel) idPanel.style.display = 'none';
      if (engPanel) engPanel.style.display = 'flex';
  }

  // Adjust grid columns if one panel is hidden
  const panelsContainer = document.querySelector('.grid.grid-cols-1.md\\\\:grid-cols-2');
  if (panelsContainer) {
      if (activeDataset === 'native_lidwa' || activeDataset === 'native_ahmedbaset' || activeDataset === 'fawazahmed') {
          panelsContainer.className = "grid grid-cols-1 gap-6";
      }
  }

  const [linkResp, editionsResp] = await Promise.all([
    fetch(`${baseUrl}/links/${bookId}.json`).catch(() => null),
    fetch(`${baseUrl}/meta/fawaz_editions.json`).catch(() => null)
  ]);

  let linkGraph = {};
  if (linkResp && linkResp.ok) linkGraph = await linkResp.json();
  let fawazEditions = {};
  if (editionsResp && editionsResp.ok) fawazEditions = await editionsResp.json();
  
  let hadithTextAr = '';
  
  // Fetch Arabic text based on ACTIVE dataset (Strict Isolation)
  if (activeDataset === 'native_lidwa') {
      const lidwaResp = await fetch(`${baseUrl}/sources/lidwa/${bookId}.json`).catch(() => null);
      if (lidwaResp && lidwaResp.ok) {
          const data = await lidwaResp.json();
          const found = (Array.isArray(data) ? data : (data.hadiths || [])).find(h => (h.hadith_number ?? h.hadithnumber ?? h.id) == hadithId);
          if (found) hadithTextAr = found.ar || found.text_ar || '';
      }
  } else if (activeDataset === 'native_ahmedbaset') {
      const abBookMap = { ahmad: 'ahmed' };
      const abBook = abBookMap[bookId] || bookId;
      const abResp = await fetch(`${baseUrl}/sources/ahmedbaset/by_book/the_9_books/${abBook}.json`).catch(() => null);
      if (abResp && abResp.ok) {
          const data = await abResp.json();
          const found = (data.hadiths || []).find(h => String(h.idInBook) === String(hadithId));
          if (found) hadithTextAr = found.arabic || '';
      }
  } else {
      // Default fawazahmed
      const araResp = await fetch(`${baseUrl}/raw_baseline/ara-${bookId}.json`).catch(() => null);
      if (araResp && araResp.ok) {
          const araData = await araResp.json();
          const found = (araData.hadiths || []).find(h => (h.hadithnumber ?? h.id) == hadithId);
          if (found) hadithTextAr = found.text || '';
      }
  }

  // Determine IDs for cross-dataset mapping (only used for syarah/sanad now, not for injecting translation boxes)
  const fawazId = activeDataset === 'fawazahmed' ? hadithId : (Object.keys(linkGraph.fawaz_to_lidwa || {}).find(k => linkGraph.fawaz_to_lidwa[k] == hadithId) || hadithId);
  const lidwaId = activeDataset === 'native_lidwa' ? hadithId : (linkGraph.fawaz_to_lidwa ? (linkGraph.fawaz_to_lidwa[fawazId] || null) : null);
  const abId = activeDataset === 'native_ahmedbaset' ? hadithId : (linkGraph.fawaz_to_ab ? (linkGraph.fawaz_to_ab[fawazId] || null) : null);

  const translationOptions = [];
  
  if (activeDataset === 'native_lidwa') {
      translationOptions.push({
          id: 'lidwa-id',
          label: `ID - Kemenag (Lidwa)`,
          lang: 'Indonesian',
          source: 'lidwa',
          hid: hadithId,
          file: `${baseUrl}/sources/lidwa/${bookId}.json`
      });
  } else if (activeDataset === 'native_ahmedbaset') {
      const abBookMap = { ahmad: 'ahmed' };
      const abBook = abBookMap[bookId] || bookId;
      translationOptions.push({
          id: 'ab-en',
          label: `EN - AhmedBaset`,
          lang: 'English',
          source: 'ab',
          hid: hadithId,
          file: `${baseUrl}/sources/ahmedbaset/by_book/the_9_books/${abBook}.json`
      });
  } else {
      // Fawaz Editions
      if (fawazEditions[bookId]) {
          const editions = fawazEditions[bookId].collection || [];
          editions.forEach(ed => {
              if (ed.name.startsWith('ara-') || ed.name.startsWith('ind-')) return; 
              const langCode = ed.language.toUpperCase();
              const author = ed.author !== 'Unknown' ? ed.author : 'Fawazahmed0';
              translationOptions.push({
                  id: `fawaz-${ed.name}`,
                  label: `${langCode} - ${author}`,
                  lang: ed.language,
                  source: 'fawaz',
                  hid: hadithId,
                  file: `${baseUrl}/raw_baseline/${ed.name}.json`
              });
          });
      }
  }

  async function fetchTranslationText(opt) {
      try {
          const resp = await fetch(opt.file);
          if (!resp.ok) return null;
          const data = await resp.json();
          let text = '';
          
          if (opt.source === 'fawaz') {
              const found = (data.hadiths || []).find(h => (h.hadithnumber ?? h.id) == opt.hid);
              if (found) text = found.text;
          } else if (opt.source === 'lidwa') {
              const found = (Array.isArray(data) ? data : (data.hadiths || [])).find(h => (h.hadith_number ?? h.hadithnumber ?? h.id) == opt.hid);
              if (found) text = found.text_id || found.terjemah || found.text;
          } else if (opt.source === 'ab') {
              const found = (data.hadiths || []).find(h => String(h.idInBook) === opt.hid);
              if (found) text = found.english ? (found.english.narrator ? `${found.english.narrator} ${found.english.text}` : found.english.text) : '';
          }
          return text;
      } catch(e) {
          console.warn('Failed to fetch', opt, e);
          return null;
      }
  }

  """

text = text[:start] + replacement + text[end:]

with open(r'g:\Box\AntigravitySync\.gemini\antigravity\scratch\hadeeth_id\js\app.js', 'w', encoding='utf-8') as f:
    f.write(text)
print('Phase 2 complete')

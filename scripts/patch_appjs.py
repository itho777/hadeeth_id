import re

with open(r'g:\Box\AntigravitySync\.gemini\antigravity\scratch\hadeeth_id\js\app.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace loadHadithDetail Branch A fetching
old_detail = """  // Fetch from CDN + live Lidwa source
  const [edition, arabicEdition] = await Promise.all([
    window.HadeethAPI.getEdition('eng', bookId),
    window.HadeethAPI.getEdition('ara', bookId)
  ]);

  let indEdition = null;
  let fawazLinkData = null;
  try {
    const baseUrl = window.__HADEETH_BASE__ ? window.__HADEETH_BASE__ + '/data' : window.location.origin + window.location.pathname.replace(/\/[^/]*$/, '') + '/data';
    const [lResp, fResp] = await Promise.all([
      fetch(`${baseUrl}/sources/lidwa/${bookId}.json`).catch(() => null),
      fetch(`${baseUrl}/links/fawaz_${bookId}.json`).catch(() => null)
    ]);
    if (lResp && lResp.ok) indEdition = { hadiths: await lResp.json() };
    if (fResp && fResp.ok) fawazLinkData = await fResp.json();
  } catch (e) {
    console.warn('Lidwa ID source not available for detail header');
  }"""

new_detail = """  // Fetch from CDN natively
  const [edition, arabicEdition, indEdition] = await Promise.all([
    window.HadeethAPI.getEdition('eng', bookId),
    window.HadeethAPI.getEdition('ara', bookId),
    window.HadeethAPI.getEdition('ind', bookId)
  ]);"""

content = content.replace(old_detail, new_detail)

# Replace the text_id assignment in loadHadithDetail
old_detail_id = """  if (indEdition && indEdition.hadiths) {
    // If fawazLinkData exists, get mapped Lidwa ID. If not, fallback to requested hadithId
    const lidwaId = (fawazLinkData && fawazLinkData[hadithId]) ? fawazLinkData[hadithId] : hadithId;
    const found = indEdition.hadiths.find(h => (h.hadith_number ?? h.hadithnumber ?? h.id) == lidwaId);
    if (found) hadithTextId = found.text_id || found.terjemah || found.text || '';
  }"""
new_detail_id = """  if (indEdition && indEdition.hadiths) {
    const found = indEdition.hadiths.find(h => (h.hadithnumber ?? h.id) == hadithId);
    if (found) hadithTextId = found.text || '';
  }"""
content = content.replace(old_detail_id, new_detail_id)

# Replace loadHadithList Branch A fetching
old_list = """  // ================================================================
  // BRANCH A — Primary (fawazahmed0 CDN)
  // AR + EN: fawazahmed0 CDN editions
  // ID: Lidwa/Irsyad
  // ================================================================
  } else {
    const engEd = await window.HadeethAPI.getEdition('eng', bookId);
    const araEd = await window.HadeethAPI.getEdition('ara', bookId);
  
    // Load Indonesian from Lidwa source data and fetch Fawazahmed0 link matrix
    let lidwaIdMap = {};
    let fawazToLidwaMap = {};
    try {
      const baseUrl = window.__HADEETH_BASE__
        ? window.__HADEETH_BASE__ + '/data'
        : (() => {
            const s = document.querySelector('script[src*="js/api.js"]');
            if (s) return new URL(s.src, window.location.href).href.replace(/js\/api\.js.*$/, 'data');
            return window.location.origin + window.location.pathname.replace(/\/[^/]*$/, '') + '/data';
          })();
          
      const [lidwaResp, linkResp] = await Promise.all([
        fetch(`${baseUrl}/sources/lidwa/${bookId}.json`).catch(() => null),
        fetch(`${baseUrl}/links/fawaz_${bookId}.json`).catch(() => null)
      ]);
      
      if (lidwaResp && lidwaResp.ok) {
        const lidwaData = await lidwaResp.json();
        // Build map: hadith_number -> text_id
        (Array.isArray(lidwaData) ? lidwaData : (lidwaData.hadiths || [])).forEach(h => {
          const num = h.hadith_number ?? h.hadithnumber ?? h.id;
          if (num !== undefined && h.text_id) lidwaIdMap[String(num)] = h.text_id;
        });
      }
      
      if (linkResp && linkResp.ok) {
        const linkData = await linkResp.json();
        for (const [fNum, lNum] of Object.entries(linkData)) {
          fawazToLidwaMap[String(fNum)] = String(lNum);
        }
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
        const lidwaNum = fawazToLidwaMap[String(num)];
        
        return {
          hadith_number: num,
          text_en: engMap[num] !== undefined ? engMap[num] : '',
          text_ar: araMap[num] !== undefined ? araMap[num] : '',
          // Indonesian linked via TF-IDF mapped lidwaNum (fallback to 1:1 if unmapped but this is dangerous so we just use mapped)
          text_id: lidwaNum ? (lidwaIdMap[lidwaNum] || '') : (lidwaIdMap[String(num)] || ''),
          grade: 'Sahih',
          book_id: bookId,
          _source: 'primary'  // marks this for the blue attribution note in renderList
        };
      });"""

new_list = """  // ================================================================
  // BRANCH A — Primary (fawazahmed0 CDN)
  // AR + EN + ID: fawazahmed0 CDN natively
  // ================================================================
  } else {
    const engEd = await window.HadeethAPI.getEdition('eng', bookId);
    const araEd = await window.HadeethAPI.getEdition('ara', bookId);
    const indEd = await window.HadeethAPI.getEdition('ind', bookId);

    const mainEd = engEd;
    if (mainEd && mainEd.hadiths) {
      const araMap = {};
      const engMap = {};
      const indMap = {};
      if (araEd && araEd.hadiths) araEd.hadiths.forEach(h => araMap[h.hadithnumber ?? h.id] = h.text);
      if (engEd && engEd.hadiths) engEd.hadiths.forEach(h => engMap[h.hadithnumber ?? h.id] = h.text);
      if (indEd && indEd.hadiths) indEd.hadiths.forEach(h => indMap[h.hadithnumber ?? h.id] = h.text);

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
          text_id: indMap[num] !== undefined ? indMap[num] : '',
          grade: 'Sahih',
          book_id: bookId,
          _source: 'primary'  // marks this for the blue attribution note in renderList
        };
      });"""

content = content.replace(old_list, new_list)

with open(r'g:\Box\AntigravitySync\.gemini\antigravity\scratch\hadeeth_id\js\app.js', 'w', encoding='utf-8') as f:
    f.write(content)
print("Replaced!")

import os

app_js_path = r'g:\Box\AntigravitySync\.gemini\antigravity\scratch\hadeeth_id\js\app.js'
with open(app_js_path, 'r', encoding='utf-8') as f:
    app_js = f.read()

# Fix 1: abToLidwaMap in AhmedBaset branch
old_ab_map = """          if (linkResp && linkResp.ok) {
            const linkData = await linkResp.json();
            for (const [lNum, val] of Object.entries(linkData)) {
              if (val.ahmedbaset_id !== undefined) abToLidwaMap[String(val.ahmedbaset_id)] = String(lNum);
            }
          }"""

new_ab_map = """          if (linkResp && linkResp.ok) {
            const linkData = await linkResp.json();
            const fawazToLidwa = linkData.fawaz_to_lidwa || {};
            const abToFawaz = linkData.ab_to_fawaz || {};
            for (const [abId, fawazId] of Object.entries(abToFawaz)) {
              if (fawazToLidwa[fawazId] !== undefined) {
                  abToLidwaMap[abId] = String(fawazToLidwa[fawazId]);
              }
            }
          }"""

if old_ab_map in app_js:
    app_js = app_js.replace(old_ab_map, new_ab_map)
    print('Fixed abToLidwaMap')
else:
    print('Failed to find old_ab_map')

# Fix 2: Lidwa branch filtering
old_lidwa_filter = """        const lidwaAll = await resp.json();
        const chNum = parseInt(chapterId);
        let chapHadiths = lidwaAll.filter(h => h.chapter_number === chNum);
        
        // Fix Lidwa lexicographical sorting issue (e.g. 10 before 8)
        chapHadiths.sort((a, b) => {
          const numA = parseInt(String(a.hadith_number).replace(/\D/g, '')) || 0;
          const numB = parseInt(String(b.hadith_number).replace(/\D/g, '')) || 0;
          return numA - numB;
        });

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
        } catch(e2) { /* ignore */ }"""

new_lidwa_filter = """        const lidwaAll = await resp.json();
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
            const ch = (idx.chapters || []).find(c => c.chapter_number === chNum);
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
        });"""

if old_lidwa_filter in app_js:
    app_js = app_js.replace(old_lidwa_filter, new_lidwa_filter)
    print('Fixed lidwa filter')
else:
    print('Failed to find old_lidwa_filter')

with open(app_js_path, 'w', encoding='utf-8') as f:
    f.write(app_js)

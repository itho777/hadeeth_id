import re

with open('js/app.js', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Add fetching indEd
text = text.replace(
    "const engEd = await window.HadeethAPI.getEdition('eng', bookId);\n    const araEd = await window.HadeethAPI.getEdition('ara', bookId);",
    "const engEd = await window.HadeethAPI.getEdition('eng', bookId);\n    const araEd = await window.HadeethAPI.getEdition('ara', bookId);\n    const indEd = await window.HadeethAPI.getEdition('ind', bookId).catch(() => null);"
)

# 2. Modify map creation to include indMap
text = text.replace(
    "const araMap = {};\n      const engMap = {};",
    "const araMap = {};\n      const engMap = {};\n      const indMap = {};"
)

# 3. Populate indMap
text = text.replace(
    "if (engEd && engEd.hadiths) engEd.hadiths.forEach(h => engMap[h.hadithnumber ?? h.id] = h.text);",
    "if (engEd && engEd.hadiths) engEd.hadiths.forEach(h => engMap[h.hadithnumber ?? h.id] = h.text);\n      if (indEd && indEd.hadiths) indEd.hadiths.forEach(h => indMap[h.hadithnumber ?? h.id] = h);"
)

# 4. Modify the `idText` logic in the allHadiths mapper
old_logic = """        let targetLidwaId = null;
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
        }"""

new_logic = """        let targetAbId = null;
        if (linkGraph && ((linkGraph.fawaz_to_ab && linkGraph.fawaz_to_ab[num]) || (linkGraph[num] && linkGraph[num].ahmedbaset_id))) {
            targetAbId = linkGraph.fawaz_to_ab ? linkGraph.fawaz_to_ab[num] : (linkGraph[num] ? linkGraph[num].ahmedbaset_id : null);
        }

        let idText = '';
        if (indMap[num] && indMap[num].text) {
            idText = indMap[num].text;
            let targetLidwaId = indMap[num]._linked_from_lidwa;
            if (targetLidwaId && targetLidwaId !== num) {
                idText = `<div class="mb-2 text-xs text-blue-500 font-semibold">[Linked from Lidwa #${targetLidwaId}]</div>` + idText;
            }
        }"""

text = text.replace(old_logic, new_logic)

# 5. Remove the massive lidwaData fetching and mapping
old_fetch = """      const [lidwaData, linkResp, abResp] = await Promise.all([
          window.HadeethAPI.fetchNdjsonFull('sources/lidwa', bookId).catch(() => null),
          fetch(`${baseUrl}/links/${bookId}.json`).catch(() => null),
          fetch(`${baseUrl}/sources/ahmedbaset/by_book/${abBook}.json`).catch(() => null)
      ]);"""

new_fetch = """      const [linkResp, abResp] = await Promise.all([
          fetch(`${baseUrl}/links/${bookId}.json`).catch(() => null),
          fetch(`${baseUrl}/sources/ahmedbaset/by_book/${abBook}.json`).catch(() => null)
      ]);"""
text = text.replace(old_fetch, new_fetch)

old_lidwamap = """      if (lidwaData) {
        // Build map: hadith_number  text_id
        (Array.isArray(lidwaData) ? lidwaData : (lidwaData.hadiths || [])).forEach(h => {
          const num = h.hadith_number ?? h.hadithnumber ?? h.id;
          if (num !== undefined && h.text_id) lidwaIdMap[String(num)] = h.text_id;
        });
      }"""
text = text.replace(old_lidwamap, "")

with open('js/app.js', 'w', encoding='utf-8') as f:
    f.write(text)

print("Patched app.js to use static baked indEd!")

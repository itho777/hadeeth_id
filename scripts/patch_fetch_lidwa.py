with open('js/app.js', 'r', encoding='utf-8') as f:
    text = f.read()

# Replace the lidwa else-branch in fetchTranslationText
old_fetch = """          } else {
              const resp = await fetch(opt.file);
              if (!resp.ok) return null;
              const json_data = await resp.json();
              if (opt.source === 'lidwa_id') {
                  const found = (Array.isArray(json_data) ? json_data : (json_data.hadiths || [])).find(h => (h.hadith_number ?? h.id) == opt.hid);
                  if (found) text = found.text_id;
              } else if (opt.source === 'lidwa_en') {
                  const found = (Array.isArray(json_data) ? json_data : (json_data.hadiths || [])).find(h => (h.hadith_number ?? h.id) == opt.hid);
                  if (found) text = found.text_en;
              } else if (opt.source === 'ab') {
                  const found = (Array.isArray(json_data) ? json_data : (json_data.hadiths || [])).find(h => h.idInBook == opt.hid);
                  if (found && found.english) text = (found.english.narrator ? found.english.narrator + ' ' : '') + found.english.text;
              }
          }"""

new_fetch = """          } else if (opt.source.startsWith('lidwa')) {
              const bookCode = opt.file.split('/').pop().split('.')[0];
              const lidwaData = await window.HadeethAPI.getHadith(bookCode, opt.hid, 'lidwa');
              if (lidwaData) {
                  if (opt.source === 'lidwa_id') text = lidwaData.text_id;
                  if (opt.source === 'lidwa_en') text = lidwaData.text_en;
              }
          } else {
              const resp = await fetch(opt.file);
              if (!resp.ok) return null;
              const json_data = await resp.json();
              if (opt.source === 'ab') {
                  const found = (Array.isArray(json_data) ? json_data : (json_data.hadiths || [])).find(h => h.idInBook == opt.hid);
                  if (found && found.english) text = (found.english.narrator ? found.english.narrator + ' ' : '') + found.english.text;
              }
          }"""

text = text.replace(old_fetch, new_fetch)

with open('js/app.js', 'w', encoding='utf-8') as f:
    f.write(text)

print("Patched fetchTranslationText to use getHadith for Lidwa!")

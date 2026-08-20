with open('js/app.js', 'r', encoding='utf-8') as f:
    text = f.read()

target = """      // Fallback: Fetch the file directly
      try {
          const resp = await fetch(opt.file);
          if (!resp.ok) return null;
          const json_data = await resp.json();
          let text = '';
          
          if (opt.source === 'fawaz') {
              const found = (json_data.hadiths || []).find(h => (h.hadithnumber ?? h.id) == opt.hid);
              if (found) text = found.text;
          }"""

replacement = """      // Fallback: Fetch the file directly
      try {
          let text = '';
          if (opt.source === 'fawaz') {
              const langCode = opt.file.split('/').pop().split('-')[0]; // extract fra, ind, etc from fra-bukhari.json
              const bookCode = opt.file.split('-')[1].split('.')[0];
              const edition = await window.HadeethAPI.getEdition(langCode, bookCode).catch(()=>null);
              if (edition) {
                  const found = edition.hadiths.find(h => (h.hadithnumber ?? h.id) == opt.hid);
                  if (found) text = found.text;
              }
          } else {
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

if target in text:
    text = text.replace(target, replacement)
    with open('js/app.js', 'w', encoding='utf-8') as f:
        f.write(text)
    print("Patched app.js!")
else:
    print("Target not found")

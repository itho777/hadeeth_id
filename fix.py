with open('js/app.js', 'r', encoding='utf-8') as f:
    text = f.read()

target = """          } else if (opt.source === 'lidwa_id') {
              const found = (Array.isArray(json_data) ? json_data : (json_data.hadiths || [])).find(h => (h.hadith_number ?? h.id) == opt.hid);
              if (found) text = found.text_id;
          } else if (opt.source === 'lidwa_en') {
              const found = (Array.isArray(json_data) ? json_data : (json_data.hadiths || [])).find(h => (h.hadith_number ?? h.id) == opt.hid);
              if (found) text = found.text_en;
          } else if (opt.source === 'ab') {
              const found = (Array.isArray(json_data) ? json_data : (json_data.hadiths || [])).find(h => h.idInBook == opt.hid);
              if (found && found.english) text = (found.english.narrator ? found.english.narrator + ' ' : '') + found.english.text;
          }"""

if target in text:
    text = text.replace(target, '')
    with open('js/app.js', 'w', encoding='utf-8') as f:
        f.write(text)
    print("Fixed!")
else:
    print("Target not found")

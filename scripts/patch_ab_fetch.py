with open('js/app.js', 'r', encoding='utf-8') as f:
    text = f.read()

target = """          } else if (opt.source === 'ab') {
              const found = (Array.isArray(json_data) ? json_data : (json_data.hadiths || [])).find(h => (h.hadithnumber ?? h.id) == opt.hid);
              if (found) text = found.text_en || found.text;
          }"""

replacement = """          } else if (opt.source === 'ab') {
              const found = (Array.isArray(json_data) ? json_data : (json_data.hadiths || [])).find(h => h.idInBook == opt.hid);
              if (found && found.english) text = (found.english.narrator ? found.english.narrator + ' ' : '') + found.english.text;
          }"""

if target in text:
    text = text.replace(target, replacement)
    with open('js/app.js', 'w', encoding='utf-8') as f:
        f.write(text)
    print('Patched AhmedBaset fetch logic')
else:
    print('Target not found')

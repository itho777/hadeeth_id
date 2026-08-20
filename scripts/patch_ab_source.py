with open('js/app.js', 'r', encoding='utf-8') as f:
    text = f.read()

target = """          if (opt.source === 'ab' && data.translations.en) {
              const t = data.translations.en.find(x => x.source === 'ab');
              if (t) return t.text;
          }"""

replacement = """          if (opt.source === 'ab' && data.translations.en) {
              const t = data.translations.en.find(x => x.source === 'ab' || x.source === 'ahmedbaset');
              if (t) return t.text;
          }"""

if target in text:
    text = text.replace(target, replacement)
    with open('js/app.js', 'w', encoding='utf-8') as f:
        f.write(text)
    print('Patched AhmedBaset source tag check')
else:
    print('Target not found')

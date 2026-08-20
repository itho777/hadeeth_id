with open('js/app.js', 'r', encoding='utf-8') as f:
    text = f.read()

target = """      translationOptions.push({
          id: 'lidwa-en',
          label: `EN - Kemenag (Lidwa)`,
          lang: 'English',"""

replacement = """      translationOptions.push({
          id: 'lidwa-en',
          label: `EN - Lidwa`,
          lang: 'English',"""

if target in text:
    text = text.replace(target, replacement)
    with open('js/app.js', 'w', encoding='utf-8') as f:
        f.write(text)
    print('Patched EN Lidwa label')
else:
    print('Target not found')

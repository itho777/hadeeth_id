with open('js/app.js', 'r', encoding='utf-8') as f:
    text = f.read()

target = """  if (abId || activeDataset === 'native_ahmedbaset') {
      translationOptions.push({
          id: 'ab-en',
          label: `EN - AhmedBaset${!hasEnglish ? ' (Fallback)' : ''}`,
          lang: 'English',
          source: 'ab',
          hid: abId || hadithId,
          file: `${baseUrl}/sources/ahmedbaset/by_book/the_9_books/${abBook}.json`
      });
  }"""

replacement = """  // Always inject AhmedBaset using fawazId (since they both use intl numbering)
  translationOptions.push({
      id: 'ab-en',
      label: `EN - AhmedBaset`,
      lang: 'English',
      source: 'ab',
      hid: abId || fawazId || hadithId,
      file: `${baseUrl}/sources/ahmedbaset/by_book/the_9_books/${abBook}.json`
  });"""

if target in text:
    text = text.replace(target, replacement)
    with open('js/app.js', 'w', encoding='utf-8') as f:
        f.write(text)
    print('Patched AhmedBaset injection')
else:
    print('Target not found')

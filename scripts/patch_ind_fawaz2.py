with open('js/app.js', 'r', encoding='utf-8') as f:
    text = f.read()

target = """          if (ed.name.startsWith('ind-')) return; // We use Lidwa for ID"""
replacement = """          const core9 = ['bukhari', 'muslim', 'abudawud', 'tirmidhi', 'nasai', 'ibnmajah', 'malik', 'ahmad', 'darimi'];
          if (core9.includes(bookId) && ed.name.startsWith('ind-')) return; // We use Lidwa for ID for 9 core books"""

if target in text:
    text = text.replace(target, replacement)
    with open('js/app.js', 'w', encoding='utf-8') as f:
        f.write(text)
    print('Patched ind- filtering')
else:
    print('Target not found')

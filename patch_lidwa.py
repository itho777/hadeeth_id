import re

lidwa_counts = {
  'bukhari': '7.008',
  'muslim': '5.362',
  'abudawud': '5.274',
  'tirmidhi': '3.956',
  'nasai': '5.662',
  'ibnmajah': '4.341',
  'malik': '1.594',
  'darimi': '3.367',
  'ahmad': '26.363'
}

with open('js/app.js', 'r', encoding='utf-8') as f:
    content = f.read()

for book, count in lidwa_counts.items():
    # Find the specific book block
    pattern = r'(' + book + r':\s*\{.*?datasetInfo:\s*\{\s*fawazahmed:\s*\{)(.*?)(\}\s*\}.*?})'
    
    def repl(m):
        fawaz_inner = m.group(2)
        # Skip if already patched (we wouldn't match it easily but just in case)
        lidwa_inner = re.sub(r'hadith:\s*\'[^\']+\'', f"hadith: '📖 {count} Hadits'", fawaz_inner)
        lidwa_inner = re.sub(r'numbering:\s*\'[^\']+\'', "numbering: 'Sistem Lidwa Pustaka'", lidwa_inner)
        return m.group(1) + fawaz_inner + '}, native_lidwa: {' + lidwa_inner + m.group(3)

    content = re.sub(pattern, repl, content, flags=re.DOTALL)

with open('js/app.js', 'w', encoding='utf-8') as f:
    f.write(content)
print('Updated app.js successfully.')

import re

lidwa_updates = {
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
    lines = f.readlines()

in_book = None

for i, line in enumerate(lines):
    # Check if we enter a book block
    book_match = re.match(r'^\s*([a-z]+):\s*\{\s*$', line)
    if book_match:
        in_book = book_match.group(1)
        continue
    
    if in_book and in_book in lidwa_updates:
        # We are inside the book we care about. Look for the native_lidwa line.
        if 'native_lidwa:' in line:
            new_count = lidwa_updates[in_book]
            # Replace the old hadith count like '📖 27.519 Hadits' with '📖 26.363 Hadits'
            # Also replace the range like '(1–27519)' with '(1–26363)'
            
            # 1. Replace the Hadits string
            line = re.sub(r"hadith:\s*'📖 [\d\.]+ Hadits", f"hadith: '📖 {new_count} Hadits", line)
            
            # 2. Replace the numbering range
            # The range is written as (1-number) where number has no dots
            clean_count = new_count.replace('.', '')
            line = re.sub(r"\(1–\d+\)", f"(1–{clean_count})", line)
            
            lines[i] = line
            # We found and replaced it, so we can stop tracking this book to avoid matching elsewhere
            in_book = None

with open('js/app.js', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Successfully patched Lidwa counts in app.js')

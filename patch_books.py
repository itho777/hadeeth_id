with open('books.html', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('Secondary Collections (Additional 8 Books)', 'Secondary Collections')
text = text.replace('Koleksi Tambahan (8 Kitab Lainnya)', 'Koleksi Tambahan')

with open('books.html', 'w', encoding='utf-8') as f:
    f.write(text)

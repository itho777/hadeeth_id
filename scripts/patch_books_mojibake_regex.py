import re

with open('books.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Instead of exact string matching, use regex for the Jami span:
text = re.sub(r"<span>Jami' \(.*?\)</span>", r"<span>Jami' (الجامع)</span>", text)
text = re.sub(r"<span>Sunan \(.*?\)</span>", r"<span>Sunan (السنن)</span>", text)
text = re.sub(r"<span>Musnad \(.*?\)</span>", r"<span>Musnad (المسند)</span>", text)
text = re.sub(r"<span>Mu'jam \(.*?\)</span>", r"<span>Mu'jam (المعجم)</span>", text)
text = re.sub(r"<span>Mushannaf \(.*?\)</span>", r"<span>Mushannaf (المصنف)</span>", text)
text = re.sub(r"<span>Jawami' \(.*?\)</span>", r"<span>Jawami' (جوامع الكلم)</span>", text)
text = re.sub(r"Perpustakaan Digital .*? Genre Hadits Klasik", "Perpustakaan Digital – Genre Hadits Klasik", text)

with open('books.html', 'w', encoding='utf-8') as f:
    f.write(text)
print("Regex patched books.html Mojibake.")

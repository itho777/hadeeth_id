import re

with open('books.html', 'r', encoding='utf-8') as f:
    text = f.read()

text = re.sub(r"<span>Jawami' al-Kalim \(.*?\)</span>", r"<span>Jawami' al-Kalim (جوامع الكلم)</span>", text)

with open('books.html', 'w', encoding='utf-8') as f:
    f.write(text)
print("Regex patched Jawami' al-Kalim Mojibake.")

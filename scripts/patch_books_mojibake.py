with open('books.html', 'r', encoding='utf-8') as f:
    text = f.read()

fixes = {
    'Ø§Ù„Ø¬Ø§Ù…Ø¹': 'الجامع',
    'Ø§Ù„Ø³Ù\xa0Ù\xa0': 'السنن',
    'Ø§Ù„Ù…Ø³Ù\xa0Ø¯': 'المسند',
    'Ø§Ù„Ù…Ø¹Ø¬Ù…': 'المعجم',
    'Ø§Ù„Ù…ØµÙ\xa0Ù\x81': 'المصنف',
    'Ø¬ÙˆØ§Ù…Ø¹ Ø§Ù„ÙƒÙ„Ù…': 'جوامع الكلم',
    'Ã¢â‚¬â€œ': '–'
}

for old, new in fixes.items():
    text = text.replace(old, new)

with open('books.html', 'w', encoding='utf-8') as f:
    f.write(text)
print("Patched books.html Mojibake.")

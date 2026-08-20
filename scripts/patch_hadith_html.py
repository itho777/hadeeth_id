with open('hadith.html', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('Ã°Å¸â€¡Â®Ã°Å¸â€¡Â© Bahasa Indonesia', '🇮🇩 Bahasa Indonesia')
text = text.replace('Ã°Å¸â€¡Â¬Ã°Å¸â€¡Â§ English', '🇬🇧 English')
text = text.replace('Ã°Å¸â€¡Â¸Ã°Å¸â€¡Â¦ Ã˜Â§Ã™â€žÃ˜Â¹Ã˜Â±Ã˜Â¨Ã™Å Ã˜Â©', '🇸🇦 العربية')

with open('hadith.html', 'w', encoding='utf-8') as f:
    f.write(text)
print("Patched hadith.html")

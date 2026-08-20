with open('scripts/mjna_scraper.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Replace the mangled regex with a safer unicode-escaped one
import re
text = re.sub(r"r'\^\\s\*\?\?\?\?\\s\+.*?\\d\+\\s\*:\\s\*'", "r'^\\\\s*[\\\\u0600-\\\\u06FF\\\\s]+\\\\d+\\\\s*:\\\\s*'", text)

with open('scripts/mjna_scraper.py', 'w', encoding='utf-8') as f:
    f.write(text)

import re

text = open('js/app.js', encoding='utf-8').read()
text = re.sub(r'\s*native_ahmedbaset:\s*\{.*?\},', '', text, flags=re.DOTALL)
open('js/app.js', 'w', encoding='utf-8').write(text)

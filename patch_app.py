import re

text = open('js/app.js', encoding='utf-8').read()

text = re.sub(r'\s*\{\s*id:\s*\'native_ahmedbaset\'.*?noteId:.*?\},', '', text, flags=re.DOTALL)
text = re.sub(r"label:\s*'Fawazahmed0 Edition',\s*labelId:\s*'Edisi Fawazahmed0'", r"label: 'International Numbering', labelId: 'Penomoran Internasional'", text)
text = re.sub(r"label:\s*'Lidwa Edition',\s*labelId:\s*'Edisi Lidwa'", r"label: 'Lidwa Numbering', labelId: 'Penomoran Lidwa'", text)

open('js/app.js', 'w', encoding='utf-8').write(text)

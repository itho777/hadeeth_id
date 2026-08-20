import re
text = open('kitab.html', encoding='utf-8').read()
text = re.sub(r'      <a href="topics\.html".*?Topics</a>\n', '', text)
open('kitab.html', 'w', encoding='utf-8').write(text)

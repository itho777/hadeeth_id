import re

# Fix hadith-list.html (Keep Books, remove Topics)
text = open('hadith-list.html', encoding='utf-8').read()
text = re.sub(r'\s*<a href="topics.html".*?Topics</a>\n', '\n', text)
open('hadith-list.html', 'w', encoding='utf-8').write(text)

# Fix profile-detail.html (Keep Scholars, wait, it says Books Topics? Let's check what it should be)
text = open('profile-detail.html', encoding='utf-8').read()
text = re.sub(r'\s*<a href="books.html".*?Books</a>\s*<a href="topics.html".*?Topics</a>', r'\n    <a href="scholars.html" class="hover:underline" data-i18n="nav_scholars">Scholars</a>', text)
open('profile-detail.html', 'w', encoding='utf-8').write(text)

# Fix topic-hadiths.html (Keep Topics, remove Books)
text = open('topic-hadiths.html', encoding='utf-8').read()
text = re.sub(r'\s*<a href="books.html".*?Books</a>\n', '\n', text)
open('topic-hadiths.html', 'w', encoding='utf-8').write(text)

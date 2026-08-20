import glob, re
for f in glob.glob('*.html'):
    text = open(f, encoding='utf-8').read()
    if re.search(r'data-i18n="nav_books">Books</a>\s*<a href="topics.html" class="hover:underline" data-i18n="nav_topics">Topics</a>', text):
        print(f + ' has the bug!')

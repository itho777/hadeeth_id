import glob
import re

files = glob.glob('*.html')
for f in files:
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    if 'href="topics.html"' not in content:
        # Match <a href="books.html" ... >...</a> and insert the topics link right after it!
        # There are desktop and mobile links.
        def replacer(match):
            books_link = match.group(0)
            topics_link = books_link.replace('books.html', 'topics.html').replace('nav_books', 'nav_topics').replace('>Books<', '>Topics<').replace('>Kitab<', '>Topik<').replace('data-nav-page="books.html"', 'data-nav-page="topics.html"')
            # To handle selected state correctly we might just replace text-primary with text-on-surface-variant for the new link just in case
            topics_link = topics_link.replace('text-primary dark:text-white', 'text-on-surface-variant dark:text-gray-400')
            topics_link = topics_link.replace('font-semibold', '')
            return books_link + '\n      ' + topics_link

        content = re.sub(r'<a href="books\.html".*?</a>', replacer, content)
        with open(f, 'w', encoding='utf-8') as file:
            file.write(content)

print('Updated headers in HTML files.')

import re

def add_books_link(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        html = f.read()
    
    # We will search for `<nav ...>` and inject the books link right after it
    link_html = '\n        <a href="books.html" data-nav-page="books.html" data-i18n="nav_books" class="text-on-surface-variant dark:text-gray-400 hover:text-primary dark:hover:text-white py-1 transition-colors">Books</a>'
    
    if 'href="books.html"' not in html:
        html = re.sub(r'(<nav[^>]*>)', r'\1' + link_html, html, count=1)
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"Added Books link to {filename}")

add_books_link('profile-detail.html')
add_books_link('topic-hadiths.html')

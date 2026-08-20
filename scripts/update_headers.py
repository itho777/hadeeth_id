import glob

files = glob.glob('*.html')
for f in files:
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    if 'data-i18n="nav_topics"' not in content:
        # Desktop Nav (Active)
        content = content.replace(
            '<a href="books.html" class="text-primary dark:text-white font-semibold" data-i18n="nav_kitab">Kitab</a>',
            '<a href="books.html" class="text-primary dark:text-white font-semibold" data-i18n="nav_kitab">Kitab</a>\n          <a href="topics.html" class="text-on-surface-variant dark:text-gray-400 hover:text-primary dark:hover:text-white transition-colors" data-i18n="nav_topics">Topik</a>'
        )
        # Desktop Nav (Inactive)
        content = content.replace(
            '<a href="books.html" class="text-on-surface-variant dark:text-gray-400 hover:text-primary dark:hover:text-white transition-colors" data-i18n="nav_kitab">Kitab</a>',
            '<a href="books.html" class="text-on-surface-variant dark:text-gray-400 hover:text-primary dark:hover:text-white transition-colors" data-i18n="nav_kitab">Kitab</a>\n          <a href="topics.html" class="text-on-surface-variant dark:text-gray-400 hover:text-primary dark:hover:text-white transition-colors" data-i18n="nav_topics">Topik</a>'
        )
        # Mobile Nav
        content = content.replace(
            '<a href="books.html" class="block px-4 py-3 text-on-surface hover:bg-surface-container-low dark:hover:bg-[#334155] rounded-xl font-medium" data-i18n="nav_kitab">Kitab</a>',
            '<a href="books.html" class="block px-4 py-3 text-on-surface hover:bg-surface-container-low dark:hover:bg-[#334155] rounded-xl font-medium" data-i18n="nav_kitab">Kitab</a>\n        <a href="topics.html" class="block px-4 py-3 text-on-surface hover:bg-surface-container-low dark:hover:bg-[#334155] rounded-xl font-medium" data-i18n="nav_topics">Topik</a>'
        )
        with open(f, 'w', encoding='utf-8') as file:
            file.write(content)

print('Updated headers in HTML files.')

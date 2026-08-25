
import io
import glob
import re

html_files = glob.glob("../*.html")
for filepath in html_files:
    with io.open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Fix spacing
    content = content.replace(u"gap-stack-lg", u"gap-8")
    
    # Add to desktop nav
    if u'href="glossary.html"' not in content:
        link = u'<a href="glossary.html" data-nav-page="glossary.html" data-i18n="nav_glossary" class="text-on-surface-variant dark:text-gray-400 hover:text-primary dark:hover:text-white py-1 transition-colors">Glossary</a>'
        content = re.sub(ur'(?s)(<a href="admin.html".*?>.*?</a>)', link + u'\n      \\1', content)

    # Re-apply JS fix for glossary
    if filepath.endswith("glossary.html"):
        old_js = u"""        const container = document.getElementById('glossary-container');
        document.getElementById('loading-indicator').style.display = 'none';
        container.innerHTML = '';"""
        new_js = u"""        const container = document.getElementById('glossary-container');
        const indicator = document.getElementById('loading-indicator');
        if (indicator) indicator.style.display = 'none';
        container.innerHTML = '';"""
        content = content.replace(old_js, new_js)

    with io.open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

print("Fixed HTML files successfully!")


import io
import re
import glob

# 1. Restore Glossary Management UI in admin.html
with io.open("../current_admin.html", "r", encoding="utf-8") as f:
    current_admin = f.read()

glossary_ui_match = re.search(ur'(?s)<!-- GLOSSARY MANAGEMENT SECTION -->.*<!-- END GLOSSARY MANAGEMENT SECTION -->'), current_admin)
glossary_ui = glossary_ui_match.group(0) if glossary_ui_match else u''

glossary_script_match = re.search(ur'(?s)// --- GLOSSARY MANAGEMENT LOGIC ---.*// --- END GLOSSARY MANAGEMENT LOGIC ---'), current_admin)
glossary_script = glossary_script_match.group(0) if glossary_script_match else u''

with io.open("../admin.html", "r", encoding="utf-8") as f:
    admin_content = f.read()

if glossary_ui and glossary_ui not in admin_content:
    # Insert before the last </div></main> or similar
    admin_content = admin_content.replace(u'</main>', glossary_ui + u'\n</main>')

if glossary_script and glossary_script not in admin_content:
    admin_content = admin_content.replace(u'</script>', glossary_script + u'\n</script>')

with io.open("../admin.html", "w", encoding="utf-8") as f:
    f.write(admin_content)

# 2. Re-apply index footer to all HTML files safely
with io.open("../index.html", "r", encoding="utf-8") as f:
    index_content = f.read()

footer_match = re.search(ur'(?s)(<footer.*?>.*?</footer>)', index_content)
if footer_match:
    footer = footer_match.group(1)
    # Ensure glossary link is in the footer
    if u'glossary.html' not in footer:
        link = u'<a href="glossary.html" class="hover:text-primary dark:hover:text-white transition-colors">Glossary</a>'
        footer = footer.replace(u'<a href="privacy.html"', link + u'\n        <a href="privacy.html"')

    html_files = glob.glob("../*.html")
    for filepath in html_files:
        if filepath.endswith("index.html"):
            continue
        with io.open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        content = re.sub(ur'(?s)<footer.*?>.*?</footer>', footer, content)
        with io.open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

# 3. Apply gap-8 and Glossary top nav to all HTML files
html_files = glob.glob("../*.html")
for filepath in html_files:
    with io.open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    content = content.replace(u"gap-stack-lg", u"gap-8")
    
    if u'href="glossary.html"' not in content and u'<nav' in content:
        link = u'<a href="glossary.html" data-nav-page="glossary.html" data-i18n="nav_glossary" class="text-on-surface-variant dark:text-gray-400 hover:text-primary dark:hover:text-white py-1 transition-colors">Glossary</a>'
        content = re.sub(ur'(?s)(<a href="admin.html".*?>.*?</a>)', link + u'\n      \\1', content)
    
    with io.open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

print("All fixes applied perfectly!")

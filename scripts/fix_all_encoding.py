
# -*- coding: utf-8 -*-
import io
import re
import glob
import subprocess

# get current admin html
proc = subprocess.Popen(["git", "show", "HEAD:admin.html"], stdout=subprocess.PIPE)
current_admin, _ = proc.communicate()
current_admin = current_admin.decode("utf-8")

html_pattern = ur"""(?s)(<div class="bg-surface dark:bg-\[#1e293b\] rounded-2xl shadow-sm border border-outline-variant/40 dark:border-\[#334155\] overflow-hidden mb-8">\s*<div class="p-6 border-b border-outline-variant/30 dark:border-\[#334155\]">\s*<h2 class="font-bold text-xl text-primary dark:text-white flex items-center gap-2">.*?</div>\s*</div>)"""
html_match = re.search(html_pattern, current_admin)
glossary_ui = html_match.group(1) if html_match else u''

js_pattern = ur"""(?s)(// --- Glossary Manager Logic ---.*\}\s*document\.addEventListener\('DOMContentLoaded', loadGlossaryDrafts\);\s*)"""
js_match = re.search(js_pattern, current_admin)
glossary_js = js_match.group(1) if js_match else u''

# Re-checkout to ensure completely pristine files
subprocess.call("git checkout 40c254b5e4 -- index.html admin.html books.html books2.html docs.html hadith-list.html hadith.html kitab.html master-link-viewer.html node_diagram.html privacy.html profile-detail.html sanad.html scholars.html test_hotd.html topic-hadiths.html topics-in-kitab.html topics.html", shell=True)

with io.open("../admin.html", "r", encoding="utf-8") as f:
    admin_content = f.read()

if glossary_ui:
    admin_content = admin_content.replace(u'</main>', glossary_ui + u'\n</main>')
if glossary_js:
    admin_content = admin_content.replace(u'</script>', glossary_js + u'\n</script>')

with io.open("../admin.html", "w", encoding="utf-8") as f:
    f.write(admin_content)

footer = u"""<footer class="bg-surface-container-low dark:bg-[#10141a] text-on-surface-variant dark:text-gray-400 font-label-sm text-label-sm w-full py-stack-lg px-margin-main flex flex-col md:flex-row justify-between items-center max-w-content-width-max mx-auto border-t border-outline-variant dark:border-[#1e293b] mt-12">
    <div class="text-primary dark:text-white font-bold mb-4 md:mb-0 opacity-90"><span data-i18n="footer_text">© 2026 hadeeth.id - Digital Hadith Manuscript Preservation</span></div>
    <div class="flex flex-wrap gap-4 items-center justify-center">
      <a href="https://tafseer.id" target="_blank" rel="noopener" class="hover:text-secondary dark:hover:text-[#10b981] transition-colors">tafseer.id</a>
      <a href="docs.html" class="hover:text-secondary dark:hover:text-[#10b981] transition-colors">Data Sources</a>
      <a href="privacy.html" class="hover:text-secondary dark:hover:text-[#10b981] transition-colors">Privacy Policy</a>
      <a href="glossary.html" class="hover:text-secondary dark:hover:text-[#10b981] transition-colors">Glossary</a>
    </div>
  </footer>"""

def read_file(filepath):
    try:
        with io.open(filepath, "r", encoding="utf-8-sig") as f:
            return f.read()
    except UnicodeDecodeError:
        with io.open(filepath, "r", encoding="utf-16") as f:
            return f.read()

html_files = glob.glob("../*.html")
for filepath in html_files:
    if filepath.endswith("glossary.html"):
        continue

    content = read_file(filepath)

    content = content.replace(u"gap-stack-lg", u"gap-8")

    nav_match = re.search(ur'(?s)<nav.*?>.*?</nav>', content)
    if nav_match:
        nav_content = nav_match.group(0)
        if u'href="glossary.html"' not in nav_content:
            link = u'<a href="glossary.html" data-nav-page="glossary.html" data-i18n="nav_glossary" class="text-on-surface-variant dark:text-gray-400 hover:text-primary dark:hover:text-white py-1 transition-colors">Glossary</a>'
            # replace inside the first matching <nav> block
            content = re.sub(ur'(?s)(<nav.*?>.*?)(<a href="admin.html".*?>.*?</a>)', ur'\1' + link + u'\n      \\2', content, count=1)

    content = re.sub(ur'(?s)<footer.*?>.*?</footer>', footer, content)

    with io.open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

print("Done restoring HTML files!")

with open('profile-detail.html', 'r', encoding='utf-8') as f:
    html = f.read()

target = """<script src="js/api.js?v=2026081411"></script>
<script src="js/app.js?v=2026082009"></script>
<script src="js/api.js?v=2026081411"></script>
<script src="js/app.js?v=2026082009"></script>"""

replacement = """<script src="js/api.js?v=2026081411"></script>
<script src="js/app.js?v=2026082009"></script>"""

if target in html:
    html = html.replace(target, replacement)
    with open('profile-detail.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("Fixed duplicate script tags in profile-detail.html")
else:
    # Try a regex approach in case formatting is slightly different
    import re
    html = re.sub(r'(<script src="js/api\.js[^>]+></script>\s*<script src="js/app\.js[^>]+></script>\s*){2,}', 
                  r'\1', html)
    with open('profile-detail.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("Fixed duplicate script tags in profile-detail.html via regex")

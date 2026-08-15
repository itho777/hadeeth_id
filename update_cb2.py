import os, glob, re

for html_file in glob.glob(r'g:\Box\AntigravitySync\.gemini\antigravity\scratch\hadeeth_id\*.html'):
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    new_content = re.sub(r'src="js/api\.js\?v=\d+"', 'src="js/api.js?v=2026081403"', content)
    new_content = re.sub(r'src="js/app\.js\?v=\d+"', 'src="js/app.js?v=2026081403"', new_content)
    if new_content != content:
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f'Updated {html_file}')

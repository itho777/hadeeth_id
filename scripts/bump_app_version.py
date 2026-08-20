import os

# Find all HTML files and bump app.js version
for filename in os.listdir('.'):
    if not filename.endswith('.html'): continue
    with open(filename, 'r', encoding='utf-8') as f:
        html = f.read()
    
    if 'js/app.js?v=' in html:
        import re
        html = re.sub(r'js/app.js\?v=\d+', 'js/app.js?v=2026082009', html)
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"Bumped app.js version in {filename}")


import os

# 1. Fix missing theme.js in books.html, topics.html, topics-in-kitab.html
files_to_fix = ['books.html', 'topics.html', 'topics-in-kitab.html']
for fn in files_to_fix:
    with open(fn, 'r', encoding='utf-8') as f:
        html = f.read()
    
    if '<script src="js/theme.js"></script>' not in html:
        # inject before api.js
        html = html.replace('<script src="js/api.js', '<script src="js/theme.js"></script>\n<script src="js/api.js')
        with open(fn, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"Injected theme.js into {fn}")

# 2. Fix JSON parsing in topics-in-kitab.html
with open('topics-in-kitab.html', 'r', encoding='utf-8') as f:
    html = f.read()

target = """            const topicRes = await fetch('data/api/topics_metadata.json');
            const topics = await topicRes.json();"""
            
replacement = """            const topicRes = await fetch('data/api/topics_metadata.ndjson');
            const topicText = await topicRes.text();
            const topics = topicText.trim().split('\\n').filter(l => l.trim()).map(line => JSON.parse(line));"""

if target in html:
    html = html.replace(target, replacement)
    with open('topics-in-kitab.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("Patched topics-in-kitab.html NDJSON parsing.")
else:
    print("Target not found in topics-in-kitab.html.")

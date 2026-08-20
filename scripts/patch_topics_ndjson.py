with open('topics.html', 'r', encoding='utf-8') as f:
    html = f.read()

target = """            const response = await fetch('data/api/topics_metadata.json');
            if (!response.ok) throw new Error('Failed to load topics');
            const topics = await response.json();"""

replacement = """            const response = await fetch('data/api/topics_metadata.ndjson');
            if (!response.ok) throw new Error('Failed to load topics');
            const text = await response.text();
            const topics = text.trim().split('\\n').filter(l => l.trim()).map(line => JSON.parse(line));"""

if target in html:
    html = html.replace(target, replacement)
    with open('topics.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("Patched topics.html for NDJSON.")
else:
    print("Target not found in topics.html")

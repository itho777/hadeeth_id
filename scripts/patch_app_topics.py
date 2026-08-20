with open('js/app.js', 'r', encoding='utf-8') as f:
    text = f.read()

target = """      const topicRes = await fetch('data/api/topics_metadata.json');
      const topics = await topicRes.json();"""

replacement = """      const topicRes = await fetch('data/api/topics_metadata.ndjson');
      const topicText = await topicRes.text();
      const topics = topicText.trim().split('\\n').filter(l => l.trim()).map(line => JSON.parse(line));"""

if target in text:
    text = text.replace(target, replacement)
    with open('js/app.js', 'w', encoding='utf-8') as f:
        f.write(text)
    print("Patched topics_metadata.json inside app.js loadTopicHadiths.")
else:
    print("Target not found in app.js")

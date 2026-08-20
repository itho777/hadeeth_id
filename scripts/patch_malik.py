import json
import re

# 1. Patch the JSON profile
with open('data/rawis/profiles/rawi_malik_bin_anas.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
data['generation'] = 'Collector'
with open('data/rawis/profiles/rawi_malik_bin_anas.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2)

# 2. Patch scholars.html
with open('scholars.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Replace Tabi' al-Tabi'in with Collector for Imam Malik
html = re.sub(r'id:\s*\'rawi_malik_bin_anas\',.*?generation:\s*"Tabi\' al-Tabi\'in"', lambda m: m.group(0).replace('Tabi\' al-Tabi\'in', 'Collector'), html)

with open('scholars.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("Changed Imam Malik's generation to Collector")

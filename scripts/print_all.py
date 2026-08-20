import re

html = open('scholars.html', 'r', encoding='utf-8').read()
matches = re.findall(r'id:\s*\'([^\']+)\'[\s\S]*?name_ar:\s*"([^"]+)"', html)
with open('temp.txt', 'w', encoding='utf-8') as f:
    for k, v in matches:
        f.write(f"{k} -> {v}\n")

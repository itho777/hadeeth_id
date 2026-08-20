import re
html = open('scholars.html', 'r', encoding='utf-8').read()
matches = re.finditer(r'name_ar:\s*"([^"]+)"', html)
with open('temp.txt', 'w', encoding='utf-8') as f:
    for i, m in enumerate(matches):
        if i < 5:
            f.write(m.group(1) + '\n')

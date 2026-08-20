import re
html = open('scholars.html', 'r', encoding='utf-8').read()

match = re.search(r'id:\s*\'rawi_tabarani\'.*?name_ar:\s*"([^"]+)"', html)
print("Before:", repr(match.group(0)) if match else "No match")

replaced = re.sub(r'name_ar:\s*"[^"]+"', 'name_ar: "الطبراني"', match.group(0))
print("Replaced:", repr(replaced))

html = html.replace(match.group(0), replaced)

match_after = re.search(r'id:\s*\'rawi_tabarani\'.*?name_ar:\s*"([^"]+)"', html)
print("After:", repr(match_after.group(0)) if match_after else "No match")

with open('scholars.html', 'w', encoding='utf-8') as f:
    f.write(html)

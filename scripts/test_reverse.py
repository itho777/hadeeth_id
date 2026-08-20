import re
import json

def test_reverse():
    html = open('scholars.html', 'r', encoding='utf-8').read()
    match = re.search(r'name_ar:\s*"(.*?)"', html)
    if match:
        corrupted = match.group(1)
        print("Corrupted string:", repr(corrupted))
        try:
            # Revert the corruption: encode to cp1252 (or latin1), decode to utf-8
            fixed = corrupted.encode('cp1252').decode('utf-8')
            print("Fixed:", fixed)
        except Exception as e:
            print("Could not reverse directly:", e)

test_reverse()

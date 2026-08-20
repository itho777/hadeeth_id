import os
import re

for fn in os.listdir('.'):
    if not fn.endswith('.html'): continue
    with open(fn, encoding='utf-8') as f:
        html = f.read()
    c1 = len(re.findall(r'<script src="js/api.js', html))
    c2 = len(re.findall(r'<script src="js/app.js', html))
    if c1 > 1 or c2 > 1:
        print(f"{fn}: api={c1}, app={c2}")

import glob
import re

for filename in glob.glob('*.html'):
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    new_content = re.sub(r'(app\.js|api\.js)\?v=[a-zA-Z0-9_]+', r'\1?v=20260813_05', content)
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(new_content)
        
print("Cache busters updated!")

import glob
import re
import sys

with open('index.html', 'r', encoding='utf-8') as f:
    index_html = f.read()

footer_match = re.search(r'(<footer.*?>.*?</footer>)', index_html, re.DOTALL)
if footer_match:
    footer_content = footer_match.group(1)
    
    for file in glob.glob('*.html'):
        if file == 'index.html':
            continue
            
        try:
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            new_content = re.sub(r'<footer.*?>.*?</footer>', lambda m: footer_content, content, flags=re.DOTALL)
            
            with open(file, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Updated {file}")
        except Exception as e:
            print(f"Failed to update {file}: {e}")
            
    print("Replaced footers successfully!")
else:
    print("Could not find footer in index.html")

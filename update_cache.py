import glob

html_files = glob.glob('*.html')
for file in html_files:
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    new_content = content.replace('?v=2026081706', '?v=2026082001')
    new_content = new_content.replace('?v=2026081707', '?v=2026082001')
    new_content = new_content.replace('?v=2026081801', '?v=2026082001')
    
    with open(file, 'w', encoding='utf-8') as f:
        f.write(new_content)

print(f"Updated cache busters in {len(html_files)} HTML files!")

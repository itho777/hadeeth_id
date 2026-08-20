with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
# Find the Other Collections section
pattern = r'(\s*<section[^>]*>\s*<div[^>]*>\s*<span[^>]*>collections_bookmark</span>\s*<h2[^>]*data-i18n="other_collections_title"[^>]*>Other Collections</h2>\s*</div>\s*<div[^>]*id="secondary-grid"[^>]*>\s*<!--[^>]*-->\s*</div>\s*</section>)'
matches = re.findall(pattern, text)

if len(matches) == 1:
    text = text.replace(matches[0], '')
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(text)
    print("Removed Other Collections from index.html")
else:
    print(f"Target found {len(matches)} times. Did not patch.")

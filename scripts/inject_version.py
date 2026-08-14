import os
import re

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

def inject_dropdown(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    target = r'(<!-- Breadcrumbs -->[\s\S]*?</div>)'
    replacement = r'''<div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
    \1
    <!-- Version Selector -->
    <div class="flex items-center gap-2 text-sm">
      <label for="dataset-version" class="text-on-surface-variant dark:text-gray-400 font-semibold text-xs whitespace-nowrap">Dataset:</label>
      <select id="dataset-version" class="bg-surface-container-high dark:bg-[#1e293b] border border-outline-variant/30 dark:border-[#334155] rounded-lg px-3 py-1.5 text-primary dark:text-white focus:outline-none focus:ring-2 focus:ring-secondary text-xs w-full max-w-[250px]">
        <option value="primary">Primary Architecture (Linked)</option>
        <option value="native_lidwa">Native Lidwa (Indonesian Anchor)</option>
        <option value="native_ahmedbaset">Native AhmedBaset (Strict Darussalam)</option>
      </select>
    </div>
  </div>'''

    new_content = re.sub(target, replacement, content, count=1)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
        
inject_dropdown(os.path.join(BASE_DIR, 'kitab.html'))
inject_dropdown(os.path.join(BASE_DIR, 'hadith-list.html'))
print("[+] Injected into kitab.html and hadith-list.html")

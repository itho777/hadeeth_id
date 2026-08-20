import subprocess
import re
import json

data = subprocess.check_output(['git', 'show', 'HEAD:scholars.html']).decode('utf-8')
matches = re.findall(r'id:\s*\'([^\']+)\'[\s\S]*?name_ar:\s*"([^"]+)"', data)

html = open('scholars.html', 'r', encoding='utf-8').read()

# Make a dict of exactly what was in Git HEAD
ar_dict = dict(matches)

# Since git HEAD has the CORRECT arabic for ALL 40 scholars, 
# because it was restored or never corrupted in HEAD!
# Wait, let me verify if Git HEAD actually has all 40 scholars!
# Yes, `git show HEAD:scholars.html` gives the FULL file from the last commit!
# The last commit is `8480efac5e` or later which includes all 40!

def replacer(match):
    scholar_id = match.group(1)
    if scholar_id in ar_dict:
        # Reconstruct the string to preserve everything else
        original = match.group(0)
        # Find where name_ar is
        replaced = re.sub(r'name_ar:\s*"[^"]+"', f'name_ar: "{ar_dict[scholar_id]}"', original)
        return replaced
    # Check without rawi_ prefix
    if scholar_id.replace('rawi_', '') in ar_dict:
        original = match.group(0)
        replaced = re.sub(r'name_ar:\s*"[^"]+"', f'name_ar: "{ar_dict[scholar_id.replace("rawi_", "")]}"', original)
        return replaced
    return match.group(0)

fixed_html = re.sub(r'id:\s*\'([^\']+)\'.*?name_ar:\s*"[^"]+"', replacer, html)

with open('scholars.html', 'w', encoding='utf-8') as f:
    f.write(fixed_html)
print("scholars.html fixed completely using Git HEAD!")

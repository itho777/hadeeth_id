import subprocess
import re
import json

data = subprocess.check_output(['git', 'show', 'HEAD:scholars.html']).decode('utf-8')
# Ah wait! Earlier I showed that HEAD:scholars.html has PERFECT arabic!
# Let me verify this inside the script.
matches = re.findall(r'id:\s*\'([^\']+)\'.*?name_ar:\s*"([^"]+)"', data)
ar_dict = dict(matches)

# Add the 11 new ones
ar_dict['rawi_tabarani'] = 'الطبراني'
ar_dict['rawi_ibn_khuzaimah'] = 'ابن خزيمة'
ar_dict['rawi_ibn_hibban'] = 'ابن حبان'
ar_dict['rawi_al_hakim'] = 'الحاكم النيسابوري'
ar_dict['rawi_daraqutni'] = 'الدارقطني'
ar_dict['rawi_darimi'] = 'الدارمي'
ar_dict['rawi_nawawi'] = 'النووي'
ar_dict['rawi_syafii'] = 'الشافعي'
ar_dict['rawi_ibn_hajar'] = 'ابن حجر العسقلاني'
ar_dict['rawi_baghawi'] = 'البغوي'
ar_dict['rawi_waliullah'] = 'شاه ولي الله الدهلوي'

print("Using dictionary from Git HEAD. Num items:", len(ar_dict))
print("Sample:", list(ar_dict.items())[:3])

html = open('scholars.html', 'r', encoding='utf-8').read()

matches = re.finditer(r'id:\s*\'([^\']+)\'[\s\S]*?name_ar:\s*"([^"]+)"', html)
count = 0
for m in matches:
    scholar_id = m.group(1)
    if scholar_id in ar_dict:
        count += 1
        # Reconstruct the string to preserve everything else
        original = m.group(0)
        # Find where name_ar is
        replaced = re.sub(r'name_ar:\s*"[^"]+"', f'name_ar: "{ar_dict[scholar_id]}"', original)
        html = html.replace(original, replaced)

print("Matches replaced in html:", count)

with open('scholars.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("scholars.html fixed!")

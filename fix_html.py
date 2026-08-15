import sys
with open(r'g:\Box\AntigravitySync\.gemini\antigravity\scratch\hadeeth_id\profile-detail.html', 'r', encoding='utf-8') as f:
    text = f.read()

script_start = text.find('<script>\n  const supabaseUrl')
script_end = text.find('</script>', script_start) + 9

new_script = '<script src="js/api.js?v=2026081411"></script>\n<script src="js/app.js?v=2026081411"></script>\n'

if script_start != -1:
    new_text = text[:script_start] + new_script + text[script_end:]
    with open(r'g:\Box\AntigravitySync\.gemini\antigravity\scratch\hadeeth_id\profile-detail.html', 'w', encoding='utf-8') as f:
        f.write(new_text)
    print('Replaced inline script with api.js and app.js')
else:
    print('Could not find script block')

import re
import sys
sys.stdout.reconfigure(encoding='utf-8')
with open(r'g:\Box\AntigravitySync\.gemini\antigravity\scratch\hadeeth_id\scratch\irsyadulibad_db\shahih-bukhari.sql', encoding='utf-8') as f:
    content = f.read()

pattern = r"\(\s*'?(\d+)'?,\s*'shahih_bukhari',\s*'(.*?)',\s*'(.*?)'\)"
matches = re.findall(pattern, content, re.DOTALL)
lidwa_trans = {int(m[0]): m[2] for m in matches}
lidwa_arab = {int(m[0]): m[1] for m in matches}

print('Lidwa #1189 Indo:', lidwa_trans.get(1189, 'Not found')[:100].replace('\n',' '))
print('Lidwa #1189 Arab:', lidwa_arab.get(1189, 'Not found')[:100].replace('\n',' '))

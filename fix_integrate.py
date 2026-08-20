import re
text = open('scripts/integrate_mjna.py', encoding='utf-8').read()
text = re.sub(r"\s*'daruquthni'.*?,?\n", "\n", text)
text = text.replace("'daruquthni', ", "")
text = text.replace("        'daruquthni': 'Sunan Daruquthni ({BOOKS['daruquthni']['count']})',\n", "")
open('scripts/integrate_mjna.py', 'w', encoding='utf-8').write(text)

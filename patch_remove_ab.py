
text = open('scripts/3c_build.py', encoding='utf-8').read()
import re
text = re.sub(r'\s*# Ahmedbaset Fallbacks.*?# Gradings', '\n                # Gradings', text, flags=re.DOTALL)
open('scripts/3c_build.py', 'w', encoding='utf-8').write(text)


import io
import re

with io.open("js/app.js", "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace("Ac 2026 hadeeth.id", u"\u00A9 2026 hadeeth.id")
content = content.replace(u"\u00C2\u00A9 2026", u"\u00A9 2026")

with io.open("js/app.js", "w", encoding="utf-8") as f:
    f.write(content)

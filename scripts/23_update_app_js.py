import os
import re

APP_JS_PATH = "js/app.js"

with open(APP_JS_PATH, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace fetchChunkedJson with fetchNdjsonFull for lidwa
content = re.sub(
    r"window\.HadeethAPI\.fetchChunkedJson\(`\$\{baseUrl\}/sources/lidwa/\$\{bookId\}\.json`\)",
    r"window.HadeethAPI.fetchNdjsonFull('sources/lidwa', bookId)",
    content
)

content = re.sub(
    r"window\.HadeethAPI\.fetchChunkedJson\(`data/sources/lidwa/\$\{bookId\}\.json`\)",
    r"window.HadeethAPI.fetchNdjsonFull('sources/lidwa', bookId)",
    content
)

with open(APP_JS_PATH, 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated js/app.js")

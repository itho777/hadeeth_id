import os

APP_JS_PATH = "js/app.js"

with open(APP_JS_PATH, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the specific UI banner text
content = content.replace(
    "(dicocokkan berdasarkan nomor hadits)",
    "(dicocokkan berdasarkan algoritma kecocokan teks Arab pada hadits)"
)

# Replace the note in metadata
content = content.replace(
    "matched by hadith number",
    "matched using Arabic text similarity"
)

content = content.replace(
    "dicocokkan berdasarkan nomor",
    "dicocokkan berdasarkan algoritma kecocokan teks Arab"
)

with open(APP_JS_PATH, 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated app.js texts")

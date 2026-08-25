import io
import re

with io.open('../js/app.js', 'r', encoding='utf-8') as f:
    js = f.read()

# Fix LastReadTracker
js = js.replace(
    "  if (window.LastReadTracker) window.LastReadTracker.save(bookId, data.hadith_number, bookName, `${bookName} Hadith #${data.hadith_number}`);",
    "  if (window.LastReadTracker) window.LastReadTracker.save(bookId, displayNum, bookName, `${bookName} Hadith #${displayNum}`);"
)

with io.open('../js/app.js', 'w', encoding='utf-8') as f:
    f.write(js)

print("Fixed LastReadTracker logic in app.js")
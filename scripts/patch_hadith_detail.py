with open('js/app.js', 'r', encoding='utf-8') as f:
    app_js = f.read()

# 1. Remove the line that skips 'ind-' for core9 books
app_js = app_js.replace(
    "if (core9.includes(bookId) && ed.name.startsWith('ind-')) return; // We use Lidwa for ID for 9 core books",
    "// Removed skip for ind- because we baked them"
)

# 2. Rename the label for ind- editions so it says 'ID - Lidwa (Baked)' instead of 'ID - Fawazahmed0'
old_label_logic = "const author = ed.author !== 'Unknown' ? ed.author : 'Fawazahmed0';"
new_label_logic = """let author = ed.author !== 'Unknown' ? ed.author : 'Fawazahmed0';
          if (ed.name.startsWith('ind-') && core9.includes(bookId)) author = 'Lidwa / Irsyad';"""
app_js = app_js.replace(old_label_logic, new_label_logic)

with open('js/app.js', 'w', encoding='utf-8') as f:
    f.write(app_js)

print("Patched app.js for hadith.html dropdown!")

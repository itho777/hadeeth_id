with open('js/app.js', 'r', encoding='utf-8') as f:
    app_js = f.read()

# Make it ALWAYS load the link graphs and fallbacks since indEd might just be a stub
app_js = app_js.replace("if (!indEd) {", "if (true) {")

with open('js/app.js', 'w', encoding='utf-8') as f:
    f.write(app_js)
print("Patched app.js to always load Lidwa graph.")

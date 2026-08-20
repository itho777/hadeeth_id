with open('js/app.js', 'r', encoding='utf-8') as f:
    app_js = f.read()

old = "const defaultId = translationOptions.find(o => o.id === 'mjna-id') || translationOptions.find(o => o.id === 'lidwa-id') || translationOptions[0];"
new = "const defaultId = translationOptions.find(o => o.id === 'mjna-id') || translationOptions.find(o => o.id === 'lidwa-id') || translationOptions.find(o => o.lang === 'Indonesian') || translationOptions[0];"
app_js = app_js.replace(old, new)

with open('js/app.js', 'w', encoding='utf-8') as f:
    f.write(app_js)
print("Patched defaultId fallback logic.")

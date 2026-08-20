with open('js/app.js', 'r', encoding='utf-8') as f:
    app_js = f.read()

app_js = app_js.replace("const namesEn = reversedRawis.map(r => r.name_en || r.ar);",
                        "const namesEn = reversedRawis.map(r => r.name_en || r.name || r.ar || r.id);")
app_js = app_js.replace("const namesId = reversedRawis.map(r => r.name_id || r.ar);",
                        "const namesId = reversedRawis.map(r => r.name_id || r.name || r.ar || r.id);")

with open('js/app.js', 'w', encoding='utf-8') as f:
    f.write(app_js)
print("Patched sanad rawis extraction.")

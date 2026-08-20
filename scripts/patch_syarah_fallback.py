with open('js/app.js', 'r', encoding='utf-8') as f:
    app_js = f.read()

app_js = app_js.replace("let textExp = data[`explanation_${lang}`] || data[`explanation_en`] || '';",
                        "let textExp = data[`explanation_${lang}`] || data[`explanation_en`] || data[`syarah_${lang}`] || data[`syarah_ar`] || '';")

with open('js/app.js', 'w', encoding='utf-8') as f:
    f.write(app_js)
print("Patched syarah text fallback.")

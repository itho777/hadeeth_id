with open('js/app.js', 'r', encoding='utf-8') as f:
    app_js = f.read()

app_js = app_js.replace("} else if (resolvedDataset === 'native_lidwa') {",
                        "} else if (resolvedDataset === 'native_lidwa' || resolvedDataset === 'native_mjna' || resolvedDataset === 'native_irsyad') {")

with open('js/app.js', 'w', encoding='utf-8') as f:
    f.write(app_js)
print("Patched branches.")

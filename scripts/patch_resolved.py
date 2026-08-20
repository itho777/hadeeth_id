with open('js/app.js', 'r', encoding='utf-8') as f:
    app_js = f.read()

app_js = app_js.replace("const resolvedDataset = validDs ? activeDataset : 'primary';",
                        "const resolvedDataset = validDs ? activeDataset : (dsConfig.length > 0 ? dsConfig[0].id : 'fawazahmed');")

with open('js/app.js', 'w', encoding='utf-8') as f:
    f.write(app_js)
print("Patched.")

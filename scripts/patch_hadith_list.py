with open('js/app.js', 'r', encoding='utf-8') as f:
    app_js = f.read()

# Replace the branch condition
app_js = app_js.replace("} else if (activeDataset === 'native_lidwa') {",
                        "} else if (activeDataset === 'native_lidwa' || activeDataset === 'native_mjna' || activeDataset === 'native_irsyad') {")

# Replace the nativeSourceDir logic
old_logic = """      const mjnaBooks = ['ibnukhuzaimah', 'ibnuhibban', 'mustadrak', 'daruquthni'];
      const isMjnaBook = mjnaBooks.includes(bookId);
      const nativeSourceDir = isMjnaBook ? 'sources/mjna' : 'sources/lidwa';
      const nativeSourceLabel = isMjnaBook ? 'MJNA.or.id' : 'Lidwa';"""

new_logic = """      const mjnaBooks = ['ibnukhuzaimah', 'ibnuhibban', 'mustadrak', 'daruquthni'];
      const irsyadBooks = ['syafii', 'riyad_arab'];
      const isMjnaBook = mjnaBooks.includes(bookId);
      const isIrsyadBook = irsyadBooks.includes(bookId);
      let nativeSourceDir = 'sources/lidwa';
      let nativeSourceLabel = 'Lidwa';
      if (isMjnaBook) {
        nativeSourceDir = 'sources/mjna';
        nativeSourceLabel = 'MJNA.or.id';
      } else if (isIrsyadBook) {
        nativeSourceDir = 'sources/irsyadulibad';
        nativeSourceLabel = 'IrsyadulIbad';
      }"""

app_js = app_js.replace(old_logic, new_logic)

with open('js/app.js', 'w', encoding='utf-8') as f:
    f.write(app_js)
print("Patched.")

import io

with io.open('../js/app.js', 'r', encoding='utf-8') as f:
    js = f.read()

old_logic = "if (opt.source.startsWith('eng-') || window.fawazEditions?.[bookId]?.['eng']?.find(e => e.name === opt.source)) isMismatchRisk = true;"
new_logic = "if (opt.source !== 'lidwa_id' && opt.source !== 'lidwa_en' && opt.source !== 'ab' && opt.source !== 'ara-' + bookId) isMismatchRisk = true;"

js = js.replace(old_logic, new_logic)

with io.open('../js/app.js', 'w', encoding='utf-8') as f:
    f.write(js)

print("Updated logic in app.js")
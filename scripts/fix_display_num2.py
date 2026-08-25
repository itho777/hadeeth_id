import io
import re

with io.open('../js/app.js', 'r', encoding='utf-8') as f:
    js = f.read()

# Fix displayNum logic
js = js.replace(
    "const displayNum = (localStorage.getItem('numbering_system') === 'lidwa' && data.lidwa_id) ? data.lidwa_id : data.hadith_number;",
    "const displayNum = (activeDataset === 'native_lidwa' && data.lidwa_id) ? data.lidwa_id : ((activeDataset === 'native_ahmedbaset' && data.ab_id) ? data.ab_id : (data.hadith_number || data.id));"
)

with io.open('../js/app.js', 'w', encoding='utf-8') as f:
    f.write(js)

print("Fixed displayNum logic in app.js")
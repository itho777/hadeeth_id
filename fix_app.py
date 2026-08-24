import os

with open("js/app.js", "r", encoding="utf-8") as f:
    content = f.read()

# Fix the first replacement
bad_str = "let displayNum = data.id || data.hadith_number; if (data.lidwa_id && Array.isArray(data.lidwa_id) && data.lidwa_id.length > 0) { displayNum +=  (Native: ); } else if (data.lidwa_id) { displayNum +=  (Native: ); }"
good_str = "let displayNum = data.id || data.hadith_number; if (data.lidwa_id && Array.isArray(data.lidwa_id) && data.lidwa_id.length > 0) { displayNum += ' (Lidwa: ' + data.lidwa_id.join(', ') + ')'; } else if (data.lidwa_id) { displayNum += ' (Lidwa: ' + data.lidwa_id + ')'; }"

content = content.replace(bad_str, good_str)

# Fix the second replacement inside pageItems (topic/chapters pagination)
old_page_items = "const displayNum = (localStorage.getItem('numbering_system') === 'lidwa' && item.lidwa_id) ? item.lidwa_id : num;"
new_page_items = "let displayNum = item.id || num; if (item.lidwa_id && Array.isArray(item.lidwa_id) && item.lidwa_id.length > 0) { displayNum += ' (Lidwa: ' + item.lidwa_id.join(', ') + ')'; } else if (item.lidwa_id) { displayNum += ' (Lidwa: ' + item.lidwa_id + ')'; }"

content = content.replace(old_page_items, new_page_items)

# Fix the `num` variable that is passed to the anchor links in pageItems!
# Wait, `num` is what is used in the href: `<a href="hadith.html?book=${bookId}&id=${num}"`
# If we pass `num = item.id || num`, it will route perfectly!
# Let's change `const num = item.hadith_number || (startIdx + idx + 1);` to `const num = item.id || item.hadith_number || (startIdx + idx + 1);`
content = content.replace("const num = item.hadith_number || (startIdx + idx + 1);", "const num = item.id || item.hadith_number || (startIdx + idx + 1);")

with open("js/app.js", "w", encoding="utf-8") as f:
    f.write(content)
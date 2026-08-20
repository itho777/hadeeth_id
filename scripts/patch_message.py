with open('js/app.js', 'r', encoding='utf-8') as f:
    app_js = f.read()

old_msg = "(dicocokkan berdasarkan algoritma kecocokan teks Arab pada hadits)"
new_msg = "(dicocokkan berdasarkan tabel relasi/mapping metadata)"
app_js = app_js.replace(old_msg, new_msg)

# Also for the AhmedBaset warning
old_msg2 = "matched by using Arabic Hadith text matching algoritm"
new_msg2 = "matched using the relational metadata map"
app_js = app_js.replace(old_msg2, new_msg2)

with open('js/app.js', 'w', encoding='utf-8') as f:
    f.write(app_js)
print("Patched info messages.")

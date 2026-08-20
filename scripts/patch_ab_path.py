with open('js/app.js', 'r', encoding='utf-8') as f:
    app_js = f.read()

ab_map_old = "const abBookMap = { ahmad: 'ahmed' };"
ab_map_new = """const abBookMap = { 
      ahmad: 'the_9_books/ahmed',
      bukhari: 'the_9_books/bukhari',
      muslim: 'the_9_books/muslim',
      abudawud: 'the_9_books/abudawud',
      tirmidhi: 'the_9_books/tirmidhi',
      nasai: 'the_9_books/nasai',
      ibnmajah: 'the_9_books/ibnmajah',
      malik: 'the_9_books/malik',
      darimi: 'the_9_books/darimi',
      nawawi: 'forties/nawawi40',
      qudsi: 'forties/qudsi40',
      dehlawi: 'forties/shahwaliullah40',
      riyad: 'other_books/riyad_assalihin',
      shamail: 'other_books/shamail_muhammadiyah',
      bulugh: 'other_books/bulugh_almaram',
      adab: 'other_books/aladab_almufrad',
      mishkat: 'other_books/mishkat_almasabih'
    };"""

app_js = app_js.replace(ab_map_old, ab_map_new)

# Replace the fetch URLs
app_js = app_js.replace("sources/ahmedbaset/by_book/the_9_books/${abBook}.json",
                        "sources/ahmedbaset/by_book/${abBook}.json")
app_js = app_js.replace("sources/ahmedbaset/by_chapter/the_9_books/${abBook}/${chapterId}.json",
                        "sources/ahmedbaset/by_chapter/${abBook}/${chapterId}.json")

with open('js/app.js', 'w', encoding='utf-8') as f:
    f.write(app_js)
print("Patched AhmedBaset paths.")

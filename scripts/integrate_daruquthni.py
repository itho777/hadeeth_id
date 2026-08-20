import json, os, re

BOOKS = {
    'daruquthni': {'name': 'Sunan Daruquthni', 'count': 4790, 'desc': 'Koleksi hadits sunan dari Imam Ad-Daruquthni.', 'icon': 'menu_book'}
}

for book, info in BOOKS.items():
    print(f"Integrating {book}...")
    # 1. Process NDJSON
    in_file = f'data/sources/mjna/{book}.ndjson'
    out_file = f'data/api/{book}.ndjson'
    
    if not os.path.exists(in_file):
        print(f"Missing {in_file}, skipping...")
        continue
        
    index = {'number': {}, 'chapter': {}}
    offsets = []
    current_offset = 0
    
    # Needs sorting since asyncio could be out of order
    lines = []
    with open(in_file, 'r', encoding='utf-8') as fin:
        for line in fin:
            lines.append(json.loads(line))
            
    lines.sort(key=lambda x: x['hadith_number'])
    
    with open(out_file, 'w', encoding='utf-8') as fout:
        for data in lines:
            data['id'] = str(data['hadith_number'])
            data['chapter_id'] = "1"
            data['text_en'] = ""
            
            new_line = json.dumps(data, ensure_ascii=False) + '\n'
            
            offsets.append((current_offset, len(new_line)))
            current_offset += len(new_line)
            fout.write(new_line)
            
            hadith_no = str(data['id'])
            chap_no = str(data['chapter_id'])
            
            index['number'][hadith_no] = offsets[-1]
            if chap_no not in index['chapter']:
                index['chapter'][chap_no] = []
            index['chapter'][chap_no].append(offsets[-1])
            
    # 2. Write Index
    with open(f'data/api/{book}_ndjson_index.json', 'w', encoding='utf-8') as f:
        json.dump(index, f)
        
    # 3. Write Chapter Data
    ch = {
      'title_en_source': 'MJNA',
      'title_id_source': 'MJNA',
      'chapters': [{
          'chapter_id': '1',
          'title_en': info['name'],
          'title_id': info['name'],
          'title_ar': info['name'], # Optional, can just use the indonesian name
          'hadith_range': f"1-{info['count']}",
          'count': info['count']
      }]
    }
    with open(f'data/lidwa-chapters/{book}.json', 'w', encoding='utf-8') as f:
        json.dump(ch, f, indent=2, ensure_ascii=False)

# 4. Update books_v2.json
books_meta = json.load(open('data/books_v2.json', encoding='utf-8'))
existing = {b['id'] for b in books_meta}
for book, info in BOOKS.items():
    if book not in existing:
        books_meta.append({
            'id': book,
            'name': info['name'],
            'nameId': info['name'],
            'count': info['count'],
            'description': info['desc'],
            'descriptionId': info['desc'],
            'icon': info['icon']
        })
with open('data/books_v2.json', 'w', encoding='utf-8') as f:
    json.dump(books_meta, f, indent=2, ensure_ascii=False)

# 5. Update app.js BOOK_DATASETS
app_js = open('js/app.js', encoding='utf-8').read()
new_datasets = []
for book, info in BOOKS.items():
    if f"  {book}: [" not in app_js:
        new_datasets.append(f"""  {book}: [
    {{ id: 'native_lidwa',
      label: 'MJNA Edition', labelId: 'Edisi MJNA',
      sources: 'AR/ID: MJNA ({info['count']} entries)',
      sourcesId: 'AR/ID: MJNA ({info['count']} entri)',
      note: 'Dataset {info['name']} berasal dari mjna.or.id', noteId: 'Dataset {info['name']} berasal dari mjna.or.id' }}
  ]""")

if new_datasets:
    insertion = ",\n" + ",\n".join(new_datasets)
    app_js = re.sub(
        r'(  mustadrak: \[\s*\{.*?\}\s*\]\s*)\};',
        r'\1' + insertion + r'\n};',
        app_js,
        flags=re.DOTALL
    )
    
    # Also add them to validBooksWithNote
    for book in BOOKS:
        if f"'{book}'" not in app_js:
            app_js = app_js.replace(
                "const validBooksWithNote = ['bukhari', 'muslim', 'syafii', 'ibnukhuzaimah', 'ibnuhibban', 'mustadrak'];",
                f"const validBooksWithNote = ['bukhari', 'muslim', 'syafii', 'ibnukhuzaimah', 'ibnuhibban', 'mustadrak', 'daruquthni'];"
            )
            app_js = app_js.replace(
                "'mustadrak': 'Mustadrak Al-Hakim (673)'",
                f"'mustadrak': 'Mustadrak Al-Hakim (673)',\n        'daruquthni': 'Sunan Daruquthni ({BOOKS['daruquthni']['count']})'"
            )
            break

open('js/app.js', 'w', encoding='utf-8').write(app_js)

# 6. Update index.html
html = open('index.html', encoding='utf-8').read()
html_additions = []
dropdown_additions = []
for book, info in BOOKS.items():
    if f'value="{book}"' not in html:
        dropdown_additions.append(f'<option value="{book}">{info["name"]}</option>')
        html_additions.append(f'''        <a href="hadith-list.html?book={book}" class="bg-surface dark:bg-[#1e293b] border border-outline-variant/30 dark:border-[#334155] rounded-xl p-5 hover:shadow-md transition-all group flex flex-col justify-between h-full">
          <div>
            <div class="flex items-center gap-3 mb-3">
              <div class="w-10 h-10 rounded-full bg-secondary/10 dark:bg-[#10b981]/20 flex items-center justify-center text-secondary dark:text-[#10b981] group-hover:bg-secondary group-hover:text-white dark:group-hover:bg-[#10b981] dark:group-hover:text-black transition-colors">
                <span class="material-symbols-outlined">{info["icon"]}</span>
              </div>
              <h3 class="font-bold text-lg text-primary dark:text-white" data-lang-en="{info["name"]}" data-lang-id="{info["name"]}">{info["name"]}</h3>
            </div>
            <p class="text-sm text-outline dark:text-gray-400 mb-4" data-lang-en="{info["desc"]}" data-lang-id="{info["desc"]}">{info["desc"]}</p>
          </div>
          <div class="flex justify-between items-center text-xs font-semibold">
            <span class="text-secondary dark:text-[#10b981]" data-lang-en="{info["count"]} Ahadith" data-lang-id="{info["count"]} Hadits">{info["count"]} Hadits</span>
            <span class="material-symbols-outlined text-outline dark:text-gray-500 group-hover:text-secondary dark:group-hover:text-[#10b981] transition-colors">arrow_forward</span>
          </div>
        </a>''')

if html_additions:
    mustadrak_card = r'data-lang-id="Mustadrak Al-Hakim">Mustadrak Al-Hakim</h3>\s*</div>\s*<p class="text-sm.*?</a>'
    m = re.search(mustadrak_card, html, re.DOTALL)
    if m:
        html = html.replace(m.group(0), m.group(0) + '\n' + '\n'.join(html_additions))
    
    html = html.replace('<option value="mustadrak">Mustadrak Al-Hakim</option>', '<option value="mustadrak">Mustadrak Al-Hakim</option>\n            ' + '\n            '.join(dropdown_additions))
    
    open('index.html', 'w', encoding='utf-8').write(html)

print("Done integrating Daruquthni!")

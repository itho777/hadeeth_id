import json

with open('data/books_v2.json', 'r', encoding='utf-8') as f:
    books = json.load(f)

for b in books:
    if b['id'] == 'ibnukhuzaimah':
        b['title_ar'] = 'صحيح ابن خزيمة'
    elif b['id'] == 'ibnuhibban':
        b['title_ar'] = 'صحيح ابن حبان'
    elif b['id'] == 'mustadrak':
        b['title_ar'] = 'مستدرك الحاكم'
    elif b['id'] == 'daruquthni':
        b['title_ar'] = 'سنن الدارقطني'

with open('data/books_v2.json', 'w', encoding='utf-8') as f:
    json.dump(books, f, ensure_ascii=False, indent=2)

print("Updated books_v2.json metadata with correct Arabic!")

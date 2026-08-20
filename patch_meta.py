import json

with open('data/books_v2.json', 'r', encoding='utf-8') as f:
    books = json.load(f)

for b in books:
    if b['id'] == 'ibnukhuzaimah':
        b['title_ar'] = '???? ??? ?????'
        b['author_en'] = 'Imam Ibnu Khuzaimah'
        b['author_id'] = 'Imam Ibnu Khuzaimah'
    elif b['id'] == 'ibnuhibban':
        b['title_ar'] = '???? ??? ????'
        b['author_en'] = 'Imam Ibnu Hibban'
        b['author_id'] = 'Imam Ibnu Hibban'
    elif b['id'] == 'mustadrak':
        b['title_ar'] = '?????? ??????'
        b['author_en'] = 'Imam Al-Hakim'
        b['author_id'] = 'Imam Al-Hakim'
    elif b['id'] == 'daruquthni':
        b['title_ar'] = '??? ?????????'
        b['author_en'] = 'Imam Ad-Daruquthni'
        b['author_id'] = 'Imam Ad-Daruquthni'

with open('data/books_v2.json', 'w', encoding='utf-8') as f:
    json.dump(books, f, ensure_ascii=False, indent=2)

print("Updated books_v2.json metadata!")

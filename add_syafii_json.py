import json
books = json.load(open('data/books_v2.json', encoding='utf-8'))
books.append({
    'id': 'syafii',
    'name': "Musnad Syafi'i",
    'nameId': "Musnad Syafi'i",
    'count': 1800,
    'description': "The famous collection attributed to Imam Al-Shafi'i.",
    'descriptionId': "Koleksi hadits musnad dari Imam As-Syafi'i.",
    'icon': 'menu_book'
})
with open('data/books_v2.json', 'w', encoding='utf-8') as f:
    json.dump(books, f, indent=2, ensure_ascii=False)

import json
import os

books_path = 'data/books_v2.json'
with open(books_path, 'r', encoding='utf-8') as f:
    books = json.load(f)

# check if already exists
if not any(b['id'] == 'tabarani' for b in books):
    books.append({
        'id': 'tabarani',
        'title_ar': 'المعجم الكبير',
        'title_en': 'Al-Mu\'jam al-Kabir',
        'title_id': 'Mu\'jam al-Kabir',
        'author_ar': 'الطبراني',
        'author_en': 'Imam At-Tabarani',
        'author_id': 'Imam At-Tabarani',
        'death_year_ah': 360,
        'total_hadiths': 21850,
        'total_chapters': 1,
        'grade_summary': 'Mixed',
        'order_index': 18,
        'editions': ['ara-tabarani']
    })
    with open(books_path, 'w', encoding='utf-8') as f:
        json.dump(books, f, indent=2, ensure_ascii=False)
    print("Updated books_v2.json")

edits_path = 'data/meta/fawaz_editions.json'
with open(edits_path, 'r', encoding='utf-8') as f:
    edits = json.load(f)

if 'tabarani' not in edits:
    edits['tabarani'] = {
        'name': 'Mu\'jam al-Kabir',
        'collection': [
            {
                'name': 'ara-tabarani',
                'book': 'tabarani',
                'author': 'OpenITI',
                'language': 'Arabic',
                'has_sections': True,
                'direction': 'rtl',
                'source': 'OpenITI',
                'comments': '',
                'link': '',
                'linkmin': ''
            }
        ],
        'editions': [
            {
                'name': 'ara-tabarani',
                'book': 'tabarani',
                'author': 'OpenITI',
                'language': 'Arabic',
                'has_sections': True,
                'direction': 'rtl',
                'source': 'OpenITI',
                'comments': '',
                'link': '',
                'linkmin': ''
            }
        ]
    }
    with open(edits_path, 'w', encoding='utf-8') as f:
        json.dump(edits, f, indent=2, ensure_ascii=False)
    print("Updated fawaz_editions.json")

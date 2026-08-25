# -*- coding: utf-8 -*-
import json, codecs

with codecs.open("check_ab_chap.txt", "w", "utf-8") as out:
    with open("../data/sources/ahmedbaset/by_book/the_9_books/muslim.json", "r") as f:
        data = json.load(f)
        
    books = {}
    for h in data.get('hadiths', []):
        book_id = h.get('book', {}).get('book_id')
        if book_id not in books:
            books[book_id] = {
                'name': h.get('book', {}).get('book_name', ''),
                'hadith_start': h.get('idInBook'),
                'hadith_end': h.get('idInBook'),
                'count': 1
            }
        else:
            books[book_id]['hadith_end'] = h.get('idInBook')
            books[book_id]['count'] += 1
            
    for b_id in sorted(books.keys())[:10]:
        name = books[b_id]['name']
        start = books[b_id]['hadith_start']
        end = books[b_id]['hadith_end']
        count = books[b_id]['count']
        out.write("Book " + str(b_id) + ": " + name + " | Hadiths: " + str(start) + " to " + str(end) + " (" + str(count) + " total chains)\n")
# -*- coding: utf-8 -*-
import json, codecs

with codecs.open("check_ab_struct.txt", "w", "utf-8") as out:
    with open("../data/sources/ahmedbaset/by_book/the_9_books/muslim.json", "r") as f:
        data = json.load(f)
        
    books = {}
    for h in data.get('hadiths', []):
        chapter_id = h.get('chapterId')
        # Wait, the structure had "book" -> book_id, book_name? No, let's look at the actual hadith keys
        book_info = h.get('book', {})
        b_name = book_info.get('book_name', '') if isinstance(book_info, dict) else ''
        
        # AhmedBaset sometimes has chapterId, but does it map to "Book of Faith", "Book of Purification"?
        # Let's group by whatever increments linearly and matches the 56 books!
        if chapter_id not in books:
            books[chapter_id] = {
                'start': h.get('idInBook'),
                'count': 1,
                'name': b_name,
                'first_text': h.get('english', {}).get('text', '')[:50]
            }
        else:
            books[chapter_id]['count'] += 1
            
    for cid in sorted(books.keys())[:15]:
        b = books[cid]
        out.write("ChapterId " + str(cid) + " | Start: " + str(b['start']) + " | Count: " + str(b['count']) + " | " + b['first_text'].replace('\n', ' ') + "\n")
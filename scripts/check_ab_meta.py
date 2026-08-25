# -*- coding: utf-8 -*-
import json, codecs

with codecs.open("check_ab_meta.txt", "w", "utf-8") as out:
    with open("../data/sources/ahmedbaset/by_book/the_9_books/muslim.json", "r") as f:
        data = json.load(f)
        
    out.write(json.dumps(data.get('metadata', {}))[:500] + "\n")
    
    # Check the first few hadiths to see if they have chapter or book info
    for h in data.get('hadiths', [])[:2]:
        out.write(json.dumps(h, indent=2)[:500] + "\n")
    
    # Let's find hadiths that DO have book_id
    for h in data.get('hadiths', []):
        b = h.get('book')
        if b and b.get('book_id'):
            out.write("Found a valid book info at hadith " + str(h.get('idInBook')) + ": " + json.dumps(b) + "\n")
            break
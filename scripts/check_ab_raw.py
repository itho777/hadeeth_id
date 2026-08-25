# -*- coding: utf-8 -*-
import json, codecs

with codecs.open("check_ab_raw.txt", "w", "utf-8") as out:
    with open("../data/sources/ahmedbaset/by_book/the_9_books/muslim.json", "r") as f:
        data = json.load(f)
    out.write("Total Ahmedbaset hadiths: " + str(len(data['hadiths'])) + "\n")
    for h in data['hadiths'][:5]:
        out.write("ID: " + str(h.get('idInBook')) + " | " + h.get('english', {}).get('text', '')[:100].replace('\n', ' ') + "\n")
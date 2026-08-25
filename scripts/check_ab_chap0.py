# -*- coding: utf-8 -*-
import json, codecs
with codecs.open("check_ab_chap0.txt", "w", "utf-8") as out:
    with open("../data/sources/ahmedbaset/by_book/the_9_books/muslim.json", "r") as f:
        data = json.load(f)
    for h in data.get('hadiths', []):
        if h.get('idInBook') == 7369:
            out.write("Found 7369:\n")
            out.write(json.dumps(h, indent=2) + "\n")
            break
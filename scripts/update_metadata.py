import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
CHAPTERS_OUT = os.path.join(BASE_DIR, "data", "chapters")
BOOKS_V2 = os.path.join(BASE_DIR, "data", "books_v2.json")

with open(BOOKS_V2, "r", encoding="utf-8") as f:
    books = json.load(f)

for b in books:
    b_id = b["id"]
    c_path = os.path.join(CHAPTERS_OUT, f"{b_id}.json")
    if os.path.exists(c_path):
        with open(c_path, "r", encoding="utf-8") as fc:
            chaps = json.load(fc)
            if isinstance(chaps, dict): chaps = chaps.get("chapters", [])
            if chaps:
                b["hadiths_count"] = chaps[-1].get("hadith_end", 0)

with open(BOOKS_V2, "w", encoding="utf-8") as f:
    json.dump(books, f, indent=2, ensure_ascii=False)
    
print("Updated books_v2.json")
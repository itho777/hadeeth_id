import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
BOOKS_V2 = os.path.join(BASE_DIR, "data", "books_v2.json")
API_DIR = os.path.join(BASE_DIR, "data", "api")

with open(BOOKS_V2, "r", encoding="utf-8") as f:
    books = json.load(f)

for b in books:
    b_id = b["id"]
    api_path = os.path.join(API_DIR, f"{b_id}.ndjson")
    if os.path.exists(api_path):
        with open(api_path, "r", encoding="utf-8") as f_api:
            count = sum(1 for line in f_api if line.strip())
            b["hadiths_count"] = count

with open(BOOKS_V2, "w", encoding="utf-8") as f:
    json.dump(books, f, indent=2, ensure_ascii=False)
    
print("Updated books_v2.json counts based on actual API entries!")
import json
with open("../data/books_v2.json", "r") as f:
    books = json.load(f)
for b in books:
    if b['id'] == 'muslim':
        print(json.dumps(b, indent=2))
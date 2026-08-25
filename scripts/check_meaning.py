import json
import random
import sys

books = ["muslim", "bukhari", "abudawud"]
random.seed(42) # For reproducible checks

for book in books:
    print(f"--- BOOK: {book.upper()} ---")
    with open(f"../data/api/{book}.ndjson", "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    samples = random.sample(lines, 3)
    for s in samples:
        obj = json.loads(s)
        print(f"\n[Intl ID: {obj['id']}]")
        
        indo = ""
        for t in obj['translations'].get('id', []):
            if t['source'] == 'lidwa':
                indo = t['text']
                break
                
        eng = ""
        for t in obj['translations'].get('en', []):
            if t['source'] == 'fawazahmed':
                eng = t['text']
                break
                
        # Safely print
        print("LIDWA (Indonesian): " + indo[:250].replace('\n', ' ').encode('ascii', 'ignore').decode('ascii'))
        print("FAWAZ (English):    " + eng[:250].replace('\n', ' ').encode('ascii', 'ignore').decode('ascii'))
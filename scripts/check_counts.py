import json
import os

fawaz_dir = "data/sources/fawaz_api/editions/"
lidwa_dir = "data/sources/lidwa/"
books_9 = ['bukhari', 'muslim', 'nasai', 'abudawud', 'tirmidhi', 'ibnmajah', 'malik', 'ahmad', 'darimi']

print("Comparing Hadith Counts:")
for book in books_9:
    lidwa_file = os.path.join(lidwa_dir, f"{book}.ndjson")
    fawaz_file = os.path.join(fawaz_dir, f"ara-{book}", f"ara-{book}.min.json")
    if not os.path.exists(fawaz_file):
        fawaz_file = os.path.join(fawaz_dir, f"ara-{book}.min.json")

    l_count = 0
    f_count = 0

    if os.path.exists(lidwa_file):
        with open(lidwa_file, 'r', encoding='utf-8') as f:
            for _ in f:
                l_count += 1
                
    if os.path.exists(fawaz_file):
        try:
            with open(fawaz_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    f_count = len(data)
                elif 'hadiths' in data:
                    f_count = len(data['hadiths'])
        except Exception:
            pass

    print(f"{book:10s}: Lidwa {l_count} | Fawaz {f_count}")

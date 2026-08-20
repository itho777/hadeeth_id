import os
import json
import io

books = ["bukhari", "muslim", "tirmidhi", "abudawud", "nasai", "ibnmajah", "malik", "darimi", "ahmad"]

print("--- HADITH COUNTS FOR 9 BOOKS ---")

for book in books:
    print("\nBook: {}".format(book.upper()))
    
    # 1. Lidwa
    lidwa_count = 0
    lidwa_path = os.path.join("data", "lidwa-chapters", "{}.json".format(book))
    if os.path.exists(lidwa_path):
        with io.open(lidwa_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for c in data.get("chapters", []):
                val = c.get("hadith_end", 0)
                if isinstance(val, int) and val > lidwa_count:
                    lidwa_count = val
                elif isinstance(val, str) and val.isdigit() and int(val) > lidwa_count:
                    lidwa_count = int(val)
    print("  Lidwa: {}".format(lidwa_count))
    
    # 2. Fawaz (Darussalam)
    fawaz_count = 0
    fawaz_path = os.path.join("data", "fawaz_combined", "{}_combined.json".format(book))
    if os.path.exists(fawaz_path):
        with io.open(fawaz_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, list):
                fawaz_count = len(data)
                if fawaz_count > 0:
                    last_item = data[-1]
                    if isinstance(last_item, dict) and 'hadithnumber' in last_item:
                        try:
                            # e.g. "hadithnumber": 7563
                            fawaz_count = int(float(last_item['hadithnumber']))
                        except:
                            pass
            elif isinstance(data, dict):
                fawaz_count = len(data.get("hadiths", []))
    print("  Fawaz: {}".format(fawaz_count))
    
    # 3. AhmedBaset
    ahmed_count = 0
    ahmed_file = book + ".json"
    if book == "muslim": ahmed_file = "sahih_muslim.json"
    elif book == "bukhari": ahmed_file = "sahih_bukhari.json"
    elif book == "abudawud": ahmed_file = "sunan_abudawud.json"
    elif book == "ibnmajah": ahmed_file = "sunan_ibnmajah.json"
    elif book == "nasai": ahmed_file = "sunan_nasai.json"
    elif book == "tirmidhi": ahmed_file = "jami_tirmidhi.json"
    elif book == "malik": ahmed_file = "muwatta_malik.json"
    elif book == "ahmad": ahmed_file = "musnad_ahmad.json"
    elif book == "darimi": ahmed_file = "sunan_darimi.json"
    
    ahmed_path = os.path.join("h:\\", "Itho", "2026", "Project", "Hadeeth", "data source", "ahmedbaset", "by_book", "the_9_books", ahmed_file)
    if os.path.exists(ahmed_path):
        with io.open(ahmed_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, list):
                ahmed_count = len(data)
                if ahmed_count > 0:
                    last_item = data[-1]
                    if isinstance(last_item, dict) and 'idInBook' in last_item:
                        try:
                            ahmed_count = int(last_item['idInBook'])
                        except:
                            pass
            elif isinstance(data, dict):
                h_list = data.get("hadiths", [])
                ahmed_count = len(h_list)
                if ahmed_count > 0:
                    last_item = h_list[-1]
                    if isinstance(last_item, dict) and 'idInBook' in last_item:
                        try:
                            ahmed_count = int(last_item['idInBook'])
                        except:
                            pass
    print("  Ahmed: {}".format(ahmed_count))

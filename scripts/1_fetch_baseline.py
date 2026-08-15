import os
import json
import urllib.request
import time

BASE_URL = "https://cdn.jsdelivr.net/gh/fawazahmed0/hadith-api@1/editions/{}.json"
EDITIONS_LIST_URL = "https://cdn.jsdelivr.net/gh/fawazahmed0/hadith-api@1/editions.json"
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "raw_baseline")
BOOKS_META_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "meta")

def fetch_baseline():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    if not os.path.exists(BOOKS_META_DIR):
        os.makedirs(BOOKS_META_DIR)
        
    print("[*] Fetching editions metadata from Fawazahmed0...")
    try:
        req = urllib.request.Request(EDITIONS_LIST_URL, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            editions_data = json.loads(response.read().decode('utf-8'))
            with open(os.path.join(BOOKS_META_DIR, "fawaz_editions.json"), "w", encoding="utf-8") as f:
                json.dump(editions_data, f, indent=2)
    except Exception as e:
        print(f"[!] Failed to fetch editions.json: {e}")
        return

    # To avoid rate limits, we'll only fetch the 9 major books for now (or what's available)
    TARGET_BOOKS = ["bukhari", "muslim", "abudawud", "tirmidhi", "nasai", "ibnmajah", "malik", "darimi", "ahmad"]

    for book, info in editions_data.items():
        if book not in TARGET_BOOKS:
            continue
            
        print(f"\n[*] Processing book: {book}")
        for edition in info.get("collection", []):
            ed_name = edition.get("name")
            if not ed_name:
                continue
                
            # If it's the stripped/diacriticless version (e.g., ara-bukhari1), we can skip it to save space
            if ed_name.endswith("1") and "ara" in ed_name:
                continue
                
            url = BASE_URL.format(ed_name)
            out_path = os.path.join(OUTPUT_DIR, f"{ed_name}.json")
            
            if os.path.exists(out_path):
                print(f"[-] Already exists: {out_path}, skipping download.")
                continue
                
            print(f"[*] Downloading {ed_name}...")
            try:
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req) as response:
                    data = json.loads(response.read().decode('utf-8'))
                    with open(out_path, 'w', encoding='utf-8') as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)
                    print(f"  [+] Successfully saved {ed_name}")
                time.sleep(0.5) # Basic rate limiting
            except Exception as e:
                print(f"  [!] Failed to download {ed_name}: {e}")

if __name__ == "__main__":
    fetch_baseline()

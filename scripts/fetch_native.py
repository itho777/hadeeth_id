import os
import urllib.request
import zipfile
import sqlite3
import json
import shutil

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
SOURCES_DIR = os.path.join(BASE_DIR, "data", "sources")

AHMEDBASET_URL = "https://github.com/AhmedBaset/hadith-json/archive/refs/heads/main.zip"

def ensure_dirs():
    for d in ["ahmedbaset", "lidwa", "kaggle", "openhadith"]:
        os.makedirs(os.path.join(SOURCES_DIR, d), exist_ok=True)

def fetch_ahmedbaset():
    print("[*] Fetching native AhmedBaset (17 Books) data...")
    zip_path = os.path.join(SOURCES_DIR, "ahmedbaset.zip")
    extract_path = os.path.join(SOURCES_DIR, "ahmedbaset_temp")
    target_path = os.path.join(SOURCES_DIR, "ahmedbaset")
    
    if os.path.exists(os.path.join(target_path, "by_book")):
        print("[-] AhmedBaset native data already exists.")
        return
        
    try:
        req = urllib.request.Request(AHMEDBASET_URL, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            with open(zip_path, 'wb') as out:
                out.write(response.read())
                
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_path)
            
        # Move the inner folders
        db_path = os.path.join(extract_path, "hadith-json-main", "db")
        for item in os.listdir(db_path):
            s = os.path.join(db_path, item)
            d = os.path.join(target_path, item)
            if os.path.isdir(s):
                shutil.copytree(s, d, dirs_exist_ok=True)
            else:
                shutil.copy2(s, d)
                
        # Cleanup
        os.remove(zip_path)
        shutil.rmtree(extract_path)
        print("[+] AhmedBaset native data imported.")
    except Exception as e:
        print(f"[!] Failed to fetch AhmedBaset: {e}")

def export_lidwa_native():
    print("[*] Exporting Lidwa native data from SQLite...")
    target_dir = os.path.join(SOURCES_DIR, "lidwa")
    db_path = os.path.join(BASE_DIR, "data", "sqlite", "hadith_final.db")
    
    if not os.path.exists(db_path):
        print("[!] hadith_final.db not found. Cannot export Lidwa natively.")
        return
        
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT DISTINCT book_id FROM hadiths")
    books = [row['book_id'] for row in cursor.fetchall()]
    
    for book in books:
        out_path = os.path.join(target_dir, f"{book}.json")
        if os.path.exists(out_path):
            continue
            
        cursor.execute("SELECT * FROM hadiths WHERE book_id = ? ORDER BY id", (book,))
        rows = [dict(row) for row in cursor.fetchall()]
        
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(rows, f, ensure_ascii=False, indent=2)
            
    print("[+] Lidwa native data exported.")
    conn.close()

def export_kaggle_native():
    print("[*] Exporting Kaggle Narrators native data from SQLite...")
    target_path = os.path.join(SOURCES_DIR, "kaggle", "narrators.json")
    if os.path.exists(target_path):
        print("[-] Kaggle native data already exists.")
        return
        
    db_path = os.path.join(BASE_DIR, "data", "sqlite", "hadith.db")
    if not os.path.exists(db_path):
        print("[!] hadith.db not found.")
        return
        
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT * FROM narrators")
        rows = [dict(row) for row in cursor.fetchall()]
        with open(target_path, 'w', encoding='utf-8') as f:
            json.dump(rows, f, ensure_ascii=False, indent=2)
        print("[+] Kaggle native data exported.")
    except Exception as e:
        print(f"[!] Kaggle export failed: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    ensure_dirs()
    fetch_ahmedbaset()
    export_lidwa_native()
    export_kaggle_native()

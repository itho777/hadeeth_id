import os
import json

def build_topics_index():
    hid = r"g:\AntigravityPortable\.gemini\antigravity\scratch\hadeeth_id"
    meta_path = os.path.join(hid, "data", "api", "topics_metadata.ndjson")
    out_file = os.path.join(hid, "data", "api", "topics_index.json")
    
    topics_list = []
    with open(meta_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                topics_list.append(json.loads(line))
                
    books = [
        'bukhari', 'muslim', 'tirmidhi', 'abudawud', 'nasai',
        'ibnmajah', 'malik', 'ahmad', 'darimi', 'nawawi', 'bulugh', 'riyad'
    ]
    
    index_data = {
        "version": "1.0",
        "generated_at": "2026-08-25",
        "topics": {}
    }
    
    for t in topics_list:
        tid = str(t["id"])
        index_data["topics"][tid] = {
            "id": t["id"],
            "name_en": t["name_en"],
            "name_id": t["name_id"],
            "books": {}
        }
        
    for bookId in books:
        ndjson_file = os.path.join(hid, "data", "api", f"{bookId}.ndjson")
        if not os.path.exists(ndjson_file):
            continue
            
        print(f"Indexing topics for {bookId}...")
        with open(ndjson_file, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    h = json.loads(line)
                    tags = h.get("tags") or []
                    hid_num = h.get("id") or h.get("hadith_number")
                    if not hid_num:
                        continue
                    for t in topics_list:
                        tid = str(t["id"])
                        name_en = t["name_en"]
                        if name_en in tags:
                            if bookId not in index_data["topics"][tid]["books"]:
                                index_data["topics"][tid]["books"][bookId] = []
                            index_data["topics"][tid]["books"][bookId].append(hid_num)
                except Exception:
                    pass
                    
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(index_data, f, ensure_ascii=False)
        
    file_size_kb = os.path.getsize(out_file) / 1024
    print(f"Generated {out_file} ({file_size_kb:.1f} KB) successfully!")

if __name__ == "__main__":
    build_topics_index()

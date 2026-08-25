import os
import json
import glob

def build_topic_slices():
    hid = r"g:\AntigravityPortable\.gemini\antigravity\scratch\hadeeth_id"
    meta_path = os.path.join(hid, "data", "api", "topics_metadata.ndjson")
    out_dir = os.path.join(hid, "data", "topics")
    os.makedirs(out_dir, exist_ok=True)
    
    topics = []
    with open(meta_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                topics.append(json.loads(line))
                
    print(f"Loaded {len(topics)} topics from metadata.")
    
    books = [
        'bukhari', 'muslim', 'tirmidhi', 'abudawud', 'nasai',
        'ibnmajah', 'malik', 'ahmad', 'darimi', 'nawawi', 'bulugh', 'riyad'
    ]
    
    total_slices = 0
    for bookId in books:
        ndjson_file = os.path.join(hid, "data", "api", f"{bookId}.ndjson")
        if not os.path.exists(ndjson_file):
            continue
            
        print(f"Processing {bookId}...")
        hadiths = []
        with open(ndjson_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    hadiths.append(json.loads(line))
                    
        for t in topics:
            tid = t["id"]
            name_en = t["name_en"]
            
            slice_data = []
            for h in hadiths:
                tags = h.get("tags") or []
                if name_en in tags:
                    ar = ""
                    if h.get("text_ar"): ar = h["text_ar"]
                    elif h.get("translations", {}).get("ar"):
                        ar = h["translations"]["ar"][0].get("text", "")
                        
                    en = ""
                    if h.get("text_en"): en = h["text_en"]
                    elif h.get("translations", {}).get("en"):
                        en = h["translations"]["en"][0].get("text", "")
                        
                    id_txt = ""
                    if h.get("text_id"): id_txt = h["text_id"]
                    elif h.get("translations", {}).get("id"):
                        id_txt = h["translations"]["id"][0].get("text", "")
                        
                    grade = h.get("grade") or h.get("grade_en") or ""
                    if not grade and h.get("gradings"):
                        grade = h["gradings"][0].get("grade", "")
                    if not grade:
                        grade = "Sahih" if bookId in ["bukhari", "muslim"] else ""
                        
                    slice_data.append({
                        "id": h.get("id") or h.get("hadith_number"),
                        "hadith_number": h.get("hadith_number") or h.get("id"),
                        "text_ar": ar,
                        "text_id": id_txt,
                        "text_en": en,
                        "grade": grade,
                        "id_link_text": h.get("id_link_text", ""),
                        "en_link_text": h.get("en_link_text", "")
                    })
                    
            out_file = os.path.join(out_dir, f"{tid}_{bookId}.json")
            with open(out_file, "w", encoding="utf-8") as f:
                json.dump(slice_data, f, ensure_ascii=False)
                
            total_slices += 1
            
    print(f"Successfully generated {total_slices} topic slice files in {out_dir}!")

if __name__ == "__main__":
    build_topic_slices()

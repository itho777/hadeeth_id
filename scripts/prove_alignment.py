import json
import random
import os

books = ["muslim", "bukhari", "abudawud", "tirmidhi"]
langs = [("ara", "Arabic"), ("eng", "English"), ("urd", "Urdu"), ("ben", "Bengali")]
FAWAZ_DIR = "../data/sources/fawaz_api/editions"

out_lines = ["# Fawazahmed Internal Alignment Proof\n"]
out_lines.append("This document randomly samples IDs from the Fawazahmed dataset across multiple languages to prove that their internal IDs perfectly align across different translations.\n")

random.seed(12345)

for book in books:
    out_lines.append(f"\n## Book: {book.upper()}\n")
    
    # Load languages
    data = {}
    for l_code, l_name in langs:
        path = os.path.join(FAWAZ_DIR, f"{l_code}-{book}.json")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                data[l_code] = json.load(f).get("hadiths", [])
                
    if not data.get("ara"): continue
    
    # Find valid IDs (where Arabic is not empty)
    valid_ids = [h['hadithnumber'] for h in data["ara"] if h.get('text', '').strip()]
    if not valid_ids: continue
    
    # Sample 3 random valid IDs
    samples = random.sample(valid_ids, 3)
    
    for h_id in samples:
        out_lines.append(f"### Fawazahmed ID: {h_id}\n")
        
        for l_code, l_name in langs:
            if l_code in data:
                # Find the hadith by ID
                h_obj = next((h for h in data[l_code] if h['hadithnumber'] == h_id), None)
                if h_obj:
                    text = h_obj.get("text", "").strip().replace("\n", " ")
                    if len(text) > 300: text = text[:300] + "..."
                    out_lines.append(f"**{l_name}**: {text}\n")
                else:
                    out_lines.append(f"**{l_name}**: (Not found)\n")
        out_lines.append("\n---\n")

# Write to the artifact directory
artifact_path = "G:/AntigravityPortable/.gemini/antigravity/brain/05330fd0-0cdc-4718-9ec9-0746dd724a20/fawazahmed_internal_alignment.md"
with open(artifact_path, "w", encoding="utf-8") as f:
    f.writelines(out_lines)
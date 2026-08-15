import json
import re
import os

def parse_openiti(filepath):
    print("Reading OpenITI file...")
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    hadiths = []
    sections = {}
    section_details = {}
    
    current_book_id = 0
    current_book_name = "مقدمة"
    sections["0"] = current_book_name
    
    current_hadith_num = None
    current_hadith_text = []
    
    hadith_pattern = re.compile(r'### \|\s*(\d+)\s*-')
    chapter_pattern = re.compile(r'### \|\s*(.+)')
    
    def save_hadith():
        nonlocal current_hadith_num, current_hadith_text
        if current_hadith_num is not None:
            text = " ".join(current_hadith_text).strip()
            # clean inline tags like ms0001
            text = re.sub(r'ms\d+', '', text)
            hadiths.append({
                "hadithnumber": current_hadith_num,
                "arabicnumber": current_hadith_num,
                "text": text,
                "grades": [],
                "reference": {
                    "book": current_book_id,
                    "hadith": current_hadith_num
                }
            })
            
            if str(current_book_id) not in section_details:
                section_details[str(current_book_id)] = {
                    "hadithnumber_first": current_hadith_num,
                    "hadithnumber_last": current_hadith_num,
                    "arabicnumber_first": current_hadith_num,
                    "arabicnumber_last": current_hadith_num
                }
            else:
                section_details[str(current_book_id)]["hadithnumber_last"] = current_hadith_num
                section_details[str(current_book_id)]["arabicnumber_last"] = current_hadith_num

            current_hadith_num = None
            current_hadith_text = []

    for line in lines:
        line = line.strip()
        if not line or line.startswith('#META#') or line.startswith('# Page'):
            continue
            
        # Match Hadith number
        m_hadith = hadith_pattern.match(line)
        if m_hadith:
            save_hadith()
            current_hadith_num = int(m_hadith.group(1))
            continue
            
        # Match Chapter/Section heading
        if line.startswith('### |'):
            m_chapter = chapter_pattern.match(line)
            if m_chapter and not hadith_pattern.match(line):
                save_hadith()
                chapter_title = m_chapter.group(1).strip()
                current_book_id += 1
                sections[str(current_book_id)] = chapter_title
            continue
            
        # It's text
        if current_hadith_num is not None:
            if line.startswith('# '):
                current_hadith_text.append(line[2:].strip())
            elif line.startswith('~~'):
                current_hadith_text.append(line[2:].strip())
            else:
                current_hadith_text.append(line)

    save_hadith()
    
    output_data = {
        "metadata": {
            "name": "Mu'jam al-Kabir",
            "sections": sections,
            "section_details": section_details
        },
        "hadiths": hadiths
    }
    
    out_path = os.path.join("data", "raw_baseline", "ara-tabarani.json")
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(hadiths)} hadiths to {out_path}")
    
    # Generate chapters file
    chapters_data = {}
    for b_id, title in sections.items():
        if str(b_id) in section_details:
            details = section_details[str(b_id)]
            chapters_data[str(b_id)] = {
                "id": str(b_id),
                "title": title,
                "first_hadith": str(details["hadithnumber_first"]),
                "last_hadith": str(details["hadithnumber_last"])
            }
            
    chap_out_path = os.path.join("data", "chapters", "tabarani.json")
    with open(chap_out_path, 'w', encoding='utf-8') as f:
        json.dump(chapters_data, f, ensure_ascii=False, indent=2)
    print(f"Saved chapters to {chap_out_path}")

if __name__ == '__main__':
    parse_openiti('scratch/raw_tabarani.txt')

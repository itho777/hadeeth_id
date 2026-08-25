
import re

SURAH_MAP = {
    r"baqarah": 2,
    r"ali\s*[\'`]?i?mraan": 3,
    r"ali\s*[\'`]?i?mran": 3,
    r"lmraan": 3,
    r"nisaa?": 4,
    r"maa?[\'`]?i?dah": 5,
    r"an[\'`]?aam": 6,
    r"an[\'`]?am": 6,
    r"a[\'`]?raf": 7,
    r"anfaal": 8,
    r"anfal": 8,
    r"nafaal": 8,
    r"taubah": 9,
    r"yunus": 10,
    r"huud": 11,
    r"ibrahim": 14,
    r"15": 15,
    r"nahl": 16,
    r"israa?": 17,
    r"kahfi": 18,
    r"maryam": 19,
    r"thaahaa": 20,
    r"anbiyaa?": 21,
    r"hajj": 22,
    r"mukminuun": 23,
    r"nuur": 24,
    r"furqan": 25,
    r"syu[\'`]?araa?": 26,
    r"naml": 27,
    r"qashash": 28,
    r"ankabuut": 29,
    r"ruum": 30,
    r"luqmaan": 31,
    r"luqman": 31,
    r"sajadah": 32,
    r"sajdah": 32,
    r"ahzaab": 33,
    r"ahzab": 33,
    r"saba": 34,
    r"yasin": 36,
    r"shaffaat": 37,
    r"shaaffaat": 37,
    r"syaffat": 37,
    r"shaad": 38,
    r"zumar": 39,
    r"fushilat": 41,
    r"syura": 42,
    r"dukhaan": 44,
    r"dukhan": 44,
    r"muhammad": 47,
    r"fath": 48,
    r"hujurat": 49,
    r"qaaf": 50,
    r"najm": 53,
    r"mujadilah": 58,
    r"hasyr": 59,
    r"mumtahanah": 60,
    r"munaafiquun": 63,
    r"thall?aaq": 65,
    r"tahriim": 66,
    r"tahrim": 66,
    r"jin": 72,
    r"72": 72,
    r"mudatstsir": 74,
    r"qiyamah": 75,
    r"takwir": 81,
    r"insyiqaaq": 84,
    r"a1-laii": 92,
    r"[\'`]?alaq": 96,
    r"takaatsur": 102,
    r"ikhlash": 112,
}

def get_surah_num(sura_name):
    # Try exact number first
    m = re.search(r"\((\d+)\)", sura_name)
    if m:
        return int(m.group(1))
    
    # Check regexes
    name = sura_name.lower().replace("al-", "").replace("al ", "").replace("as-", "").replace("as ", "")
    for pattern, num in SURAH_MAP.items():
        if re.search(pattern, name):
            return num
    return None

import json
import glob
import io

def process_file(filepath):
    print("Processing " + filepath)
    with io.open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    out_lines = []
    changes = 0
    
    # Regex to capture the whole QS reference
    # E.g. (QS. Al Baqarah: 2) or (Qs. Ali Imran: 1-3)
    p = re.compile(ur"(\((?:QS|Qs|qs|Q\.S|q\.s)\.?\s*([^:]+?)\s*:\s*([0-9]+)(?:-[0-9]+)?[a-z]?\))")
    
    for line in lines:
        new_line = line
        matches = p.findall(line)
        for full_match, sura_name, verse in matches:
            snum = get_surah_num(sura_name)
            if snum:
                link = u'<a href="https://tafseer.id/#sura/{sura}/verse/{verse}" target="_blank" class="text-secondary dark:text-[#10b981] hover:underline" rel="noopener">{text}</a>'.format(
                    sura=snum,
                    verse=verse,
                    text=full_match
                )
                new_line = new_line.replace(full_match, link)
                changes += 1
        out_lines.append(new_line)
        
    if changes > 0:
        with io.open(filepath, "w", encoding="utf-8") as f:
            for l in out_lines:
                f.write(l)
    return changes

total_changes = 0
for f in glob.glob("../data/editions/ind-*.ndjson"):
    total_changes += process_file(f)
    
print("Total changes: " + str(total_changes))


import re
import glob
import io

def process_file(filepath):
    print("Processing " + filepath)
    with io.open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    out_lines = []
    changes = 0
    
    # Matches (75.16) or (75.16-17) or (V.3:144) or (3:144)
    # Be careful not to match standard text like (1.5)
    # Let's use regex for (V.x:y) or (Quran x.y) or (x.y)
    # Wait, (x.y) is risky if it means something else.
    # Let's match (V. \d+:\d+) and (\d+\.\d+(?:-\d+)?) ONLY if it has a V. or the file is eng-bukhari where it's heavily used for Quran
    
    # Actually, we can just match (V. \d+:\d+) or (V.\d+:\d+)
    p_v = re.compile(ur"(\(V\.\s*([0-9]+)\s*:\s*([0-9]+)(?:-[0-9]+)?\))")
    p_dot = re.compile(ur"(\(([0-9]+)\.([0-9]+)(?:-[0-9]+)?\))")
    
    for line in lines:
        new_line = line
        
        matches_v = p_v.findall(line)
        for full_match, sura, verse in matches_v:
            link = u'<a href="https://tafseer.id/#sura/{sura}/verse/{verse}" target="_blank" class="text-secondary dark:text-[#10b981] hover:underline" rel="noopener">{text}</a>'.format(
                sura=sura,
                verse=verse,
                text=full_match
            )
            new_line = new_line.replace(full_match, link)
            changes += 1
            
        matches_dot = p_dot.findall(line)
        for full_match, sura, verse in matches_dot:
            # Check if it's a valid surah (1-114) and verse (1-286)
            if 1 <= int(sura) <= 114 and 1 <= int(verse) <= 286:
                link = u'<a href="https://tafseer.id/#sura/{sura}/verse/{verse}" target="_blank" class="text-secondary dark:text-[#10b981] hover:underline" rel="noopener">{text}</a>'.format(
                    sura=sura,
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
for f in glob.glob("../data/editions/eng-*.ndjson"):
    total_changes += process_file(f)
    
print("Total changes: " + str(total_changes))

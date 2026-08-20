import json
import os
import glob

print("Checking commentaries encoding...")
for filepath in glob.glob('data/commentaries/*.json'):
    with open(filepath, 'rb') as f:
        raw = f.read()
    
    try:
        text = raw.decode('utf-8')
        # Check for typical cp1252-decoded-as-utf8 mojibake signatures for Arabic
        if 'O' in text or 'O"' in text or 'O_' in text or 'U,' in text or 'U.' in text:
            # Re-encode to cp1252 and decode to utf-8
            try:
                fixed = text.encode('cp1252').decode('utf-8')
                with open(filepath, 'w', encoding='utf-8') as fw:
                    fw.write(fixed)
                print(f"Fixed {filepath}")
            except Exception as e:
                pass
    except Exception as e:
        pass

print("Done.")

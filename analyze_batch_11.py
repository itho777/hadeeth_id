import sqlite3
import json
import re

db_path = r'g:\Box\AntigravitySync\.gemini\antigravity\scratch\hadeeth_id\data\sqlite\hadith.db'
batch_path = r"C:\Users\waverider\.gemini\antigravity\brain\a8b4a1aa-b3d0-485e-90c7-42c1496cd802\scratch\batch_11.json"

conn = sqlite3.connect(db_path)
c = conn.cursor()

with open(batch_path, "r", encoding="utf-8") as f:
    batch = json.load(f)

with open("batch_11_contexts.txt", "w", encoding="utf-8") as out:
    for i, item in enumerate(batch):
        hid = item['id']
        targets = item.get('targets', [])
        c.execute("SELECT text_id, text_ar FROM hadiths WHERE id=?", (hid,))
        row = c.fetchone()
        if row:
            txt_id, txt_ar = row
            out.write(f"=== [{i}] ID: {hid} ===\n")
            out.write(f"TARGETS: {targets}\n")
            out.write(f"ARABIC:\n{txt_ar}\n")
            out.write("INDONESIAN CONTEXTS:\n")
            for t in targets:
                pattern = re.compile(r'(.{0,60}\[' + re.escape(t) + r'\].{0,60})')
                matches = pattern.findall(txt_id)
                for m in matches:
                    out.write(f"  Target [{t}]: ... {m} ...\n")
            out.write("-" * 50 + "\n")

conn.close()
print("Written to batch_11_contexts.txt")

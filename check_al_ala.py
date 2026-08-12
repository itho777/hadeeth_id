import sqlite3
import json

db_path = r'g:\Box\AntigravitySync\.gemini\antigravity\scratch\hadeeth_id\data\sqlite\hadith.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

c.execute("SELECT id, text_id FROM hadiths WHERE text_id LIKE '%[Al %Ala%|%' OR text_id LIKE '%Abdurrahman bin Ya%qub%' LIMIT 10")
rows = c.fetchall()
print("Matches in DB for Al 'Ala' father:")
for r in rows:
    print(r[0], r[1][:150])

conn.close()

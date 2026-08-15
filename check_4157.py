import sqlite3

conn = sqlite3.connect(r'g:\Box\AntigravitySync\.gemini\antigravity\scratch\hadeeth_id\data\sqlite\hadith.db')
c = conn.cursor()

c.execute("SELECT text_id FROM hadiths WHERE id='muslim_4157'")
row = c.fetchone()
if row:
    print("text_id for muslim_4157:")
    print(row[0])

conn.close()

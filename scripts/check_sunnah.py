import sqlite3
import sys

sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect(r'g:\Box\AntigravitySync\.gemini\antigravity\scratch\hadeeth_id\scratch\SunnahDb.db')
c = conn.cursor()

c.execute("SELECT HadithText, Tafseel FROM Hadiths WHERE HadithText LIKE '%Telah menceritakan%' LIMIT 1")
row = c.fetchone()
if row:
    print('Found Indo in HadithText:', row[0][:100])
else:
    print('No Indo in HadithText')
    
c.execute("SELECT HadithText, Tafseel FROM Hadiths WHERE Tafseel LIKE '%Telah menceritakan%' LIMIT 1")
row = c.fetchone()
if row:
    print('Found Indo in Tafseel:', row[1][:100])
else:
    print('No Indo in Tafseel')

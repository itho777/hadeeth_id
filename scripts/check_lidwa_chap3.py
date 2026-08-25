# -*- coding: utf-8 -*-
import sqlite3, json, codecs

with codecs.open("check_lidwa_chap3.txt", "w", "utf-8") as out:
    out.write("--- LIDWA (datakitab_muslim) ---\n")
    conn = sqlite3.connect('../data/sources/lidwa/lidwa.new.db')
    c = conn.cursor()
    c.execute("SELECT k.idKitab, k.kitab FROM datakitab_muslim k ORDER BY k.idKitab ASC LIMIT 5")
    for row in c.fetchall():
        out.write("Kitab " + str(row[0]) + ": " + row[1] + "\n")
        
    out.write("\n--- LIDWA (databab_muslim) for Kitab 1 (Iman) ---\n")
    c.execute("SELECT idBab, bab, startId, endId FROM databab_muslim WHERE idKitab = 1 ORDER BY idBab ASC LIMIT 5")
    for row in c.fetchall():
        out.write("Bab " + str(row[0]) + ": " + row[1] + " (Hadith " + str(row[2]) + " to " + str(row[3]) + ")\n")
        
    out.write("\n--- INTERNATIONAL (AhmedBaset/Chapters API) ---\n")
    with open("../data/chapters/muslim.json", "r") as f:
        chapters = json.load(f)
    for ch in chapters[:5]:
        out.write("Chap " + str(ch.get('chapter_number')) + ": " + ch.get('title_en', '') + " (" + ch.get('title_id', '') + ") | Hadiths: " + str(ch.get('hadith_start')) + " to " + str(ch.get('hadith_end')) + "\n")
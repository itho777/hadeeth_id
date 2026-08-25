# -*- coding: utf-8 -*-
import sqlite3, codecs

with codecs.open("check_lidwa_chap.txt", "w", "utf-8") as out:
    conn = sqlite3.connect('../data/sqlite/lidwa.new.db')
    c = conn.cursor()
    c.execute("SELECT NoKitab, KitabId FROM kitab WHERE Kitab LIKE '%muslim%' LIMIT 10")
    books = c.fetchall()
    
    # We know Muslim is KitabId = 2 in Lidwa. Let's check bab for KitabId = 2.
    c.execute("SELECT NoBab, BabId, Deskripsi FROM bab WHERE KitabId = 2 LIMIT 5")
    babs = c.fetchall()
    
    for b in babs:
        out.write(str(b) + "\n")
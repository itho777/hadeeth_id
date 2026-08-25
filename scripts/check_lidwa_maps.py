import sqlite3
import os

db_path = "../data/sources/lidwa/lidwa.new.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

books = ["bukhari", "muslim", "abudaud", "tirmidzi", "nasai", "ibnumajah", "darimi", "ahmad", "malik"]
for b in books:
    cursor.execute("SELECT COUNT(*) FROM mapping_" + b)
    count = cursor.fetchone()[0]
    cursor.execute("SELECT MAX(NoHdt), MAX(NoMapping) FROM mapping_" + b)
    max_hdt, max_map = cursor.fetchone()
    print("%s: count=%s, max Lidwa ID=%s, max Intl ID=%s" % (b, count, max_hdt, max_map))
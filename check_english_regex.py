import io
import re

sql_file = r'h:\Itho\2026\Project\Hadeeth\data source\lidwa\lidwa.new.db.sql'

print("Parsing SQL line by line...")
counts = {book: {'total': 0, 'english': 0} for book in ['bukhari', 'muslim', 'ahmad', 'abudaud', 'tirmidzi', 'nasai', 'ibnumajah', 'malik', 'darimi']}

with io.open(sql_file, 'r', encoding='utf-8') as f:
    in_agregat = False
    current_tuple = ""
    for line in f:
        if 'INSERT INTO "had_agregat"' in line:
            in_agregat = True
        elif line.startswith('INSERT INTO'):
            in_agregat = False
            
        if in_agregat:
            # We are inside had_agregat inserts.
            # A tuple starts with `('bookname',`
            # and ends with `),` or `);`
            # But they can span multiple lines. We'll just look for `('bookname',` and see if there are 6 elements.
            # Actually, a simpler way: if we find `('muslim',` we count a total.
            # If the tuple has 6 elements and the 6th is not empty, we count english.
            # Since splitting SQL is hard due to strings containing commas, let's just count occurrences of English text.
            # The user's screenshot showed `Isi_English` has English characters.
            pass

# Let's use a simpler streaming regex for tuples.
def extract_counts():
    import re
    # We will read the file in chunks
    chunk_size = 1024 * 1024 * 10 # 10 MB
    leftover = ""
    with io.open(sql_file, 'r', encoding='utf-8') as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            text = leftover + chunk
            # find all tuples like ('muslim', 123, 'ar', 'id', 'ar_gundul', 'en')
            # we can't reliably regex parse SQL strings. 
            # But we can just use the sqlite3 command line tool to query it directly from the DB the user made!
            leftover = ""

extract_counts()


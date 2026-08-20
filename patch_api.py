with open('js/api.js', 'r', encoding='utf-8') as f:
    text = f.read()

target_hadith = """      const idx = await this.fetchNdjsonIndex('api', bookId);
      if (idx && idx.hadiths && idx.hadiths[hadithNumber]) {
          const range = idx.hadiths[hadithNumber];
          const hadiths = await this.fetchNdjsonRange('api', bookId, range[0], range[1]);
          h = hadiths[0] || null;
      } else {"""

replacement_hadith = """      const idx = await this.fetchNdjsonIndex('api', bookId);
      if (idx && Array.isArray(idx)) {
          const entry = idx.find(e => String(e.id) === String(hadithNumber) || String(e.lidwa_id) === String(hadithNumber));
          if (entry) {
              const hadiths = await this.fetchNdjsonRange('api', bookId, entry.start, entry.end);
              h = hadiths[0] || null;
          } else {
              const allHadiths = await this.fetchNdjsonFull('api', bookId);
              h = allHadiths.find(item => String(item.hadith_number) === String(hadithNumber) || String(item.id) === String(hadithNumber)) || null;
          }
      } else if (idx && idx.hadiths && idx.hadiths[hadithNumber]) {
          const range = idx.hadiths[hadithNumber];
          const hadiths = await this.fetchNdjsonRange('api', bookId, range[0], range[1]);
          h = hadiths[0] || null;
      } else {"""

if target_hadith in text:
    text = text.replace(target_hadith, replacement_hadith)
    with open('js/api.js', 'w', encoding='utf-8') as f:
        f.write(text)
    print("Patched api.js getHadith!")
else:
    print("Target not found in getHadith")


import io
import re

with io.open("../js/api.js", "r", encoding="utf-8") as f:
    js = f.read()

# Fix getHadith signature and logic
js = js.replace("async getHadith(bookId, hadithNumber) {", "async getHadith(bookId, hadithNumber, dsPrefix = 'fawaz') {")

old_logic = """        if (idx && Array.isArray(idx)) {
            const entry = idx.find(e => String(e.id) === String(hadithNumber) || String(e.lidwa_id) === String(hadithNumber));
            if (entry) {
                const hadiths = await this.fetchNdjsonRange('api', bookId, entry.start, entry.end);
                h = hadiths[0] || null;
            } else {
                const allHadiths = await this.fetchNdjsonFull('api', bookId);
                h = allHadiths.find(item => String(item.hadith_number) === String(hadithNumber) || String(item.id) === String(hadithNumber)) || null;
            }
        } else if (idx && idx.hadiths && idx.hadiths[hadithNumber]) {"""

new_logic = """        if (idx && Array.isArray(idx)) {
            const entry = idx.find(e => {
                if (dsPrefix === 'lidwa') return String(e.lidwa_id) === String(hadithNumber);
                if (dsPrefix === 'ab') return String(e.idInBook) === String(hadithNumber) || String(e.ab_id) === String(hadithNumber);
                return String(e.id) === String(hadithNumber);
            });
            if (entry) {
                const hadiths = await this.fetchNdjsonRange('api', bookId, entry.start, entry.end);
                h = hadiths[0] || null;
            } else {
                const allHadiths = await this.fetchNdjsonFull('api', bookId);
                h = allHadiths.find(item => {
                    if (dsPrefix === 'lidwa') return String(item.lidwa_id) === String(hadithNumber);
                    return String(item.id) === String(hadithNumber) || String(item.hadith_number) === String(hadithNumber);
                }) || null;
            }
        } else if (idx && idx.hadiths && idx.hadiths[hadithNumber]) {"""

js = js.replace(old_logic, new_logic)

old_fallback = """        } else {
            const allHadiths = await this.fetchNdjsonFull('api', bookId);
            h = allHadiths.find(item => String(item.hadith_number) === String(hadithNumber) || String(item.id) === String(hadithNumber)) || null;
        }"""

new_fallback = """        } else {
            const allHadiths = await this.fetchNdjsonFull('api', bookId);
            h = allHadiths.find(item => {
                if (dsPrefix === 'lidwa') return String(item.lidwa_id) === String(hadithNumber);
                return String(item.id) === String(hadithNumber) || String(item.hadith_number) === String(hadithNumber);
            }) || null;
        }"""

js = js.replace(old_fallback, new_fallback)

with io.open("../js/api.js", "w", encoding="utf-8") as f:
    f.write(js)

print("Patched api.js")
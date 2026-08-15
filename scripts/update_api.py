import os
import re

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
API_JS_PATH = os.path.join(BASE_DIR, "js", "api.js")

def update_api_js():
    with open(API_JS_PATH, 'r', encoding='utf-8') as f:
        content = f.read()
        
    target_getedition = r"(async getEdition\(langCode, bookId\) \{)([\s\S]*?)(// 1\. Fetch the master link)"
    
    new_getedition = r"""\1
    try {
      const cacheBuster = '20260813';
      const version = localStorage.getItem('dataset_version') || 'primary';
      
      // Native Fallbacks
      if (version === 'native_lidwa') {
         const res = await fetch(`${this.baseUrl}/../sources/lidwa/${bookId}.json`);
         if (!res.ok) throw new Error('Not available in Lidwa');
         const data = await res.json();
         const mapped = data.map(row => {
            let text = '';
            if (langCode === 'ara') text = row.text_ar;
            else if (langCode === 'eng') text = row.text_en;
            else if (langCode === 'ind') text = row.text_id;
            return {
               id: row.id,
               hadithNumber: row.id,
               text: text || "Translation missing in Native Lidwa."
            };
         });
         return { metadata: {}, hadiths: mapped };
      }
      
      if (version === 'native_ahmedbaset') {
         let abPath = `other_books/${bookId}`;
         if (['nawawi', 'qudsi', 'shah'].includes(bookId)) abPath = `forties/${bookId}`;
         if (['bukhari', 'muslim', 'abudawud', 'tirmidhi', 'nasai', 'ibnmajah', 'malik', 'darimi', 'ahmad'].includes(bookId)) {
            abPath = `the_9_books/${bookId}`;
         }
         const res = await fetch(`${this.baseUrl}/../sources/ahmedbaset/by_book/${abPath}.json`);
         if (!res.ok) throw new Error('Not available in AhmedBaset');
         const data = await res.json();
         const mapped = (data.hadiths || []).map(row => {
            let text = '';
            if (langCode === 'ara') text = row.arabic;
            else if (langCode === 'eng') text = row.english ? row.english.text : '';
            return {
               id: row.idInBook,
               hadithNumber: row.idInBook,
               text: text || "Translation missing in Native AhmedBaset."
            };
         });
         return { metadata: {}, hadiths: mapped };
      }
      
      \3"""
      
    content = re.sub(target_getedition, new_getedition, content, count=1)
    
    with open(API_JS_PATH, 'w', encoding='utf-8') as f:
        f.write(content)
        
    print("[+] Updated api.js with correct returning object structure!")

if __name__ == "__main__":
    update_api_js()

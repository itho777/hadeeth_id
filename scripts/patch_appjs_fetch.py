import re

with open('js/app.js', 'r', encoding='utf-8') as f:
    text = f.read()

fetch_func = """  async function fetchTranslationText(opt) {
      // First try to use the consolidated API translations if available
      if (data && data.translations) {
          if (opt.source === 'lidwa_id' && data.translations.id) {
              const t = data.translations.id.find(x => x.source === 'lidwa');
              if (t) return t.text;
          }
          if (opt.source === 'lidwa_en' && data.translations.en) {
              const t = data.translations.en.find(x => x.source === 'lidwa');
              if (t) return t.text;
          }
          if (opt.source === 'ab' && data.translations.en) {
              const t = data.translations.en.find(x => x.source === 'ab');
              if (t) return t.text;
          }
      }
      
      // Also fallback to properties if injected directly
      if (opt.source === 'lidwa_id' && data.text_id) return data.text_id;
      if (opt.source === 'lidwa_en' && data.text_en_lidwa) return data.text_en_lidwa;
      if (opt.source === 'ab' && data.text_en) return data.text_en;
      
      // Fallback: Fetch the file directly
      try {
          const resp = await fetch(opt.file);
          if (!resp.ok) return null;
          const json_data = await resp.json();
          let text = '';
          
          if (opt.source === 'fawaz') {
              const found = (json_data.hadiths || []).find(h => (h.hadithnumber ?? h.id) == opt.hid);
              if (found) text = found.text;
          } else if (opt.source === 'lidwa_id') {
              const found = (Array.isArray(json_data) ? json_data : (json_data.hadiths || [])).find(h => (h.hadith_number ?? h.id) == opt.hid);
              if (found) text = found.text_id;
          } else if (opt.source === 'lidwa_en') {
              const found = (Array.isArray(json_data) ? json_data : (json_data.hadiths || [])).find(h => (h.hadith_number ?? h.id) == opt.hid);
              if (found) text = found.text_en;
          } else if (opt.source === 'ab') {
              const found = (Array.isArray(json_data) ? json_data : (json_data.hadiths || [])).find(h => (h.hadithnumber ?? h.id) == opt.hid);
              if (found) text = found.text_en || found.text;
          }
          return text;
      } catch(e) {
          console.warn('Failed to fetch', opt, e);
      }
      return null;
  }"""

# Replace the entire fetchTranslationText function
text = re.sub(
    r"  async function fetchTranslationText\(opt\) \{.*?return null;\s+\}",
    fetch_func,
    text,
    flags=re.DOTALL
)

with open('js/app.js', 'w', encoding='utf-8') as f:
    f.write(text)

print('Patched fetchTranslationText')

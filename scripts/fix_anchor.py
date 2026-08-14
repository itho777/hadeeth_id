import os
import re

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
API_JS_PATH = os.path.join(BASE_DIR, "js", "api.js")
APP_JS_PATH = os.path.join(BASE_DIR, "js", "app.js")

def fix_api_js():
    with open(API_JS_PATH, 'r', encoding='utf-8') as f:
        content = f.read()
        
    if "getPrimaryAnchorId" not in content:
        target = r'(class ApiClient \{)'
        replacement = r'''\1

  async getPrimaryAnchorId(bookId, currentId) {
     const version = localStorage.getItem('dataset_version') || 'primary';
     if (version === 'primary') return currentId;
     
     const core9 = ['bukhari', 'muslim', 'abudawud', 'tirmidhi', 'nasai', 'ibnmajah', 'malik', 'darimi', 'ahmad'];
     
     if (version === 'native_lidwa') {
        if (core9.includes(bookId)) return currentId;
        return currentId;
     }
     
     if (version === 'native_ahmedbaset') {
        if (!core9.includes(bookId)) {
           return currentId;
        }
        try {
            const res = await fetch(`${this.baseUrl}/links/${bookId}.json`);
            if (!res.ok) return currentId;
            const linkMap = await res.json();
            for (const [lidwaId, mapping] of Object.entries(linkMap)) {
                if (String(mapping.ab) === String(currentId)) {
                    return lidwaId;
                }
            }
        } catch (e) {
            console.warn("Reverse link lookup failed", e);
        }
     }
     return currentId;
  }
'''
        content = re.sub(target, replacement, content, count=1)
        with open(API_JS_PATH, 'w', encoding='utf-8') as f:
            f.write(content)
        print("[+] Added getPrimaryAnchorId to api.js")

def fix_app_js():
    with open(APP_JS_PATH, 'r', encoding='utf-8') as f:
        content = f.read()

    # Fix loadSanadChain
    target_sanad = r"(let dbNarrators = \[\];\s*try \{\s*const res = await fetch\(`data/hadiths/\$\{bookId\}/\$\{hadithNum\}\.json`\);)"
    replacement_sanad = r"""let dbNarrators = [];
  try {
    const primaryId = await window.HadeethAPI.getPrimaryAnchorId(bookId, hadithNum);
    const res = await fetch(`data/hadiths/${bookId}/${primaryId}.json`);"""
    
    if "getPrimaryAnchorId" not in content[:content.find("loadSanadChain")+500]:
        content = re.sub(target_sanad, replacement_sanad, content, count=1)
        print("[+] Fixed loadSanadChain")

    # Fix loadHadithSyarah
    target_syarah = r"(async function loadHadithSyarah\(bookId, hadithNum\) \{[\s\S]*?try \{\s*const res = await fetch\(`data/commentaries/\$\{bookId\}/\$\{hadithNum\}\.json`\);)"
    replacement_syarah = r"""async function loadHadithSyarah(bookId, hadithNum) {
  if (!bookId || !hadithNum) return;
  
  const container = document.getElementById('syarah-container');
  const errorEl = document.getElementById('syarah-error');
  const sourceSelect = document.getElementById('syarah-source-select');
  const langSelect = document.getElementById('syarah-lang-select');
  if (!container) return;

  try {
    const primaryId = await window.HadeethAPI.getPrimaryAnchorId(bookId, hadithNum);
    const res = await fetch(`data/commentaries/${bookId}/${primaryId}.json`);"""
    
    if "getPrimaryAnchorId" not in content[content.find("loadHadithSyarah"):]:
        content = re.sub(target_syarah, replacement_syarah, content, count=1)
        print("[+] Fixed loadHadithSyarah")
        
    with open(APP_JS_PATH, 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == "__main__":
    fix_api_js()
    fix_app_js()

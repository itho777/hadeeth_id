import json
import os
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAWIS_JSON = os.path.join(BASE_DIR, "data", "rawis", "active_rawis.min.json")

def normalize_name(name):
    n = name.lower()
    n = re.sub(r'\(.*?\)', '', n)
    n = n.replace('bin', 'ibn').replace('binti', 'ibn').replace('bint', 'ibn')
    n = n.replace('radhiyallahu anhu', '').replace('radhiyallahu anha', '')
    n = n.replace('radhiyallahu \'anhu', '').replace('radhiyallahu \'anha', '')
    n = n.replace('al ', 'al-').replace('asy ', 'ash-').replace('asy-', 'ash-')
    n = n.replace('sy', 'sh').replace('thth', 'tt').replace('th', 't')
    n = n.replace('ts', 's').replace('dz', 'z').replace('zh', 'z')
    n = n.replace('\'', '').replace('`', '').replace('’', '')
    n = n.replace('awwam', 'awam').replace('khattab', 'khatab')
    n = n.replace('qutaibah', 'qutaybah').replace('humaidi', 'humaydi')
    n = n.replace('aisyah', 'aisha').replace('hafshah', 'hafsa')
    n = n.replace('khadijah', 'khadija').replace('fatimah', 'fathimah')
    n = n.replace('fathimah', 'fatima')
    n = re.sub(r'[^a-z\s\-]', '', n)
    n = re.sub(r'\s+', ' ', n).strip()
    return n

def main():
    print("[*] Starting Faster Arabic Cross-linking (Lidwa <-> Kaggle)...")
    
    with open(RAWIS_JSON, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    lidwa_rawis = {k: v for k, v in data.items() if k.startswith('lidwa_')}
    kaggle_rawis = {k: v for k, v in data.items() if not k.startswith('lidwa_')}
    
    # Precompute maps
    kaggle_exact_map = {}
    kaggle_two_words_map = {}
    
    for k_id, k_data in kaggle_rawis.items():
        if not k_data.get('ar'): continue
        k_norm = normalize_name(k_data['en'])
        k_ar = k_data['ar']
        kaggle_exact_map[k_norm] = k_ar
        
        words = k_norm.split()
        if len(words) >= 3 and words[1] == 'ibn':
            two_words = f"{words[0]} {words[1]} {words[2]}"
            if two_words not in kaggle_two_words_map:
                kaggle_two_words_map[two_words] = k_ar
        elif len(words) >= 2:
            two_words = f"{words[0]} {words[1]}"
            if two_words not in kaggle_two_words_map:
                kaggle_two_words_map[two_words] = k_ar
                
    print(f"[*] Prepared mappings from Kaggle.")
    
    matched = 0
    
    for l_id, l_data in lidwa_rawis.items():
        current_ar = str(l_data.get('ar', ''))
        if not current_ar or not re.search(r'[\u0600-\u06FF]', current_ar):
            l_norm = normalize_name(l_data['en'])
            
            best_match = None
            if l_norm in kaggle_exact_map:
                best_match = kaggle_exact_map[l_norm]
            else:
                words = l_norm.split()
                if len(words) >= 3 and words[1] == 'ibn':
                    two_words = f"{words[0]} {words[1]} {words[2]}"
                    if two_words in kaggle_two_words_map:
                        best_match = kaggle_two_words_map[two_words]
                elif len(words) >= 2:
                    two_words = f"{words[0]} {words[1]}"
                    if two_words in kaggle_two_words_map:
                        best_match = kaggle_two_words_map[two_words]
            
            if best_match:
                data[l_id]['ar'] = best_match
                matched += 1
                
    print(f"[+] Successfully injected rich Arabic names into {matched} Lidwa profiles.")
    
    with open(RAWIS_JSON, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, separators=(',', ':'))

if __name__ == '__main__':
    main()

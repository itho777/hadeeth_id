import json
import os

books = ['nawawi', 'qudsi', 'shah', 'adab', 'bulugh', 'mishkat', 'riyad', 'shamail']

for book in books:
    link_path = rf'g:\Box\AntigravitySync\.gemini\antigravity\scratch\hadeeth_id\data\links\{book}.json'
    
    if os.path.exists(link_path):
        with open(link_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # Check if already new format
        if 'fawaz_to_lidwa' in data:
            print(f'{book} is already in Tripartite format.')
            continue
            
        # Convert old format to new format
        fawaz_to_lidwa = {}
        for k, v in data.items():
            if isinstance(v, dict) and 'lidwa_id' in v:
                fawaz_to_lidwa[str(k)] = str(v['lidwa_id'])
                
        new_data = {
            'fawaz_to_lidwa': fawaz_to_lidwa,
            'fawaz_to_ab': {},
            'lidwa_to_fawaz': {v: k for k, v in fawaz_to_lidwa.items()}
        }
        
        with open(link_path, 'w', encoding='utf-8') as f:
            json.dump(new_data, f, ensure_ascii=False, indent=2)
            
        print(f'Converted {book} to Tripartite format!')
    else:
        print(f'{book} link file not found.')

import json
import os

books = ['ahmad', 'darimi']

for book in books:
    lidwa_path = rf'g:\Box\AntigravitySync\.gemini\antigravity\scratch\hadeeth_id\data\sources\lidwa\{book}.json'
    
    with open(lidwa_path, 'r', encoding='utf-8') as f:
        l_data = json.load(f)
        
    ara_hadiths = []
    eng_hadiths = [] # Will leave english empty, since Lidwa only has Indonesian
    links = {}
    
    for h in l_data:
        h_id = str(h.get('hadith_number', ''))
        if not h_id: continue
        
        ara_text = h.get('text_ar', '')
        
        ara_hadiths.append({'hadithnumber': h_id, 'text': ara_text})
        eng_hadiths.append({'hadithnumber': h_id, 'text': ''})
        
        links[str(h_id)] = {'lidwa_id': h_id, 'ahmedbaset_id': ''}
        
    ara_out = rf'g:\Box\AntigravitySync\.gemini\antigravity\scratch\hadeeth_id\data\editions\ara-{book}.json'
    eng_out = rf'g:\Box\AntigravitySync\.gemini\antigravity\scratch\hadeeth_id\data\editions\eng-{book}.json'
    
    with open(ara_out, 'w', encoding='utf-8') as f:
        json.dump({'metadata': {'name': f'Arabic {book}'}, 'hadiths': ara_hadiths}, f, ensure_ascii=False, indent=2)
        
    with open(eng_out, 'w', encoding='utf-8') as f:
        json.dump({'metadata': {'name': f'English {book}'}, 'hadiths': eng_hadiths}, f, ensure_ascii=False, indent=2)
        
    link_out = rf'g:\Box\AntigravitySync\.gemini\antigravity\scratch\hadeeth_id\data\links\{book}.json'
    
    tripartite_links = {
        'fawaz_to_lidwa': {str(h_id): str(h_id) for h_id in links.keys()},
        'fawaz_to_ab': {},
        'lidwa_to_fawaz': {str(h_id): str(h_id) for h_id in links.keys()}
    }
    with open(link_out, 'w', encoding='utf-8') as f:
        json.dump(tripartite_links, f, ensure_ascii=False, indent=2)
        
    print(f'Populated {book} baselines and links! ({len(ara_hadiths)} hadiths)')

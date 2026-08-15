import json
import os

books = [('ahmad', 'ahmed'), ('darimi', 'darimi')]

for book, ab_name in books:
    ab_path = rf'g:\Box\AntigravitySync\.gemini\antigravity\scratch\hadeeth_id\data\sources\ahmedbaset\by_book\the_9_books\{ab_name}.json'
    
    with open(ab_path, 'r', encoding='utf-8') as f:
        ab_data = json.load(f)
        
    ara_hadiths = []
    eng_hadiths = []
    links = {}
    
    hadiths = ab_data.get('hadiths', []) if isinstance(ab_data, dict) else ab_data
    
    for h in hadiths:
        h_id = h.get('hadith_id', h.get('id', h.get('idInBook', '')))
        if not h_id: continue
        
        ara_text = h.get('arabic', '')
        eng_obj = h.get('english', {})
        eng_text = ''
        if isinstance(eng_obj, dict):
            eng_text = f"{eng_obj.get('narrator', '')} {eng_obj.get('text', '')}".strip()
            
        ara_hadiths.append({'hadithnumber': h_id, 'text': ara_text})
        eng_hadiths.append({'hadithnumber': h_id, 'text': eng_text})
        
        # 1:1 mapping to lidwa and ab
        links[str(h_id)] = {'lidwa_id': h_id, 'ahmedbaset_id': h_id}
        
    ara_out = rf'g:\Box\AntigravitySync\.gemini\antigravity\scratch\hadeeth_id\data\editions\ara-{book}.json'
    eng_out = rf'g:\Box\AntigravitySync\.gemini\antigravity\scratch\hadeeth_id\data\editions\eng-{book}.json'
    
    with open(ara_out, 'w', encoding='utf-8') as f:
        json.dump({'metadata': {'name': f'Arabic {book}'}, 'hadiths': ara_hadiths}, f, ensure_ascii=False, indent=2)
        
    with open(eng_out, 'w', encoding='utf-8') as f:
        json.dump({'metadata': {'name': f'English {book}'}, 'hadiths': eng_hadiths}, f, ensure_ascii=False, indent=2)
        
    link_out = rf'g:\Box\AntigravitySync\.gemini\antigravity\scratch\hadeeth_id\data\links\{book}.json'
    
    tripartite_links = {
        'fawaz_to_lidwa': {str(h_id): str(h_id) for h_id in links.keys()},
        'fawaz_to_ab': {str(h_id): str(h_id) for h_id in links.keys()},
        'lidwa_to_fawaz': {str(h_id): str(h_id) for h_id in links.keys()}
    }
    with open(link_out, 'w', encoding='utf-8') as f:
        json.dump(tripartite_links, f, ensure_ascii=False, indent=2)
        
    print(f'Populated {book} baselines and links! ({len(ara_hadiths)} hadiths)')

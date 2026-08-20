import os
import json

API_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'api')

for filename in os.listdir(API_DIR):
    if filename.endswith('.ndjson'):
        ndjson_path = os.path.join(API_DIR, filename)
        base_name = filename.replace('.ndjson', '')
        index_path = os.path.join(API_DIR, f"{base_name}_ndjson_index.json")
        
        # We need to compute byte offsets
        id_index = {}
        chapter_index = {}
        current_offset = 0
        
        # To compute bytes exactly, open in 'rb'
        with open(ndjson_path, 'rb') as f:
            for line_bytes in f:
                byte_len = len(line_bytes)
                start_byte = current_offset
                end_byte = current_offset + byte_len - 1
                
                line_str = line_bytes.decode('utf-8')
                item = json.loads(line_str)
                
                item_id = str(item.get('id') or item.get('hadithnumber') or item.get('hadith_number'))
                chapter_id = str(item.get('chapter_id') or item.get('chapter_number') or '')
                
                if item_id and item_id != 'None':
                    id_index[item_id] = [start_byte, end_byte]
                
                if chapter_id and chapter_id != 'None':
                    if chapter_id not in chapter_index:
                        chapter_index[chapter_id] = {'start': start_byte, 'end': end_byte}
                    else:
                        chapter_index[chapter_id]['end'] = end_byte
                        
                current_offset += byte_len
                
        idx_payload = {
            "metadata": {},
            "array_key": None,
            "hadiths": id_index,
            "chapters": chapter_index
        }
        
        with open(index_path, 'w', encoding='utf-8') as idx_f:
            json.dump(idx_payload, idx_f, ensure_ascii=False)
            
        print(f"Re-indexed {ndjson_path}")

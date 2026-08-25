import os
import json

api_dir = 'data/api'
for filename in os.listdir(api_dir):
    if filename.endswith('.ndjson') and not filename.startswith('topics_metadata'):
        ndjson_path = os.path.join(api_dir, filename)
        base_name = filename.replace('.ndjson', '')
        index_path = os.path.join(api_dir, f"{base_name}_ndjson_index.json")
        
        print(f"Rebuilding index for {ndjson_path}...")
        
        # Load existing index just to keep metadata if any
        dict_meta = {}
        array_key = None
        if os.path.exists(index_path):
            with open(index_path, 'r', encoding='utf-8') as f:
                try:
                    old_idx = json.load(f)
                    dict_meta = old_idx.get("metadata", {})
                    array_key = old_idx.get("array_key")
                except:
                    pass

        id_index = {}
        chapter_index = {}
        current_offset = 0
        
        with open(ndjson_path, 'rb') as f:
            for line_bytes in f:
                byte_len = len(line_bytes)
                start_byte = current_offset
                end_byte = current_offset + byte_len - 1
                
                try:
                    item = json.loads(line_bytes.decode('utf-8'))
                    item_id = str(item.get('id') or item.get('hadithnumber') or item.get('hadith_number'))
                    chapter_id = str(item.get('chapter_id') or item.get('chapter_number') or '')
                    
                    if item_id and item_id != 'None':
                        id_index[item_id] = [start_byte, end_byte]
                    
                    if chapter_id and chapter_id != 'None':
                        if chapter_id not in chapter_index:
                            chapter_index[chapter_id] = {'start': start_byte, 'end': end_byte}
                        else:
                            chapter_index[chapter_id]['end'] = end_byte
                except Exception as e:
                    pass
                
                current_offset += byte_len
                
        idx_payload = {
            "metadata": dict_meta,
            "array_key": array_key,
            "hadiths": id_index,
            "chapters": chapter_index
        }
        
        with open(index_path, 'w', encoding='utf-8') as idx_f:
            json.dump(idx_payload, idx_f, ensure_ascii=False)
            
print("Done rebuilding indices.")

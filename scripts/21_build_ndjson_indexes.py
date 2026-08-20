import os
import json
import re

TARGET_DIRS = [
    "data/api",
    "data/sources/lidwa",
    "data/editions"
]

def process_file(filepath):
    # Skip if it's already an ndjson or a new index
    if filepath.endswith('.ndjson') or filepath.endswith('_ndjson_index.json'):
        return

    # Skip books.json
    if os.path.basename(filepath) in ['books.json', 'books_v2.json']:
        return

    # If it's a chunked index from previous script
    if filepath.endswith('_index.json'):
        base_name = filepath.replace('_index.json', '')
        with open(filepath, 'r', encoding='utf-8') as f:
            idx_data = json.load(f)
            
        total_chunks = idx_data.get('total_chunks', 0)
        all_items = []
        is_dict = False
        dict_meta = {}
        array_key = None

        for i in range(1, total_chunks + 1):
            chunk_path = f"{base_name}_{i}.json"
            if not os.path.exists(chunk_path):
                print(f"Error: Missing chunk {chunk_path}")
                return
            with open(chunk_path, 'r', encoding='utf-8') as cf:
                cdata = json.load(cf)
                if isinstance(cdata, list):
                    all_items.extend(cdata)
                elif isinstance(cdata, dict):
                    is_dict = True
                    if 'hadiths' in cdata and isinstance(cdata['hadiths'], list):
                        array_key = 'hadiths'
                        all_items.extend(cdata['hadiths'])
                        if not dict_meta:
                            dict_meta = {k: v for k, v in cdata.items() if k != 'hadiths'}
                    elif 'data' in cdata and isinstance(cdata['data'], list):
                        array_key = 'data'
                        all_items.extend(cdata['data'])
                        if not dict_meta:
                            dict_meta = {k: v for k, v in cdata.items() if k != 'data'}
        
        # Build ndjson
        ndjson_path = f"{base_name}.ndjson"
        index_path = f"{base_name}_ndjson_index.json"
        write_ndjson(ndjson_path, index_path, all_items, dict_meta, array_key)
        
        # Cleanup old chunk files
        os.remove(filepath)
        for i in range(1, total_chunks + 1):
            os.remove(f"{base_name}_{i}.json")
            
        return

    # Skip the chunk files themselves since they are processed by the _index.json block
    if re.search(r'_\d+\.json$', filepath):
        return

    # Normal JSON file processing
    with open(filepath, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            print(f"Skipping {filepath} (invalid json)")
            return

    all_items = []
    dict_meta = {}
    array_key = None

    if isinstance(data, list):
        all_items = data
    elif isinstance(data, dict):
        if 'hadiths' in data and isinstance(data['hadiths'], list):
            array_key = 'hadiths'
            all_items = data['hadiths']
            dict_meta = {k: v for k, v in data.items() if k != 'hadiths'}
        elif 'data' in data and isinstance(data['data'], list):
            array_key = 'data'
            all_items = data['data']
            dict_meta = {k: v for k, v in data.items() if k != 'data'}
        else:
            print(f"Skipping {filepath} (no target array found)")
            return
    else:
        print(f"Skipping {filepath} (not list or dict)")
        return

    base_name = filepath.replace('.json', '')
    ndjson_path = f"{base_name}.ndjson"
    index_path = f"{base_name}_ndjson_index.json"
    write_ndjson(ndjson_path, index_path, all_items, dict_meta, array_key)
    os.remove(filepath)

def write_ndjson(ndjson_path, index_path, items, dict_meta, array_key):
    print(f"Writing {ndjson_path}...")
    
    id_index = {}
    chapter_index = {}
    
    current_offset = 0
    
    with open(ndjson_path, 'wb') as out_f:
        for item in items:
            # We must serialize strictly to a single line
            line_str = json.dumps(item, ensure_ascii=False, separators=(',', ':')) + '\n'
            line_bytes = line_str.encode('utf-8')
            byte_len = len(line_bytes)
            
            # Record start/end
            start_byte = current_offset
            end_byte = current_offset + byte_len - 1
            
            # Determine IDs
            item_id = str(item.get('id') or item.get('hadithnumber') or item.get('hadith_number'))
            chapter_id = str(item.get('chapter_id') or item.get('chapter_number') or '')
            
            if item_id and item_id != 'None':
                id_index[item_id] = [start_byte, end_byte]
            
            if chapter_id and chapter_id != 'None':
                if chapter_id not in chapter_index:
                    chapter_index[chapter_id] = {'start': start_byte, 'end': end_byte}
                else:
                    # Update end byte
                    chapter_index[chapter_id]['end'] = end_byte
                    
            out_f.write(line_bytes)
            current_offset += byte_len
            
    # Write the index
    idx_payload = {
        "metadata": dict_meta,
        "array_key": array_key, # Tells the frontend if it originally lived inside {"hadiths": [...]}
        "hadiths": id_index,
        "chapters": chapter_index
    }
    
    with open(index_path, 'w', encoding='utf-8') as idx_f:
        json.dump(idx_payload, idx_f, ensure_ascii=False)

def main():
    repo_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    
    for d in TARGET_DIRS:
        full_dir = os.path.join(repo_dir, d)
        if not os.path.exists(full_dir):
            continue
            
        for root, dirs, files in os.walk(full_dir):
            for file in files:
                if file.endswith('.json') and not file.endswith('_ndjson_index.json'):
                    filepath = os.path.join(root, file)
                    process_file(filepath)

if __name__ == "__main__":
    main()

import os
import json
import sys
import re

MAX_FILE_SIZE_MB = 15
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

TARGET_DIRS = [
    "data/api",
    "data/sources/lidwa",
    "data/editions"
]

def chunk_file(filepath):
    size = os.path.getsize(filepath)
    if size <= MAX_FILE_SIZE_BYTES:
        return

    print(f"File {filepath} is {size / 1024 / 1024:.2f}MB, splitting...")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    is_dict = isinstance(data, dict)
    
    if is_dict:
        if 'hadiths' in data and isinstance(data['hadiths'], list):
            items = data['hadiths']
            dict_type = 'hadiths'
        elif 'data' in data and isinstance(data['data'], list):
            items = data['data']
            dict_type = 'data'
        else:
            print(f"Skipping {filepath}: Dictionary has no primary list array ('hadiths' or 'data')")
            return
    elif isinstance(data, list):
        items = data
        dict_type = 'list'
    else:
        print(f"Skipping {filepath}: Unsupported JSON format.")
        return
        
    total_items = len(items)
    
    # Estimate items per chunk
    est_bytes_per_item = size / max(1, total_items)
    items_per_chunk = max(1, int(MAX_FILE_SIZE_BYTES / est_bytes_per_item))
    # Be conservative
    items_per_chunk = int(items_per_chunk * 0.9)
    
    base_name, ext = os.path.splitext(filepath)
    
    chunks_created = 0
    for i in range(0, total_items, items_per_chunk):
        chunk_items = items[i:i+items_per_chunk]
        chunks_created += 1
        
        chunk_path = f"{base_name}_{chunks_created}{ext}"
        
        if is_dict:
            # Shallow copy the dict and replace the array
            out_data = dict(data)
            out_data[dict_type] = chunk_items
        else:
            out_data = chunk_items
            
        with open(chunk_path, 'w', encoding='utf-8') as out_f:
            json.dump(out_data, out_f, ensure_ascii=False)
            
        print(f"Created chunk {chunk_path} with {len(chunk_items)} items")

    if chunks_created > 0:
        # Write an index file
        index_path = f"{base_name}_index.json"
        with open(index_path, 'w', encoding='utf-8') as idx_f:
            json.dump({"total_chunks": chunks_created}, idx_f)
            
        print(f"Deleted original massive file: {filepath}")
        os.remove(filepath)

def main():
    repo_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    
    for d in TARGET_DIRS:
        full_dir = os.path.join(repo_dir, d)
        if not os.path.exists(full_dir):
            continue
            
        for root, dirs, files in os.walk(full_dir):
            for file in files:
                # Do not recursively chunk already chunked files!
                if file.endswith(".json") and not "_index.json" in file:
                    # Also exclude _1.json, _2.json regex
                    if re.search(r'_\d+\.json$', file):
                        continue
                        
                    filepath = os.path.join(root, file)
                    if os.path.getsize(filepath) > MAX_FILE_SIZE_BYTES:
                        chunk_file(filepath)

if __name__ == "__main__":
    main()

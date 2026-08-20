import os
import json

def rebuild_index(folder='data/api'):
    for filename in os.listdir(folder):
        if not filename.endswith('.ndjson'): continue
        book = filename.split('.')[0]
        ndjson_path = os.path.join(folder, filename)
        index_path = os.path.join(folder, f"{book}_ndjson_index.json")
        
        index_data = []
        
        with open(ndjson_path, 'rb') as f:
            while True:
                start = f.tell()
                line = f.readline()
                if not line:
                    break
                end = f.tell()
                
                try:
                    text = line.decode('utf-8').strip()
                    if not text: continue
                    obj = json.loads(text)
                    hid = obj.get('id')
                    lidwa_id = obj.get('lidwa_id')
                    
                    if hid is not None:
                        index_data.append({
                            'id': hid,
                            'lidwa_id': lidwa_id,
                            'start': start,
                            'end': end
                        })
                except Exception as e:
                    pass
        
        with open(index_path, 'w', encoding='utf-8') as f:
            json.dump(index_data, f)
        print(f"Rebuilt index for {book}")

if __name__ == '__main__':
    rebuild_index()

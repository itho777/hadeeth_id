import os
import json

def rebuild_index(folder='data/api'):
    for filename in os.listdir(folder):
        if not filename.endswith('.ndjson'): continue
        book = filename.split('.')[0]
        ndjson_path = os.path.join(folder, filename)
        index_path = os.path.join(folder, f"{book}_ndjson_index.json")
        
        index_data = {'hadiths': {}}
        
        with open(ndjson_path, 'rb') as f:
            while True:
                start = f.tell()
                line = f.readline()
                if not line:
                    break
                end = f.tell()
                
                try:
                    # decode to get the JSON payload
                    text = line.decode('utf-8').strip()
                    if not text: continue
                    obj = json.loads(text)
                    hid = str(obj.get('id', ''))
                    lidwa_id = str(obj.get('lidwa_id', ''))
                    
                    if hid:
                        index_data['hadiths'][hid] = [start, end]
                    if lidwa_id and lidwa_id != hid:
                        # Also index by lidwa_id if different, just in case
                        # wait, the original index didn't do this, let's just stick to 'id'
                        # Actually let's just check what the original index had.
                        pass
                except Exception as e:
                    pass
        
        with open(index_path, 'w', encoding='utf-8') as f:
            json.dump(index_data, f)
        print(f"Rebuilt index for {book}")

if __name__ == '__main__':
    rebuild_index()

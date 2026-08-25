
import os
import json
import glob
import io

def rebuild_index(folder):
    for ndjson_path in glob.glob(os.path.join(folder, "*.ndjson")):
        basename = os.path.basename(ndjson_path)
        book = basename.split(".")[0]
        index_path = os.path.join(folder, book + "_ndjson_index.json")
        
        index_data = {}
        
        with open(ndjson_path, "rb") as f:
            while True:
                start = f.tell()
                line = f.readline()
                if not line:
                    break
                end = f.tell()
                
                try:
                    text = line.decode("utf-8").strip()
                    if not text: continue
                    obj = json.loads(text)
                    
                    # Fawaz Ahmed format usually uses hadithnumber or reference.hadith
                    # Let's try hadithnumber first, then arabicnumber, then reference.hadith
                    hid = obj.get("hadithnumber")
                    if hid is None:
                        hid = obj.get("arabicnumber")
                    if hid is None and "reference" in obj and "hadith" in obj["reference"]:
                        hid = obj["reference"]["hadith"]
                        
                    if hid is not None:
                        index_data[str(hid)] = [start, end]
                except Exception as e:
                    pass
        
        with io.open(index_path, "w", encoding="utf-8") as f:
            f.write(unicode(json.dumps(index_data)))
        print("Rebuilt index for " + book)

if __name__ == "__main__":
    rebuild_index("../data/editions")

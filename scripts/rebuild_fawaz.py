import os
import json
import shutil
import glob

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EDITIONS_DIR = os.path.join(BASE_DIR, "data", "editions")
FAWAZ_API_DIR = os.path.join(BASE_DIR, "data", "sources", "fawaz_api", "editions")

FAWAZ_LIST = [
    "ara-bukhari", "ara-bukhari1", "ben-bukhari", "eng-bukhari", "fra-bukhari", "ind-bukhari", "rus-bukhari", "tam-bukhari", "tur-bukhari", "urd-bukhari",
    "ara-muslim", "ara-muslim1", "ben-muslim", "eng-muslim", "fra-muslim", "ind-muslim", "rus-muslim", "tam-muslim", "tur-muslim", "urd-muslim",
    "ara-nasai", "ara-nasai1", "ben-nasai", "eng-nasai", "fra-nasai", "ind-nasai", "tur-nasai", "urd-nasai",
    "ara-abudawud", "ara-abudawud1", "ben-abudawud", "eng-abudawud", "fra-abudawud", "ind-abudawud", "rus-abudawud", "tur-abudawud", "urd-abudawud",
    "ara-tirmidhi", "ara-tirmidhi1", "ben-tirmidhi", "eng-tirmidhi", "ind-tirmidhi", "tur-tirmidhi", "urd-tirmidhi",
    "ara-ibnmajah", "ara-ibnmajah1", "ben-ibnmajah", "eng-ibnmajah", "fra-ibnmajah", "ind-ibnmajah", "tur-ibnmajah", "urd-ibnmajah",
    "ara-malik", "ara-malik1", "ben-malik", "eng-malik", "fra-malik", "ind-malik", "tur-malik", "urd-malik",
    "ara-dehlawi", "ara-dehlawi1", "eng-dehlawi", "fra-dehlawi",
    "ara-nawawi", "ara-nawawi1", "ben-nawawi", "eng-nawawi", "fra-nawawi", "tur-nawawi",
    "ara-qudsi", "ara-qudsi1", "eng-qudsi", "fra-qudsi"
]

print("Cleaning data/editions (ndjson/index files)...")
if os.path.exists(EDITIONS_DIR):
    for f in glob.glob(os.path.join(EDITIONS_DIR, "*.ndjson")):
        os.remove(f)
    for f in glob.glob(os.path.join(EDITIONS_DIR, "*_ndjson_index.json")):
        os.remove(f)
    for f in glob.glob(os.path.join(EDITIONS_DIR, "*.json")):
        if "_ndjson_index" not in f:
            os.remove(f)
else:
    os.makedirs(EDITIONS_DIR, exist_ok=True)

for edition in FAWAZ_LIST:
    src_file = os.path.join(FAWAZ_API_DIR, edition, f"{edition}.min.json")
    if not os.path.exists(src_file):
        src_file = os.path.join(FAWAZ_API_DIR, f"{edition}.min.json")
        
    dest_file = os.path.join(EDITIONS_DIR, f"{edition}.json")
    
    if os.path.exists(src_file):
        shutil.copy2(src_file, dest_file)
    else:
        print(f"[!] Missing {edition} from Fawaz API!")

print("Successfully copied verified Fawaz editions.")

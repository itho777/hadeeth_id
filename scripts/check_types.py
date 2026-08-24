import json
import os
for b in ["bukhari", "muslim", "abudawud", "tirmidhi", "nasai", "ibnmajah", "malik", "darimi", "ahmad"]:
    c_path = f"../data/chapters/{b}.json"
    if os.path.exists(c_path):
        with open(c_path, "r", encoding="utf-8") as f:
            chaps = json.load(f)
            print(f"{b}: type={type(chaps)}")
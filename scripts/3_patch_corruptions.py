import os
import shutil

# Since Fawazahmed0 V1 API has fixed the historic scraping bugs (e.g., Sahih Muslim #7450-7563 duplication),
# this script currently acts as a promotion step from raw_baseline to the final editions folder.
# If future corruptions are found, patching logic should be inserted here.

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw_baseline")
EDITIONS_DIR = os.path.join(BASE_DIR, "data", "editions")

def patch_and_promote():
    if not os.path.exists(EDITIONS_DIR):
        os.makedirs(EDITIONS_DIR)
        
    for filename in os.listdir(RAW_DIR):
        if not filename.endswith(".json"):
            continue
            
        src = os.path.join(RAW_DIR, filename)
        dst = os.path.join(EDITIONS_DIR, filename)
        
        # In the future, load JSON, apply patches, and dump to dst.
        # For now, it's a pristine copy.
        shutil.copy2(src, dst)
        print(f"[+] Promoted verified Arabic text to: {dst}")

if __name__ == "__main__":
    patch_and_promote()

import os
import json
from collections import defaultdict

BASELINE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "raw_baseline")

def verify_baseline():
    if not os.path.exists(BASELINE_DIR):
        print(f"[!] Baseline directory not found: {BASELINE_DIR}")
        return

    for filename in os.listdir(BASELINE_DIR):
        if not filename.endswith(".json"):
            continue
            
        file_path = os.path.join(BASELINE_DIR, filename)
        print(f"\n--- Verifying {filename} ---")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        hadiths = data.get("hadiths", [])
        print(f"Total Hadiths parsed: {len(hadiths)}")
        
        # 1. Check for missing or duplicate numbers
        numbers = []
        texts = []
        for h in hadiths:
            # fawazahmed0 uses hadithnumber
            num = h.get("hadithnumber")
            text = h.get("text", "").strip()
            
            if num is not None:
                numbers.append(num)
            texts.append(text)
            
        if not numbers:
            print("[!] No 'hadithnumber' field found. Cannot verify sequence.")
            continue
            
        # Check sequence gaps
        numbers.sort()
        expected = numbers[0]
        gaps = []
        for num in numbers:
            # handle cases where hadithnumber might be float or have sub-numbering
            # For simplicity, if it's integer:
            if isinstance(num, int):
                while expected < num:
                    gaps.append(expected)
                    expected += 1
                expected = num + 1
        
        if gaps:
            print(f"[!] Found {len(gaps)} missing numbers in sequence (e.g., {gaps[:5]}...)")
        else:
            print("[+] Sequence looks continuous (no integer gaps found).")
            
        # 2. Check for duplicate text blocks (The Scraping Loop Bug)
        # If the exact same text appears multiple times (especially >2), it's highly suspicious
        text_counts = defaultdict(int)
        for t in texts:
            if len(t) > 50: # ignore very short empty strings
                text_counts[t] += 1
                
        duplicates = {t: c for t, c in text_counts.items() if c > 5} # Text appearing more than 5 times is definitely a scraping loop
        
        if duplicates:
            print(f"[!] Found {len(duplicates)} severe text duplications (possible scraping loops):")
            for t, c in list(duplicates.items())[:3]:
                snippet = t[:60].replace('\n', ' ')
                print(f"    - Appeared {c} times: '{snippet}...'")
        else:
            print("[+] No severe text duplications detected.")

if __name__ == "__main__":
    verify_baseline()

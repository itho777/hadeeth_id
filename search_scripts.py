import os
import glob
import re

scratch_dir = r"C:\Users\waverider\.gemini\antigravity\brain\a8b4a1aa-b3d0-485e-90c7-42c1496cd802\scratch"
py_files = glob.glob(os.path.join(scratch_dir, "*.py"))

for pf in py_files:
    with open(pf, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
        if "Ala" in content or "Abdurrahman" in content:
            print(f"File: {os.path.basename(pf)}")
            for line in content.splitlines():
                if "Ala" in line or "Abdurrahman" in line or "Ya'qub" in line:
                    print("  ", line[:120])

import os
import re
import json

base_dir = 'data/sources/usm_grading'
files = {
    'tirmidzi': "Jami' Tirmidhi Grades.txt",
    'ahmad': "Musnad Imam Ahmad Grades.txt",
    'abudaud': "Sunan Abu Dawood Grades.txt",
    'ibnumajah': "Sunan Ibn e Majah Grades.txt",
    'nasai': "Sunan Nisai Grades.txt"
}

out_dir = 'data/sources/usm_parsed'
os.makedirs(out_dir, exist_ok=True)

for book, filename in files.items():
    filepath = os.path.join(base_dir, filename)
    if not os.path.exists(filepath):
        continue
    
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        text = f.read()
    
    grades = {}
    current_grade = None
    
    # Simple state machine to parse grades
    for line in text.split('\n'):
        line = line.strip()
        if not line:
            continue
        
        # Check if line is a grade header (e.g. "Da'if (International Numberings ) :")
        if re.search(r'(Da\'if|Sahih|Hasan|Maudu|Munkar)', line, re.IGNORECASE) and ':' in line:
            current_grade = line.split('(')[0].strip()
            # print("Found grade header:", current_grade)
            continue
            
        # Extract numbers using regex if we are inside a grade block
        if current_grade:
            # find all numbers in the line (it could be like "[ 3, 15, 29 ]" or just comma separated)
            nums = re.findall(r'\b\d+\b', line)
            for num in nums:
                grades[int(num)] = current_grade

    with open(os.path.join(out_dir, f'{book}.json'), 'w', encoding='utf-8') as f:
        json.dump(grades, f, indent=2)

print("Usm12345 parsing complete.")

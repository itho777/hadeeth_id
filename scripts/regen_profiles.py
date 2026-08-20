import re
import json
import os

with open('scholars.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Extract the fallbackScholars array content
match = re.search(r'const fallbackScholars = \[([\s\S]*?)\];', html)
if not match:
    print("Could not find fallbackScholars")
    exit(1)

content = match.group(1)
profiles = re.findall(r'\{\s*id:\s*\'([^\']+)\'(.*?)\}', content)

os.makedirs('data/rawis/profiles', exist_ok=True)

for scholar_id, attrs in profiles:
    profile = {"id": scholar_id}
    
    # Extract each attribute
    name_en = re.search(r'name_en:\s*"([^"]+)"', attrs)
    name_id = re.search(r'name_id:\s*"([^"]+)"', attrs)
    name_ar = re.search(r'name_ar:\s*"([^"]+)"', attrs)
    is_sahabi = re.search(r'is_sahabi:\s*(true|false)', attrs)
    generation = re.search(r'generation:\s*"([^"]+)"', attrs)
    grade = re.search(r'grade:\s*"([^"]+)"', attrs)
    died_ah = re.search(r'died_ah:\s*"([^"]+)"', attrs)
    died_ce = re.search(r'died_ce:\s*"([^"]+)"', attrs)
    hadith_count = re.search(r'hadith_count:\s*(\d+)', attrs)
    city = re.search(r'city_of_death:\s*"([^"]+)"', attrs)
    bio = re.search(r'bio_en:\s*"([^"]+)"', attrs)
    books = re.search(r'books:\s*\[(.*?)\]', attrs)
    
    if name_en: profile["name_en"] = name_en.group(1)
    if name_id: profile["name_id"] = name_id.group(1)
    if name_ar: profile["name_ar"] = name_ar.group(1)
    if is_sahabi: profile["is_sahabi"] = is_sahabi.group(1)
    if generation: profile["generation"] = generation.group(1)
    if grade: profile["grade"] = grade.group(1)
    if died_ah: profile["died_ah"] = died_ah.group(1)
    if died_ce: profile["died_ce"] = died_ce.group(1)
    if hadith_count: profile["hadith_count"] = hadith_count.group(1)
    if city: profile["city_of_death"] = city.group(1)
    if bio: profile["bio_en"] = bio.group(1)
    if books: 
        book_list = re.findall(r'"([^"]+)"', books.group(1))
        profile["books"] = book_list

    with open(f'data/rawis/profiles/{scholar_id}.json', 'w', encoding='utf-8') as pf:
        json.dump(profile, pf, indent=2, ensure_ascii=False)

print("Generated 40 profiles!")

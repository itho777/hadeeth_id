import cloudscraper
from bs4 import BeautifulSoup
import json

with open("test_dorar_output.txt", "r", encoding="utf-8") as f:
    html = f.read()

# find where `<div id="sharh-text-content">` starts
start_idx = html.find('<div id="sharh-text-content">')
html = html[start_idx:]

soup = BeautifulSoup(html, 'html.parser')
sharh_content = soup.find('div', id='sharh-text-content')

result = {
    "hadith_ar": "",
    "rawi": "",
    "muhaddith": "",
    "masdar": "",
    "grade": "",
    "takhrij": "",
    "syarah_ar": "Not Available"
}

if sharh_content:
    first_div = sharh_content.find('div')
    if first_div:
        text_div = first_div.find('div')
        if text_div:
            result["hadith_ar"] = text_div.get_text(strip=True)
            
    for span in sharh_content.find_all('span'):
        classes = span.get('class', [])
        if '#ae8422' in classes or span.get('style') == 'color: #ae8422':
            prev_text = span.parent.get_text()
            if "الراوي" in prev_text: result["rawi"] = span.get_text(strip=True)
            if "المحدث" in prev_text and "خلاصة" not in prev_text: result["muhaddith"] = span.get_text(strip=True)
            if "المصدر" in prev_text: result["masdar"] = span.get_text(strip=True)
            if "خلاصة" in prev_text: result["grade"] = span.get_text(strip=True)
            if "التخريج" in prev_text: result["takhrij"] = span.get_text(strip=True)

    hr = sharh_content.find('hr')
    if hr:
        syarah_parts = []
        for sibling in hr.next_siblings:
            if sibling.name:
                syarah_parts.append(sibling.get_text(separator='\n\n', strip=True))
            elif str(sibling).strip():
                syarah_parts.append(str(sibling).strip())
        result["syarah_ar"] = "\n\n".join(filter(None, syarah_parts))

print(json.dumps(result, ensure_ascii=False, indent=2))

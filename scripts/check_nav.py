import glob
import re

for f in ['index.html', 'books.html', 'scholars.html', 'topics.html', 'profile-detail.html', 'admin.html', 'hadith.html']:
    try:
        with open(f, 'r', encoding='utf-8') as file:
            content = file.read()
            nav_match = re.search(r'<header[^>]*>.*?</header>', content, re.DOTALL | re.IGNORECASE)
            if not nav_match:
                nav_match = re.search(r'<nav[^>]*>.*?</nav>', content, re.DOTALL | re.IGNORECASE)
            
            footer_match = re.search(r'<footer[^>]*>.*?</footer>', content, re.DOTALL | re.IGNORECASE)
            print(f'--- {f} ---')
            if nav_match:
                links = re.findall(r'<a[^>]+href=[\'\"]([^\'\"]+)[\'\"][^>]*>(.*?)</a>', nav_match.group(0), re.IGNORECASE | re.DOTALL)
                print('Nav Links:', [(l[0], re.sub(r'<[^>]+>', '', l[1]).strip()) for l in links])
            if footer_match:
                links = re.findall(r'<a[^>]+href=[\'\"]([^\'\"]+)[\'\"][^>]*>(.*?)</a>', footer_match.group(0), re.IGNORECASE | re.DOTALL)
                print('Footer Links:', [(l[0], re.sub(r'<[^>]+>', '', l[1]).strip()) for l in links])
    except Exception as e:
        print(f"Error reading {f}: {e}")

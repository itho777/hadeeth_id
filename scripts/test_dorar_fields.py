import cloudscraper
from bs4 import BeautifulSoup
import json

scraper = cloudscraper.create_scraper(browser='chrome')
# Let's grab an example. Dorar ID for a known bukhari hadith (e.g. Innamal a'mal binniyat).
response = scraper.get("https://www.dorar.net/hadith/search?q=إنما+الأعمال+بالنيات")
soup = BeautifulSoup(response.text, 'html.parser')
xplain_tag = soup.find('a', attrs={'xplain': True})
if xplain_tag:
    xplain_id = xplain_tag['xplain']
    url = f"https://dorar.net/hadith/sharh/{xplain_id}"
    res = scraper.get(url)
    soup = BeautifulSoup(res.text, 'html.parser')
    tj = soup.find('div', class_='text-justify')
    
    with open("test_dorar_output.txt", "w", encoding="utf-8") as f:
        f.write("--- text-justify ---\n")
        if tj:
            f.write(tj.prettify() + "\n")
            ns = tj.find_next_sibling()
            if ns:
                f.write("--- next sibling ---\n")
                f.write(ns.prettify() + "\n")
                full_text = ns.get_text(separator='\n\n', strip=True)
                f.write("--- full_text ---\n")
                f.write(full_text + "\n")

import urllib.request
import json
import os

BOOKS = ['bukhari', 'muslim', 'abudawud', 'tirmidhi', 'nasai', 'ibnmajah', 'malik']
BASE_URL = 'https://cdn.jsdelivr.net/gh/fawazahmed0/hadith-api@1/editions/ind-{book}.json'
DEST_DIR = r'g:\Box\AntigravitySync\.gemini\antigravity\scratch\hadeeth_id\data\editions'

def download_book(book):
    url = BASE_URL.format(book=book)
    dest = os.path.join(DEST_DIR, f'ind-{book}.json')
    print(f'Downloading {url} ...')
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            with open(dest, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        print(f'  Saved {dest}')
    except Exception as e:
        print(f'  Error: {e}')

def main():
    if not os.path.exists(DEST_DIR):
        os.makedirs(DEST_DIR)
    
    for book in BOOKS:
        download_book(book)
        
    print('All done.')

if __name__ == '__main__':
    main()

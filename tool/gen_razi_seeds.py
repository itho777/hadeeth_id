"""OBSOLETE — do not use for shipped answers.

Asked the live Razi bridge for each starter question. Two replies answered a
hadith question with Qur'an verses and one gave a wrong isnad, so that output
was discarded. Shipped answers are authored against rows read from the CDN:
see `tool/gen_prepared_answers.py`.
"""
import io, json, os, time, urllib.request

ENDPOINT = 'https://razi.hadeeth.id/api/chat'
OUT = os.path.join('assets', 'data', 'razi_seeds.json')

SEEDS = [
    ('id', 'Apa hadis tentang niat dan amal?'),
    ('id', 'Jelaskan sanad hadis tentang riba'),
    ('id', 'Hadis apa saja tentang berbakti kepada orang tua?'),
    ('id', 'Bandingkan riwayat Bukhari dan Muslim tentang ilmu'),
    ('en', 'What hadith discusses intention and deeds?'),
    ('en', 'Explain the isnad of the hadith on riba'),
    ('en', 'Which hadiths speak about kindness to parents?'),
    ('en', 'Compare Bukhari and Muslim on seeking knowledge'),
]


def ask(text, lang):
    body = json.dumps({'message': text, 'lang': lang}).encode()
    req = urllib.request.Request(
        ENDPOINT,
        data=body,
        headers={
            'Content-Type': 'application/json',
            'Origin': 'https://hadeeth.id',
            # Cloudflare rejects the default Python-urllib UA with a 403.
            'User-Agent':
                'Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 '
                '(KHTML, like Gecko) Chrome/126 Mobile Safari/537.36',
        },
    )
    with urllib.request.urlopen(req, timeout=300) as r:
        return json.load(r)


def main():
    data = {}
    if os.path.exists(OUT):
        data = json.load(io.open(OUT, encoding='utf-8'))
    for n, (lang, text) in enumerate(SEEDS, 1):
        key = f'{lang}|{text}'
        if key in data:
            print(f'[{n}/{len(SEEDS)}] cached {lang}')
            continue
        t0 = time.time()
        try:
            d = ask(text, lang)
            reply = (d.get('reply') or '').strip()
        except Exception as e:  # noqa: BLE001
            print(f'[{n}/{len(SEEDS)}] FAIL {lang} {e}')
            continue
        if not reply:
            print(f'[{n}/{len(SEEDS)}] EMPTY {lang}')
            continue
        data[key] = {'lang': lang, 'question': text, 'reply': reply}
        os.makedirs(os.path.dirname(OUT), exist_ok=True)
        with io.open(OUT, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=1)
        print(f'[{n}/{len(SEEDS)}] ok {lang} {len(reply)} chars in {time.time() - t0:.0f}s')
    print('done', len(data))


if __name__ == '__main__':
    main()

import json, os
os.makedirs('data/lidwa-chapters', exist_ok=True)
ch = {
  'title_en_source': 'Lidwa / Irsyad',
  'title_id_source': 'Lidwa / Irsyad',
  'chapters': [
    {
      'chapter_id': '1',
      'title_en': "Musnad Syafi'i",
      'title_id': "Musnad Syafi'i",
      'title_ar': '???? ???????',
      'hadith_range': '1-1800',
      'count': 1800
    }
  ]
}
with open('data/lidwa-chapters/syafii.json', 'w', encoding='utf-8') as f:
    json.dump(ch, f, indent=2, ensure_ascii=False)

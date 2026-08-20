import re
text = open('js/app.js', encoding='utf-8').read()

syafii_dataset = """  syafii: [
    { id: 'native_lidwa',
      label: 'Lidwa Edition', labelId: 'Edisi Lidwa',
      sources: 'AR/ID: IrsyadulIbad / Lidwa SQL (1,800 entries)',
      sourcesId: 'AR/ID: SQL Lidwa / IrsyadulIbad (1.800 entri)',
      note: 'Musnad Syafii dataset originally from IrsyadulIbad', noteId: 'Dataset Musnad Syafii berasal dari IrsyadulIbad' }
  ]
"""

# Insert right before the end of BOOK_DATASETS dict
text = re.sub(
    r'(  nawawi: \[\s*\{.*?\}\s*\]\s*)\};',
    r'\1,\n' + syafii_dataset + r'};',
    text,
    flags=re.DOTALL
)

open('js/app.js', 'w', encoding='utf-8').write(text)

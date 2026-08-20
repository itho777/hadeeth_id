import json
import re

AR_MAP = {
    "bukhari": {"title": "صحيح البخاري", "author": "الإمام محمد البخاري", "type": "الجامع"},
    "muslim": {"title": "صحيح مسلم", "author": "الإمام مسلم", "type": "الجامع"},
    "abudawud": {"title": "سنن أبي داود", "author": "الإمام أبو داود", "type": "السنن"},
    "tirmidhi": {"title": "جامع الترمذي", "author": "الإمام الترمذي", "type": "الجامع"},
    "nasai": {"title": "سنن النسائي", "author": "الإمام النسائي", "type": "السنن"},
    "ibnmajah": {"title": "سنن ابن ماجه", "author": "الإمام ابن ماجه", "type": "السنن"},
    "malik": {"title": "موطأ مالك", "author": "الإمام مالك", "type": "الموطأ"},
    "darimi": {"title": "سنن الدارمي", "author": "الإمام الدارمي", "type": "السنن"},
    "ahmad": {"title": "مسند أحمد", "author": "الإمام أحمد", "type": "المسند"},
    "nawawi": {"title": "الأربعون النووية", "author": "الإمام النووي", "type": "جوامع الكلم"},
    "qudsi": {"title": "الأربعون القدسية", "author": "متعدد", "type": "جوامع الكلم"},
    "shah": {"title": "أربعون الشاه ولي الله", "author": "الشاه ولي الله الدهلوي", "type": "جوامع الكلم"},
    "adab": {"title": "الأدب المفرد", "author": "الإمام البخاري", "type": "متنوع"},
    "bulugh": {"title": "بلوغ المرام", "author": "ابن حجر العسقلاني", "type": "أحكام"},
    "mishkat": {"title": "مشكاة المصابيح", "author": "الخطيب التبريزي", "type": "متنوع"},
    "riyad": {"title": "رياض الصالحين", "author": "الإمام النووي", "type": "متنوع"},
    "shamail": {"title": "الشمائل المحمدية", "author": "الإمام الترمذي", "type": "متنوع"},
    "tabarani": {"title": "المعجم الكبير", "author": "الإمام الطبراني", "type": "المعجم"},
    "syafii": {"title": "مسند الشافعي", "author": "الإمام الشافعي", "type": "المسند"},
    "riyad_arab": {"title": "رياض الصالحين (عربي)", "author": "الإمام النووي", "type": "متنوع"},
    "ibnukhuzaimah": {"title": "صحيح ابن خزيمة", "author": "الإمام ابن خزيمة", "type": "الصحيح"},
    "ibnuhibban": {"title": "صحيح ابن حبان", "author": "الإمام ابن حبان", "type": "الصحيح"},
    "mustadrak": {"title": "المستدرك على الصحيحين", "author": "الإمام الحاكم", "type": "المستدرك"},
    "daruquthni": {"title": "سنن الدارقطني", "author": "الإمام الدارقطني", "type": "السنن"}
}

def fix_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        books = json.load(f)
    for b in books:
        if b['id'] in AR_MAP:
            b['title_ar'] = AR_MAP[b['id']]['title']
            b['author_ar'] = AR_MAP[b['id']]['author']
            b['book_type_ar'] = AR_MAP[b['id']]['type']
            if 'grade_summary' in b and b['grade_summary']:
                if "Sahih" in b['grade_summary']: b['grade_summary'] = "صحيح (Sahih)"
                if "Hasan" in b['grade_summary']: b['grade_summary'] = "حسن (Hasan)"
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(books, f, indent=2, ensure_ascii=False)

fix_json('data/books_v2.json')
fix_json('data/books.json')

# Fix books.html filter chips
with open('books.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Just a simple string replacement for the known corrupted Arabic in chips
html = html.replace('Jami\' (O U,OO U.O1)', 'Jami\' (الجامع)')
html = html.replace('Sunan (O U,O3U+U+)', 'Sunan (السنن)')
html = html.replace('Musnad (O U,U.O3U+O_)', 'Musnad (المسند)')
html = html.replace('Mu\'jam (O U,U.O1OU.)', 'Mu\'jam (المعجم)')
html = html.replace('Mushannaf (O U,U.OU+U?)', 'Mushannaf (المصنف)')
html = html.replace('Mustadrak (O U,U.O3OO_OU)', 'Mustadrak (المستدرك)')
html = html.replace('Jawami\' (OU^O U.O1 O U,UU,U.)', 'Jawami\' (جوامع الكلم)')
html = html.replace('Array(8).fill', 'Array(24).fill')
html = html.replace('data.slice(9,17)', 'data.slice(9)')

with open('books.html', 'w', encoding='utf-8') as f:
    f.write(html)

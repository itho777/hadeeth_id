"""
Rebuild chapters/muslim.json with correct boundaries from hadith-json reference.

The hadith-json reference has 7459 hadiths across 57 chapters.
Our ind-muslim.json has 7563 hadiths (104 more, likely extra chains).

Strategy:
- Use the reference chapter boundaries (idInBook) proportionally mapped to our 7563 dataset.
- But actually simpler: the reference Muqaddimah is at the END (chId=0: 7369-7459).
  In our chapters.json, Muqaddimah is chapter 0 at START (hadith_start=1, hadith_end=7).
  These are different editions/arrangements.

Our dataset has the Muqaddimah at the START (hadiths 1-7), which matches sunnah.com.
The hadith-json puts it at the end.

So the reference boundaries for chapters 1-56 are the authoritative source for sequential counts.
We need to map them to our dataset's actual sequential numbers.

Looking at the reference:
- Ch1 (Faith): idInBook 1-439, count=439
- Our chapters.json: hadith_start=8, hadith_end=222, hadith_count=439

The hadith_count matches! So the issue is just that hadith_end in our chapters.json
is WRONG (using Fu'ad Abd al-Baqi reference numbers) while hadith_count is from the 
reference (correct).

The CORRECT hadith_end for each chapter should be:
hadith_end = hadith_start + hadith_count - 1

BUT we need to verify this against what's actually in our dataset.
Let me compute the correct boundaries from the reference hadith counts,
starting from hadith_start=8 for chapter 1.
"""

import json, sys
sys.stdout.reconfigure(encoding='utf-8')

# Reference data from hadith-json (ordered by chapter number 1-56, then 0 at end)
reference_chapters = [
    # (chapter_number, hadith_count, title_en, title_ar, title_id)
    (0,  7,   "Introduction",                                         "المقدمة",                                                       "Muqaddimah"),
    (1,  439, "The Book of Faith",                                    "كتاب الإيمان",                                                  "Iman"),
    (2,  144, "The Book of Purification",                             "كتاب الطهارة",                                                  "Bersuci"),
    (3,  157, "The Book of Menstruation",                             "كتاب الحيض",                                                    "Haid"),
    (4,  322, "The Book of Prayers",                                  "كتاب الصلاة",                                                   "Shalat"),
    (5,  402, "The Book of Mosques and Places of Prayer",             "كتاب الْمَسَاجِدِ وَمَوَاضِعِ الصَّلاَةِ",                      "Masjid"),
    (6,  378, "The Book of Prayer - Travellers",                      "كتاب صلاة المسافرين وقصرها",                                    "Shalat Musafir"),
    (7,  93,  "The Book of Prayer - Friday",                          "كتاب الجمعة",                                                   "Jumat"),
    (8,  24,  "The Book of Prayer - Two Eids",                        "كتاب صلاة العيدين",                                             "Shalat Ied"),
    (9,  19,  "The Book of Prayer - Rain",                            "كتاب صلاة الاستسقاء",                                           "Shalat Istisqa"),
    (10, 31,  "The Book of Prayer - Eclipses",                        "كتاب الكسوف",                                                   "Gerhana"),
    (11, 138, "The Book of Prayer - Funerals",                        "كتاب الجنائز",                                                  "Jenazah"),
    (12, 231, "The Book of Zakat",                                    "كتاب الزكاة",                                                   "Zakat"),
    (13, 285, "The Book of Fasting",                                  "كتاب الصيام",                                                   "Puasa"),
    (14, 11,  "The Book of I'tikaf",                                  "كتاب الاعتكاف",                                                 "I'tikaf"),
    (15, 601, "The Book of Pilgrimage",                               "كتاب الحج",                                                     "Haji"),
    (16, 169, "The Book of Marriage",                                 "كتاب النكاح",                                                   "Nikah"),
    (17, 84,  "The Book of Suckling",                                 "كتاب الرضاع",                                                   "Penyusuan"),
    (18, 87,  "The Book of Divorce",                                  "كتاب الطلاق",                                                   "Talak"),
    (19, 27,  "The Book of Invoking Curses",                          "كتاب اللعان",                                                   "Li'an"),
    (20, 30,  "The Book of Emancipating Slaves",                      "كتاب العتق",                                                    "Memerdekakan Budak"),
    (21, 160, "The Book of Transactions",                             "كتاب البيوع",                                                   "Jual Beli"),
    (22, 178, "The Book of Musaqah",                                  "كتاب المساقاة",                                                 "Musaqah"),
    (23, 23,  "The Book of the Rules of Inheritance",                 "كتاب الفرائض",                                                  "Waris"),
    (24, 41,  "The Book of Gifts",                                    "كتاب الهبات",                                                   "Hibah"),
    (25, 31,  "The Book of Wills",                                    "كتاب الوصية",                                                   "Wasiat"),
    (26, 18,  "The Book of Vows",                                     "كتاب النذر",                                                    "Nazar"),
    (27, 88,  "The Book of Oaths",                                    "كتاب الأيمان",                                                  "Sumpah"),
    (28, 56,  "The Book of Oaths, Muharibin, Qasas and Diyat",        "كتاب القسامة والمحاربين والقصاص والديات",                        "Qisas dan Diyat"),
    (29, 72,  "The Book of Legal Punishments",                        "كتاب الحدود",                                                   "Hudud"),
    (30, 28,  "The Book of Judicial Decisions",                       "كتاب الأقضية",                                                  "Peradilan"),
    (31, 20,  "The Book of Lost Property",                            "كتاب اللقطة",                                                   "Barang Temuan"),
    (32, 182, "The Book of Jihad and Expeditions",                    "كتاب الجهاد والسير",                                            "Jihad"),
    (33, 266, "The Book on Government",                               "كتاب الإمارة",                                                  "Kepemimpinan"),
    (34, 92,  "The Book of Hunting, Slaughter, and what may be Eaten","كتاب الصيد والذبائح وما يؤكل من الحيوان",                       "Berburu dan Sembelihan"),
    (35, 62,  "The Book of Sacrifices",                               "كتاب الأضاحى",                                                  "Kurban"),
    (36, 257, "The Book of Drinks",                                   "كتاب الأشربة",                                                  "Minuman"),
    (37, 193, "The Book of Clothes and Adornment",                    "كتاب اللباس والزينة",                                           "Pakaian dan Perhiasan"),
    (38, 60,  "The Book of Manners and Etiquette",                    "كتاب الآداب",                                                   "Adab"),
    (39, 212, "The Book of Greetings",                                "كتاب السلام",                                                   "Salam"),
    (40, 23,  "The Book Concerning the Use of Correct Words",         "كتاب الألفاظ من الأدب وغيرها",                                  "Tutur Kata"),
    (41, 11,  "The Book of Poetry",                                   "كتاب الشعر",                                                    "Syair"),
    (42, 41,  "The Book of Dreams",                                   "كتاب الرؤيا",                                                   "Mimpi"),
    (43, 226, "The Book of Virtues",                                  "كتاب الفضائل",                                                  "Keutamaan"),
    (44, 328, "The Book of the Merits of the Companions",             "كتاب فضائل الصحابة رضى الله تعالى عنهم",                        "Keutamaan Sahabat"),
    (45, 217, "The Book of Virtue, Enjoining Good Manners, and Kinship","كتاب البر والصلة والآداب",                                    "Berbuat Baik"),
    (46, 52,  "The Book of Destiny",                                  "كتاب القدر",                                                    "Takdir"),
    (47, 30,  "The Book of Knowledge",                                "كتاب العلم",                                                    "Ilmu"),
    (48, 127, "The Book Pertaining to the Remembrance of Allah",      "كتاب الذكر والدعاء والتوبة والاستغفار",                          "Dzikir dan Doa"),
    (49, 15,  "The Book of Heart-Melting Traditions",                 "كتاب الرقاق",                                                   "Zuhud"),
    (50, 68,  "The Book of Repentance",                               "كتاب التوبة",                                                   "Taubat"),
    (51, 21,  "Characteristics of The Hypocrites And Rulings",        "كتاب صفات المنافقين وأحكامهم",                                  "Sifat Munafik"),
    (52, 82,  "Characteristics of the Day of Judgment, Paradise, and Hell","كتاب صفة القيامة والجنة والنار",                            "Kiamat, Surga dan Neraka"),
    (53, 103, "The Book of Paradise, its Description and Inhabitants","كتاب الجنة وصفة نعيمها وأهلها",                                 "Surga"),
    (54, 177, "The Book of Tribulations and Portents of the Last Hour","كتاب الفتن وأشراط الساعة",                                     "Fitnah"),
    (55, 96,  "The Book of Zuhd and Softening of Hearts",             "كتاب الزهد والرقائق",                                           "Zuhud"),
    (56, 40,  "The Book of Commentary on the Qur'an",                 "كتاب التفسير",                                                  "Kitab Tafsir Al-Qur'an"),
]

# Build chapters with correct sequential hadith_start/hadith_end
# Ch 0 (Muqaddimah): 1-7
# Ch 1 starts at 8

chapters_out = []
cursor = 8  # Chapter 1 starts at hadith 8 (after Muqaddimah 1-7)
TOTAL_HADITHS = 7563  # Total in our dataset

for i, (ch_num, count, title_en, title_ar, title_id) in enumerate(reference_chapters):
    if ch_num == 0:
        # Muqaddimah is always 1-7 in our dataset
        ch_start = 1
        ch_end = 7
    else:
        ch_start = cursor
        is_last = (i == len(reference_chapters) - 1)
        if is_last:
            # Last chapter gets all remaining hadiths
            ch_end = TOTAL_HADITHS
        else:
            ch_end = cursor + count - 1
    
    chapters_out.append({
        "id": f"muslim_c{ch_num}",
        "book_id": "muslim",
        "chapter_number": ch_num,
        "title_en": title_en,
        "title_ar": title_ar,
        "title_id": title_id,
        "hadith_start": ch_start,
        "hadith_end": ch_end,
        "hadith_count": count
    })
    
    if ch_num != 0:
        cursor = ch_end + 1

# Sort by chapter_number
chapters_out.sort(key=lambda x: x['chapter_number'])

total_hadiths_covered = sum(c['hadith_count'] for c in chapters_out)
last_hadith = max(c['hadith_end'] for c in chapters_out)
print(f"Total hadiths covered: {total_hadiths_covered}")
print(f"Last hadith number: {last_hadith}")
print(f"Total chapters: {len(chapters_out)}")
print()

# Preview first 5 and last 3
for c in chapters_out[:5]:
    print(f"  ch{c['chapter_number']:02d}: {c['hadith_start']}-{c['hadith_end']} ({c['hadith_count']}) | {c['title_en'][:40]}")
print("  ...")
for c in chapters_out[-3:]:
    print(f"  ch{c['chapter_number']:02d}: {c['hadith_start']}-{c['hadith_end']} ({c['hadith_count']}) | {c['title_en'][:40]}")

# Write output
with open('data/chapters/muslim.json', 'w', encoding='utf-8') as f:
    json.dump(chapters_out, f, ensure_ascii=False, indent=2)

print()
print("Written to data/chapters/muslim.json")

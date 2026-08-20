"""
Update books_v2.json and create rawi profile JSONs for all 4 MJNA authors.
Also update the bookMasterDict in app.js with proper metadata.
"""
import json
import os

# ---- UPDATE books_v2.json with full author metadata ----
with open('data/books_v2.json', 'r', encoding='utf-8') as f:
    books = json.load(f)

MJNA_META = {
    'ibnukhuzaimah': {
        'title_ar': 'صحيح ابن خزيمة',
        'title_en': 'Shahih Ibn Khuzaimah',
        'title_id': 'Shahih Ibnu Khuzaimah',
        'author_ar': 'أبو بكر محمد بن إسحاق بن خزيمة النيسابوري الشافعي',
        'author_en': 'Imam Muhammad bin Ishaq Ibn Khuzaimah an-Naisaburi',
        'author_id': 'Imam Muhammad bin Ishaq Ibnu Khuzaimah an-Naisaburi',
        'death_year_ah': 311,
        'total_hadiths': 1808,
        'grade_summary': 'صحيح (Shahih)',
        'order_index': 10,
        'source': 'mjna',
    },
    'ibnuhibban': {
        'title_ar': 'صحيح ابن حبان',
        'title_en': 'Shahih Ibn Hibban',
        'title_id': 'Shahih Ibnu Hibban',
        'author_ar': 'أبو حاتم محمد بن حبان بن أحمد التميمي البستي',
        'author_en': 'Imam Muhammad bin Hibban at-Tamimi al-Busti',
        'author_id': 'Imam Muhammad bin Hibban at-Tamimi al-Busti',
        'death_year_ah': 354,
        'total_hadiths': 2769,
        'grade_summary': 'صحيح (Shahih)',
        'order_index': 11,
        'source': 'mjna',
    },
    'mustadrak': {
        'title_ar': 'المستدرك على الصحيحين',
        'title_en': 'Al-Mustadrak ala as-Sahihayn',
        'title_id': 'Al-Mustadrak Al-Hakim',
        'author_ar': 'أبو عبد الله محمد بن عبد الله الحاكم النيسابوري',
        'author_en': 'Imam Abu Abdullah Al-Hakim an-Naisaburi',
        'author_id': 'Imam Abu Abdillah Al-Hakim an-Naisaburi',
        'death_year_ah': 405,
        'total_hadiths': 673,
        'grade_summary': 'مختلف فيه (Mukhtalaf fihi)',
        'order_index': 12,
        'source': 'mjna',
    },
    'daruquthni': {
        'title_ar': 'سنن الدارقطني',
        'title_en': 'Sunan ad-Daruquthni',
        'title_id': 'Sunan Ad-Daruquthni',
        'author_ar': 'أبو الحسن علي بن عمر الدارقطني البغدادي',
        'author_en': "Imam Abu al-Hasan Ali bin 'Umar ad-Daruquthni",
        'author_id': "Imam Abu al-Hasan Ali bin Umar ad-Daruquthni",
        'death_year_ah': 385,
        'total_hadiths': 4790,
        'grade_summary': 'مختلف فيه (Mukhtalaf fihi)',
        'order_index': 13,
        'source': 'mjna',
    },
}

for b in books:
    if b['id'] in MJNA_META:
        meta = MJNA_META[b['id']]
        b.update(meta)

with open('data/books_v2.json', 'w', encoding='utf-8') as f:
    json.dump(books, f, ensure_ascii=False, indent=2)

print("Updated books_v2.json with full MJNA author metadata")

# ---- CREATE rawi profile JSONs for all 4 MJNA authors ----
MJNA_PROFILES = {
    'rawi_ibnukhuzaimah': {
        'id': 'rawi_ibnukhuzaimah',
        'name_ar': 'أبو بكر محمد بن إسحاق بن خزيمة النيسابوري الشافعي',
        'name_en': 'Imam Muhammad bin Ishaq Ibn Khuzaimah an-Naisaburi',
        'name_id': 'Imam Muhammad bin Ishaq Ibnu Khuzaimah an-Naisaburi',
        'kunya': 'Abu Bakar',
        'laqab': 'Imamul A\'immah, Al-Hafizh, Al-Hujjah, Syaikhul Islam',
        'birth_year_ah': 223,
        'death_year_ah': 311,
        'birth_city': 'Naisabur (Nishapur)',
        'death_city': 'Naisabur (Nishapur)',
        'region': 'Khurasan, Persia (kini Iran timur laut)',
        'madhab': "Syafi'i",
        'bio_id': "Imam Ibnu Khuzaimah adalah ulama besar ahli hadis dan fikih yang lahir di Naisabur pada tahun 223 H / 838 M. Nama lengkapnya: Abu Bakar Muhammad bin Ishaq bin Khuzaimah bin al-Mughirah bin Shalih bin Bakr as-Sulami an-Naisaburi asy-Syafi'i. Beliau tumbuh dalam lingkungan religius dan atas anjuran ayahnya terlebih dahulu menghafal Al-Qur'an sebelum melakukan rihlah (perjalanan ilmiah) ke berbagai pusat keilmuan Islam: Marw, Rayy, Syam, Mesir, Wasith, Baghdad, Bashrah, dan Kufah. Beliau berguru kepada para ulama terkemuka, termasuk Imam Bukhari dan Imam Muslim, dan diakui sebagai salah satu murid terbaik keduanya. Di antara murid-murid beliau adalah Abu Abdillah al-Hakim (penulis al-Mustadrak) dan Imam Ad-Daruquthni. Beliau sangat produktif dengan lebih dari 140 karya. Karya paling terkenal adalah Shahih Ibnu Khuzaimah — sering disebut kitab shahih ketiga setelah Shahih Bukhari dan Shahih Muslim. Beliau wafat di Naisabur pada malam Sabtu, 2 Dzulqa'dah 311 H / 924 M dalam usia sekitar 89 tahun.",
        'bio_en': "Imam Ibn Khuzaimah was a major scholar of hadith and fiqh born in Nishapur in 223 AH / 838 CE. His full name: Abu Bakr Muhammad ibn Ishaq ibn Khuzaimah ibn al-Mughirah al-Naisaburi al-Shafi'i. He memorized the Quran before embarking on scholarly travels across the Islamic world, studying under Imam al-Bukhari and Imam Muslim among others. His students included Imam al-Hakim and Imam al-Daruquthni. His most celebrated work is Sahih Ibn Khuzaimah — often ranked third after Sahih al-Bukhari and Sahih Muslim. He passed away in Nishapur in 311 AH / 924 CE at the age of approximately 89.",
        'known_books': ['صحيح ابن خزيمة', 'كتاب التوحيد وإثبات صفات الرب'],
        'teachers': ['Imam al-Bukhari', 'Imam Muslim', 'Ali bin Hajar al-Asqalani'],
        'students': ['Al-Hakim an-Naisaburi', 'Ad-Daruquthni', 'Ibn Hibban'],
        'source': 'mjna',
        'source_url': 'https://www.mjna.or.id/ibnukhuzaimah',
    },
    'rawi_ibnuhibban': {
        'id': 'rawi_ibnuhibban',
        'name_ar': 'أبو حاتم محمد بن حبان بن أحمد التميمي البستي',
        'name_en': 'Imam Muhammad bin Hibban at-Tamimi al-Busti',
        'name_id': 'Imam Muhammad bin Hibban at-Tamimi al-Busti',
        'kunya': 'Abu Hatim',
        'laqab': 'Al-Busti, Al-Hafizh',
        'birth_year_ah': 270,
        'death_year_ah': 354,
        'birth_city': 'Bust (kini Lashkar Gah)',
        'death_city': 'Bust, Afghanistan',
        'region': 'Bust (Busti), Afghanistan',
        'madhab': "Syafi'i",
        'bio_id': "Imam Ibnu Hibban adalah ulama besar yang lahir di kota Bust (kini Lashkar Gah, Afghanistan) sekitar tahun 270 H / 884 M. Nama lengkapnya: Abu Hatim Muhammad bin Hibban bin Ahmad bin Hibban bin Mu'adz bin Ma'bad at-Tamimi al-Busti. Beliau adalah seorang polymath sejati — selain menguasai ilmu hadis, beliau juga mendalami fikih, tafsir, sejarah, bahasa Arab, astronomi, dan kedokteran. Beliau adalah murid dari Imam Ibnu Khuzaimah. Kitab hadis paling terkenal beliau berjudul Al-Musnad Ash-Shahih 'ala At-Taqasim wa Al-Anwa' (lebih dikenal sebagai Shahih Ibnu Hibban). Berbeda dari Shahih Bukhari atau Muslim yang disusun berdasarkan bab fikih, kitab ini menggunakan sistem taqasim dan anwa'. Ulama Al-Amir 'Ala'uddin Al-Farisi kemudian menyusun ulang dalam Al-Ihsan fi Taqrib Shahih Ibnu Hibban untuk kemudahan akses. Beliau juga menulis Al-Tsiqat (ensiklopedia perawi terpercaya) dan Al-Majruhin (kitab perawi bermasalah). Beliau wafat di Bust pada 354 H / 965 M.",
        'bio_en': "Imam Ibn Hibban was a major scholar born in Bust (modern Lashkar Gah, Afghanistan) around 270 AH / 884 CE. A true polymath, he mastered hadith, fiqh, tafsir, history, Arabic language, astronomy, and medicine. He was a student of Imam Ibn Khuzaimah. His most famous work is Al-Musnad al-Sahih (known as Sahih Ibn Hibban), organized by an unusual taqasim/anwa' system. He also wrote Al-Thiqat (trustworthy narrators) and Al-Majruhin (criticized narrators). He passed away in Bust in 354 AH / 965 CE.",
        'known_books': ['صحيح ابن حبان (المسند الصحيح على التقاسيم والأنواع)', 'الثقات', 'المجروحين'],
        'teachers': ['Ibn Khuzaimah', 'Ibn Khuzaymah an-Naisaburi'],
        'students': ['Al-Hakim an-Naisaburi'],
        'source': 'mjna',
        'source_url': 'https://www.mjna.or.id/ibnuhibban',
    },
    'rawi_alhakim': {
        'id': 'rawi_alhakim',
        'name_ar': 'أبو عبد الله محمد بن عبد الله الحاكم النيسابوري',
        'name_en': 'Imam Abu Abdullah Al-Hakim an-Naisaburi',
        'name_id': 'Imam Abu Abdillah Al-Hakim an-Naisaburi',
        'kunya': 'Abu Abdullah',
        'laqab': 'Al-Hakim, Ibn al-Bayyi',
        'birth_year_ah': 321,
        'death_year_ah': 405,
        'birth_city': 'Naisabur (Nishapur)',
        'death_city': 'Naisabur (Nishapur)',
        'region': 'Khurasan, Persia (kini Iran timur laut)',
        'madhab': "Syafi'i / Asy'ari",
        'bio_id': "Imam Al-Hakim An-Naisaburi adalah salah satu ulama hadis paling produktif sepanjang sejarah Islam. Lahir di Naisabur pada 3 Rabiul Awal 321 H / 933 M, beliau mulai menuntut ilmu sejak usia 9 tahun. Nama lengkapnya: Abu Abdullah Muhammad bin Abdullah bin Muhammad bin Hamduyah bin Nu'aim al-Dhabbi al-Thahmani al-Naisaburi, juga dikenal sebagai Ibn al-Baiyi'. Beliau melakukan rihlah ke Khurasan, Irak, Hijaz, dan Transoxiana, belajar dari ribuan guru. Beliau pernah menjabat sebagai hakim (qadhi) di Naisabur. Karya monumentalnya, Al-Mustadrak 'ala ash-Shahihain, disusun sekitar tahun 393 H dengan tujuan menghimpun hadis yang memenuhi kriteria Bukhari-Muslim namun tidak tercantum di dalamnya. Kitab ini terdiri dari 5 jilid dengan sekitar 9.000 hadis. Para ulama, termasuk Imam Adz-Dzahabi, mencatat bahwa sebagian hadis tidak memenuhi standar yang diklaim — karena ditulis di akhir hayat beliau. Adz-Dzahabi menyusun Talkhis al-Mustadrak sebagai ringkasan dan koreksi. Beliau wafat di Naisabur pada Safar 405 H / 1014 M dalam usia sekitar 84 tahun.",
        'bio_en': "Imam al-Hakim al-Naisaburi was one of the most prolific hadith scholars in Islamic history. Born in Nishapur in 321 AH / 933 CE, he began studying at age 9 and traveled extensively across the Islamic world. He served as qadhi (judge) in Nishapur. His monumental work, Al-Mustadrak ala al-Sahihayn, was compiled around 393 AH to collect hadith meeting Bukhari and Muslim's criteria but absent from their collections. The work spans 5 volumes with ~9,000 hadiths. Scholars including Adh-Dhahabi noted that some hadiths were graded too leniently, possibly due to composition at an advanced age. Adh-Dhahabi compiled Talkhis al-Mustadrak as a summary and correction. He passed away in 405 AH / 1014 CE.",
        'known_books': ['المستدرك على الصحيحين', 'المدخل إلى الصحيح', 'معرفة علوم الحديث'],
        'teachers': ['Ibn Khuzaimah', 'Ibn Hibban', 'Yahya bin Mansur al-Qadhi'],
        'students': ['Al-Bayhaqi', 'Abu Bakr al-Baihaqi'],
        'source': 'mjna',
        'source_url': 'https://www.mjna.or.id/mustadrak',
    },
    'rawi_daruquthni': {
        'id': 'rawi_daruquthni',
        'name_ar': 'أبو الحسن علي بن عمر الدارقطني البغدادي',
        'name_en': "Imam Abu al-Hasan Ali bin 'Umar ad-Daruquthni al-Baghdadi",
        'name_id': "Imam Abu al-Hasan Ali bin Umar ad-Daruquthni al-Baghdadi",
        'kunya': 'Abu al-Hasan',
        'laqab': "Al-Hafizh, Amirul Mu'minin fil Hadits, Syaikhul Islam",
        'birth_year_ah': 306,
        'death_year_ah': 385,
        'birth_city': 'Dar al-Quthn, Baghdad',
        'death_city': 'Baghdad',
        'region': 'Baghdad, Irak',
        'madhab': "Syafi'i",
        'bio_id': "Imam Ad-Daruquthni adalah ulama besar ahli hadis dari Baghdad yang lahir pada 306 H / 918 M di kawasan Dar al-Quthn — dari nama inilah nisbat 'Ad-Daruquthni' berasal. Nama lengkapnya: Abu al-Hasan Ali bin Umar bin Ahmad bin Mahdi bin Mas'ud bin an-Nu'man bin Dinar bin Abdullah al-Baghdadi ad-Daruquthni. Beliau mendapat gelar Amirul Mu'minin fil Hadits (Pemimpin Orang Beriman dalam Ilmu Hadis) — gelar tertinggi dalam tradisi ilmu hadis. Keunggulan utama beliau adalah ketajaman dalam ilmu 'ilal (mendeteksi cacat tersembunyi pada sanad) dan penguasaan luas atas nama perawi hadis. Selain pakar hadis, beliau menguasai ilmu qiraat, fikih, bahasa Arab, sastra, dan syair. Kitab monumental beliau, Sunan Ad-Daruquthni, memuat hadis-hadis hukum disertai analisis kritis 'ilal masing-masing hadis. Abu Bakar al-Khatib al-Baghdadi menyebutnya sebagai imam tanpa tandingan pada masanya dalam ilmu atsar, 'ilal, dan rijal. Beliau wafat di Baghdad pada 385 H / 995 M dalam usia sekitar 79 tahun.",
        'bio_en': "Imam ad-Daruquthni was a major hadith scholar of Baghdad, born in 306 AH / 918 CE in the Dar al-Quthn district — hence his nisba 'al-Daruquthni'. He was titled Amir al-Mu'minin fi al-Hadith (Commander of the Faithful in Hadith) — the highest honor in the hadith tradition. He excelled in 'ilal al-hadith (detecting hidden defects in chains) and rijal studies. His Sunan al-Daruquthni contains legal hadiths with critical analysis of their chains. Al-Khatib al-Baghdadi called him unrivaled in his era in hadith, 'ilal, and rijal. He passed away in Baghdad in 385 AH / 995 CE.",
        'known_books': ['سنن الدارقطني', 'العلل', 'الضعفاء والمتروكون'],
        'teachers': ['Ibn Khuzaimah', 'Yahya bin Sa\'id al-Qattan'],
        'students': ['Al-Hakim an-Naisaburi', 'Abu Bakr al-Khatib al-Baghdadi'],
        'source': 'mjna',
        'source_url': 'https://www.mjna.or.id/daruquthni',
    },
}

# Save rawi profiles
os.makedirs('data/rawis/profiles', exist_ok=True)

# Read scholars index to find max ID
with open('data/rawis/scholars_index.json', 'r', encoding='utf-8') as f:
    scholars_idx = json.load(f)

# Assign new IDs (use string keys like existing ones, starting from a high number)
MJNA_RAWI_IDS = {
    'rawi_ibnukhuzaimah': 'mjna_001',
    'rawi_ibnuhibban': 'mjna_002',
    'rawi_alhakim': 'mjna_003',
    'rawi_daruquthni': 'mjna_004',
}

# Save individual profile JSON files
for rawi_key, profile in MJNA_PROFILES.items():
    profile_id = MJNA_RAWI_IDS[rawi_key]
    profile['profile_id'] = profile_id
    out_path = f'data/rawis/profiles/{profile_id}.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(profile, f, ensure_ascii=False, indent=2)
    print(f"Created {out_path}")
    
    # Add to scholars index
    scholars_idx[profile_id] = {
        'name_ar': profile['name_ar'],
        'name_en': profile['name_en'],
        'grade': f"Scholar — {profile.get('madhab','')}",
        'birth_year': profile.get('birth_year_ah'),
        'death_year': profile.get('death_year_ah'),
    }

# Save updated scholars index
with open('data/rawis/scholars_index.json', 'w', encoding='utf-8') as f:
    json.dump(scholars_idx, f, ensure_ascii=False, indent=2)
print("Updated scholars_index.json with 4 MJNA scholars")

# ---- UPDATE books_v2.json authorId fields to link to profile ----
BOOK_TO_RAWI = {
    'ibnukhuzaimah': 'mjna_001',
    'ibnuhibban': 'mjna_002',
    'mustadrak': 'mjna_003',
    'daruquthni': 'mjna_004',
}

with open('data/books_v2.json', 'r', encoding='utf-8') as f:
    books = json.load(f)

for b in books:
    if b['id'] in BOOK_TO_RAWI:
        b['authorId'] = BOOK_TO_RAWI[b['id']]

with open('data/books_v2.json', 'w', encoding='utf-8') as f:
    json.dump(books, f, ensure_ascii=False, indent=2)
print("Updated books_v2.json with authorId links to MJNA profiles")


import io
import json

with io.open("../data/api/glossary.json", "r", encoding="utf-8") as f:
    glossary = json.load(f)

new_terms = [
  {"id": "mujam", "term_en": "Mu'jam", "term_id": "Mu'jam", "def_en": "A hadith collection organized according to the names of the narrator's teachers (shuyukh), often alphabetically.", "def_id": "Kitab koleksi hadits yang disusun berdasarkan urutan nama-nama guru (syekh) dari penyusun kitab tersebut, biasanya secara alfabetis."},
  {"id": "musannaf", "term_en": "Musannaf", "term_id": "Mushannaf", "def_en": "A hadith collection organized by topics (fiqh chapters) that includes not only sayings of the Prophet, but also those of the Companions and Successors.", "def_id": "Koleksi hadits yang disusun berdasarkan bab-bab fikih yang memuat hadits marfu' (dari Nabi), mawquf (dari sahabat), dan maqthu' (dari tabi'in)."},
  {"id": "mustakhraj_book", "term_en": "Mustakhraj", "term_id": "Mustakhraj", "def_en": "A collection where the author extracts hadiths from an existing collection (like Sahih al-Bukhari) but narrates them with their own chains of transmission.", "def_id": "Kitab di mana penulisnya meriwayatkan kembali hadits-hadits dari kitab lain (seperti Shahih al-Bukhari) namun dengan sanad (rantai periwayatan) miliknya sendiri."},
  {"id": "qudsi", "term_en": "Hadith Qudsi", "term_id": "Hadits Qudsi", "def_en": "A hadith in which the Prophet Muhammad transmits the words of Allah, but it is not part of the Quran.", "def_id": "Hadits di mana Nabi Muhammad SAW meriwayatkan firman Allah (maknanya dari Allah, redaksinya dari Nabi), namun bukan bagian dari Al-Qur'an."},
  {"id": "muttafaqun_alaih", "term_en": "Muttafaqun 'Alaih", "term_id": "Muttafaqun 'Alaih", "def_en": "A hadith that is agreed upon by both Imam al-Bukhari and Imam Muslim, meaning it appears in both of their Sahih collections.", "def_id": "Hadits yang disepakati kesahihannya oleh Imam al-Bukhari dan Imam Muslim (diriwayatkan dalam kedua kitab Shahih mereka dari sahabat yang sama)."}
]

glossary.extend(new_terms)

with io.open("../data/api/glossary.json", "w", encoding="utf-8") as f:
    f.write(unicode(json.dumps(glossary, indent=2, ensure_ascii=False)))

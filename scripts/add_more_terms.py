
import io
import json

with io.open("../data/api/glossary.json", "r", encoding="utf-8") as f:
    glossary = json.load(f)

new_terms = [
  {"id": "syarah", "term_en": "Syarah", "term_id": "Syarah", "def_en": "Commentary or explanation of a book or hadith collection, providing detailed insights into its meanings, grammar, and rulings.", "def_id": "Penjelasan atau komentar terhadap suatu kitab atau kumpulan hadits yang menguraikan makna, tata bahasa, dan hukum-hukum di dalamnya."},
  {"id": "tsiqah", "term_en": "Tsiqah", "term_id": "Tsiqah", "def_en": "Trustworthy narrator. A narrator who is both just ('Adl) and precise in memory/preservation (Dhabit).", "def_id": "Perawi yang terpercaya, yaitu perawi yang memiliki kejujuran/keadilan ('Adl) serta kuat hafalan dan penjagaannya terhadap hadits (Dhabit)."},
  {"id": "atsar", "term_en": "Atsar", "term_id": "Atsar", "def_en": "Statements or actions attributed to someone other than the Prophet, typically the Companions (Sahabah) or Successors (Tabi'in).", "def_id": "Ucapan atau perbuatan yang disandarkan kepada selain Rasulullah SAW, yakni kepada para sahabat dan tabi'in."},
  {"id": "marfu", "term_en": "Marfu'", "term_id": "Marfu'", "def_en": "A statement, action, or approval directly attributed to the Prophet Muhammad.", "def_id": "Suatu ucapan, perbuatan, atau persetujuan yang secara langsung disandarkan kepada Rasulullah SAW."},
  {"id": "mauquf", "term_en": "Mauquf", "term_id": "Mauquf", "def_en": "A statement or action attributed to a Companion (Sahabi) of the Prophet, stopping at them rather than reaching the Prophet.", "def_id": "Suatu ucapan atau perbuatan yang disandarkan kepada sahabat Nabi (terhenti pada sahabat)."},
  {"id": "jayyid", "term_en": "Jayyid", "term_id": "Jayyid", "def_en": "Good or excellent. Used by scholars as another term for a Sahih (authentic) hadith.", "def_id": "Bagus. Istilah lain yang sering digunakan oleh para ulama untuk menyebut hadits yang berderajat Shahih."},
  {"id": "muhaddits", "term_en": "Muhaddits", "term_id": "Muhaddits", "def_en": "A scholar of hadith who occupies themselves with the science of narration and hadith jurisprudence, and knows many narrators and their conditions.", "def_id": "Ulama ahli hadits yang menyibukkan diri dengan ilmu riwayat dan dirayat (fikih hadits), serta banyak mengetahui keadaan para perawi."},
  {"id": "al_hafizh", "term_en": "Al-Hafizh", "term_id": "Al-Hafizh", "def_en": "A title for a hadith scholar of very high rank who knows more narrators in every level of the chain than those they do not know.", "def_id": "Gelar bagi ulama hadits yang kedudukannya lebih tinggi dari muhaddits, yang lebih banyak mengetahui perawi di setiap tingkatan sanad daripada yang tidak ia ketahui."},
  {"id": "majhul", "term_en": "Majhul", "term_id": "Majhul", "def_en": "An unknown narrator. A narrator whose reliability is neither affirmed nor discredited because they are not well known among scholars.", "def_id": "Perawi yang tidak dikenal jati dirinya atau tidak diketahui kredibilitasnya oleh para ulama kritikus hadits, sehingga haditsnya cenderung dihukumi lemah."},
  {"id": "jarh", "term_en": "Jarh", "term_id": "Jarh", "def_en": "Criticism or invalidation of a narrator's reliability, rendering their narration weak or rejected.", "def_id": "Kritik atau pencacatan terhadap keadilan dan hafalan perawi yang menyebabkan riwayatnya menjadi lemah atau ditolak."},
  {"id": "tadil", "term_en": "Ta'dil", "term_id": "Ta'dil", "def_en": "Validation or declaration of a narrator as just, reliable, and trustworthy.", "def_id": "Penilaian adil terhadap seorang perawi, yang menyatakan bahwa perawi tersebut terpercaya dan dapat diterima riwayatnya."}
]

# Check if terms already exist to avoid duplicates
existing_ids = set([item["id"] for item in glossary])
for term in new_terms:
    if term["id"] not in existing_ids:
        glossary.append(term)

with io.open("../data/api/glossary.json", "w", encoding="utf-8") as f:
    f.write(unicode(json.dumps(glossary, indent=2, ensure_ascii=False)))

print("Added {} terms.".format(len(new_terms)))

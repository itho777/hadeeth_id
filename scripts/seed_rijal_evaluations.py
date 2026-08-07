import requests
import json

headers = {
    "apikey": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imlkb2t5c3Bva2VuYm16b2VnYWhxIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4NjAwODMwMywiZXhwIjoyMTAxNTg0MzAzfQ.7A9HplPzO5Hp1ZinOPquIymil1PRQzjrxmbdt6Wng-c",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imlkb2t5c3Bva2VuYm16b2VnYWhxIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4NjAwODMwMywiZXhwIjoyMTAxNTg0MzAzfQ.7A9HplPzO5Hp1ZinOPquIymil1PRQzjrxmbdt6Wng-c",
    "Content-Type": "application/json"
}
base = "https://idokyspokenbmzoegahq.supabase.co/rest/v1/"

evaluations = [
    {
        "rawi_id": "rawi_abu_hurairah",
        "evaluator_en": "Ibn Hajar al-Asqalani",
        "evaluator_ar": "ابن حجر العسقلاني",
        "verdict_en": "Sahabi Adl (Utmost Reliability)",
        "verdict_ar": "صحابي جليل",
        "quote_en": "Sahabi Jaleel, the most prolific narrator of Hadith among the Companions. All Companions are trustworthy by consensus.",
        "quote_ar": "صحابي جليل أجمع المسلمون على عدالته وهو أكثر الصحابة حديثاً عن النبي صلى الله عليه وسلم.",
        "source_book_en": "Taqrib al-Tahdhib",
        "source_vol": "1",
        "source_page": "681"
    },
    {
        "rawi_id": "rawi_abu_hurairah",
        "evaluator_en": "Al-Dhahabi",
        "evaluator_ar": "الذهبي",
        "verdict_en": "Hafiz al-Sahabah",
        "verdict_ar": "حافظ الصحابة",
        "quote_en": "The Master Hafiz of the Companions, gifted with unparalleled memory through the supplication of the Prophet ﷺ.",
        "quote_ar": "إمام الحفاظ وسيد من حفظ الحديث في عصره بدعوة النبي صلى الله عليه وسلم له.",
        "source_book_en": "Siyar A'lam al-Nubala",
        "source_vol": "2",
        "source_page": "578"
    },
    {
        "rawi_id": "rawi_umar_ibn_al_khattab",
        "evaluator_en": "Ibn Hajar al-Asqalani",
        "evaluator_ar": "ابن حجر العسقلاني",
        "verdict_en": "Sahabi Jaleel (Al-Farooq)",
        "verdict_ar": "صحابي أمير المؤمنين",
        "quote_en": "Commander of the Faithful. Highly cautious in narration and established rigorous standards for hadith verification.",
        "quote_ar": "أمير المؤمنين الفاروق، كان شديد التثبت في قبول الروايات.",
        "source_book_en": "Tahdhib al-Tahdhib",
        "source_vol": "7",
        "source_page": "438"
    },
    {
        "rawi_id": "rawi_aisha_bint_abi_bakr",
        "evaluator_en": "Al-Zuhri",
        "evaluator_ar": "الزهري",
        "verdict_en": "A'lam al-Nas (Most Knowledgeable Woman)",
        "verdict_ar": "أعلم الناس",
        "quote_en": "If the knowledge of all women was gathered alongside the Mother of Believers 'Aisha, 'Aisha's knowledge would excel.",
        "quote_ar": "لو جمع علم الناس كلهم وعلم أزواج النبي صلى الله عليه وسلم لكانت عائشة أوسعهم علماً.",
        "source_book_en": "Al-Mustadrak",
        "source_vol": "4",
        "source_page": "11"
    },
    {
        "rawi_id": "rawi_ibn_shihab_al_zuhri",
        "evaluator_en": "Ibn Ma'in",
        "evaluator_ar": "يحيى بن معين",
        "verdict_en": "Thiqah Hafiz (Unanimously Trustworthy)",
        "verdict_ar": "ثقة ثبت حافظ",
        "quote_en": "Al-Zuhri is the most trustworthy of all people in Hadith, the ocean of knowledge of Madinah.",
        "quote_ar": "الزهري أثبت الناس في الحديث وأعلمهم بالسنة.",
        "source_book_en": "Tarikh Ibn Ma'in",
        "source_vol": "1",
        "source_page": "142"
    },
    {
        "rawi_id": "rawi_said_bin_jubair",
        "evaluator_en": "Sufyan al-Thawri",
        "evaluator_ar": "سفيان الثوري",
        "verdict_en": "Imam fi al-Tafsir wa al-Hadith",
        "verdict_ar": "إمام التابعين",
        "quote_en": "Learn Quranic explanation from Sa'id bin Jubair, for he is the master scholar among the Successors.",
        "quote_ar": "خذوا التفسير عن سعيد بن جبير فإنه من أعلم التابعين بالتنزيل.",
        "source_book_en": "Tahdhib al-Tahdhib",
        "source_vol": "4",
        "source_page": "11"
    },
    {
        "rawi_id": "rawi_yahya_bin_said",
        "evaluator_en": "Ahmad bin Hanbal",
        "evaluator_ar": "أحمد بن حنبل",
        "verdict_en": "Thiqah Thiqah (Highest Reliability)",
        "verdict_ar": "ثقة ثقة ثبت",
        "quote_en": "Yahya bin Sa'id is among the firmest pillars of Hadith transmission in Madinah.",
        "quote_ar": "يحيى بن سعيد الأنصاري أثبت الناس وأصحهم حديثاً.",
        "source_book_en": "Al-Jarh wa al-Ta'dil",
        "source_vol": "9",
        "source_page": "140"
    }
]

print("Seeding classical Rijal Evaluations into Supabase...")
r = requests.post(f"{base}/rijal_evaluations", headers=headers, json=evaluations)
if r.status_code in (200, 201):
    print(f"✅ Successfully inserted {len(evaluations)} scholarly evaluations into Supabase `rijal_evaluations` table!")
else:
    print(f"Error seeding evaluations: {r.status_code} {r.text}")

import json
import os

translations = {
    1: {"id": "Iman", "en": "Faith"},
    2: {"id": "Ilmu", "en": "Knowledge"},
    3: {"id": "Ummat-ummat terdahulu", "en": "Preceding Nations"},
    4: {"id": "Siroh (perjalanan hidup)", "en": "Prophetic Biography (Seerah)"},
    5: {"id": "Al Qur'an", "en": "The Quran"},
    6: {"id": "Akhlaq dan adab", "en": "Morals and Manners"},
    7: {"id": "Ibadat", "en": "Acts of Worship"},
    8: {"id": "Minuman dan makanan", "en": "Food and Drink"},
    9: {"id": "Pakaian dan perhiasan", "en": "Clothing and Adornment"},
    10: {"id": "Masalah kepribadian individu", "en": "Personal Affairs"},
    11: {"id": "Mu'amalat", "en": "Transactions and Trade"},
    12: {"id": "Keputusan, hakim dan hukum-hukum", "en": "Judgments and Rulings"},
    13: {"id": "Kriminalitas", "en": "Crimes and Penalties"},
    14: {"id": "Jihad", "en": "Jihad"}
}

out_data = []
for k, v in translations.items():
    out_data.append({
        "tag_id": k,
        "name_id": v["id"],
        "name_en": v["en"]
    })

with open('data/lidwa_extracts/topic_tags.json', 'w', encoding='utf-8') as f:
    json.dump(out_data, f, indent=2, ensure_ascii=False)

print("Topic tags translated and saved to data/lidwa_extracts/topic_tags.json")

import re

with open('scholars.html', 'r', encoding='utf-8') as f:
    html = f.read()

missing_authors_2 = """
      { id: 'rawi_tabarani', name_en: "Imam at-Tabarani", name_id: "Imam at-Thabarani", name_ar: "الطبراني", is_sahabi: false, generation: "Collector", grade: "Imam Hafiz", died_ah: "360", died_ce: "971", hadith_count: 25000, books: ["Al-Mujam al-Kabir"], city_of_death: "Isfahan", bio_en: "Compiler of the three massive Mu'jam collections of Hadith." },
      { id: 'rawi_ibn_khuzaimah', name_en: "Imam Ibn Khuzaimah", name_id: "Imam Ibnu Khuzaimah", name_ar: "ابن خزيمة", is_sahabi: false, generation: "Collector", grade: "Imam Hafiz Faqih", died_ah: "311", died_ce: "924", hadith_count: 3079, books: ["Shahih Ibn Khuzaimah"], city_of_death: "Nishapur", bio_en: "Known as 'Imam of Imams', author of one of the most authentic collections after the Sahihayn." },
      { id: 'rawi_ibn_hibban', name_en: "Imam Ibn Hibban", name_id: "Imam Ibnu Hibban", name_ar: "ابن حبان", is_sahabi: false, generation: "Collector", grade: "Imam Hafiz", died_ah: "354", died_ce: "965", hadith_count: 7491, books: ["Shahih Ibn Hibban"], city_of_death: "Bust", bio_en: "Author of Sahih Ibn Hibban, highly regarded for his strict conditions of authenticity." },
      { id: 'rawi_al_hakim', name_en: "Imam al-Hakim", name_id: "Imam al-Hakim an-Naisaburi", name_ar: "الحاكم النيسابوري", is_sahabi: false, generation: "Collector", grade: "Imam Hafiz", died_ah: "405", died_ce: "1014", hadith_count: 8803, books: ["Al-Mustadrak ala as-Sahihayn"], city_of_death: "Nishapur", bio_en: "Compiler of Al-Mustadrak, collecting Sahih hadiths that met the conditions of Bukhari and Muslim." },
      { id: 'rawi_daraqutni', name_en: "Imam ad-Daraqutni", name_id: "Imam ad-Daruquthni", name_ar: "الدارقطني", is_sahabi: false, generation: "Collector", grade: "Imam Hafiz", died_ah: "385", died_ce: "995", hadith_count: 4836, books: ["Sunan ad-Daruquthni"], city_of_death: "Baghdad", bio_en: "Master of 'Ilal (hidden defects in Hadith) and compiler of the famous Sunan." },
"""

if 'rawi_tabarani' not in html:
    html = html.replace("const fallbackScholars = [\n", "const fallbackScholars = [\n" + missing_authors_2)
    with open('scholars.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("Added the remaining 5 authors to scholars.html.")
else:
    print("Already added.")

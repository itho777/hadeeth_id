import re
import json

with open('scholars.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Update fallbackScholars to include the missing ones
missing_authors = """
      { id: 'rawi_darimi', name_en: "Imam ad-Darimi", name_id: "Imam ad-Darimi", name_ar: "الدارمي", is_sahabi: false, generation: "Collector", grade: "Imam Hafiz", died_ah: "255", died_ce: "869", hadith_count: 3500, books: ["Sunan ad-Darimi"], city_of_death: "Samarqand", bio_en: "Compiler of Sunan ad-Darimi, highly respected scholar of Khorasan." },
      { id: 'rawi_nawawi', name_en: "Imam an-Nawawi", name_id: "Imam an-Nawawi", name_ar: "النووي", is_sahabi: false, generation: "Collector", grade: "Imam Hafiz Faqih", died_ah: "676", died_ce: "1277", hadith_count: 2795, books: ["Forty Nawawi", "Riyad as-Salihin"], city_of_death: "Nawa", bio_en: "Prominent Shafi'i jurist and author of Arba'in and Riyad as-Salihin." },
      { id: 'rawi_syafii', name_en: "Imam as-Syafi'i", name_id: "Imam as-Syafi'i", name_ar: "الشافعي", is_sahabi: false, generation: "Collector", grade: "Imam Mujtahid", died_ah: "204", died_ce: "820", hadith_count: 2500, books: ["Musnad as-Syafi'i"], city_of_death: "Fustat", bio_en: "Founder of Shafi'i Madhhab and architect of Islamic Jurisprudence (Usul al-Fiqh)." },
      { id: 'rawi_ibn_hajar', name_en: "Ibn Hajar al-Asqalani", name_id: "Ibnu Hajar al-Asqalani", name_ar: "ابن حجر العسقلاني", is_sahabi: false, generation: "Collector", grade: "Hafiz / Amir al-Mu'minin fi al-Hadith", died_ah: "852", died_ce: "1449", hadith_count: 1596, books: ["Bulugh al-Maram"], city_of_death: "Cairo", bio_en: "The greatest Hadith commentator, author of Fath al-Bari and Bulugh al-Maram." },
      { id: 'rawi_baghawi', name_en: "Imam al-Baghawi", name_id: "Imam al-Baghawi", name_ar: "البغوي", is_sahabi: false, generation: "Collector", grade: "Imam Hafiz", died_ah: "516", died_ce: "1122", hadith_count: 5945, books: ["Mishkat al-Masabih"], city_of_death: "Marw", bio_en: "Reviver of Sunnah, author of Masabih as-Sunnah (expanded into Mishkat)." },
      { id: 'rawi_waliullah', name_en: "Shah Waliullah ad-Dahlawi", name_id: "Shah Waliullah ad-Dahlawi", name_ar: "شاه ولي الله الدهلوي", is_sahabi: false, generation: "Collector", grade: "Imam Mujaddid", died_ah: "1176", died_ce: "1762", hadith_count: 40, books: ["Shah Waliullah's Arba'in"], city_of_death: "Delhi", bio_en: "Great reviver of Islam in the Indian subcontinent." },
"""

# Find where the fallbackScholars array starts and insert the missing authors at the end of the array.
if 'rawi_darimi' not in html:
    html = html.replace("const fallbackScholars = [", "const fallbackScholars = [\n" + missing_authors)


# 2. Modify fetchAndRenderScholars to merge validNarrators with filterFallbackScholars
target_merge = """          const validNarrators = (data || []).filter(r => (r.hadith_count > 0 || r.is_sahabi) && r.name_en && !r.name_en.includes('Kampung'));
          allScholars = validNarrators.length > 0 ? validNarrators : filterFallbackScholars(gen, role, query);"""

replacement_merge = """          const validNarrators = (data || []).filter(r => (r.hadith_count > 0 || r.is_sahabi) && r.name_en && !r.name_en.includes('Kampung'));
          // Merge Supabase validNarrators with fallbackScholars to ensure offline/local kitabs are included
          const localScholars = filterFallbackScholars(gen, role, query);
          const merged = [...validNarrators];
          localScholars.forEach(local => {
             if (!merged.find(m => m.name_en === local.name_en || m.id === local.id)) {
                 merged.push(local);
             }
          });
          allScholars = merged;"""

if target_merge in html:
    html = html.replace(target_merge, replacement_merge)

with open('scholars.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("Patched scholars.html with merged Supabase + Fallback logic.")

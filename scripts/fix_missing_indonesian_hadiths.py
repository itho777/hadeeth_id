import requests

headers = {
    "apikey": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imlkb2t5c3Bva2VuYm16b2VnYWhxIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4NjAwODMwMywiZXhwIjoyMTAxNTg0MzAzfQ.7A9HplPzO5Hp1ZinOPquIymil1PRQzjrxmbdt6Wng-c",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imlkb2t5c3Bva2VuYm16b2VnYWhxIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4NjAwODMwMywiZXhwIjoyMTAxNTg0MzAzfQ.7A9HplPzO5Hp1ZinOPquIymil1PRQzjrxmbdt6Wng-c",
    "Content-Type": "application/json",
    "Prefer": "return=minimal"
}
base = "https://idokyspokenbmzoegahq.supabase.co/rest/v1/"

# Standard Kemenag translation for Sahih al-Bukhari #4
bukhari_4_id = "Ibnu Syihab berkata; Dan telah mengabarkan kepadaku [Abu Salamah bin Abdurrahman] bahwa [Jabir bin Abdullah Al Anshari] bercerita tentang terhentinya wahyu, beliau bersabda dalam haditsnya: \"Ketika aku sedang berjalan, tiba-tiba aku mendengar suara dari langit. Aku mendongakkan pandanganku, ternyata Malaikat yang pernah mendatangi aku di Gua Hira sedang duduk di atas kursi antara langit dan bumi. Maka aku merasa takut kepadanya, lalu aku pulang dan berkata: Selimutilah aku! Maka Allah Ta'ala menurunkan ayat: {Wahai orang yang berselimut, bangunlah lalu berilah peringatan} sampai {dan perbuatan dosa tinggalkanlah}. Maka wahai pun berturut-turut turun.\" Hadits ini diikuti pula oleh [Abdullah bin Yusuf] dan [Abu Shalih]. Dan diikuti pula oleh [Hilal bin Raddad] dari [Az Zuhri]. Dan [Yunus] serta [Ma'mar] berkata: \"Bawadiruhu\"."

print("Updating Hadith 4 Indonesian translation in Supabase...")
r = requests.patch(
    f"{base}/hadiths?id=eq.bukhari_4",
    headers=headers,
    json={"text_id": bukhari_4_id}
)

if r.status_code in (200, 204):
    print("✅ Successfully updated Hadith 4 Indonesian translation in Supabase!")
else:
    print(f"Error updating Hadith 4: {r.status_code} {r.text}")

# Check for any other Hadiths with empty text_id in the first 100
r2 = requests.get(f"{base}/hadiths?select=id,hadith_number,text_en,text_ar&text_id=eq.&limit=50", headers=headers)
missing = r2.json()
print(f"\nFound {len(missing)} other hadiths with empty text_id in database sample.")
for m in missing:
    print(f"  - {m['id']} (# {m['hadith_number']})")

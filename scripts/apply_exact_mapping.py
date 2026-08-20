import sqlite3, json, glob, os

conn = sqlite3.connect('scratch/lidwa_plaintext.db')
cursor = conn.cursor()
cursor.execute('SELECT Kode_Rawi, bukhari, muslim, abudaud, tirmidzi, nasai, ibnumajah, ahmad, malik, darimi FROM perawi_daftar')
db_counts = {r[0]: {'bukhari': r[1], 'muslim': r[2], 'abudaud': r[3], 'tirmidzi': r[4], 'nasai': r[5], 'ibnumajah': r[6], 'ahmad': r[7], 'malik': r[8], 'darimi': r[9]} for r in cursor.fetchall()}

# Precise mapping of profile -> Kode_Rawi
MAPPING = {
    "rawi_abdullah_bin_dinar": 4797,
    "rawi_abdullah_bin_masud": 5079,
    "rawi_abu_dawud": None,
    "rawi_abu_hurairah": 4396,
    "rawi_abu_said_al_khudri": 3260,
    "rawi_ahmad": None,
    "rawi_aisha_bint_abi_bakr": 4049,
    "rawi_al_bukhari": None,
    "rawi_al_hakim": None,
    "rawi_al_nasai": None,
    "rawi_al_tirmidhi": None,
    "rawi_al_zuhri": 7272,
    "rawi_anas_bin_malik": 720,
    "rawi_atho_bin_yasar": 5640,
    "rawi_baghawi": None,
    "rawi_daraqutni": None,
    "rawi_darimi": None,
    "rawi_hilal_bin_ali": 8085,
    "rawi_ibn_abbas": 4883,
    "rawi_ibn_hajar": None,
    "rawi_ibn_hibban": None,
    "rawi_ibn_khuzaimah": None,
    "rawi_ibn_majah": None,
    "rawi_ibn_umar": 4967,
    "rawi_ismail_bin_jafar": 1012,
    "rawi_jaber_bin_abdullah": 2069,
    "rawi_malik_bin_anas": 6659,
    "rawi_muslim_ibn_hajjaj": None,
    "rawi_nafi": 7863,
    "rawi_nawawi": None,
    "rawi_qutaibah_bin_said": 6460,
    "rawi_said_bin_jubair": 3307,
    "rawi_salim": 3194,
    "rawi_sufyan_al_thawri": 3436,
    "rawi_syafii": None,
    "rawi_tabarani": None,
    "rawi_umar_ibn_al_khattab": 5913,
    "rawi_urwah": 5594,
    "rawi_waliullah": None,
    "rawi_yahya_bin_said": 8272
}

zeros = { 'bukhari': 0, 'muslim': 0, 'abudaud': 0, 'tirmidzi': 0, 'nasai': 0, 'ibnumajah': 0, 'ahmad': 0, 'malik': 0, 'darimi': 0 }

for filepath in glob.glob('data/rawis/profiles/rawi_*.json'):
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    rawi_id = data.get('id')
    if rawi_id in MAPPING:
        kode = MAPPING[rawi_id]
        if kode is not None:
            data['book_counts'] = db_counts[kode]
        else:
            data['book_counts'] = zeros
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Updated {rawi_id} (Kode: {kode})")

print("All exact mappings applied!")

import re

with open('js/app.js', 'r', encoding='utf-8') as f:
    app_js = f.read()

# Locate BOOK_DATASETS dictionary
start_idx = app_js.find('const BOOK_DATASETS = {')
end_idx = app_js.find('};', start_idx) + 2

new_dict = """const BOOK_DATASETS = {
  // 9 Books (Kutubut Tis'ah)
  bukhari: [
    { id: 'fawazahmed', label: 'International Numbering (Main)', labelId: 'Penomoran Internasional (Utama)' },
    { id: 'native_lidwa', label: 'Lidwa Numbering', labelId: 'Penomoran Lidwa' }
  ],
  muslim: [
    { id: 'fawazahmed', label: 'International Numbering (Main)', labelId: 'Penomoran Internasional (Utama)' },
    { id: 'native_lidwa', label: 'Lidwa Numbering', labelId: 'Penomoran Lidwa' }
  ],
  nasai: [
    { id: 'fawazahmed', label: 'International Numbering (Main)', labelId: 'Penomoran Internasional (Utama)' },
    { id: 'native_lidwa', label: 'Lidwa Numbering', labelId: 'Penomoran Lidwa' }
  ],
  abudawud: [
    { id: 'fawazahmed', label: 'International Numbering (Main)', labelId: 'Penomoran Internasional (Utama)' },
    { id: 'native_lidwa', label: 'Lidwa Numbering', labelId: 'Penomoran Lidwa' }
  ],
  tirmidhi: [
    { id: 'fawazahmed', label: 'International Numbering (Main)', labelId: 'Penomoran Internasional (Utama)' },
    { id: 'native_lidwa', label: 'Lidwa Numbering', labelId: 'Penomoran Lidwa' }
  ],
  ibnmajah: [
    { id: 'fawazahmed', label: 'International Numbering (Main)', labelId: 'Penomoran Internasional (Utama)' },
    { id: 'native_lidwa', label: 'Lidwa Numbering', labelId: 'Penomoran Lidwa' }
  ],
  malik: [
    { id: 'fawazahmed', label: 'International Numbering (Main)', labelId: 'Penomoran Internasional (Utama)' },
    { id: 'native_lidwa', label: 'Lidwa Numbering', labelId: 'Penomoran Lidwa' }
  ],
  ahmad: [
    { id: 'native_lidwa', label: 'Lidwa Numbering (Main)', labelId: 'Penomoran Lidwa (Utama)' },
    { id: 'native_ahmedbaset', label: 'AhmedBaset Edition', labelId: 'Edisi AhmedBaset' }
  ],
  darimi: [
    { id: 'native_lidwa', label: 'Lidwa Numbering (Main)', labelId: 'Penomoran Lidwa (Utama)' },
    { id: 'native_ahmedbaset', label: 'AhmedBaset Edition', labelId: 'Edisi AhmedBaset' }
  ],

  // 8 Books (AhmedBaset as Main)
  riyad: [
    { id: 'native_ahmedbaset', label: 'AhmedBaset Edition (Main)', labelId: 'Edisi AhmedBaset (Utama)' }
  ],
  shamail: [
    { id: 'native_ahmedbaset', label: 'AhmedBaset Edition (Main)', labelId: 'Edisi AhmedBaset (Utama)' }
  ],
  bulugh: [
    { id: 'native_ahmedbaset', label: 'AhmedBaset Edition (Main)', labelId: 'Edisi AhmedBaset (Utama)' }
  ],
  adab: [
    { id: 'native_ahmedbaset', label: 'AhmedBaset Edition (Main)', labelId: 'Edisi AhmedBaset (Utama)' }
  ],
  mishkat: [
    { id: 'native_ahmedbaset', label: 'AhmedBaset Edition (Main)', labelId: 'Edisi AhmedBaset (Utama)' }
  ],
  nawawi: [
    { id: 'native_ahmedbaset', label: 'AhmedBaset Edition (Main)', labelId: 'Edisi AhmedBaset (Utama)' },
    { id: 'fawazahmed', label: 'Fawaz Edition', labelId: 'Edisi Fawaz' }
  ],
  qudsi: [
    { id: 'native_ahmedbaset', label: 'AhmedBaset Edition (Main)', labelId: 'Edisi AhmedBaset (Utama)' },
    { id: 'fawazahmed', label: 'Fawaz Edition', labelId: 'Edisi Fawaz' }
  ],
  dehlawi: [
    { id: 'native_ahmedbaset', label: 'AhmedBaset Edition (Main)', labelId: 'Edisi AhmedBaset (Utama)' },
    { id: 'fawazahmed', label: 'Fawaz Edition', labelId: 'Edisi Fawaz' }
  ],

  // IrsyadulIbad
  syafii: [
    { id: 'native_irsyad', label: 'IrsyadulIbad (Main)', labelId: 'IrsyadulIbad (Utama)' }
  ],
  riyad_arab: [
    { id: 'native_irsyad', label: 'IrsyadulIbad (850 Hadith)', labelId: 'IrsyadulIbad (850 Hadits)' }
  ],

  // MJNA
  ibnukhuzaimah: [
    { id: 'native_mjna', label: 'MJNA Edition (Main)', labelId: 'Edisi MJNA (Utama)' }
  ],
  ibnuhibban: [
    { id: 'native_mjna', label: 'MJNA Edition (Main)', labelId: 'Edisi MJNA (Utama)' }
  ],
  mustadrak: [
    { id: 'native_mjna', label: 'MJNA Edition (Main)', labelId: 'Edisi MJNA (Utama)' }
  ],
  daruquthni: [
    { id: 'native_mjna', label: 'MJNA Edition (Main)', labelId: 'Edisi MJNA (Utama)' }
  ]
};"""

app_js = app_js[:start_idx] + new_dict + app_js[end_idx:]

with open('js/app.js', 'w', encoding='utf-8') as f:
    f.write(app_js)

print("Patched BOOK_DATASETS in app.js successfully.")

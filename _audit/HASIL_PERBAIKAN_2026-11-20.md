# Hasil perbaikan hadeeth.id — 2026-11-20 (WIB)

Dikerjakan setelah audit `HADEETH_ID_AUDIT_2026-11-20.md`. Pengukuran ulang
memakai Chrome/Playwright terhadap salinan lokal di `http://127.0.0.1:8765`
dengan data R2 produksi, lalu unggah R2 untuk sidecar bab yang berubah.

## Ringkasan terukur

| Item | Sebelum | Sesudah | Bukti |
|---|---|---|---|
| EN di halaman topik, 6 kitab | 0/10 kartu | 10/10 kartu memuat terjemahan English + atribusi `[Terjemahan EN: Fawazahmed #n]` | `verify_topic_en.txt` |
| `chapters/muntaqa.ndjson` | 1.109 judul berupa ID `turath:` | 1.109 judul Arab asli dari `syarah_muntaqa.db`; 0 string `turath:` tampil | `fix_chapter_data.py`, `verify_muntaqa.txt` |
| `chapters/tabarani.ndjson` | 2.248 bab, 294 jumlah hadits bertentangan dengan rentang | 4.567 bab dari `data/chapters/tabarani.json`, rentang & jumlah unik sesuai sumber | unggah terverifikasi |
| `privacy.html` | 9 × `Ã¢â‚¬â€\x9d` | 0 | `apply_html_fixes.py` |
| `scholars.html` `arNameDict` | 20 nama rusak | 0 pola mojibake | `apply_html_fixes.py` |
| `js/app.js` | 8 string mojibake | 0 | `apply_client_fixes.py`, `node --check` lolos |
| Perawi dalam tanda kurung | `<a inline-flex>` + SVG memecah `[]` | tautan inline tanpa SVG, kurung rapat | `verify_fixes_local.py` |
| `<div>` di dalam `<p>` terjemahan | 2 per halaman hadits | 0 (kontainer jadi `<div>`) | `hadith.html` |
| Panel terjemahan kosong | 2 per halaman untuk qudsi/tabarani/maani | placeholder teks eksplisit | `hadith.html` |
| Sanad 19 kitab tanpa data | node `Sanad tidak terdeteksi` + kolektor `Imam al-Bukhari` | pesan `Rantai sanad belum tersedia`, kolektor tidak dirender, 0 Perawi | `verify_sanad.txt` |
| `&bull;` literal di scholars | 9 | 0 (memakai `•`) | `scholars.html` |
| `Source: unified NDJSON engine` | 3 × per halaman topik | 0 | `verify_fixes_local.py` |
| Head kitab `maani/masabih/umdat/muntaqa` | `MAANI`, `By Author Sheikh`, `HADITH BOOK` | judul/penulis Arab + genre dari `books.ndjson` | `kitab.html?book=muntaqa` |
| `favicon.ico` | 404 di semua halaman | 200, berkas ICO 1.150 byte | `curl` |
| `data/rawis/indexes/idx_*.json` | 404 lalu pemindaian penuh | fetch mati dihapus; pemindaian langsung | `profile-detail.html` |
| Halaman scholars | fallback 40 kartu + Supabase mati | 14.330 perawi dari `data/rawis/active_rawis.min.json` | `verify_scholars.txt` (dump lokal) |

## Koreksi terhadap klaim audit sebelumnya

- Klaim "bab pertama bernomor 260" salah. `getChapters()` mengurutkan
  `chapter_number` secara numerik; 260 memang ID terkecil. Yang salah adalah
  jumlah hadits, bukan nomor awal. Proba: `data/chapters/tabarani.json`.
- Klaim "anon key terpotong" salah. `js/config.js` memakai kunci format
  `sb_publishable_*`, bukan JWT `eyJhbG...`. Yang mati adalah DNS Supabase.
- Hitungan audit "338 bab buruk" tidak sama dengan hitungan perbaikan (294)
  karena audit memakai pemeriksaan rentang longgar; pemeriksaan akhir memakai
  `hadith_count > hadith_end - hadith_start + 1` per baris R2.
- "10 kitab tanpa bab" bukan cacat data: sumber memang tidak punya metadata
  bab, dan desain memakai satu pseudo-bab "Semua Hadits". Perbaikan hanya
  menambahkan judul Arab pada empat pseudo-bab yang kosong.

## Cara kerja

- Terjemahan EN: `enrichTopicEnglish()` mengubah `fawaz_to_lidwa` menjadi
  peta terbalik, lalu memanggil `getEditionText('eng', book, fawazNumber)`.
  Perbandingan nomor memakai `hadithNumberOf(item, 'lidwa')`, bukan nomor baris.
  `ahmad` dan `darimi` dilewati karena tidak punya edition `eng-*` di R2.
- Data bab: tidak ada teks Arab yang direkayasa. Judul tabarani diambil dari
  `data/chapters/tabarani.json`; judul muntaqa dari tabel `syarah_chapters`
  di `syarah_muntaqa.db`; judul pseudo-bab dari `books.ndjson`.
  `hadith_count` kini jumlah nomor unik, `row_count` jumlah baris edisi.
- `export_site/_manifest.ndjson` ikut diperbarui agar `site_r2.py verify`
  tidak melaporkan selisih ukuran.

## Masih terbuka

1. `sources/lidwa/bukhari.ndjson`, `commentaries/matched/qudsi*.ndjson`,
   `data/links/maani.json` masih 404 saat halaman tertentu mencobanya;
   ketiganya jalur fallback lama dan tidak menghalangi render. Perlu sumber
   pengganti jika ingin benar-benar hilang dari network log.
2. `books.ndjson.editions` masih mengiklankan 17 file edition yang tidak ada.
   Dropdown memakai `editions/_catalog.ndjson`, jadi tidak ada klik mati.
3. Indeks perawi-number (`idx_*.json`) tidak diterbitkan; profil kini memindai
   langsung tanpa 404, tetapi tetap memuat 10 kitab saat pencarian.
4. Orphan `test_hotd.html` dan `books2.html` masih tersaji (tidak ditautkan).
   Penghapusan tidak dilakukan karena bersifat destruktif dan tidak diminta
   secara eksplisit.

## Berkas terkait

`_audit/apply_client_fixes.py`, `apply_html_fixes.py`,
`apply_scholars_and_assets.py`, `fix_dead_urls.py`,
`fix_last_client_details.py`, `fix_chapter_data.py`,
`verify_fixes_local.py`, `verify_*.txt`.

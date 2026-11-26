import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:url_launcher/url_launcher.dart';

import '../state/app_state.dart';
import '../theme.dart';
import 'widgets.dart';

class _Section {
  const _Section(this.title, this.body);
  final String title;
  final String body;
}

class PrivacyPage extends StatelessWidget {
  const PrivacyPage({super.key});

  static const _sections = <_Section>[
    _Section(
      '1. Who we are',
      'hadeeth.id is a non-commercial, educational hadith reference platform, operated '
          'independently and not affiliated with any commercial organisation.',
    ),
    _Section(
      '2. What this app collects',
      'Nothing by default. The mobile edition has no analytics, no advertising SDK and no '
          'tracking identifiers. Reading preferences — language, theme, Arabic text size, '
          'translation mode, bookmarks and last-read position — are written to app storage '
          'on your device only.',
    ),
    _Section(
      '3. Optional account',
      'Signing in is optional and only needed to sync bookmarks across devices. Signing in '
          'with email or Google stores your email address, display name and profile picture '
          '(if the provider supplies one) through Supabase Auth. Nothing else is kept.',
    ),
    _Section(
      '4. What we do not collect',
      'We do not collect personal information beyond what is needed to keep an account and '
          'sync preferences. We do not use tracking cookies for advertising. We do not sell, '
          'rent or share user data for marketing. Reading the archive without an account is '
          'fully supported.',
    ),
    _Section(
      '5. Local storage keys',
      'hadeeth_lang — interface language (EN or ID). hadeeth_theme — light, dark or system. '
          'hadeeth_last_read — the last narration you opened (book and number). '
          'hadeeth_bookmarks — saved narrations. hadeeth_hotd — the Hadith of the Day pin, '
          'when an administrator has set one. Clearing app data removes all of it.',
    ),
    _Section(
      '6. Third-party services',
      'Cloudflare — hosts the CDN that serves the collection files and may log IP addresses '
          'for security. Supabase — accounts, when you choose to sign in. razi.hadeeth.id — '
          'receives the text of a question you send to the AI assistant, so it can answer and '
          'keep the thread. Google Fonts — fonts. Algolia — search, when enabled.',
    ),
    _Section(
      '7. Children\'s privacy',
      'hadeeth.id is a general-audience reference resource. We do not knowingly collect '
          'personal information from children under 13.',
    ),
    _Section(
      '8. Security',
      'The archive itself is static files, so it holds no personal data on our servers. What '
          'you keep locally stays in this app\'s storage, protected by the device sandbox.',
    ),
    _Section(
      '9. Your rights and data deletion',
      'Request deletion: email info@hadeeth.id with the subject "Data Deletion Request" and '
          'we permanently remove the account and its data from Supabase within 7 business '
          'days. Local data: Settings → Reset preferences, or clear the app\'s storage.',
    ),
    _Section(
      '10. Changes and contact',
      'This policy may be updated; the date below changes with it. Questions: info@hadeeth.id '
          'or the sister project tafseer.id.',
    ),
  ];

  @override
  Widget build(BuildContext context) {
    final p = context.p;
    final lang = context.watch<AppState>().lang;
    final isId = lang == 'id';
    return Scaffold(
      body: SafeArea(
        bottom: false,
        child: ListView(
          padding: const EdgeInsets.fromLTRB(16, 12, 16, 28),
          children: [
            PageHeader(
              title: t('Privacy policy', 'Kebijakan privasi', lang),
              subtitle: t('LEGAL • AUGUST 2026', 'LEGAL • AGUSTUS 2026'),
              showLogo: false,
              leading: const BackButton2(),
            ),
            const SizedBox(height: 16),
            CardSurface(
              padding: const EdgeInsets.all(16),
              child: Text(
                t(
                  'This page explains what the hadeeth.id mobile edition stores, what it sends, '
                      'and how to remove it. It follows the policy published at hadeeth.id/privacy.',
                  'Halaman ini menjelaskan apa yang disimpan edisi seluler hadeeth.id, apa yang '
                      'dikirim, dan cara menghapusnya. Mengikuti kebijakan di hadeeth.id/privacy.',
                  lang,
                ),
                style: HText.bodySm.copyWith(color: p.textSecondary, height: 1.55),
              ),
            ),
            const SizedBox(height: 18),
            for (final s in _sections) ...[
              Text(s.title, style: HText.h3.copyWith(fontSize: 13, color: p.textPrimary)),
              const SizedBox(height: 5),
              Text(
                isId ? _translateId(s.title) : s.body,
                style: HText.bodySm.copyWith(color: p.textMuted, fontSize: 11.5, height: 1.6),
              ),
              const SizedBox(height: 16),
            ],
            GestureDetector(
              onTap: () => launchUrl(Uri.parse('https://hadeeth.id/privacy'), mode: LaunchMode.externalApplication),
              child: Row(
                children: [
                  Icon(Icons.open_in_new_rounded, size: 13, color: p.emerald),
                  const SizedBox(width: 6),
                  Text('hadeeth.id/privacy', style: HText.labelSm.copyWith(color: p.emerald, fontSize: 10)),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  /// Indonesian body copy. The English sections stay the canonical text.
  static String _translateId(String title) {
    switch (title) {
      case '1. Who we are':
        return 'hadeeth.id adalah platform rujukan hadis nirlaba untuk pendidikan, dikelola '
            'secara independen dan tidak berafiliasi dengan organisasi komersial mana pun.';
      case '2. What this app collects':
        return 'Tidak ada secara bawaan. Edisi seluler ini tanpa analitik, tanpa SDK iklan, dan '
            'tanpa pengenal pelacak. Preferensi bacaan — bahasa, tema, ukuran teks Arab, mode '
            'terjemahan, riwayat tersimpan, dan posisi baca terakhir — ditulis ke penyimpanan '
            'aplikasi di perangkat Anda saja.';
      case '3. Optional account':
        return 'Masuk bersifat opsional dan hanya diperlukan untuk menyinkronkan riwayat antar '
            'perangkat. Masuk dengan email atau Google menyimpan alamat email, nama tampilan, '
            'dan foto profil (bila penyedia memberikannya) melalui Supabase Auth. Tidak ada data lain.';
      case '4. What we do not collect':
        return 'Kami tidak mengumpulkan data pribadi melebihi yang diperlukan untuk akun dan '
            'sinkronisasi preferensi. Tidak ada cookie pelacak untuk iklan. Kami tidak menjual, '
            'menyewakan, atau membagikan data pengguna untuk pemasaran. Membaca arsip tanpa akun '
            'tetap didukung penuh.';
      case '5. Local storage keys':
        return 'hadeeth_lang — bahasa antarmuka (EN atau ID). hadeeth_theme — terang, gelap, atau '
            'sistem. hadeeth_last_read — riwayat terakhir yang dibuka (kitab dan nomor). '
            'hadeeth_bookmarks — riwayat tersimpan. hadeeth_hotd — penetapan Hadis Hari Ini bila '
            'diatur administrator. Menghapus data aplikasi menghapus semuanya.';
      case '6. Third-party services':
        return 'Cloudflare — CDN yang menyajikan berkas koleksi dan dapat mencatat alamat IP untuk '
            'keamanan. Supabase — akun, bila Anda memilih masuk. razi.hadeeth.id — menerima teks '
            'pertanyaan yang Anda kirim ke asisten AI agar dapat menjawab dan menyimpan utas. '
            'Google Fonts — huruf. Algolia — pencarian, bila diaktifkan.';
      case '7. Children\'s privacy':
        return 'hadeeth.id adalah rujukan untuk khalayak umum. Kami tidak dengan sengaja '
            'mengumpulkan data pribadi anak di bawah 13 tahun.';
      case '8. Security':
        return 'Arsip berupa berkas statis, sehingga tidak menyimpan data pribadi di server kami. '
            'Data lokal tetap di penyimpanan aplikasi, dilindungi sandbox perangkat.';
      case '9. Your rights and data deletion':
        return 'Permintaan penghapusan: kirim email ke info@hadeeth.id dengan subjek '
            '"Data Deletion Request"; akun dan datanya dihapus permanen dari Supabase dalam 7 hari '
            'kerja. Data lokal: Pengaturan → Atur ulang preferensi, atau hapus penyimpanan aplikasi.';
      case '10. Changes and contact':
        return 'Kebijakan ini dapat diperbarui; tanggal di atas ikut berubah. Pertanyaan: '
            'info@hadeeth.id atau proyek saudari tafseer.id.';
      default:
        return '';
    }
  }
}

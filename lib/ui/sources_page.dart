import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:url_launcher/url_launcher.dart';

import '../state/app_state.dart';
import '../theme.dart';
import 'dataset_line.dart';
import 'widgets.dart';

class _Source {
  const _Source(this.title, this.role, this.body, this.label, this.url);
  final String title;
  final String role;
  final String body;
  final String label;
  final String url;
}

class _Collection {
  const _Collection(this.name, this.arabic, this.hadiths, this.db, this.langs);
  final String name;
  final String arabic;
  final int hadiths;
  final String db;
  final String langs;
}

const List<_Source> _sources = [
  _Source(
    'Fawazahmed0 DB',
    'PRIMARY ANCHOR',
    'Supplies the translations: nine languages across eight collections — 54 language–collection editions, 285,647 translated hadiths. Rows from this source also carry the numbering that links each translation back to its collection.',
    'fawazahmed0.github.io',
    'https://fawazahmed0.github.io',
  ),
  _Source(
    'Lidwa Hadith DB',
    'LINKED SOURCE',
    'Mapped dynamically to supply Indonesian translations, isnād chains (sanad) and Kedudukan (status) / grading for the core nine books — Kutubut Tis\'ah.',
    'Lidwa Pusaka',
    'https://lidwapusaka.com',
  ),
  _Source(
    'AhmedBaset DB',
    'LINKED SOURCE',
    'Comprehensive mapping for the secondary collections (Adab, Bulugh, Mishkat, Riyad, Shamail, Nawawi, Qudsi, Shah) and the base anchors for English/Arabic alignment.',
    'hadithapi.com',
    'https://hadithapi.com',
  ),
  _Source(
    'Usm12345',
    'GRADING SOURCE',
    'Explicit crediting for rigorous grading: Tirmidhi 847 da\'if and 1 mawdu\'; Abu Dawud 847 da\'if, 18 shadh, 26 munkar, 2 mawdu\'; Ibn Majah 1,074+ da\'if; Nasa\'i 235 da\'if, 6 munkar; Ahmad 300+ da\'if (in progress).',
    'github.com/Usm12345',
    'https://github.com/Usm12345',
  ),
  _Source(
    'Irsyadulibad & MJNA',
    'INDONESIAN COLLECTIONS',
    'Sources for Musnad Syafi\'i, Mustadrak Imam Al Hakim, Shahih Ibnu Khuzaimah, Sunan Ad-Daruquthni and Shahih Ibnu Hibban, with Arabic and Indonesian translations.',
    'irsyadulibad · mjna.or.id',
    'https://mjna.or.id',
  ),
  _Source(
    'meeAtif & Dorar',
    'SYARAH & REFERENCE',
    'meeAtif provides JSON alignments for the Kutub al-Sittah (Arabic, English, grading, sunnah.com references). Dorar supplies Arabic commentary fragments, shown under their own tab.',
    'meeAtif · dorar.net',
    'https://dorar.net',
  ),
  _Source(
    'Syarah corpus (turath.io)',
    'COMMENTARY',
    'Twenty-four classical editions in Arabic — Fath al-Bari, Sharh al-Nawawi, Awn al-Ma\'bud, Tuhfat al-Ahwadhi, Mirqat al-Mafatih, Sharh al-Zurqani and others — 75,358 passages across 56,932 hadiths, each with volume, page and a link to the digitised page. Texts are public domain; digitisation by turath.io.',
    'turath.io',
    'https://turath.io',
  ),
  _Source(
    'Narrators & biographies',
    'RIJAL INDEX',
    'The narrator engine combines Lidwa\'s internal database (exact collection counts and basic biographies for 8,600+ narrators) with Kaggle scholarly remarks and Jarh wa Ta\'dil assessments for primary transmitters.',
    'Lidwa DB + Kaggle',
    'https://www.kaggle.com',
  ),
];

const List<_Collection> _collections = [
  _Collection('Sahih al-Bukhari', 'صحيح البخاري', 7008, 'Lidwa + Fawaz + meeAtif', 'AR, EN, ID, BN, FR, RU, TA, TR, UR'),
  _Collection('Sahih Muslim', 'صحيح مسلم', 5362, 'Lidwa + Fawaz + meeAtif', 'AR, EN, ID, BN, FR, RU, TA, TR, UR'),
  _Collection('Sunan Abi Dawud', 'سنن أبي داود', 4590, 'Lidwa + Fawaz + meeAtif', 'AR, EN, ID, BN, FR, RU, TR, UR'),
  _Collection("Jami' at-Tirmidhi", 'جامع الترمذي', 3891, 'Lidwa + Fawaz + meeAtif', 'AR, EN, ID, BN, TR, UR'),
  _Collection("Sunan an-Nasa'i", 'سنن النسائي', 5662, 'Lidwa + Fawaz + meeAtif', 'AR, EN, ID, BN, FR, TR, UR'),
  _Collection('Sunan Ibn Majah', 'سنن ابن ماجه', 4332, 'Lidwa + Fawaz + meeAtif', 'AR, EN, ID, BN, FR, TR, UR'),
  _Collection('Muwatta Malik', 'موطأ مالك', 1595, 'Lidwa + Fawaz', 'AR, EN, ID, BN, FR, TR, UR'),
  _Collection('Sunan ad-Darimi', 'سنن الدارمي', 3367, 'Lidwa + Fawaz', 'AR, ID'),
  _Collection('Musnad Ahmad', 'مسند أحمد', 26363, 'Lidwa + Fawaz', 'AR, ID'),
  _Collection('Forty Hadith of an-Nawawi', 'الأربعون النووية', 42, 'AhmedBaset + Fawaz', 'AR, ID'),
  _Collection('40 Hadith Qudsi', 'الأربعون القدسية', 40, 'AhmedBaset + Fawaz', 'AR, ID'),
  _Collection('Forty Hadith of Shah Waliullah', 'أربعون الشاه ولي الله', 40, 'AhmedBaset + Fawaz', 'AR, ID'),
  _Collection('Al-Adab Al-Mufrad', 'الأدب المفرد', 1326, 'AhmedBaset + Fawaz', 'AR, ID'),
  _Collection('Bulugh al-Maram', 'بلوغ المرام', 1767, 'AhmedBaset + Fawaz', 'AR, ID'),
  _Collection('Mishkat al-Masabih', 'مشكاة المصابيح', 4428, 'AhmedBaset + Fawaz', 'AR, ID'),
  _Collection('Riyad as-Salihin', 'رياض الصالحين', 1896, 'AhmedBaset + Fawaz', 'AR, ID'),
  _Collection('Shamail al-Muhammadiyah', 'الشمائل المحمدية', 402, 'Fawazahmed0', 'AR, ID'),
  _Collection('Al-Mujam al-Kabir', 'المعجم الكبير', 21850, 'Fawazahmed0', 'AR'),
  _Collection("Musnad al-Shafi'i", 'مسند الشافعي', 1800, 'Irsyadulibad', 'AR, ID'),
  _Collection('Riyad as-Salihin (Arabic)', 'رياض الصالحين (عربي)', 850, 'Irsyadulibad', 'AR'),
  _Collection('Shahih Ibn Khuzaimah', 'صحيح ابن خزيمة', 1808, 'MJNA', 'AR, ID'),
  _Collection('Shahih Ibn Hibban', 'صحيح ابن حبان', 2769, 'MJNA', 'AR, ID'),
  _Collection('Al-Mustadrak ala as-Sahihayn', 'المستدرك على الصحيحين', 673, 'MJNA', 'AR, ID'),
  _Collection('Sunan ad-Daruquthni', 'سنن الدارقطني', 236, 'MJNA', 'AR, ID'),
  _Collection('Muntaqa al-Akhbar', 'منتقى الأخبار', 3944, 'Turath', 'AR'),
  _Collection("Ma'ani al-Athar", 'معاني الآثار', 7013, 'Turath', 'AR'),
  _Collection('Masabih al-Sunna', 'مصابيح السنة', 4929, 'Turath', 'AR'),
  _Collection('Umdat al-Ahkam', 'عمدة الأحكام', 414, 'Turath', 'AR'),
];

class SourcesPage extends StatelessWidget {
  const SourcesPage({super.key});

  @override
  Widget build(BuildContext context) {
    final p = context.p;
    final lang = context.watch<AppState>().lang;
    final total = _collections.fold<int>(0, (a, c) => a + c.hadiths);

    return Scaffold(
      body: SafeArea(
        bottom: false,
        child: ListView(
          padding: const EdgeInsets.fromLTRB(16, 12, 16, 28),
          children: [
            PageHeader(
              title: t('Data sources & credits', 'Sumber data & kredit', lang),
              subtitle: t('DATA PROVENANCE • VALIDATION', 'ASAL DATA • VALIDASI'),
              showLogo: false,
              leading: const BackButton2(),
            ),
            const SizedBox(height: 16),
            CardSurface(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    '${_collections.length} ${t('collections', 'koleksi', lang)} • ${formatNumber(total)} ${t('hadiths', 'hadis', lang)}',
                    style: HText.h3.copyWith(fontSize: 15, color: p.textPrimary),
                  ),
                  const SizedBox(height: 6),
                  Text(
                    t(
                      '54 translation editions in 9 languages and 24 classical editions of commentary.',
                      '54 edisi terjemahan dalam 9 bahasa dan 24 edisi syarah klasik.',
                      lang,
                    ),
                    style: HText.bodySm.copyWith(color: p.textMuted, height: 1.5),
                  ),
                  const SizedBox(height: 10),
                  DatasetLine(lang: lang),
                  Container(
                    padding: const EdgeInsets.all(11),
                    decoration: BoxDecoration(color: p.surfaceLow, borderRadius: BorderRadius.circular(10), border: Border.all(color: p.border)),
                    child: Text(
                      t(
                        'Hadith text is never overwritten, never deleted, never altered. All source data is stored verbatim; editorial notes are labelled and kept apart from the original text.',
                        'Teks hadis tidak pernah ditimpa, dihapus, atau diubah. Seluruh data sumber disimpan apa adanya; catatan editorial diberi label dan dipisahkan dari teks asli.',
                        lang,
                      ),
                      style: HText.labelSm.copyWith(color: p.textSecondary, fontSize: 10, height: 1.5),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 20),
            SectionLabel(icon: Icons.source_outlined, text: t('SOURCES', 'SUMBER')),
            const SizedBox(height: 10),
            for (final s in _sources) ...[
              CardSurface(
                padding: const EdgeInsets.fromLTRB(15, 13, 15, 13),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Expanded(child: Text(s.title, style: HText.h3.copyWith(fontSize: 13.5, color: p.textPrimary))),
                        GradeBadge(label: s.role, tier: 'class', small: true),
                      ],
                    ),
                    const SizedBox(height: 6),
                    Text(s.body, style: HText.bodySm.copyWith(color: p.textMuted, fontSize: 11.5, height: 1.55)),
                    const SizedBox(height: 8),
                    GestureDetector(
                      onTap: () => launchUrl(Uri.parse(s.url), mode: LaunchMode.externalApplication),
                      child: Row(
                        children: [
                          Icon(Icons.open_in_new_rounded, size: 12, color: p.emerald),
                          const SizedBox(width: 5),
                          Flexible(child: Text(s.label, style: HText.labelSm.copyWith(color: p.emerald, fontSize: 9.5))),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 9),
            ],
            const SizedBox(height: 12),
            SectionLabel(icon: Icons.library_books_outlined, text: t('ALL COLLECTIONS', 'SEMUA KOLEKSI')),
            const SizedBox(height: 10),
            CardSurface(
              padding: const EdgeInsets.fromLTRB(14, 6, 14, 6),
              child: Column(
                children: [
                  for (final c in _collections)
                    Padding(
                      padding: const EdgeInsets.symmetric(vertical: 9),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Expanded(
                                child: Text(c.name, style: HText.bodySm.copyWith(color: p.textPrimary, fontWeight: FontWeight.w600, fontSize: 12)),
                              ),
                              const SizedBox(width: 8),
                              Text(formatNumber(c.hadiths), style: HText.labelSm.copyWith(color: p.emerald, fontSize: 9.5)),
                            ],
                          ),
                          const SizedBox(height: 2),
                          Text(
                            '${c.db} • ${c.langs}',
                            style: HText.labelSm.copyWith(color: p.textMuted, fontSize: 9),
                          ),
                        ],
                      ),
                    ),
                ],
              ),
            ),
            const SizedBox(height: 16),
            Text(
              t(
                'Infrastructure: Cloudflare CDN serves the collection files; Supabase handles optional accounts; the AI assistant answers through razi.hadeeth.id.',
                'Infrastruktur: CDN Cloudflare menyajikan berkas koleksi; Supabase menangani akun opsional; asisten AI menjawab melalui razi.hadeeth.id.',
                lang,
              ),
              style: HText.labelSm.copyWith(color: p.textMuted, fontSize: 9.5, height: 1.5),
            ),
          ],
        ),
      ),
    );
  }
}

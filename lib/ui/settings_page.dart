import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:url_launcher/url_launcher.dart';

import '../data/auth_service.dart';
import '../state/app_state.dart';
import '../theme.dart';
import 'donate_sheet.dart';
import 'downloads_page.dart';
import 'privacy_page.dart';
import 'profile_page.dart';
import 'sources_page.dart';
import 'widgets.dart';

class SettingsPage extends StatefulWidget {
  const SettingsPage({super.key});

  @override
  State<SettingsPage> createState() => _SettingsPageState();
}

class _SettingsPageState extends State<SettingsPage> {
  @override
  Widget build(BuildContext context) {
    final p = context.p;
    final state = context.watch<AppState>();
    final lang = state.lang;

    return Scaffold(
      body: SafeArea(
        bottom: false,
        child: ListView(
          padding: const EdgeInsets.fromLTRB(16, 12, 16, 28),
          children: [
            PageHeader(
              title: t('Settings', 'Pengaturan', lang),
              subtitle: t(
                'APPEARANCE • READING • DATA',
                'TAMPILAN • BACAAN • DATA',
              ),
              showLogo: false,
              leading: const BackButton2(),
            ),
            const SizedBox(height: 16),
            CardSurface(
              onTap: () => Navigator.of(
                context,
              ).push(MaterialPageRoute(builder: (_) => const ProfilePage())),
              child: Row(
                children: [
                  Container(
                    width: 38,
                    height: 38,
                    decoration: BoxDecoration(
                      color: p.dark
                          ? Brand.emeraldBright.withValues(alpha: 0.16)
                          : Brand.emerald.withValues(alpha: 0.10),
                      borderRadius: BorderRadius.circular(11),
                    ),
                    child: Icon(
                      Icons.person_outline_rounded,
                      size: 19,
                      color: p.emerald,
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          t('Profile', 'Profil', lang),
                          style: HText.body.copyWith(
                            color: p.textPrimary,
                            fontWeight: FontWeight.w600,
                            fontSize: 13.5,
                          ),
                        ),
                        const SizedBox(height: 2),
                        ListenableBuilder(
                          listenable: AuthService.instance,
                          builder: (context, _) {
                            final email = AuthService.instance.email;
                            return Text(
                              email ??
                                  t(
                                    'Sign in, register, reading record',
                                    'Masuk, daftar, catatan bacaan',
                                    lang,
                                  ),
                              style: HText.labelSm.copyWith(
                                color: p.textMuted,
                                fontSize: 10,
                              ),
                              overflow: TextOverflow.ellipsis,
                            );
                          },
                        ),
                      ],
                    ),
                  ),
                  Icon(Icons.chevron_right_rounded, size: 18, color: p.outline),
                ],
              ),
            ),
            const SizedBox(height: 20),
            SectionLabel(
              icon: Icons.palette_outlined,
              text: t('APPEARANCE', 'TAMPILAN'),
            ),
            const SizedBox(height: 10),
            CardSurface(
              padding: const EdgeInsets.fromLTRB(16, 15, 16, 15),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    t('Theme', 'Tema', lang),
                    style: HText.body.copyWith(
                      color: p.textPrimary,
                      fontWeight: FontWeight.w600,
                      fontSize: 13.5,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    t(
                      'Dark mode uses the exact hadeeth.id ink-black and emerald palette.',
                      'Mode gelap memakai palet hitam-tinta dan hijau zamrud hadeeth.id.',
                      lang,
                    ),
                    style: HText.labelSm.copyWith(
                      color: p.textMuted,
                      fontSize: 10,
                    ),
                  ),
                  const SizedBox(height: 14),
                  Row(
                    children: [
                      _themeCard(
                        context,
                        state,
                        ThemeMode.system,
                        t('System', 'Sistem', lang),
                        const Color(0xFFFDFBF7),
                        const Color(0xFF0D0D10),
                      ),
                      const SizedBox(width: 9),
                      _themeCard(
                        context,
                        state,
                        ThemeMode.light,
                        t('Paper', 'Kertas', lang),
                        const Color(0xFFFDFBF7),
                        const Color(0xFF001932),
                      ),
                      const SizedBox(width: 9),
                      _themeCard(
                        context,
                        state,
                        ThemeMode.dark,
                        t('Ink', 'Tinta', lang),
                        const Color(0xFF0D0D10),
                        const Color(0xFF10B981),
                      ),
                    ],
                  ),
                ],
              ),
            ),
            const SizedBox(height: 12),
            CardSurface(
              padding: const EdgeInsets.fromLTRB(16, 15, 16, 15),
              child: Row(
                children: [
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          t('Interface language', 'Bahasa antarmuka', lang),
                          style: HText.body.copyWith(
                            color: p.textPrimary,
                            fontWeight: FontWeight.w600,
                            fontSize: 13.5,
                          ),
                        ),
                        const SizedBox(height: 3),
                        Text(
                          t(
                            'Hadith text stays Arabic with ID/EN translation.',
                            'Teks hadis tetap Arab dengan terjemahan ID/EN.',
                            lang,
                          ),
                          style: HText.labelSm.copyWith(
                            color: p.textMuted,
                            fontSize: 10,
                          ),
                        ),
                      ],
                    ),
                  ),
                  LangToggle(lang: lang, onChanged: (v) => state.setLang(v)),
                ],
              ),
            ),
            const SizedBox(height: 22),
            SectionLabel(
              icon: Icons.text_fields_rounded,
              text: t('READING', 'BACAAN'),
            ),
            const SizedBox(height: 10),
            CardSurface(
              padding: const EdgeInsets.fromLTRB(16, 15, 16, 16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Text(
                        t('Arabic text size', 'Ukuran teks Arab', lang),
                        style: HText.body.copyWith(
                          color: p.textPrimary,
                          fontWeight: FontWeight.w600,
                          fontSize: 13.5,
                        ),
                      ),
                      const Spacer(),
                      Text(
                        '${state.arabicSize.toInt()} px',
                        style: HText.labelSm.copyWith(
                          color: p.emerald,
                          fontSize: 10,
                        ),
                      ),
                    ],
                  ),
                  Slider(
                    value: state.arabicSize,
                    min: 18,
                    max: 44,
                    divisions: 13,
                    activeColor: p.dark ? Brand.emeraldBright : Brand.emerald,
                    onChanged: (v) => state.setArabicSize(v),
                  ),
                  const SizedBox(height: 4),
                  Container(
                    width: double.infinity,
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: p.surfaceLow,
                      borderRadius: BorderRadius.circular(11),
                      border: Border.all(color: p.border),
                    ),
                    child: Directionality(
                      textDirection: TextDirection.rtl,
                      child: Text(
                        'إِنَّمَا الْأَعْمَالُ بِالنِّيَّاتِ',
                        textAlign: TextAlign.center,
                        style: HText.arabic(
                          state.arabicSize,
                        ).copyWith(color: p.textPrimary),
                      ),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 12),
            CardSurface(
              padding: const EdgeInsets.fromLTRB(16, 15, 16, 15),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    t('Translation display', 'Tampilan terjemahan', lang),
                    style: HText.body.copyWith(
                      color: p.textPrimary,
                      fontWeight: FontWeight.w600,
                      fontSize: 13.5,
                    ),
                  ),
                  const SizedBox(height: 12),
                  Row(
                    children: [
                      for (final entry in {
                        'id': 'Bahasa Indonesia',
                        'en': 'English',
                        'both': t('Both', 'Keduanya', lang),
                      }.entries)
                        Padding(
                          padding: const EdgeInsets.only(right: 8),
                          child: ChipButton(
                            label: entry.value,
                            selected: state.translationMode == entry.key,
                            onTap: () => state.setTranslationMode(entry.key),
                          ),
                        ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  SwitchListTile(
                    contentPadding: EdgeInsets.zero,
                    value: state.showTranslation,
                    onChanged: (v) => state.setShowTranslation(v),
                    activeColor: p.dark ? Brand.emeraldBright : Brand.emerald,
                    title: Text(
                      t(
                        'Show translation by default',
                        'Tampilkan terjemahan secara default',
                        lang,
                      ),
                      style: HText.bodySm.copyWith(color: p.textPrimary),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 22),
            SectionLabel(
              icon: Icons.storage_outlined,
              text: t('DATA & STORAGE', 'DATA & PENYIMPANAN'),
            ),
            const SizedBox(height: 10),
            CardSurface(
              onTap: () => Navigator.of(
                context,
              ).push(MaterialPageRoute(builder: (_) => const DownloadsPage())),
              child: Row(
                children: [
                  Icon(Icons.download_outlined, size: 19, color: p.gold),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          t('Offline collections', 'Koleksi luring', lang),
                          style: HText.body.copyWith(
                            color: p.textPrimary,
                            fontWeight: FontWeight.w600,
                            fontSize: 13.5,
                          ),
                        ),
                        const SizedBox(height: 2),
                        Text(
                          '${state.downloads.length} ${t('downloaded', 'diunduh', lang)}  •  ${formatBytes(state.downloadBytes)}',
                          style: HText.labelSm.copyWith(
                            color: p.textMuted,
                            fontSize: 10,
                          ),
                        ),
                      ],
                    ),
                  ),
                  Icon(Icons.chevron_right_rounded, size: 18, color: p.outline),
                ],
              ),
            ),
            const SizedBox(height: 9),
            CardSurface(
              child: SwitchListTile(
                contentPadding: const EdgeInsets.symmetric(horizontal: 2),
                value: state.preferOffline,
                onChanged: (v) => state.setPreferOffline(v),
                activeColor: p.dark ? Brand.emeraldBright : Brand.emerald,
                secondary: Icon(
                  Icons.wifi_off_rounded,
                  size: 19,
                  color: p.gold,
                ),
                title: Text(
                  t(
                    'Prefer downloaded copies',
                    'Utamakan salinan luring',
                    lang,
                  ),
                  style: HText.body.copyWith(
                    color: p.textPrimary,
                    fontWeight: FontWeight.w600,
                    fontSize: 13,
                  ),
                ),
                subtitle: Text(
                  t(
                    'Use local files before the CDN when available.',
                    'Gunakan berkas lokal sebelum CDN bila tersedia.',
                    lang,
                  ),
                  style: HText.labelSm.copyWith(
                    color: p.textMuted,
                    fontSize: 9.5,
                  ),
                ),
              ),
            ),
            const SizedBox(height: 22),
            SectionLabel(
              icon: Icons.favorite_border_rounded,
              text: t('SUPPORT & LEGAL', 'DUKUNGAN & LEGAL'),
            ),
            const SizedBox(height: 10),
            CardSurface(
              onTap: () => Navigator.of(
                context,
              ).push(MaterialPageRoute(builder: (_) => const SourcesPage())),
              child: Row(
                children: [
                  Icon(Icons.source_outlined, size: 19, color: p.gold),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          t(
                            'Data sources & credits',
                            'Sumber data & kredit',
                            lang,
                          ),
                          style: HText.body.copyWith(
                            color: p.textPrimary,
                            fontWeight: FontWeight.w600,
                            fontSize: 13.5,
                          ),
                        ),
                        const SizedBox(height: 2),
                        Text(
                          t(
                            '28 collections, every upstream database credited',
                            '28 koleksi, setiap basis data sumber dikreditkan',
                            lang,
                          ),
                          style: HText.labelSm.copyWith(
                            color: p.textMuted,
                            fontSize: 10,
                          ),
                        ),
                      ],
                    ),
                  ),
                  Icon(Icons.chevron_right_rounded, size: 18, color: p.outline),
                ],
              ),
            ),
            const SizedBox(height: 9),
            CardSurface(
              onTap: () => Navigator.of(
                context,
              ).push(MaterialPageRoute(builder: (_) => const PrivacyPage())),
              child: Row(
                children: [
                  Icon(Icons.shield_outlined, size: 19, color: p.gold),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          t('Privacy policy', 'Kebijakan privasi', lang),
                          style: HText.body.copyWith(
                            color: p.textPrimary,
                            fontWeight: FontWeight.w600,
                            fontSize: 13.5,
                          ),
                        ),
                        const SizedBox(height: 2),
                        Text(
                          t(
                            'What is stored, what is sent, how to delete it',
                            'Apa yang disimpan, dikirim, dan cara menghapusnya',
                            lang,
                          ),
                          style: HText.labelSm.copyWith(
                            color: p.textMuted,
                            fontSize: 10,
                          ),
                        ),
                      ],
                    ),
                  ),
                  Icon(Icons.chevron_right_rounded, size: 18, color: p.outline),
                ],
              ),
            ),
            const SizedBox(height: 9),
            CardSurface(
              onTap: () => showDonateSheet(context),
              child: Row(
                children: [
                  Icon(
                    Icons.volunteer_activism_outlined,
                    size: 19,
                    color: p.gold,
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          t('Support this project', 'Dukung proyek ini', lang),
                          style: HText.body.copyWith(
                            color: p.textPrimary,
                            fontWeight: FontWeight.w600,
                            fontSize: 13.5,
                          ),
                        ),
                        const SizedBox(height: 2),
                        Text(
                          t(
                            'QRIS or USDT (BEP20)',
                            'QRIS atau USDT (BEP20)',
                            lang,
                          ),
                          style: HText.labelSm.copyWith(
                            color: p.textMuted,
                            fontSize: 10,
                          ),
                        ),
                      ],
                    ),
                  ),
                  Icon(Icons.chevron_right_rounded, size: 18, color: p.outline),
                ],
              ),
            ),
            const SizedBox(height: 22),
            SectionLabel(
              icon: Icons.info_outline_rounded,
              text: t('ABOUT', 'TENTANG'),
            ),
            const SizedBox(height: 10),
            CardSurface(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      const BrandLogo(height: 34),
                      const SizedBox(width: 10),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            RichText(
                              text: TextSpan(
                                children: [
                                  TextSpan(
                                    text: 'hadeeth',
                                    style: HText.h3.copyWith(
                                      color: p.textPrimary,
                                      fontSize: 16,
                                    ),
                                  ),
                                  TextSpan(
                                    text: '.id',
                                    style: HText.h3.copyWith(
                                      color: p.gold,
                                      fontSize: 16,
                                    ),
                                  ),
                                ],
                              ),
                            ),
                            Text(
                              t(
                                'Digital Hadith Manuscript Preservation',
                                'Pelestarian Naskah Hadis Digital',
                                lang,
                              ),
                              style: HText.labelSm.copyWith(
                                color: p.textMuted,
                                fontSize: 9,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  Text(
                    t(
                      'Mobile edition v1.0.0. Reads the same public CDN files and AI scholar endpoint as hadeeth.id. Saved notes stay on this device.',
                      'Edisi seluler v1.0.0. Membaca berkas CDN dan layanan AI yang sama dengan hadeeth.id. Catatan tersimpan di perangkat ini.',
                      lang,
                    ),
                    style: HText.bodySm.copyWith(
                      color: p.textSecondary,
                      height: 1.5,
                    ),
                  ),
                  const SizedBox(height: 12),
                  GestureDetector(
                    onTap: () => launchUrl(
                      Uri.parse('https://hadeeth.id'),
                      mode: LaunchMode.externalApplication,
                    ),
                    child: Row(
                      children: [
                        Icon(
                          Icons.open_in_new_rounded,
                          size: 14,
                          color: p.emerald,
                        ),
                        const SizedBox(width: 6),
                        Text(
                          'hadeeth.id',
                          style: HText.labelSm.copyWith(
                            color: p.emerald,
                            fontSize: 11,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 16),
            Center(
              child: GestureDetector(
                onTap: () async {
                  await state.resetSettings();
                  if (mounted)
                    showSnack(
                      context,
                      t('Preferences reset', 'Pengaturan diatur ulang', lang),
                    );
                },
                child: Text(
                  t('Reset preferences', 'Atur ulang preferensi', lang),
                  style: HText.labelSm.copyWith(
                    color: p.textMuted,
                    fontSize: 10,
                    decoration: TextDecoration.underline,
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _bar(Color accent, double alpha, double width, {double height = 5}) =>
      Container(
        width: width,
        height: height,
        decoration: BoxDecoration(
          color: accent.withValues(alpha: alpha),
          borderRadius: BorderRadius.circular(height / 2),
        ),
      );

  Widget _themeCard(
    BuildContext context,
    AppState state,
    ThemeMode mode,
    String label,
    Color swatch,
    Color accent,
  ) {
    final p = context.p;
    final selected = state.themeMode == mode;
    return Expanded(
      child: GestureDetector(
        onTap: () => state.setThemeMode(mode),
        child: Container(
          padding: const EdgeInsets.all(9),
          decoration: BoxDecoration(
            color: selected
                ? (p.dark
                      ? Brand.emeraldBright.withValues(alpha: 0.12)
                      : Brand.emerald.withValues(alpha: 0.06))
                : p.surfaceLow,
            borderRadius: BorderRadius.circular(12),
            border: Border.all(
              color: selected
                  ? (p.dark ? Brand.emeraldBright : Brand.emerald)
                  : p.border,
              width: selected ? 1.5 : 1,
            ),
          ),
          child: Column(
            children: [
              Container(
                height: 40,
                decoration: BoxDecoration(
                  color: swatch,
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: p.border),
                ),
                child: Stack(
                  children: [
                    Positioned(
                      left: 7,
                      top: 7,
                      right: 7,
                      child: _bar(accent, 0.7, 5),
                    ),
                    Positioned(
                      left: 7,
                      top: 16,
                      child: _bar(accent, 0.28, 28, height: 4),
                    ),
                    Positioned(
                      left: 7,
                      top: 24,
                      child: _bar(accent, 0.16, 20, height: 4),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 7),
              Text(
                label,
                style: HText.labelSm.copyWith(
                  color: selected ? p.emerald : p.textSecondary,
                  fontSize: 9.5,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

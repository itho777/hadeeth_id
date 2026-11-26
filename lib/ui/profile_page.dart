import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../data/auth_service.dart';
import '../data/sync_service.dart';
import '../state/app_state.dart';
import '../theme.dart';
import 'dataset_line.dart';
import 'hadith_detail_page.dart';
import 'login_page.dart';
import 'saved_page.dart';
import 'widgets.dart';

/// Reader record. Sign-in (email/password + Google) runs against Supabase Auth;
/// bookmarks and last-read sync through `SyncService` once a session exists, and
/// stay local when signed out.
class ProfilePage extends StatelessWidget {
  const ProfilePage({super.key, this.inShell = false});

  /// Root tab: no back arrow, brand mark instead. Pushed from Settings: back.
  final bool inShell;

  @override
  Widget build(BuildContext context) {
    final p = context.p;
    final state = context.watch<AppState>();
    final lang = state.lang;
    final reads = state.lastRead.values.toList()
      ..sort((a, b) => b.at.compareTo(a.at));

    return Scaffold(
      body: SafeArea(
        bottom: false,
        child: ListView(
          padding: const EdgeInsets.fromLTRB(16, 12, 16, 28),
          children: [
            PageHeader(
              title: t('Profile', 'Profil', lang),
              subtitle: t('READING RECORD', 'CATATAN BACAAN'),
              showLogo: inShell,
              leading: inShell ? null : const BackButton2(),
            ),
            const SizedBox(height: 16),
            ListenableBuilder(
              listenable: AuthService.instance,
              builder: (context, _) {
                final auth = AuthService.instance;
                final signedIn = auth.signedIn;
                return CardSurface(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Container(
                            width: 52,
                            height: 52,
                            decoration: BoxDecoration(
                              color: p.dark
                                  ? Brand.emeraldBright.withValues(alpha: 0.16)
                                  : Brand.emerald.withValues(alpha: 0.10),
                              borderRadius: BorderRadius.circular(14),
                              border: Border.all(
                                color: p.dark
                                    ? Brand.emeraldBright.withValues(alpha: 0.3)
                                    : Brand.emerald.withValues(alpha: 0.2),
                              ),
                            ),
                            child: Icon(
                              Icons.person_outline_rounded,
                              size: 24,
                              color: p.emerald,
                            ),
                          ),
                          const SizedBox(width: 13),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  signedIn
                                      ? (auth.email ?? '')
                                      : t(
                                          'Reader on this device',
                                          'Pembaca di perangkat ini',
                                          lang,
                                        ),
                                  style: HText.h3.copyWith(
                                    fontSize: 14,
                                    color: p.textPrimary,
                                  ),
                                  overflow: TextOverflow.ellipsis,
                                ),
                                const SizedBox(height: 3),
                                Text(
                                  signedIn
                                      ? t(
                                          'Signed in with Supabase Auth',
                                          'Masuk dengan Supabase Auth',
                                          lang,
                                        )
                                      : t(
                                          'Reading stays on this device until you sign in.',
                                          'Bacaan tetap di perangkat ini sampai Anda masuk.',
                                          lang,
                                        ),
                                  style: HText.labelSm.copyWith(
                                    color: p.textMuted,
                                    fontSize: 10,
                                    height: 1.4,
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ],
                      ),
                      if (auth.configured) ...[
                        const SizedBox(height: 12),
                        if (signedIn)
                          SecondaryButton(
                            label: t('Sign out', 'Keluar', lang),
                            icon: Icons.logout_rounded,
                            expand: true,
                            onTap: auth.signOut,
                          )
                        else
                          PrimaryButton(
                            label: t(
                              'Sign in or register',
                              'Masuk atau daftar',
                              lang,
                            ),
                            icon: Icons.login_rounded,
                            onTap: () => Navigator.of(context).push(
                              MaterialPageRoute(
                                builder: (_) => const LoginPage(),
                              ),
                            ),
                          ),
                      ] else ...[
                        const SizedBox(height: 10),
                        Text(
                          t(
                            'Sign-in is not configured in this build.',
                            'Login belum dikonfigurasi pada build ini.',
                            lang,
                          ),
                          style: HText.labelSm.copyWith(
                            color: p.textMuted,
                            fontSize: 9.5,
                          ),
                        ),
                      ],
                    ],
                  ),
                );
              },
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                _stat(
                  context,
                  '${state.readsToday}',
                  t('read today', 'dibaca hari ini', lang),
                ),
                const SizedBox(width: 9),
                _stat(
                  context,
                  '${state.bookmarks.length}',
                  t('bookmarks', 'tersimpan', lang),
                ),
                const SizedBox(width: 9),
                _stat(
                  context,
                  '${state.downloads.length}',
                  t('offline', 'luring', lang),
                ),
              ],
            ),
            const SizedBox(height: 20),
            SectionLabel(
              icon: Icons.bookmark_rounded,
              text: t('BOOKMARKS', 'BOOKMARK', lang),
            ),
            const SizedBox(height: 10),
            if (state.bookmarks.isEmpty)
              CardSurface(
                padding: const EdgeInsets.all(15),
                child: Row(
                  children: [
                    Icon(
                      Icons.bookmark_border_rounded,
                      size: 18,
                      color: p.textMuted,
                    ),
                    const SizedBox(width: 10),
                    Expanded(
                      child: Text(
                        t(
                          'No bookmarks yet. Tap the bookmark icon on any narration.',
                          'Belum ada bookmark. Ketuk ikon bookmark pada riwayat mana pun.',
                          lang,
                        ),
                        style: HText.bodySm.copyWith(
                          color: p.textMuted,
                          height: 1.5,
                        ),
                      ),
                    ),
                  ],
                ),
              )
            else
              for (final b in state.sortedBookmarks.take(3))
                Padding(
                  padding: const EdgeInsets.only(bottom: 9),
                  child: CardSurface(
                    onTap: () => Navigator.of(context).push(
                      MaterialPageRoute(
                        builder: (_) => HadithDetailPage(
                          bookId: b.bookId,
                          number: b.number,
                          bookTitle: b.bookTitle,
                        ),
                      ),
                    ),
                    padding: const EdgeInsets.fromLTRB(14, 12, 14, 12),
                    child: Row(
                      children: [
                        Container(
                          width: 34,
                          height: 34,
                          decoration: BoxDecoration(
                            color: p.dark
                                ? Brand.emeraldBright.withValues(alpha: 0.14)
                                : Brand.emerald.withValues(alpha: 0.09),
                            borderRadius: BorderRadius.circular(10),
                          ),
                          child: Icon(
                            Icons.bookmark_rounded,
                            size: 17,
                            color: p.emerald,
                          ),
                        ),
                        const SizedBox(width: 11),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                b.bookTitle,
                                maxLines: 1,
                                overflow: TextOverflow.ellipsis,
                                style: HText.bodySm.copyWith(
                                  color: p.textPrimary,
                                  fontWeight: FontWeight.w600,
                                  fontSize: 12,
                                ),
                              ),
                              const SizedBox(height: 2),
                              Text(
                                '#${b.number}${b.translation.isEmpty ? '' : ' • ${b.translation}'}',
                                maxLines: 1,
                                overflow: TextOverflow.ellipsis,
                                style: HText.labelSm.copyWith(
                                  color: p.textMuted,
                                  fontSize: 9.5,
                                ),
                              ),
                            ],
                          ),
                        ),
                        Icon(
                          Icons.chevron_right_rounded,
                          size: 17,
                          color: p.outline,
                        ),
                      ],
                    ),
                  ),
                ),
            CardSurface(
              onTap: () => Navigator.of(
                context,
              ).push(MaterialPageRoute(builder: (_) => const SavedPage())),
              padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 13),
              child: Row(
                children: [
                  Icon(
                    Icons.library_books_outlined,
                    size: 18,
                    color: p.textMuted,
                  ),
                  const SizedBox(width: 10),
                  Expanded(
                    child: Text(
                      t('Manage bookmarks', 'Kelola bookmark', lang),
                      style: HText.bodySm.copyWith(
                        color: p.textPrimary,
                        fontWeight: FontWeight.w600,
                        fontSize: 12.5,
                      ),
                    ),
                  ),
                  Text(
                    '${state.bookmarks.length}',
                    style: HText.labelSm.copyWith(
                      color: p.textMuted,
                      fontSize: 10,
                    ),
                  ),
                  const SizedBox(width: 3),
                  Icon(Icons.chevron_right_rounded, size: 17, color: p.outline),
                ],
              ),
            ),
            const SizedBox(height: 20),
            SectionLabel(
              icon: Icons.history_rounded,
              text: t('CONTINUE READING', 'LANJUTKAN BACAAN'),
            ),
            const SizedBox(height: 10),
            if (reads.isEmpty)
              CardSurface(
                padding: const EdgeInsets.all(16),
                child: Text(
                  t(
                    'Open any narration and it will show up here.',
                    'Buka riwayat mana pun, akan muncul di sini.',
                    lang,
                  ),
                  style: HText.bodySm.copyWith(color: p.textMuted),
                ),
              )
            else
              for (final r in reads.take(8))
                Padding(
                  padding: const EdgeInsets.only(bottom: 9),
                  child: CardSurface(
                    onTap: () => Navigator.of(context).push(
                      MaterialPageRoute(
                        builder: (_) => HadithDetailPage(
                          bookId: r.bookId,
                          number: r.number,
                        ),
                      ),
                    ),
                    child: Row(
                      children: [
                        Icon(
                          Icons.bookmark_border_rounded,
                          size: 17,
                          color: p.gold,
                        ),
                        const SizedBox(width: 11),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                r.bookTitle,
                                style: HText.bodySm.copyWith(
                                  color: p.textPrimary,
                                  fontWeight: FontWeight.w600,
                                  fontSize: 12,
                                ),
                              ),
                              const SizedBox(height: 2),
                              Text(
                                '#${r.number}${r.chapter.isEmpty ? '' : ' • ${r.chapter}'}',
                                style: HText.labelSm.copyWith(
                                  color: p.textMuted,
                                  fontSize: 9.5,
                                ),
                              ),
                            ],
                          ),
                        ),
                        Icon(
                          Icons.chevron_right_rounded,
                          size: 17,
                          color: p.outline,
                        ),
                      ],
                    ),
                  ),
                ),
            const SizedBox(height: 20),
            SectionLabel(
              icon: Icons.cloud_sync_outlined,
              text: t('CROSS-DEVICE SYNC', 'SINKRONISASI ANTAR PERANGKAT'),
            ),
            const SizedBox(height: 10),
            CardSurface(
              padding: const EdgeInsets.all(15),
              child: ListenableBuilder(
                listenable: Listenable.merge([
                  AuthService.instance,
                  SyncService.instance,
                ]),
                builder: (context, _) {
                  final auth = AuthService.instance;
                  final sync = SyncService.instance;
                  final String title;
                  final String body;
                  if (!auth.signedIn) {
                    title = t('Local only', 'Hanya lokal', lang);
                    body = t(
                      'Sign in to copy bookmarks and last-read positions to your account, so a second device picks up where you left off.',
                      'Masuk untuk menyalin bookmark dan posisi bacaan terakhir ke akun, sehingga perangkat lain melanjutkan dari titik yang sama.',
                      lang,
                    );
                  } else if (sync.syncing) {
                    title = t('Syncing…', 'Menyinkronkan…', lang);
                    body = t(
                      'Sending this device\'s bookmarks and reading progress.',
                      'Mengirim bookmark dan progres bacaan perangkat ini.',
                      lang,
                    );
                  } else if (sync.error != null) {
                    title = t('Sync failed', 'Sinkronisasi gagal', lang);
                    body = auth.email == null
                        ? sync.error!
                        : '${auth.email} · ${sync.error!.length > 140 ? '${sync.error!.substring(0, 140)}…' : sync.error}';
                  } else {
                    final at = sync.lastSynced;
                    final stamp = at == null
                        ? ''
                        : '${at.hour.toString().padLeft(2, '0')}:${at.minute.toString().padLeft(2, '0')}';
                    title = t('Synced', 'Tersinkron', lang);
                    body = [
                      auth.email ?? '',
                      t(
                        'bookmarks and reading progress',
                        'bookmark dan progres bacaan',
                        lang,
                      ),
                      if (stamp.isNotEmpty) stamp,
                    ].where((s) => s.isNotEmpty).join(' · ');
                  }
                  return Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        title,
                        style: HText.body.copyWith(
                          color: p.textPrimary,
                          fontWeight: FontWeight.w600,
                          fontSize: 13,
                        ),
                      ),
                      const SizedBox(height: 5),
                      Text(
                        body,
                        style: HText.labelSm.copyWith(
                          color: p.textMuted,
                          fontSize: 10,
                          height: 1.55,
                        ),
                      ),
                      const SizedBox(height: 10),
                      DatasetLine(lang: lang),
                    ],
                  );
                },
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _stat(BuildContext context, String value, String label) {
    final p = context.p;
    return Expanded(
      child: CardSurface(
        padding: const EdgeInsets.symmetric(vertical: 14, horizontal: 10),
        child: Column(
          children: [
            Text(
              value,
              style: HText.h2.copyWith(fontSize: 20, color: p.emerald),
            ),
            const SizedBox(height: 4),
            Text(
              label,
              style: HText.labelSm.copyWith(color: p.textMuted, fontSize: 9),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }
}

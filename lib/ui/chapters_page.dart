import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../data/hadeeth_repository.dart';
import '../models.dart';
import '../state/app_state.dart';
import '../theme.dart';
import 'downloads_page.dart';
import 'hadith_detail_page.dart';
import 'hadith_list_page.dart';
import 'widgets.dart';

class ChaptersPage extends StatefulWidget {
  const ChaptersPage({super.key, required this.book});

  final Book book;

  @override
  State<ChaptersPage> createState() => _ChaptersPageState();
}

class _ChaptersPageState extends State<ChaptersPage> {
  late final Future<List<Chapter>> _chapters;
  final _filter = TextEditingController();
  String _query = '';

  @override
  void initState() {
    super.initState();
    _chapters = context.read<HadeethRepository>().chapters(widget.book.id);
    _filter.addListener(() => setState(() => _query = _filter.text.trim().toLowerCase()));
  }

  @override
  void dispose() {
    _filter.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final p = context.p;
    final state = context.watch<AppState>();
    final lang = state.lang;
    final book = widget.book;
    final last = state.lastRead[book.id];

    return Scaffold(
      body: SafeArea(
        bottom: false,
        child: Column(
          children: [
            PageHeader(
              title: book.title(lang),
              subtitle: '${book.author(lang)}${book.deathYearAh > 0 ? '  •  ${book.deathYearAh} H' : ''}',
              showLogo: false,
              leading: const BackButton2(),
              actions: [
                IconPill(
                  icon: state.downloads.containsKey(book.id) ? Icons.offline_pin_outlined : Icons.download_outlined,
                  tooltip: t('Offline copy', 'Salinan luring', lang),
                  active: state.downloads.containsKey(book.id),
                  onTap: () => Navigator.of(context).push(MaterialPageRoute(builder: (_) => const DownloadsPage())),
                ),
              ],
            ),
            Expanded(
              child: FutureBuilder<List<Chapter>>(
                future: _chapters,
                builder: (context, snap) {
                  if (snap.hasError) return EmptyState(icon: Icons.cloud_off_outlined, title: t('Could not load chapters', 'Gagal memuat bab', lang), message: t('Check your connection and pull again.', 'Periksa koneksi lalu coba lagi.', lang));
                  if (!snap.hasData) return const LoadingBlock(message: 'Loading chapters…');
                  final all = snap.data!;
                  final chapters = _query.isEmpty
                      ? all
                      : all.where((c) => c.titleId.toLowerCase().contains(_query) || c.titleEn.toLowerCase().contains(_query) || c.number.toString() == _query).toList();
                  return ListView(
                    padding: const EdgeInsets.fromLTRB(16, 14, 16, 28),
                    children: [
                      _hero(context, book, lang),
                      const SizedBox(height: 14),
                      if (last != null)
                        Padding(
                          padding: const EdgeInsets.only(bottom: 12),
                          child: CardSurface(
                            onTap: () => Navigator.of(context).push(MaterialPageRoute(builder: (_) => HadithDetailPage(bookId: book.id, number: last.number, bookTitle: book.title(lang)))),
                            padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
                            child: Row(
                              children: [
                                Icon(Icons.bookmark_added_outlined, size: 18, color: p.emerald),
                                const SizedBox(width: 10),
                                Expanded(
                                  child: Text('${t('Continue at', 'Lanjutkan di', lang)} #${last.number}', style: HText.bodySm.copyWith(color: p.textPrimary)),
                                ),
                                Text(t('Resume', 'Lanjut', lang), style: HText.labelSm.copyWith(color: p.emerald)),
                              ],
                            ),
                          ),
                        ),
                      TextField(
                        controller: _filter,
                        onChanged: (_) => setState(() {}),
                        style: HText.bodySm.copyWith(color: p.textPrimary),
                        decoration: InputDecoration(
                          isDense: true,
                          hintText: t('Filter chapters…', 'Saring bab…', lang),
                          hintStyle: HText.bodySm.copyWith(color: p.textMuted),
                          prefixIcon: Icon(Icons.search_rounded, size: 18, color: p.textMuted),
                          filled: true,
                          fillColor: p.surfaceLow,
                          contentPadding: const EdgeInsets.symmetric(vertical: 12),
                          border: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: BorderSide(color: p.border)),
                          enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: BorderSide(color: p.border)),
                          focusedBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: BorderSide(color: p.emerald)),
                        ),
                      ),
                      const SizedBox(height: 16),
                      Row(
                        children: [
                          Expanded(child: SectionLabel(icon: Icons.list_alt_rounded, text: '${formatNumber(chapters.length)} ${t('CHAPTERS', 'BAB')}')),
                        ],
                      ),
                      const SizedBox(height: 10),
                      for (final c in chapters) ...[
                        _chapterTile(context, c, lang, book),
                        const SizedBox(height: 9),
                      ],
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

  Widget _hero(BuildContext context, Book book, String lang) {
    final p = context.p;
    return Container(
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: p.dark ? [const Color(0xFF0E1A2B), const Color(0xFF0A1220)] : [const Color(0xFF001932), const Color(0xFF0B2A46)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: Brand.goldLight.withValues(alpha: 0.28)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              GradeBadge(label: book.gradeSummary.isEmpty ? '—' : book.gradeSummary, tier: book.isSahih ? 'sahih' : 'unknown', small: true),
              const Spacer(),
              Text('${book.totalChapters} ${t('kitab / chapters', 'kitab / bab', lang)}'.toUpperCase(), style: HText.labelSm.copyWith(color: Brand.goldLight, fontSize: 8.5)),
            ],
          ),
          const SizedBox(height: 14),
          Directionality(
            textDirection: TextDirection.rtl,
            child: Text(book.titleAr, style: HText.arabic(26).copyWith(color: Colors.white), maxLines: 2, overflow: TextOverflow.ellipsis),
          ),
          const SizedBox(height: 8),
          Text(book.title(lang), style: HText.h3.copyWith(color: Colors.white, fontSize: 17)),
          const SizedBox(height: 4),
          Text(
            '${book.author(lang)}${book.deathYearAh > 0 ? '  •  d. ${book.deathYearAh} H' : ''}',
            style: HText.bodySm.copyWith(color: Colors.white.withValues(alpha: 0.62)),
          ),
          const SizedBox(height: 16),
          Container(height: 1, color: Colors.white.withValues(alpha: 0.12)),
          const SizedBox(height: 12),
          Row(
            children: [
              Expanded(
                child: Text(
                  '${formatNumber(book.totalHadiths)} ${t('hadiths', 'hadis', lang)}',
                  style: HText.labelSm.copyWith(color: Brand.goldLight, fontSize: 10.5),
                ),
              ),
              GestureDetector(
                onTap: () => Navigator.of(context).push(MaterialPageRoute(builder: (_) => HadithListPage(book: book))),
                child: Row(
                  children: [
                    Text(t('Read sequential', 'Baca berurutan', lang), style: HText.labelSm.copyWith(color: Colors.white, fontSize: 10.5)),
                    const SizedBox(width: 4),
                    const Icon(Icons.arrow_forward_rounded, size: 13, color: Colors.white),
                  ],
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _chapterTile(BuildContext context, Chapter c, String lang, Book book) {
    final p = context.p;
    return CardSurface(
      onTap: () => Navigator.of(context).push(MaterialPageRoute(builder: (_) => HadithListPage(book: book, chapter: c))),
      padding: const EdgeInsets.fromLTRB(14, 13, 14, 13),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            width: 34,
            height: 34,
            decoration: BoxDecoration(
              color: p.surfaceLow,
              borderRadius: BorderRadius.circular(9),
              border: Border.all(color: p.border),
            ),
            alignment: Alignment.center,
            child: Text(c.number.toString(), style: HText.labelSm.copyWith(color: p.textSecondary, fontSize: 10)),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(c.title(lang), style: HText.body.copyWith(color: p.textPrimary, fontWeight: FontWeight.w600, fontSize: 13.5)),
                if (c.titleAr.isNotEmpty) ...[
                  const SizedBox(height: 3),
                  Directionality(
                    textDirection: TextDirection.rtl,
                    child: Text(c.titleAr, style: HText.arabic(15).copyWith(color: p.textMuted), maxLines: 1, overflow: TextOverflow.ellipsis),
                  ),
                ],
                const SizedBox(height: 7),
                Row(
                  children: [
                    Icon(Icons.tag_rounded, size: 11, color: p.textMuted),
                    const SizedBox(width: 3),
                    Text('${c.hadithStart}–${c.hadithEnd}', style: HText.labelSm.copyWith(color: p.textMuted, fontSize: 9.5)),
                    const SizedBox(width: 10),
                    Container(width: 3, height: 3, decoration: BoxDecoration(color: p.outline, shape: BoxShape.circle)),
                    const SizedBox(width: 10),
                    Text('${formatNumber(c.hadithCount)} ${t('hadiths', 'hadis', lang)}', style: HText.labelSm.copyWith(color: p.emerald, fontSize: 9.5)),
                  ],
                ),
              ],
            ),
          ),
          Padding(
            padding: const EdgeInsets.only(top: 9),
            child: Icon(Icons.chevron_right_rounded, size: 20, color: p.outline),
          ),
        ],
      ),
    );
  }
}

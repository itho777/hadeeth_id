import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../data/hadeeth_repository.dart';
import '../models.dart';
import '../state/app_state.dart';
import '../theme.dart';
import 'chapters_page.dart';
import 'search_page.dart';
import 'widgets.dart';

class BooksPage extends StatefulWidget {
  const BooksPage({super.key});

  @override
  State<BooksPage> createState() => _BooksPageState();
}

class _BooksPageState extends State<BooksPage> {
  late final Future<List<Book>> _books;

  /// Selected registry classification, or null for "all".
  String? _class;

  @override
  void initState() {
    super.initState();
    _books = context.read<HadeethRepository>().books();
  }

  @override
  Widget build(BuildContext context) {
    final p = context.p;
    final state = context.watch<AppState>();
    final lang = state.lang;
    return Scaffold(
      body: SafeArea(
        bottom: false,
        child: Column(
          children: [
            PageHeader(
              title: t('Kutub — Collections', 'Kutub — Koleksi', lang),
              subtitle: t('AUTHENTICATED HADITH COMPILATIONS', 'KOMPILASI HADIS TERVERIFIKASI', lang),
              actions: [
                LangToggle(lang: lang, onChanged: (v) => state.setLang(v)),
                const SizedBox(width: 6),
                IconPill(
                  icon: Icons.search_rounded,
                  tooltip: t('Search', 'Cari', lang),
                  onTap: () => Navigator.of(context).push(MaterialPageRoute(builder: (_) => const SearchPage())),
                ),
              ],
            ),
            Divider(height: 1, color: p.border),
            Expanded(
              child: FutureBuilder<List<Book>>(
                future: _books,
                builder: (context, snap) {
                  if (!snap.hasData) return const LoadingBlock(message: 'Loading collections…');
                  if (snap.hasError) {
                    return EmptyState(
                      icon: Icons.cloud_off_outlined,
                      title: t('Offline', 'Luring', lang),
                      message: 'Check connection.',
                    );
                  }
                  final books = snap.data!;
                  // Only the classifications this registry actually ships, in
                  // the registry's own order — no invented groupings.
                  final present = bookClassOrder.where((c) => books.any((b) => b.bookClass == c)).toList();
                  if (_class != null && !present.contains(_class)) _class = null;
                  final shown = _class == null ? books : books.where((b) => b.bookClass == _class).toList();
                  return Column(
                    children: [
                      _classBar(context, books, present, lang),
                      Divider(height: 1, color: p.border),
                      Expanded(child: _list(context, shown, lang)),
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

  Widget _classBar(BuildContext context, List<Book> all, List<String> present, String lang) {
    final p = context.p;
    Widget chip(String? cls, String label, int count) {
      final on = _class == cls;
      return Padding(
        padding: const EdgeInsets.only(right: 8),
        child: GestureDetector(
          onTap: () => setState(() => _class = cls),
          child: Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 7),
            decoration: BoxDecoration(
              color: on ? p.emerald.withValues(alpha: 0.14) : p.card,
              borderRadius: BorderRadius.circular(999),
              border: Border.all(color: on ? p.emerald.withValues(alpha: 0.55) : p.border),
            ),
            child: Text(
              '$label · $count',
              style: HText.labelSm.copyWith(
                color: on ? p.emerald : p.textMuted,
                fontWeight: on ? FontWeight.w700 : FontWeight.w500,
                fontSize: 10,
              ),
            ),
          ),
        ),
      );
    }

    return SizedBox(
      height: 52,
      child: ListView(
        scrollDirection: Axis.horizontal,
        padding: const EdgeInsets.fromLTRB(16, 10, 16, 10),
        children: [
          chip(null, t('ALL', 'SEMUA', lang), all.length),
          for (final c in present) chip(c, bookClassLatin[c] ?? c, all.where((b) => b.bookClass == c).length),
        ],
      ),
    );
  }

  Widget _list(BuildContext context, List<Book> books, String lang) {
    final p = context.p;
    return ListView.builder(
      padding: const EdgeInsets.fromLTRB(16, 14, 16, 24),
      itemCount: books.length,
      itemBuilder: (context, i) {
        final b = books[i];
        return Padding(
          padding: const EdgeInsets.only(bottom: 12),
          child: CardSurface(
            onTap: () => Navigator.of(context).push(MaterialPageRoute(builder: (_) => ChaptersPage(book: b))),
            padding: const EdgeInsets.fromLTRB(16, 14, 14, 12),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Container(
                  width: 46,
                  height: 46,
                  decoration: BoxDecoration(
                    color: p.dark ? Brand.emeraldBright.withValues(alpha: 0.14) : Brand.emerald.withValues(alpha: 0.08),
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(color: p.dark ? Brand.emeraldBright.withValues(alpha: 0.2) : Brand.emerald.withValues(alpha: 0.12)),
                  ),
                  alignment: Alignment.center,
                  child: Text(b.monogram, style: HText.h3.copyWith(color: p.emerald, fontSize: 19)),
                ),
                const SizedBox(width: 14),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(b.title(lang), style: HText.h3.copyWith(fontSize: 15.5, color: p.textPrimary)),
                      const SizedBox(height: 3),
                      Text(
                        '${b.author(lang)}${b.deathYearAh > 0 ? ' • ${b.deathYearAh} H' : ''}',
                        style: HText.bodySm.copyWith(color: p.textMuted),
                      ),
                      const SizedBox(height: 8),
                      Wrap(
                        spacing: 8,
                        runSpacing: 6,
                        crossAxisAlignment: WrapCrossAlignment.center,
                        children: [
                          GradeBadge(label: b.classLabel(lang), tier: 'class', small: true),
                          if (b.gradeSummary.isNotEmpty) GradeBadge(label: b.gradeSummary, tier: b.isSahih ? 'sahih' : 'unknown', small: true),
                          Text('${formatNumber(b.totalHadiths)} ${t('hadiths', 'hadis', lang)}', style: HText.labelSm.copyWith(color: p.textMuted)),
                          Text('${formatNumber(b.totalChapters)} ${t('chapters', 'bab', lang)}', style: HText.labelSm.copyWith(color: p.textMuted)),
                        ],
                      ),
                    ],
                  ),
                ),
                Padding(
                  padding: const EdgeInsets.only(top: 14),
                  child: Icon(Icons.arrow_forward_ios_rounded, size: 15, color: p.emerald),
                ),
              ],
            ),
          ),
        );
      },
    );
  }
}

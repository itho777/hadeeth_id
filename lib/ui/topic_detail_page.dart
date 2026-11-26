import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../data/hadeeth_repository.dart';
import '../models.dart';
import '../state/app_state.dart';
import '../theme.dart';
import 'hadith_detail_page.dart';
import 'widgets.dart';

class TopicDetailPage extends StatefulWidget {
  const TopicDetailPage({super.key, required this.topic});

  final Topic topic;

  @override
  State<TopicDetailPage> createState() => _TopicDetailPageState();
}

class _TopicDetailPageState extends State<TopicDetailPage> {
  final List<Book> _books = [];
  final Map<String, List<Hadith>> _byBook = {};
  final List<String> _order = [];
  List<TopicEntry> _entries = [];
  Set<String> _loadQueue = {};
  bool _loading = true;
  bool _loadingMore = false;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    final repo = context.read<HadeethRepository>();
    try {
      final books = await repo.books();
      _books.addAll(books);
      final index = await repo.topicIndex();
      final entries = index.where((e) => e.topicId == widget.topic.id && e.numbers.isNotEmpty).toList()
        ..sort((a, b) => b.numbers.length.compareTo(a.numbers.length));
      _entries = entries.take(6).toList();
      for (final e in _entries) {
        _loadQueue.add(e.bookId);
      }
      await _loadNextBatch();
      if (mounted) setState(() => _loading = false);
    } catch (_) {
      if (mounted) setState(() => _loading = false);
    }
  }

  Future<void> _loadNextBatch({int count = 3}) async {
    final repo = context.read<HadeethRepository>();
    final pending = _entries.where((e) => _loadQueue.contains(e.bookId)).take(count).toList();
    for (final e in pending) {
      _loadQueue.remove(e.bookId);
      try {
        final hadiths = await repo.hadithsByNumbers(e.bookId, e.numbers.take(6).toList());
        if (hadiths.isNotEmpty) {
          _byBook[e.bookId] = hadiths;
          _order.add(e.bookId);
        }
      } catch (_) {}
    }
    if (mounted) setState(() {});
  }

  @override
  Widget build(BuildContext context) {
    final p = context.p;
    final lang = context.watch<AppState>().lang;
    final topic = widget.topic;
    return Scaffold(
      body: SafeArea(
        bottom: false,
        child: Column(
          children: [
            PageHeader(
              title: topic.name(lang),
              subtitle: '${t('THEME', 'TEMA')} ${topic.id}  •  ${formatNumber(topic.count)} ${t('HADITHS', 'HADIS')}',
              showLogo: false,
              leading: const BackButton2(),
            ),
            Expanded(
              child: _loading
                  ? const LoadingBlock(message: 'Gathering hadiths by theme…')
                  : ListView(
                      padding: const EdgeInsets.fromLTRB(16, 14, 16, 28),
                      children: [
                        Container(
                          padding: const EdgeInsets.all(17),
                          decoration: BoxDecoration(
                            color: p.dark ? Colors.white.withValues(alpha: 0.03) : p.surfaceLow,
                            borderRadius: BorderRadius.circular(18),
                            border: Border.all(color: p.border),
                          ),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(topic.name(lang), style: HText.h2.copyWith(color: p.textPrimary, fontSize: 20)),
                              const SizedBox(height: 6),
                              Directionality(
                                textDirection: TextDirection.rtl,
                                child: Text(topic.nameAr, style: HText.arabic(26).copyWith(color: p.gold)),
                              ),
                              const SizedBox(height: 10),
                              Text(
                                t(
                                  'A cross-collection sweep of narrations filed under this theme, sourced from the hadeeth.id thematic index.',
                                  'Sapuan lintas kitab untuk riwayat dalam tema ini, bersumber dari indeks tematik hadeeth.id.',
                                  lang,
                                ),
                                style: HText.bodySm.copyWith(color: p.textMuted, height: 1.5),
                              ),
                            ],
                          ),
                        ),
                        const SizedBox(height: 18),
                        if (_byBook.isEmpty)
                          EmptyState(
                            icon: Icons.inbox_outlined,
                            title: t('No hadiths mapped', 'Belum ada hadis terpetakan', lang),
                            message: t('This theme has no indexed narration list yet.', 'Tema ini belum memiliki daftar riwayat terindeks.', lang),
                          )
                        else
                          for (final bookId in _order) _bookSection(context, bookId, lang),
                        if (_loadQueue.isNotEmpty) ...[
                          const SizedBox(height: 4),
                          _loadingMore
                              ? const Center(child: Padding(padding: EdgeInsets.all(16), child: SizedBox(width: 22, height: 22, child: CircularProgressIndicator(strokeWidth: 2.2))))
                              : SecondaryButton(
                                  label: t('Load more collections', 'Muat koleksi lain', lang),
                                  icon: Icons.expand_more_rounded,
                                  expand: true,
                                  onTap: () async {
                                    setState(() => _loadingMore = true);
                                    await _loadNextBatch(count: 1);
                                    if (mounted) setState(() => _loadingMore = false);
                                  },
                                ),
                          const SizedBox(height: 10),
                        ],
                      ],
                    ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _bookSection(BuildContext context, String bookId, String lang) {
    final p = context.p;
    final book = _books.where((b) => b.id == bookId).toList();
    final title = book.isEmpty ? bookId : book.first.title(lang);
    final items = _byBook[bookId] ?? const [];
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Expanded(child: SectionLabel(icon: Icons.menu_book_outlined, text: title.toUpperCase())),
            Text('${items.length} ${t('shown', 'tampil', lang)}', style: HText.labelSm.copyWith(color: p.textMuted, fontSize: 9)),
          ],
        ),
        const SizedBox(height: 10),
        for (final h in items) ...[
          CardSurface(
            onTap: () => Navigator.of(context).push(MaterialPageRoute(builder: (_) => HadithDetailPage(bookId: h.bookId, number: h.number, bookTitle: title))),
            padding: const EdgeInsets.fromLTRB(15, 13, 15, 12),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Text('#${h.number}', style: HText.labelSm.copyWith(color: p.textMuted, fontSize: 10)),
                    const SizedBox(width: 8),
                    GradeBadge(label: h.grade.isNotEmpty ? h.grade : t('Hadith', 'Hadis', lang), tier: h.tier, small: true),
                    const Spacer(),
                    Icon(Icons.arrow_outward_rounded, size: 14, color: p.outline),
                  ],
                ),
                const SizedBox(height: 10),
                ArabicBlock(text: h.textAr, size: 19, align: TextAlign.right),
                const SizedBox(height: 10),
                Text(h.translation(lang), style: HText.bodySm.copyWith(color: p.textSecondary, height: 1.5), maxLines: 3, overflow: TextOverflow.ellipsis),
              ],
            ),
          ),
          const SizedBox(height: 10),
        ],
        const SizedBox(height: 8),
      ],
    );
  }
}

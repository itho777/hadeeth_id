import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../data/hadeeth_repository.dart';
import '../models.dart';
import '../state/app_state.dart';
import '../theme.dart';
import 'hadith_detail_page.dart';
import 'search_page.dart';
import 'widgets.dart';

class HadithListPage extends StatefulWidget {
  const HadithListPage({super.key, required this.book, this.chapter});

  final Book book;
  final Chapter? chapter;

  @override
  State<HadithListPage> createState() => _HadithListPageState();
}

class _HadithListPageState extends State<HadithListPage> {
  final ScrollController _scroll = ScrollController();
  final List<Hadith> _items = [];
  bool _loading = true;
  bool _done = false;
  String? _error;
  int _offset = 0;
  static const _pageSize = 12;

  bool get _sequential => widget.chapter == null;

  @override
  void initState() {
    super.initState();
    _scroll.addListener(_onScroll);
    _load();
  }

  @override
  void dispose() {
    _scroll.dispose();
    super.dispose();
  }

  void _onScroll() {
    if (!_scroll.hasClients) return;
    if (_scroll.position.pixels > _scroll.position.maxScrollExtent - 320) _load();
  }

  Future<void> _load() async {
    if (_loading && _items.isNotEmpty) return;
    if (_done) return;
    final repo = context.read<HadeethRepository>();
    if (_items.isEmpty) setState(() => _loading = true);
    try {
      final batch = _sequential
          ? await repo.page(widget.book.id, offset: _offset, limit: _pageSize)
          : (_offset == 0 ? await repo.chapterHadiths(widget.book.id, widget.chapter!) : <Hadith>[]);
      if (!mounted) return;
      setState(() {
        _items.addAll(batch);
        _offset += batch.length;
        _loading = false;
        _done = batch.length < _pageSize || !_sequential;
        _error = null;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _loading = false;
        _error = e.toString();
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final state = context.watch<AppState>();
    final lang = state.lang;
    final chapter = widget.chapter;
    return Scaffold(
      body: SafeArea(
        bottom: false,
        child: Column(
          children: [
            PageHeader(
              title: chapter?.title(lang) ?? widget.book.title(lang),
              subtitle: chapter != null
                  ? '${widget.book.title(lang)}  •  ${t('Chapter', 'Bab', lang)} ${chapter.number}'
                  : '${t('Sequential reading', 'Bacaan berurutan', lang)}  •  ${widget.book.title(lang)}',
              showLogo: false,
              leading: const BackButton2(),
              actions: [
                IconPill(
                  icon: Icons.search_rounded,
                  tooltip: t('Search', 'Cari', lang),
                  onTap: () => Navigator.of(context).push(MaterialPageRoute(builder: (_) => const SearchPage())),
                ),
              ],
            ),
            Expanded(
              child: _items.isEmpty && _loading
                  ? const LoadingBlock(message: 'Loading hadiths…')
                  : _items.isEmpty
                      ? EmptyState(
                          icon: Icons.cloud_off_outlined,
                          title: t('No hadiths here', 'Belum ada hadis', lang),
                          message: _error ?? t('This chapter has no loaded narrations yet.', 'Bab ini belum memiliki riwayat termuat.', lang),
                          action: SecondaryButton(label: t('Retry', 'Coba lagi', lang), icon: Icons.refresh_rounded, onTap: _load),
                        )
                      : ListView.builder(
                          controller: _scroll,
                          padding: const EdgeInsets.fromLTRB(16, 14, 16, 28),
                          itemCount: _items.length + (_done ? 0 : 1),
                          itemBuilder: (context, i) {
                            if (i >= _items.length) {
                              return const Padding(
                                padding: EdgeInsets.symmetric(vertical: 22),
                                child: Center(child: SizedBox(width: 22, height: 22, child: CircularProgressIndicator(strokeWidth: 2.2))),
                              );
                            }
                            final h = _items[i];
                            return Padding(
                              padding: const EdgeInsets.only(bottom: 12),
                              child: _card(context, h, lang),
                            );
                          },
                        ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _card(BuildContext context, Hadith h, String lang) {
    final p = context.p;
    final narrator = h.rawis.isNotEmpty ? h.rawis.first.name : '';
    return CardSurface(
      onTap: () => Navigator.of(context).push(MaterialPageRoute(
        builder: (_) => HadithDetailPage(bookId: h.bookId, number: h.number, bookTitle: widget.book.title(lang), chapterTitle: widget.chapter?.title(lang)),
      )),
      padding: const EdgeInsets.fromLTRB(16, 14, 16, 13),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 9, vertical: 4),
                decoration: BoxDecoration(color: p.dark ? Colors.white.withValues(alpha: 0.06) : p.surfaceLow, borderRadius: BorderRadius.circular(7), border: Border.all(color: p.border)),
                child: Text('#${h.number}', style: HText.labelSm.copyWith(color: p.textSecondary, fontSize: 10)),
              ),
              const SizedBox(width: 8),
              GradeBadge(label: h.grade.isNotEmpty ? h.grade : t('Hadith', 'Hadis', lang), tier: h.tier, small: true),
              const Spacer(),
              Icon(Icons.arrow_outward_rounded, size: 15, color: p.outline),
            ],
          ),
          const SizedBox(height: 12),
          ArabicBlock(text: h.textAr, size: 21, align: TextAlign.right, color: p.textPrimary),
          const SizedBox(height: 12),
          Text(
            h.translation(lang),
            style: HText.bodySm.copyWith(color: p.textSecondary, height: 1.55),
            maxLines: 4,
            overflow: TextOverflow.ellipsis,
          ),
          if (narrator.isNotEmpty) ...[
            const SizedBox(height: 10),
            Row(
              children: [
                Icon(Icons.person_outline, size: 12, color: p.textMuted),
                const SizedBox(width: 4),
                Expanded(child: Text(narrator, style: HText.labelSm.copyWith(color: p.textMuted, fontSize: 10), maxLines: 1, overflow: TextOverflow.ellipsis)),
              ],
            ),
          ],
        ],
      ),
    );
  }
}


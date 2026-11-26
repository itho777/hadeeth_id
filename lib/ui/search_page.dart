import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../data/hadeeth_repository.dart';
import '../data/search_service.dart';
import '../models.dart';
import '../state/app_state.dart';
import '../theme.dart';
import 'hadith_detail_page.dart';
import 'widgets.dart';

class SearchPage extends StatefulWidget {
  const SearchPage({super.key, this.initialQuery, this.onlySahih = false});

  final String? initialQuery;
  final bool onlySahih;

  @override
  State<SearchPage> createState() => _SearchPageState();
}

class _SearchPageState extends State<SearchPage> {
  late final TextEditingController _controller;
  final FocusNode _focus = FocusNode();
  List<SearchHit> _results = [];
  List<Book> _books = [];
  String _mode = 'semantic';
  String _bookFilter = 'all';
  bool _loading = false;
  String? _error;
  String _engine = '';
  bool _hydrating = false;
  int _searchSeq = 0;

  @override
  void initState() {
    super.initState();
    _controller = TextEditingController(text: widget.initialQuery ?? '');
    _loadBooks();
    if ((widget.initialQuery ?? '').isNotEmpty) {
      WidgetsBinding.instance.addPostFrameCallback((_) => _run());
    } else {
      WidgetsBinding.instance.addPostFrameCallback((_) => _focus.requestFocus());
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    _focus.dispose();
    super.dispose();
  }

  Future<void> _loadBooks() async {
    try {
      final books = await context.read<HadeethRepository>().books();
      if (mounted) setState(() => _books = books);
    } catch (_) {}
  }

  Future<void> _run() async {
    final q = _controller.text.trim();
    if (q.isEmpty) return;
    _focus.unfocus();
    final seq = ++_searchSeq;
    setState(() {
      _loading = true;
      _error = null;
      _results = [];
      _engine = '';
    });
    final service = context.read<SearchService>();
    final repo = context.read<HadeethRepository>();
    final set = await service.search(query: q, repo: repo, bookFilter: _bookFilter, method: _mode);
    if (!mounted || seq != _searchSeq) return;
    if (set.method == 'error') {
      setState(() {
        _loading = false;
        _error = set.engine;
      });
      return;
    }
    var hits = set.hits;
    setState(() {
      _results = hits;
      _loading = false;
      _engine = set.engine;
    });
    await _hydrate();
    if (!mounted || seq != _searchSeq) return;
    // The API returns ids only, so a grade filter can only be applied once the
    // matn rows have been pulled from the CDN.
    if (widget.onlySahih) {
      setState(() {
        _results = _results.where((h) => h.grade.toLowerCase().contains('sahih') || h.grade.toLowerCase().contains('shahih')).toList();
      });
    }
  }

  /// Semantic hits come back as ids; pull the matn + translation for display.
  Future<void> _hydrate() async {
    final repo = context.read<HadeethRepository>();
    final missing = _results.where((h) => h.arabic.isEmpty).toList();
    if (missing.isEmpty) return;
    setState(() => _hydrating = true);
    // Resolve in small parallel batches: each hit is one range request, and the
    // whole result page is at most 20 rows.
    for (var start = 0; start < missing.length; start += 5) {
      final batch = missing.skip(start).take(5).toList();
      await Future.wait(batch.map((hit) async {
        try {
          final h = await repo.getHadith(hit.bookId, hit.number);
          if (h == null || !mounted) return;
          final i = _results.indexWhere((r) => r.id == hit.id && r.bookId == hit.bookId);
          if (i < 0) return;
          setState(() {
            _results[i] = SearchHit(
              id: hit.id,
              bookId: hit.bookId,
              bookName: hit.bookName,
              number: hit.number,
              arabic: h.textAr,
              translation: h.translation(context.read<AppState>().lang),
              english: h.textEn,
              grade: h.grade.isNotEmpty ? h.grade : hit.grade,
              source: hit.source,
            );
          });
        } catch (_) {}
      }));
    }
    if (mounted) setState(() => _hydrating = false);
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
            Padding(
              padding: const EdgeInsets.fromLTRB(16, 12, 16, 10),
              child: Row(
                children: [
                  const BackButton2(),
                  const SizedBox(width: 10),
                  Expanded(
                    child: TextField(
                      controller: _controller,
                      focusNode: _focus,
                      textInputAction: TextInputAction.search,
                      onSubmitted: (_) => _run(),
                      style: HText.body.copyWith(color: p.textPrimary, fontSize: 14),
                      decoration: InputDecoration(
                        isDense: true,
                        hintText: t('Search by meaning or phrase…', 'Cari berdasarkan makna atau frasa…', lang),
                        hintStyle: HText.bodySm.copyWith(color: p.textMuted),
                        prefixIcon: Icon(Icons.search_rounded, size: 19, color: p.gold),
                        suffixIcon: _controller.text.isEmpty
                            ? null
                            : GestureDetector(
                                onTap: () => setState(() => _controller.clear()),
                                child: Icon(Icons.close_rounded, size: 17, color: p.textMuted),
                              ),
                        filled: true,
                        fillColor: p.card,
                        contentPadding: const EdgeInsets.symmetric(vertical: 13),
                        border: OutlineInputBorder(borderRadius: BorderRadius.circular(14), borderSide: BorderSide(color: p.border)),
                        enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(14), borderSide: BorderSide(color: p.border)),
                        focusedBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(14), borderSide: BorderSide(color: p.emerald)),
                      ),
                    ),
                  ),
                ],
              ),
            ),
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16),
              child: Row(
                children: [
                  ChipButton(label: t('AI semantic', 'AI semantik', lang), selected: _mode == 'semantic', onTap: () => setState(() => _mode = 'semantic')),
                  const SizedBox(width: 8),
                  ChipButton(label: t('Offline keyword', 'Kata kunci luring', lang), selected: _mode == 'offline', onTap: () => setState(() => _mode = 'offline')),
                  const Spacer(),
                  GestureDetector(
                    onTap: _pickBook,
                    child: Row(
                      children: [
                        Icon(Icons.tune_rounded, size: 15, color: p.textMuted),
                        const SizedBox(width: 5),
                        Text(_bookFilter == 'all' ? t('All collections', 'Semua kitab', lang) : _bookFilter, style: HText.labelSm.copyWith(color: p.textSecondary, fontSize: 10)),
                      ],
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 10),
            Expanded(child: _body(context, state, lang)),
          ],
        ),
      ),
    );
  }

  Widget _body(BuildContext context, AppState state, String lang) {
    final p = context.p;
    if (_loading) return const LoadingBlock(message: 'Searching the archive…');
    if (_error != null) {
      return EmptyState(
        icon: Icons.wifi_off_rounded,
        title: t('Search unavailable', 'Pencarian tidak tersedia', lang),
        message: _error!,
        action: Column(
          children: [
            SecondaryButton(label: t('Retry', 'Coba lagi', lang), icon: Icons.refresh_rounded, onTap: _run),
            const SizedBox(height: 8),
            Text(
              _mode == 'offline' ? t('Offline keyword search only covers downloaded collections.', 'Pencarian luring hanya mencakup kitab yang diunduh.', lang) : t('Semantic search needs a connection to hadeeth.id.', 'Pencarian semantik butuh koneksi ke hadeeth.id.', lang),
              style: HText.labelSm.copyWith(color: p.textMuted, fontSize: 9.5),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      );
    }
    if (_results.isEmpty) {
      return SingleChildScrollView(
        padding: const EdgeInsets.fromLTRB(16, 8, 16, 24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const SizedBox(height: 6),
            SectionLabel(icon: Icons.lightbulb_outline, text: t('TRY A THEME', 'COBA SEBUAH TEMA')),
            const SizedBox(height: 12),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: [
                for (final s in (lang == 'id'
                    ? ['niat dan amal', 'berbakti kepada orang tua', 'hukum riba', 'sabar dalam musibah', 'keutamaan ilmu']
                    : ['intention and deeds', 'kindness to parents', 'prohibition of riba', 'patience in hardship', 'virtue of knowledge']))
                  GestureDetector(
                    onTap: () {
                      _controller.text = s;
                      _run();
                    },
                    child: Container(
                      padding: const EdgeInsets.symmetric(horizontal: 13, vertical: 9),
                      decoration: BoxDecoration(color: p.surfaceLow, borderRadius: BorderRadius.circular(999), border: Border.all(color: p.border)),
                      child: Text(s, style: HText.bodySm.copyWith(color: p.textSecondary, fontSize: 11.5)),
                    ),
                  ),
              ],
            ),
            const SizedBox(height: 26),
            CardSurface(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  SectionLabel(icon: Icons.auto_awesome_outlined, text: t('HOW IT SEARCHES', 'CARA PENCARIANNYA')),
                  const SizedBox(height: 10),
                  Text(
                    t(
                      'AI semantic mode matches meaning, not just words — ask in Indonesian or English and it reaches the Arabic text. Offline keyword mode scans collections you have downloaded.',
                      'Mode AI semantik mencocokkan makna, bukan hanya kata — tanyakan dalam bahasa Indonesia atau Inggris dan ia menjangkau teks Arab. Mode luring memindai kitab yang sudah diunduh.',
                      lang,
                    ),
                    style: HText.bodySm.copyWith(color: p.textMuted, height: 1.55),
                  ),
                ],
              ),
            ),
          ],
        ),
      );
    }
    return Column(
      children: [
        Padding(
          padding: const EdgeInsets.fromLTRB(16, 0, 16, 8),
          child: Row(
            children: [
              Text(
                '${_results.length} ${_results.length == 1 ? t('result', 'hasil', lang) : t('results', 'hasil', lang)}',
                style: HText.labelSm.copyWith(color: p.textSecondary, fontSize: 10),
              ),
              const SizedBox(width: 8),
              if (_hydrating) const SizedBox(width: 11, height: 11, child: CircularProgressIndicator(strokeWidth: 1.8)),
              const Spacer(),
              Flexible(child: Text(_engine, style: HText.labelSm.copyWith(color: p.textMuted, fontSize: 8.5), overflow: TextOverflow.ellipsis)),
            ],
          ),
        ),
        Expanded(
          child: ListView.builder(
            padding: const EdgeInsets.fromLTRB(16, 0, 16, 26),
            itemCount: _results.length,
            itemBuilder: (context, i) => Padding(
              padding: const EdgeInsets.only(bottom: 11),
              child: _hit(context, _results[i], lang),
            ),
          ),
        ),
      ],
    );
  }

  Widget _hit(BuildContext context, SearchHit hit, String lang) {
    final p = context.p;
    return CardSurface(
      onTap: () => Navigator.of(context).push(MaterialPageRoute(
        builder: (_) => HadithDetailPage(bookId: hit.bookId, number: hit.number, bookTitle: hit.bookName),
      )),
      padding: const EdgeInsets.fromLTRB(15, 13, 15, 12),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Expanded(child: MetaLine(text: '${hit.bookName.toUpperCase()}  •  #${hit.number}')),
              if (hit.grade.isNotEmpty) GradeBadge(label: hit.grade, tier: _tier(hit.grade), small: true),
            ],
          ),
          if (hit.arabic.isNotEmpty) ...[
            const SizedBox(height: 10),
            ArabicBlock(text: hit.arabic, size: 19, align: TextAlign.right),
          ],
          if (hit.translation.isNotEmpty) ...[
            const SizedBox(height: 10),
            Text(hit.translation, style: HText.bodySm.copyWith(color: p.textSecondary, height: 1.5), maxLines: 4, overflow: TextOverflow.ellipsis),
          ] else if (hit.arabic.isEmpty) ...[
            const SizedBox(height: 10),
            Text(t('Tap to open this narration.', 'Ketuk untuk membuka riwayat ini.', lang), style: HText.bodySm.copyWith(color: p.textMuted)),
          ],
        ],
      ),
    );
  }

  String _tier(String grade) {
    final g = grade.toLowerCase();
    if (g.contains('sahih') || g.contains('shahih')) return 'sahih';
    if (g.contains('hasan')) return 'hasan';
    if (g.contains('daif') || g.contains('dhaif')) return 'daif';
    return 'unknown';
  }

  Future<void> _pickBook() async {
    final p = context.p;
    final selected = await showModalBottomSheet<String>(
      context: context,
      backgroundColor: p.card,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(borderRadius: BorderRadius.vertical(top: Radius.circular(20))),
      builder: (ctx) => SafeArea(
        child: ConstrainedBox(
          constraints: BoxConstraints(maxHeight: MediaQuery.of(ctx).size.height * 0.7),
          child: ListView(
            shrinkWrap: true,
            padding: const EdgeInsets.fromLTRB(20, 16, 20, 12),
            children: [
              Text(t('Filter by collection', 'Saring menurut kitab', context.read<AppState>().lang), style: HText.h3.copyWith(color: p.textPrimary, fontSize: 16)),
              const SizedBox(height: 12),
              for (final entry in [<String, String>{'id': 'all', 'label': t('All collections', 'Semua kitab', context.read<AppState>().lang)}, ..._books.map((b) => {'id': b.id, 'label': b.title(context.read<AppState>().lang)})])
                Padding(
                  padding: const EdgeInsets.only(bottom: 7),
                  child: GestureDetector(
                    onTap: () => Navigator.pop(ctx, entry['id']),
                    child: Container(
                      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 11),
                      decoration: BoxDecoration(
                        color: _bookFilter == entry['id'] ? p.surfaceHigh : p.surfaceLow,
                        borderRadius: BorderRadius.circular(11),
                        border: Border.all(color: p.border),
                      ),
                      child: Row(
                        children: [
                          Expanded(child: Text(entry['label']!, style: HText.bodySm.copyWith(color: p.textPrimary))),
                          if (_bookFilter == entry['id']) Icon(Icons.check_rounded, size: 16, color: p.emerald),
                        ],
                      ),
                    ),
                  ),
                ),
            ],
          ),
        ),
      ),
    );
    if (selected != null) {
      setState(() => _bookFilter = selected);
      if (_results.isNotEmpty) _run();
    }
  }
}

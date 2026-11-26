import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:provider/provider.dart';
import 'package:share_plus/share_plus.dart';

import '../data/edition_options.dart';
import '../data/hadeeth_repository.dart';
import '../models.dart';
import '../state/app_state.dart';
import '../theme.dart';
import 'export_page.dart';
import 'sanad_page.dart';
import 'syarah_page.dart';
import 'widgets.dart';

class HadithDetailPage extends StatefulWidget {
  const HadithDetailPage({
    super.key,
    required this.bookId,
    required this.number,
    this.bookTitle,
    this.chapterTitle,
  });

  final String bookId;
  final String number;
  final String? bookTitle;
  final String? chapterTitle;

  @override
  State<HadithDetailPage> createState() => _HadithDetailPageState();
}

class _HadithDetailPageState extends State<HadithDetailPage> {
  Hadith? _hadith;
  String? _error;
  String _bookTitle = '';
  String _chapterTitle = '';
  String _prev = '';
  String _next = '';
  bool _loading = true;
  bool _showAllGradings = false;
  String _transTab = 'id';
  String? _editionKey;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() {
      _loading = true;
      _error = null;
      _editionKey = null;
    });
    final repo = context.read<HadeethRepository>();
    final state = context.read<AppState>();
    try {
      final book = await repo.book(widget.bookId);
      final h = await repo.getHadith(widget.bookId, widget.number);
      if (!mounted) return;
      if (h == null) {
        setState(() {
          _loading = false;
          _error = 'not-found';
        });
        return;
      }
      String chapterTitle = widget.chapterTitle ?? '';
      if (chapterTitle.isEmpty && h.chapterId.isNotEmpty) {
        final chapters = await repo.chapters(widget.bookId);
        for (final c in chapters) {
          if ('${c.number}' == h.chapterId || c.id == h.chapterId) {
            chapterTitle = c.title(state.lang);
            break;
          }
        }
      }
      final neighbours = await repo.neighbours(widget.bookId, h.number);
      // Fetch syarah if available
      final syarah = await repo.getSyarah(widget.bookId, h.number);
      if (!mounted) return;
      setState(() {
        _hadith = syarah != null ? h.copyWith(syarah: syarah) : h;
        _bookTitle = widget.bookTitle ?? book?.title(state.lang) ?? widget.bookId;
        _chapterTitle = chapterTitle;
        _prev = neighbours.isNotEmpty ? neighbours.first.n : '';
        _next = neighbours.length > 1 ? neighbours[1].n : '';
        _loading = false;
        _transTab = state.translationMode == 'en' ? 'en' : 'id';
      });
      state.recordRead(widget.bookId, _bookTitle, h.number, chapterTitle);
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _loading = false;
        _error = e.toString();
      });
    }
  }

  void _open(String number) {
    if (number.isEmpty) return;
    Navigator.of(context).pushReplacement(MaterialPageRoute(
      builder: (_) => HadithDetailPage(bookId: widget.bookId, number: number, bookTitle: _bookTitle),
    ));
  }

  String _citation(Hadith h, String lang) {
    final book = _bookTitle;
    final ref = '$book, ${t('Hadith', 'Hadis', lang)} ${h.number}';
    final body = h.translation(lang);
    return '$body\n\n— $ref${h.grade.isNotEmpty ? ' (${h.grade})' : ''}\nhadeeth.id';
  }

  @override
  Widget build(BuildContext context) {
    final state = context.watch<AppState>();
    final lang = state.lang;

    return Scaffold(
      body: SafeArea(
        bottom: false,
        child: Column(
          children: [
            PageHeader(
              title: _bookTitle.isEmpty ? widget.bookId : _bookTitle,
              subtitle: '${t('HADITH', 'HADIS')} #${widget.number}${_chapterTitle.isNotEmpty ? '  •  $_chapterTitle' : ''}',
              showLogo: false,
              leading: const BackButton2(),
              actions: [
                IconPill(
                  icon: Icons.ios_share_rounded,
                  tooltip: t('Share', 'Bagikan', lang),
                  onTap: _hadith == null ? () {} : () => _share(_hadith!, lang),
                ),
              ],
            ),
            Expanded(
              child: _loading
                  ? const LoadingBlock(message: 'Loading hadith…')
                  : _error != null
                      ? EmptyState(
                          icon: Icons.cloud_off_outlined,
                          title: t('Hadith not available', 'Hadis tidak tersedia', lang),
                          message: _error == 'not-found'
                              ? t('This number is outside the loaded index for the collection.', 'Nomor ini di luar indeks koleksi yang termuat.', lang)
                              : '$_error',
                          action: SecondaryButton(label: t('Retry', 'Coba lagi', lang), icon: Icons.refresh_rounded, onTap: _load),
                        )
                      : ListView(
                          padding: const EdgeInsets.fromLTRB(16, 14, 16, 120),
                          children: [
                            _metaRow(context, _hadith!, lang),
                            const SizedBox(height: 14),
                            _matnCard(context, _hadith!, state, lang),
                            const SizedBox(height: 18),
                            _sanadCard(context, _hadith!, state, lang),
                            const SizedBox(height: 18),
                            _gradingsCard(context, _hadith!, lang),
                            const SizedBox(height: 18),
                            _actionsCard(context, _hadith!, lang),
                            const SizedBox(height: 18),
                            _neighbours(context, lang),
                          ],
                        ),
            ),
          ],
        ),
      ),
      bottomNavigationBar: _hadith == null ? null : _bottomBar(context, _hadith!, state, lang),
    );
  }

  Widget _metaRow(BuildContext context, Hadith h, String lang) {
    final p = context.p;
    return Row(
      children: [
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 11, vertical: 5),
          decoration: BoxDecoration(
            color: p.dark ? Brand.emeraldBright.withValues(alpha: 0.14) : Brand.emerald.withValues(alpha: 0.09),
            borderRadius: BorderRadius.circular(8),
            border: Border.all(color: (p.dark ? Brand.emeraldBright : Brand.emerald).withValues(alpha: 0.25)),
          ),
          child: Text('#${h.number}', style: HText.label.copyWith(color: p.emerald, fontSize: 11)),
        ),
        const SizedBox(width: 8),
        GradeBadge(label: h.grade.isNotEmpty ? h.grade : t('Hadith', 'Hadis', lang), tier: h.tier, small: true),
        if (h.status.isNotEmpty) ...[
          const SizedBox(width: 8),
          GradeBadge(label: h.status, tier: 'unknown', small: true),
        ],
        const Spacer(),
        if (h.elevation.isNotEmpty)
          MetaLine(text: h.elevation.toUpperCase(), color: p.gold),
      ],
    );
  }

  Widget _matnCard(BuildContext context, Hadith h, AppState state, String lang) {
    final p = context.p;
    final translations = <String, String>{
      if (h.textId.isNotEmpty) 'id': h.textId,
      if (h.textEn.isNotEmpty) 'en': h.textEn,
    };
    final showBoth = state.translationMode == 'both';
    final active = translations.containsKey(_transTab) ? _transTab : (translations.isEmpty ? 'id' : translations.keys.first);
    final editions = editionOptions(h);
    
    // Get all available translation languages from the full dataset
    final availableLangs = h.availableLanguages;
    final primaryLangs = <String>[];
    for (final l in availableLangs) {
      final t = h.primaryTranslation(l);
      if (t != null && t.isNotEmpty) primaryLangs.add(l);
    }

    return CardSurface(
      padding: const EdgeInsets.fromLTRB(18, 16, 18, 16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Row(
            children: [
              Icon(Icons.auto_stories_outlined, size: 14, color: p.gold),
              const SizedBox(width: 6),
              Text(t('MATN — TEXT', 'MATN — TEKS'), style: HText.labelSm.copyWith(color: p.gold, fontSize: 9)),
              const Spacer(),
              _miniIcon(context, Icons.text_decrease_rounded, () => state.setArabicSize(state.arabicSize - 2)),
              const SizedBox(width: 6),
              _miniIcon(context, Icons.text_increase_rounded, () => state.setArabicSize(state.arabicSize + 2)),
              const SizedBox(width: 6),
              _miniIcon(context, Icons.copy_all_outlined, () {
                Clipboard.setData(ClipboardData(text: h.textAr));
                showSnack(context, t('Arabic copied', 'Teks Arab disalin', lang));
              }),
            ],
          ),
          const SizedBox(height: 16),
          ArabicBlock(text: h.textAr, size: state.arabicSize),
          const SizedBox(height: 18),
          Container(height: 1, color: p.divider),
          const SizedBox(height: 14),
          
          // Language selector for all available translations
          if (primaryLangs.length > 1)
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(t('TRANSLATIONS', 'TERJEMAHAN'), style: HText.labelSm.copyWith(color: p.gold, fontSize: 9)),
                const SizedBox(height: 8),
                Wrap(
                  spacing: 6,
                  runSpacing: 6,
                  children: [
                    for (final l in primaryLangs)
                      _LanguageChip(
                        label: _langLabel(l),
                        selected: _transTab == l,
                        onTap: () => setState(() => _transTab = l),
                      ),
                  ],
                ),
                const SizedBox(height: 12),
              ],
            ),
          
          if (translations.isEmpty && primaryLangs.isEmpty)
            Text(t('Translation not available for this narration.', 'Terjemahan belum tersedia untuk riwayat ini.', lang), style: HText.bodySm.copyWith(color: p.textMuted))
          else
            Text(
              showBoth ? translations.values.join('\n\n') : (translations[active] ?? h.primaryTranslation(_transTab) ?? ''),
              style: HText.body.copyWith(color: p.textSecondary, height: 1.65),
            ),
          
          // Show all translations for the selected language if multiple sources
          if (primaryLangs.contains(_transTab) && h.translationsFor(_transTab).length > 1) ...[
            const SizedBox(height: 14),
            _translationSourcesCard(context, h, _transTab, lang),
          ],
          
          if (editions.isNotEmpty) ...[
            const SizedBox(height: 14),
            _otherEditions(context, h, lang, editions),
          ],
        ],
      ),
    );
  }

  Widget _translationSourcesCard(BuildContext context, Hadith h, String langCode, String uiLang) {
    final p = context.p;
    final sources = h.translationsFor(langCode);
    
    return CardSurface(
      padding: const EdgeInsets.fromLTRB(14, 12, 14, 12),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.source_outlined, size: 13, color: p.textMuted),
              const SizedBox(width: 6),
              Text('${_langLabel(langCode)} (${sources.length} sources)', style: HText.labelSm.copyWith(color: p.textMuted, fontSize: 9)),
            ],
          ),
          const SizedBox(height: 8),
          for (var i = 0; i < sources.length; i++) ...[
            if (i > 0) Container(height: 1, color: p.divider, margin: const EdgeInsets.symmetric(vertical: 8)),
            Padding(
              padding: const EdgeInsets.symmetric(vertical: 4),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                        decoration: BoxDecoration(
                          color: p.dark ? Brand.emeraldBright.withValues(alpha: 0.14) : Brand.emerald.withValues(alpha: 0.09),
                          borderRadius: BorderRadius.circular(4),
                        ),
                        child: Text(sources[i]['source']?.toUpperCase() ?? 'UNKNOWN', style: HText.labelSm.copyWith(fontSize: 8, color: p.emerald)),
                      ),
                    ],
                  ),
                  const SizedBox(height: 6),
                  Text(
                    sources[i]['text'] ?? '',
                    style: HText.bodySm.copyWith(color: p.textSecondary, height: 1.55),
                  ),
                ],
              ),
            ),
          ],
        ],
      ),
    );
  }

  String _langLabel(String code) {
    const labels = {
      'ar': 'ARABIC',
      'id': 'INDONESIA',
      'en': 'ENGLISH',
      'urd': 'URDU',
      'rus': 'RUSSIAN',
      'fra': 'FRENCH',
      'tur': 'TURKISH',
      'ben': 'BENGALI',
      'tam': 'TAMIL',
    };
    return labels[code] ?? code.toUpperCase();
  }

  Widget _LanguageChip({
    required String label,
    required bool selected,
    required VoidCallback onTap,
  }) {
    final p = context.p;
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
        decoration: BoxDecoration(
          color: selected ? (p.dark ? Brand.emeraldBright.withValues(alpha: 0.18) : Brand.emerald.withValues(alpha: 0.12)) : p.surfaceLow,
          borderRadius: BorderRadius.circular(20),
          border: Border.all(color: selected ? (p.dark ? Brand.emeraldBright : Brand.emerald) : p.border),
        ),
        child: Text(
          label,
          style: HText.labelSm.copyWith(
            fontSize: 9.5,
            color: selected ? p.emerald : p.textSecondary,
            fontWeight: selected ? FontWeight.w600 : FontWeight.normal,
          ),
        ),
      ),
    );
  }

  Widget _otherEditions(BuildContext context, Hadith h, String lang, List<EditionOption> options) {
    final p = context.p;
    if (options.isEmpty) return const SizedBox.shrink();
    EditionOption? selected;
    for (final option in options) {
      if (option.key == _editionKey) {
        selected = option;
        break;
      }
    }
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Row(
          children: [
            Icon(Icons.translate_rounded, size: 15, color: p.textMuted),
            const SizedBox(width: 6),
            Text('${t('Other editions', 'Edisi lain', lang)} (${options.length})',
                style: HText.bodySm.copyWith(color: p.textPrimary, fontWeight: FontWeight.w600)),
            const Spacer(),
            PopupMenuButton<EditionOption>(
              tooltip: '',
              onSelected: (option) => setState(() => _editionKey = option.key),
              constraints: const BoxConstraints(minWidth: 190, maxWidth: 280),
              itemBuilder: (_) => [
                for (final option in options)
                  PopupMenuItem<EditionOption>(
                    value: option,
                    child: Text(option.label, style: HText.bodySm.copyWith(color: p.textPrimary)),
                  ),
              ],
              child: Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 7),
                decoration: BoxDecoration(
                  color: p.surfaceLow,
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: p.border),
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Text(
                      selected?.label ?? t('Select', 'Pilih', lang),
                      style: HText.labelSm.copyWith(color: p.textSecondary, fontSize: 10),
                    ),
                    const SizedBox(width: 4),
                    Icon(Icons.expand_more_rounded, size: 15, color: p.textMuted),
                  ],
                ),
              ),
            ),
          ],
        ),
        if (selected != null) ...[
          const SizedBox(height: 12),
          Row(
            children: [
              Text(selected.label, style: HText.labelSm.copyWith(color: p.gold, fontSize: 9)),
              const Spacer(),
              GestureDetector(
                onTap: () => setState(() => _editionKey = null),
                child: Icon(Icons.close_rounded, size: 14, color: p.textMuted),
              ),
            ],
          ),
          const SizedBox(height: 6),
          Text(selected.text, style: HText.bodySm.copyWith(color: p.textSecondary, height: 1.55)),
        ],
      ],
    );
  }

  Widget _miniIcon(BuildContext context, IconData icon, VoidCallback onTap) {
    final p = context.p;
    return GestureDetector(
      onTap: onTap,
      child: Container(
        width: 28,
        height: 28,
        decoration: BoxDecoration(color: p.surfaceLow, borderRadius: BorderRadius.circular(8), border: Border.all(color: p.border)),
        child: Icon(icon, size: 14, color: p.textSecondary),
      ),
    );
  }

  Widget _sanadCard(BuildContext context, Hadith h, AppState state, String lang) {
    final p = context.p;
    final rawis = h.rawis;
    return CardSurface(
      onTap: () => Navigator.of(context).push(MaterialPageRoute(builder: (_) => SanadPage(hadith: h, bookTitle: _bookTitle))),
      padding: const EdgeInsets.fromLTRB(16, 15, 16, 15),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.account_tree_outlined, size: 14, color: p.gold),
              const SizedBox(width: 6),
              Expanded(child: Text(t('ISNAD — CHAIN OF TRANSMISSION', 'ISNAD — RANTAI PERIWAYATAN'), style: HText.labelSm.copyWith(color: p.gold, fontSize: 9))),
              Icon(Icons.arrow_forward_rounded, size: 14, color: p.emerald),
            ],
          ),
          const SizedBox(height: 14),
          if (rawis.isEmpty)
            Text(t('Chain not indexed for this narration yet.', 'Sanad belum terindeks untuk riwayat ini.', lang), style: HText.bodySm.copyWith(color: p.textMuted))
          else
            for (var i = 0; i < rawis.length.clamp(0, 4); i++)
              Padding(
                padding: const EdgeInsets.only(bottom: 9),
                child: Row(
                  children: [
                    Container(
                      width: 24,
                      height: 24,
                      decoration: BoxDecoration(
                        color: p.dark ? Brand.emeraldBright.withValues(alpha: 0.14) : Brand.emerald.withValues(alpha: 0.09),
                        shape: BoxShape.circle,
                        border: Border.all(color: (p.dark ? Brand.emeraldBright : Brand.emerald).withValues(alpha: 0.25)),
                      ),
                      alignment: Alignment.center,
                      child: Text('${i + 1}', style: HText.labelSm.copyWith(fontSize: 9, color: p.emerald)),
                    ),
                    const SizedBox(width: 10),
                    Expanded(
                      child: Text(rawis[i].name, style: HText.bodySm.copyWith(color: p.textPrimary, fontSize: 12.5), maxLines: 1, overflow: TextOverflow.ellipsis),
                    ),
                    if (i == rawis.length - 1)
                      Text(t('Compiler', 'Mukharrij', lang), style: HText.labelSm.copyWith(color: p.gold, fontSize: 9)),
                  ],
                ),
              ),
          if (rawis.length > 4)
            Padding(
              padding: const EdgeInsets.only(top: 2),
              child: Text('+ ${rawis.length - 4} ${t('more narrators in the full chain', 'perawi lagi di sanad lengkap', lang)}', style: HText.labelSm.copyWith(color: p.textMuted, fontSize: 10)),
            ),
          const SizedBox(height: 6),
          Container(height: 1, color: p.divider),
          const SizedBox(height: 12),
          Row(
            children: [
              Expanded(
                child: Row(
                  children: [
                    MetaLine(text: '${rawis.length} ${t('TRANSMITTERS', 'PERAWI')}', color: p.textMuted),
                    if (h.status.isNotEmpty) ...[
                      const SizedBox(width: 10),
                      MetaLine(text: h.status.toUpperCase(), color: p.emerald),
                    ],
                  ],
                ),
              ),
              Text(t('Full sanad', 'Sanad lengkap', lang), style: HText.labelSm.copyWith(color: p.emerald, fontSize: 10)),
            ],
          ),
        ],
      ),
    );
  }

  Widget _gradingsCard(BuildContext context, Hadith h, String lang) {
    final p = context.p;
    final gradings = h.gradings;
    if (gradings.isEmpty && h.grade.isEmpty) return const SizedBox.shrink();
    final shown = _showAllGradings ? gradings : gradings.take(3).toList();
    return CardSurface(
      padding: const EdgeInsets.fromLTRB(16, 15, 16, 13),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.verified_outlined, size: 14, color: p.gold),
              const SizedBox(width: 6),
              Text(t('GRADING — TAKHRIJ', 'PENILAIAN — TAKHRIJ'), style: HText.labelSm.copyWith(color: p.gold, fontSize: 9)),
            ],
          ),
          const SizedBox(height: 12),
          if (h.grade.isNotEmpty)
            Padding(
              padding: const EdgeInsets.only(bottom: 10),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Flexible(child: GradeBadge(label: h.grade, tier: h.tier)),
                  if (h.status.isNotEmpty) ...[
                    const SizedBox(width: 8),
                    Flexible(child: Text(h.status, style: HText.bodySm.copyWith(color: p.textMuted))),
                  ],
                ],
              ),
            ),
          if (shown.isEmpty)
            Text(t('No scholarly grading attached.', 'Belum ada penilaian ulama.', lang), style: HText.bodySm.copyWith(color: p.textMuted))
          else
            for (final g in shown)
              Padding(
                padding: const EdgeInsets.only(bottom: 10),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(g.sourceLabel.isNotEmpty ? g.sourceLabel : g.source, style: HText.bodySm.copyWith(color: p.textPrimary, fontWeight: FontWeight.w600, fontSize: 12.5)),
                          if (g.by.isNotEmpty)
                            Text(g.by, style: HText.labelSm.copyWith(color: p.textMuted, fontSize: 10)),
                        ],
                      ),
                    ),
                    const SizedBox(width: 10),
                    Flexible(child: GradeBadge(label: g.grade, tier: _tier(g.grade), small: true)),
                  ],
                ),
              ),
          if (gradings.length > 3)
            GestureDetector(
              onTap: () => setState(() => _showAllGradings = !_showAllGradings),
              child: Padding(
                padding: const EdgeInsets.only(top: 2),
                child: Text(
                  _showAllGradings ? t('Show less', 'Tampilkan lebih sedikit', lang) : '${t('Show all', 'Tampilkan semua', lang)} (${gradings.length})',
                  style: HText.labelSm.copyWith(color: p.emerald, fontSize: 10.5),
                ),
              ),
            ),
        ],
      ),
    );
  }

  String _tier(String grade) {
    final g = grade.toLowerCase();
    if (g.contains('sahih') || g.contains('shahih') || g.contains('صحيح')) return 'sahih';
    if (g.contains('hasan') || g.contains('حسن')) return 'hasan';
    if (g.contains('daif') || g.contains('dhaif') || g.contains('ضعيف')) return 'daif';
    return 'unknown';
  }

  Widget _actionsCard(BuildContext context, Hadith h, String lang) {
    final state = context.read<AppState>();
    final saved = state.isBookmarked(h.bookId, h.number);
    final hasSyarah = h.syarah != null;
    return Row(
      children: [
        Expanded(
          child: _actionTile(
            context,
            icon: saved ? Icons.bookmark_rounded : Icons.bookmark_border_rounded,
            label: saved ? t('Saved', 'Tersimpan', lang) : t('Save', 'Simpan', lang),
            active: saved,
            onTap: () => _saveSheet(context, h, lang),
          ),
        ),
        const SizedBox(width: 9),
        Expanded(child: _actionTile(context, icon: Icons.copy_all_outlined, label: t('Copy', 'Salin', lang), onTap: () => _copy(h, lang))),
        const SizedBox(width: 9),
        Expanded(child: _actionTile(context, icon: Icons.share_outlined, label: t('Share', 'Bagikan', lang), onTap: () => _share(h, lang))),
        const SizedBox(width: 9),
        if (hasSyarah)
          Expanded(
            child: _actionTile(
              context,
              icon: Icons.menu_book_outlined,
              label: t('Syarah', 'Syarah', lang),
              onTap: () => Navigator.of(context).push(MaterialPageRoute(builder: (_) => SyarahPage(bookId: h.bookId, number: h.number, bookTitle: _bookTitle, syarah: h.syarah))),
            ),
          ),
        const SizedBox(width: 9),
        Expanded(
          child: _actionTile(
            context,
            icon: Icons.format_quote_rounded,
            label: t('Cite', 'Kutip', lang),
            onTap: () => Navigator.of(context).push(MaterialPageRoute(builder: (_) => ExportPage(hadith: h, bookTitle: _bookTitle))),
          ),
        ),
      ],
    );
  }

  Widget _actionTile(BuildContext context, {required IconData icon, required String label, required VoidCallback onTap, bool active = false}) {
    final p = context.p;
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 12),
        decoration: BoxDecoration(
          color: active ? (p.dark ? Brand.emeraldBright.withValues(alpha: 0.14) : Brand.emerald.withValues(alpha: 0.08)) : p.card,
          borderRadius: BorderRadius.circular(13),
          border: Border.all(color: active ? (p.dark ? Brand.emeraldBright : Brand.emerald).withValues(alpha: 0.35) : p.border),
        ),
        child: Column(
          children: [
            Icon(icon, size: 18, color: active ? p.emerald : p.textSecondary),
            const SizedBox(height: 5),
            Text(label, style: HText.labelSm.copyWith(fontSize: 9.5, color: active ? p.emerald : p.textSecondary)),
          ],
        ),
      ),
    );
  }

  Widget _neighbours(BuildContext context, String lang) {
    if (_prev.isEmpty && _next.isEmpty) return const SizedBox.shrink();
    return Row(
      children: [
        Expanded(
          child: _prev.isNotEmpty
              ? SecondaryButton(label: '#$_prev', icon: Icons.arrow_back_rounded, onTap: () => _open(_prev), expand: true)
              : const SizedBox.shrink(),
        ),
        const SizedBox(width: 10),
        Expanded(
          child: _next.isNotEmpty
              ? SecondaryButton(label: '#$_next', icon: Icons.arrow_forward_rounded, onTap: () => _open(_next), expand: true)
              : const SizedBox.shrink(),
        ),
      ],
    );
  }

  Widget _bottomBar(BuildContext context, Hadith h, AppState state, String lang) {
    final p = context.p;
    return Container(
      decoration: BoxDecoration(color: p.card, border: Border(top: BorderSide(color: p.border))),
      padding: EdgeInsets.fromLTRB(16, 10, 16, 10 + MediaQuery.of(context).padding.bottom),
      child: Row(
        children: [
          GestureDetector(
            onTap: () => _saveSheet(context, h, lang),
            child: Row(
              children: [
                Icon(state.isBookmarked(h.bookId, h.number) ? Icons.bookmark_rounded : Icons.bookmark_border_rounded, size: 19, color: p.emerald),
                const SizedBox(width: 6),
                Text(t('Save', 'Simpan', lang), style: HText.labelSm.copyWith(color: p.emerald, fontSize: 11)),
              ],
            ),
          ),
          const Spacer(),
          _navChip(context, Icons.chevron_left_rounded, _prev),
          const SizedBox(width: 8),
          Text('#${h.number}', style: HText.labelSm.copyWith(color: p.textMuted, fontSize: 11)),
          const SizedBox(width: 8),
          _navChip(context, Icons.chevron_right_rounded, _next),
        ],
      ),
    );
  }

  Widget _navChip(BuildContext context, IconData icon, String number) {
    final p = context.p;
    return GestureDetector(
      onTap: number.isEmpty ? null : () => _open(number),
      child: Container(
        width: 34,
        height: 34,
        decoration: BoxDecoration(color: p.surfaceLow, borderRadius: BorderRadius.circular(10), border: Border.all(color: p.border)),
        child: Icon(icon, size: 18, color: number.isEmpty ? p.outline : p.textPrimary),
      ),
    );
  }

  void _copy(Hadith h, String lang) {
    Clipboard.setData(ClipboardData(text: _citation(h, lang)));
    showSnack(context, t('Hadith copied', 'Hadis disalin', lang));
  }

  void _share(Hadith h, String lang) {
    final text = '${_citation(h, lang)}\n\n${h.rawis.isNotEmpty ? '${t('Chain', 'Sanad', lang)}: ${h.rawis.map((r) => r.name).join(' → ')}\n' : ''}https://hadeeth.id/hadith.html?book=${h.bookId}&id=${h.number}';
    Share.share(text, subject: '${_bookTitle} #${h.number}');
  }

  Future<void> _saveSheet(BuildContext context, Hadith h, String lang) async {
    final state = context.read<AppState>();
    final p = context.p;
    if (state.isBookmarked(h.bookId, h.number)) {
      await state.removeBookmark(h.key);
      if (mounted) showSnack(context, t('Removed from saved', 'Dihapus dari simpanan', lang));
      return;
    }
    final chosen = await showModalBottomSheet<String>(
      context: context,
      backgroundColor: p.card,
      shape: const RoundedRectangleBorder(borderRadius: BorderRadius.vertical(top: Radius.circular(20))),
      builder: (ctx) => SafeArea(
        child: Padding(
          padding: const EdgeInsets.fromLTRB(20, 18, 20, 12),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(t('Save to collection', 'Simpan ke koleksi', lang), style: HText.h3.copyWith(color: p.textPrimary, fontSize: 16)),
              const SizedBox(height: 14),
              for (final c in state.collections)
                Padding(
                  padding: const EdgeInsets.only(bottom: 8),
                  child: GestureDetector(
                    onTap: () => Navigator.pop(ctx, c),
                    child: Container(
                      width: double.infinity,
                      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
                      decoration: BoxDecoration(color: p.surfaceLow, borderRadius: BorderRadius.circular(12), border: Border.all(color: p.border)),
                      child: Row(
                        children: [
                          Icon(Icons.folder_outlined, size: 16, color: p.gold),
                          const SizedBox(width: 10),
                          Text(c, style: HText.bodySm.copyWith(color: p.textPrimary)),
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
    if (chosen == null) return;
    await state.toggleBookmark(
      bookId: h.bookId,
      bookTitle: _bookTitle,
      number: h.number,
      arabic: h.textAr,
      translation: h.translation(lang),
      grade: h.grade,
      collection: chosen,
    );
    if (mounted) showSnack(context, '${t('Saved to', 'Disimpan ke', lang)} $chosen');
  }
}

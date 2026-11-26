import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:provider/provider.dart';

import '../data/hadeeth_repository.dart';
import '../models.dart';
import '../state/app_state.dart';
import '../theme.dart';
import 'widgets.dart';

class SyarahPage extends StatefulWidget {
  const SyarahPage({
    super.key,
    required this.bookId,
    required this.number,
    this.bookTitle,
    this.syarah,
  });

  final String bookId;
  final String number;
  final String? bookTitle;
  final Syarah? syarah;

  @override
  State<SyarahPage> createState() => _SyarahPageState();
}

class _SyarahPageState extends State<SyarahPage> {
  Syarah? _syarah;
  bool _loading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    if (widget.syarah != null) {
      _syarah = widget.syarah;
      _loading = false;
    } else {
      _load();
    }
  }

  Future<void> _load() async {
    final repo = context.read<HadeethRepository>();
    try {
      final s = await repo.getSyarah(widget.bookId, widget.number);
      if (!mounted) return;
      setState(() {
        _syarah = s;
        _loading = false;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _error = e.toString();
        _loading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final state = context.watch<AppState>();
    final lang = state.lang;
    final p = context.p;

    return Scaffold(
      body: SafeArea(
        bottom: false,
        child: Column(
          children: [
            PageHeader(
              title: widget.bookTitle ?? widget.bookId,
              subtitle: '${t('HADITH', 'HADIS')} #${widget.number}',
              showLogo: false,
              leading: const BackButton2(),
              actions: [
                if (_syarah != null)
                  IconPill(
                    icon: Icons.copy_all_outlined,
                    tooltip: t('Copy', 'Salin', lang),
                    onTap: () {
                      final text = _syarah!.syarahAr;
                      Clipboard.setData(ClipboardData(text: text));
                      showSnack(context, t('Copied', 'Disalin', lang));
                    },
                  ),
              ],
            ),
            Expanded(
              child: _loading
                  ? const LoadingBlock(message: 'Loading commentary…')
                  : _error != null
                      ? EmptyState(
                          icon: Icons.cloud_off_outlined,
                          title: t('Commentary not available', 'Syarah tidak tersedia', lang),
                          message: _error!,
                          action: SecondaryButton(label: t('Retry', 'Coba lagi', lang), icon: Icons.refresh_rounded, onTap: _load),
                        )
                      : _syarah == null
                          ? EmptyState(
                              icon: Icons.menu_book_outlined,
                              title: t('No commentary for this hadith', 'Tidak ada syarah untuk hadis ini', lang),
                              message: t('This narration does not have a linked commentary in the available sources.', 'Riwayat ini tidak memiliki syarah tertaut di sumber yang tersedia.', lang),
                            )
                          : ListView(
                              padding: const EdgeInsets.fromLTRB(16, 14, 16, 24),
                              children: [
                                _syarahHeader(context, _syarah!, lang),
                                const SizedBox(height: 18),
                                _syarahBody(context, _syarah!, lang),
                              ],
                            ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _syarahHeader(BuildContext context, Syarah s, String lang) {
    final p = context.p;
    return CardSurface(
      padding: const EdgeInsets.fromLTRB(16, 15, 16, 15),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.menu_book_outlined, size: 14, color: p.gold),
              const SizedBox(width: 6),
              Text(t('SYARAH — COMMENTARY', 'SYARAH — KOMENTAR'), style: HText.labelSm.copyWith(color: p.gold, fontSize: 9)),
            ],
          ),
          const SizedBox(height: 14),
          if (s.hadithAr.isNotEmpty) ...[
            Text(t('Hadith Text', 'Teks Hadis'), style: HText.labelSm.copyWith(color: p.textMuted, fontSize: 10)),
            const SizedBox(height: 4),
            ArabicBlock(text: s.hadithAr, size: 16),
            const SizedBox(height: 12),
          ],
          Row(
            children: [
              if (s.rawi.isNotEmpty) ...[
                _metaChip(context, Icons.person_outline_rounded, s.rawi, p),
                const SizedBox(width: 8),
              ],
              if (s.muhaddith.isNotEmpty) ...[
                _metaChip(context, Icons.account_balance_outlined, s.muhaddith, p),
                const SizedBox(width: 8),
              ],
              if (s.masdar.isNotEmpty) ...[
                _metaChip(context, Icons.source_outlined, s.masdar, p),
                const SizedBox(width: 8),
              ],
            ],
          ),
          if (s.grade.isNotEmpty) ...[
            const SizedBox(height: 10),
            Row(
              children: [
                GradeBadge(label: s.grade, tier: _gradeTier(s.grade)),
                if (s.takhrij.isNotEmpty) ...[
                  const SizedBox(width: 8),
                  Expanded(child: Text(s.takhrij, style: HText.bodySm.copyWith(color: p.textMuted))),
                ],
              ],
            ),
          ],
        ],
      ),
    );
  }

  Widget _metaChip(BuildContext context, IconData icon, String text, HP p) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
      decoration: BoxDecoration(
        color: p.surfaceLow,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: p.border),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 12, color: p.textMuted),
          const SizedBox(width: 4),
          Text(text, style: HText.labelSm.copyWith(fontSize: 10, color: p.textSecondary)),
        ],
      ),
    );
  }

  Widget _syarahBody(BuildContext context, Syarah s, String lang) {
    final p = context.p;
    return CardSurface(
      padding: const EdgeInsets.fromLTRB(18, 16, 18, 16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.auto_stories_outlined, size: 14, color: p.gold),
              const SizedBox(width: 6),
              Text(t('COMMENTARY', 'SYARAH'), style: HText.labelSm.copyWith(color: p.gold, fontSize: 9)),
              const Spacer(),
              if (s.source.isNotEmpty)
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                  decoration: BoxDecoration(
                    color: p.dark ? Brand.emeraldBright.withValues(alpha: 0.14) : Brand.emerald.withValues(alpha: 0.09),
                    borderRadius: BorderRadius.circular(6),
                    border: Border.all(color: (p.dark ? Brand.emeraldBright : Brand.emerald).withValues(alpha: 0.25)),
                  ),
                  child: Text(s.source, style: HText.labelSm.copyWith(fontSize: 8.5, color: p.emerald)),
                ),
            ],
          ),
          const SizedBox(height: 14),
          ArabicBlock(text: s.syarahAr, size: 17),
          const SizedBox(height: 12),
          Container(height: 1, color: p.divider),
          const SizedBox(height: 8),
          Text(
            t('Source', 'Sumber'),
            style: HText.labelSm.copyWith(color: p.textMuted, fontSize: 9),
          ),
          Text(
            'Dorar.net / ${s.masdar.isNotEmpty ? s.masdar : 'Al-Maktaba Al-Shamilah'}',
            style: HText.bodySm.copyWith(color: p.textSecondary),
          ),
        ],
      ),
    );
  }

  String _gradeTier(String grade) {
    final g = grade.toLowerCase();
    if (g.contains('sahih') || g.contains('shahih') || g.contains('صحيح')) return 'sahih';
    if (g.contains('hasan') || g.contains('حسن')) return 'hasan';
    if (g.contains('daif') || g.contains('dhaif') || g.contains('ضعيف')) return 'daif';
    return 'unknown';
  }
}
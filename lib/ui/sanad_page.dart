import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../data/hadeeth_repository.dart';
import '../models.dart';
import '../state/app_state.dart';
import '../theme.dart';
import 'scholar_page.dart';
import 'widgets.dart';

class SanadPage extends StatefulWidget {
  const SanadPage({super.key, required this.hadith, required this.bookTitle});

  final Hadith hadith;
  final String bookTitle;

  @override
  State<SanadPage> createState() => _SanadPageState();
}

class _SanadPageState extends State<SanadPage> {
  Map<String, Rawi> _details = {};
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    final repo = context.read<HadeethRepository>();
    try {
      final ids = widget.hadith.rawis.map((r) => r.id).toList();
      final map = await repo.rawisByIds(ids);
      if (!mounted) return;
      setState(() {
        _details = map;
        _loading = false;
      });
    } catch (_) {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final p = context.p;
    final lang = context.watch<AppState>().lang;
    final h = widget.hadith;
    final chain = h.rawis;

    return Scaffold(
      body: SafeArea(
        bottom: false,
        child: Column(
          children: [
            PageHeader(
              title: t('Sanad — Chain', 'Sanad — Rantai', lang),
              subtitle: '${widget.bookTitle}  •  #${h.number}',
              showLogo: false,
              leading: const BackButton2(),
            ),
            Expanded(
              child: ListView(
                padding: const EdgeInsets.fromLTRB(16, 16, 16, 32),
                children: [
                  _summary(context, h, chain.length, lang),
                  const SizedBox(height: 22),
                  SectionLabel(icon: Icons.account_tree_outlined, text: t('TRANSMISSION CHAIN', 'RANTAI PERIWAYATAN')),
                  const SizedBox(height: 4),
                  Text(
                    t('Read from the Prophet ﷺ down to the compiler.', 'Dibaca dari Nabi ﷺ hingga penyusun kitab.', lang),
                    style: HText.bodySm.copyWith(color: p.textMuted),
                  ),
                  const SizedBox(height: 16),
                  if (chain.isEmpty)
                    EmptyState(
                      icon: Icons.link_off_rounded,
                      title: t('No chain indexed', 'Sanad belum terindeks', lang),
                      message: t('This record carries the matn only; the isnad has not been mapped yet.', 'Riwayat ini hanya memuat matn; sanad belum dipetakan.', lang),
                    )
                  else
                    for (var i = 0; i < chain.length; i++) _node(context, i, chain, lang),
                  if (chain.isNotEmpty) ...[
                    const SizedBox(height: 4),
                    _matnNode(context, h, lang),
                  ],
                  if (_loading) ...[
                    const SizedBox(height: 14),
                    Row(
                      children: [
                        const SizedBox(width: 15, height: 15, child: CircularProgressIndicator(strokeWidth: 2)),
                        const SizedBox(width: 10),
                        Text(t('Loading narrator biographies…', 'Memuat biografi perawi…', lang), style: HText.labelSm.copyWith(color: p.textMuted)),
                      ],
                    ),
                  ],
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _summary(BuildContext context, Hadith h, int length, String lang) {
    final p = context.p;
    return Container(
      padding: const EdgeInsets.all(17),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: p.dark ? [const Color(0xFF0B1A17), const Color(0xFF0A1119)] : [const Color(0xFF0A2F26), const Color(0xFF001932)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(18),
        border: Border.all(color: Brand.goldLight.withValues(alpha: 0.25)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Text('ISNAD ANALYSIS', style: HText.labelSm.copyWith(color: Brand.goldLight, fontSize: 9)),
              const Spacer(),
              GradeBadge(label: h.grade.isNotEmpty ? h.grade : '—', tier: h.tier, small: true),
            ],
          ),
          const SizedBox(height: 14),
          Row(
            children: [
              _metric(context, '${widget.hadith.rawis.length}', t('Narrators', 'Perawi')),
              _divider(context),
              _metric(context, h.status.isNotEmpty ? h.status : '—', t('Status', 'Status')),
              _divider(context),
              _metric(context, h.elevation.isNotEmpty ? h.elevation : '—', t('Elevation', 'Derajat')),
            ],
          ),
          if (h.grade.isNotEmpty) ...[
            const SizedBox(height: 12),
            Text(h.grade, style: HText.bodySm.copyWith(color: Colors.white.withValues(alpha: 0.75)), maxLines: 3, overflow: TextOverflow.ellipsis),
          ],
        ],
      ),
    );
  }

  Widget _metric(BuildContext context, String value, String label) {
    return Expanded(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(value, style: HText.h3.copyWith(color: Colors.white, fontSize: 15), maxLines: 1, overflow: TextOverflow.ellipsis),
          const SizedBox(height: 2),
          Text(label.toUpperCase(), style: HText.labelSm.copyWith(color: Colors.white.withValues(alpha: 0.5), fontSize: 8)),
        ],
      ),
    );
  }

  Widget _divider(BuildContext context) {
    return Container(width: 1, height: 26, margin: const EdgeInsets.symmetric(horizontal: 12), color: Colors.white.withValues(alpha: 0.15));
  }

  Widget _node(BuildContext context, int i, List<RawiRef> chain, String lang) {
    final p = context.p;
    final ref = chain[i];
    final rawi = _details[ref.id];
    final isLast = i == chain.length - 1;
    final name = rawi != null && rawi.name(lang).isNotEmpty ? rawi.name(lang) : ref.name;

    return IntrinsicHeight(
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          SizedBox(
            width: 34,
            child: Column(
              children: [
                Container(
                  width: 30,
                  height: 30,
                  decoration: BoxDecoration(
                    color: isLast ? Brand.goldSoft : (p.dark ? Brand.emeraldBright.withValues(alpha: 0.16) : Brand.emerald.withValues(alpha: 0.10)),
                    shape: BoxShape.circle,
                    border: Border.all(color: isLast ? Brand.gold : (p.dark ? Brand.emeraldBright : Brand.emerald), width: 1.2),
                  ),
                  alignment: Alignment.center,
                  child: Text('${i + 1}', style: HText.labelSm.copyWith(fontSize: 10, color: isLast ? const Color(0xFF261900) : p.emerald)),
                ),
                if (!isLast)
                  Expanded(
                    child: Container(width: 1.4, margin: const EdgeInsets.symmetric(vertical: 3), color: p.border),
                  ),
              ],
            ),
          ),
          const SizedBox(width: 10),
          Expanded(
            child: Padding(
              padding: EdgeInsets.only(bottom: isLast ? 0 : 14),
              child: CardSurface(
                onTap: rawi == null
                    ? null
                    : () => Navigator.of(context).push(MaterialPageRoute(builder: (_) => ScholarPage(rawi: rawi, fallbackName: ref.name))),
                padding: const EdgeInsets.fromLTRB(14, 12, 14, 12),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Name and level never share a line: a long name beside a long
                    // role label squeezes the name to one glyph per line. Stack
                    // them, name reading left and the level set to the right.
                    Text(
                      name,
                      style: HText.body.copyWith(color: p.textPrimary, fontWeight: FontWeight.w600, fontSize: 13.5, height: 1.4),
                    ),
                    if (isLast || (rawi != null && rawi.level.isNotEmpty)) ...[
                      const SizedBox(height: 6),
                      Align(
                        alignment: AlignmentDirectional.centerEnd,
                        child: GradeBadge(
                          label: isLast ? t('Compiler', 'Mukharrij', lang) : rawi!.level,
                          tier: 'unknown',
                          small: true,
                        ),
                      ),
                    ],
                    if (rawi != null && rawi.nameAr.isNotEmpty) ...[
                      const SizedBox(height: 4),
                      Directionality(
                        textDirection: TextDirection.rtl,
                        child: Text(rawi.nameAr, style: HText.arabic(17).copyWith(color: p.gold), maxLines: 1, overflow: TextOverflow.ellipsis),
                      ),
                    ],
                    const SizedBox(height: 8),
                    Wrap(
                      spacing: 10,
                      runSpacing: 4,
                      children: [
                        if (rawi != null && rawi.deathAh.isNotEmpty)
                          _meta(context, Icons.event_outlined, '${t('d.', 'w.')} ${rawi.deathYear}'),
                        if (rawi != null && rawi.residence.isNotEmpty) _meta(context, Icons.place_outlined, rawi.residence),
                        if (rawi != null && rawi.counts > 0) _meta(context, Icons.numbers_rounded, '${formatNumber(rawi.counts)} ${t('riwayat', 'riwayat', lang)}'),
                      ],
                    ),
                  ],
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _meta(BuildContext context, IconData icon, String text) {
    final p = context.p;
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Icon(icon, size: 11, color: p.textMuted),
        const SizedBox(width: 3),
        Text(text, style: HText.labelSm.copyWith(color: p.textMuted, fontSize: 9.5)),
      ],
    );
  }

  Widget _matnNode(BuildContext context, Hadith h, String lang) {
    final p = context.p;
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        SizedBox(
          width: 34,
          child: Column(
            children: [
              Container(
                width: 30,
                height: 30,
                decoration: BoxDecoration(color: p.surfaceHigh, shape: BoxShape.circle, border: Border.all(color: p.border)),
                alignment: Alignment.center,
                child: Icon(Icons.format_quote_rounded, size: 14, color: p.textMuted),
              ),
            ],
          ),
        ),
        const SizedBox(width: 10),
        Expanded(
          child: Container(
            padding: const EdgeInsets.all(15),
            decoration: BoxDecoration(
              color: p.dark ? Colors.white.withValues(alpha: 0.03) : p.surfaceLow,
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: p.border),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('MATN', style: HText.labelSm.copyWith(color: p.gold, fontSize: 9)),
                const SizedBox(height: 10),
                ArabicBlock(text: h.textAr, size: 19),
                if (h.translation(lang).isNotEmpty) ...[
                  const SizedBox(height: 12),
                  Text(h.translation(lang), style: HText.bodySm.copyWith(color: p.textSecondary, height: 1.6), maxLines: 6, overflow: TextOverflow.ellipsis),
                ],
              ],
            ),
          ),
        ),
      ],
    );
  }
}

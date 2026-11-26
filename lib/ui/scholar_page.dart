import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../data/hadeeth_repository.dart';
import '../models.dart';
import '../state/app_state.dart';
import '../theme.dart';
import 'search_page.dart';
import 'widgets.dart';

class ScholarPage extends StatelessWidget {
  const ScholarPage({super.key, required this.rawi, this.fallbackName});

  final Rawi rawi;
  final String? fallbackName;

  @override
  Widget build(BuildContext context) {
    final p = context.p;
    final lang = context.watch<AppState>().lang;
    final name = rawi.name(lang).isNotEmpty ? rawi.name(lang) : (fallbackName ?? rawi.id);

    return Scaffold(
      body: SafeArea(
        bottom: false,
        child: Column(
          children: [
            PageHeader(
              title: t('Narrator', 'Perawi', lang),
              subtitle: t('RAW / TRANSMITTER PROFILE', 'PROFIL RAWI'),
              showLogo: false,
              leading: const BackButton2(),
            ),
            Expanded(
              child: ListView(
                padding: const EdgeInsets.fromLTRB(16, 18, 16, 28),
                children: [
                  Center(
                    child: Container(
                      width: 84,
                      height: 84,
                      decoration: BoxDecoration(
                        color: p.dark ? Brand.emeraldBright.withValues(alpha: 0.14) : Brand.emerald.withValues(alpha: 0.08),
                        shape: BoxShape.circle,
                        border: Border.all(color: (p.dark ? Brand.emeraldBright : Brand.emerald).withValues(alpha: 0.3)),
                      ),
                      alignment: Alignment.center,
                      child: Text(rawi.initial, style: HText.h1.copyWith(color: p.emerald)),
                    ),
                  ),
                  const SizedBox(height: 14),
                  if (rawi.nameAr.isNotEmpty)
                    Directionality(
                      textDirection: TextDirection.rtl,
                      child: Text(rawi.nameAr, textAlign: TextAlign.center, style: HText.arabic(27).copyWith(color: p.textPrimary)),
                    ),
                  const SizedBox(height: 8),
                  Text(name, textAlign: TextAlign.center, style: HText.h2.copyWith(color: p.textPrimary, fontSize: 19)),
                  if (rawi.kunyah.isNotEmpty) ...[
                    const SizedBox(height: 4),
                    Text(rawi.kunyah, textAlign: TextAlign.center, style: HText.bodySm.copyWith(color: p.textMuted)),
                  ],
                  const SizedBox(height: 18),
                  CardSurface(
                    padding: const EdgeInsets.fromLTRB(0, 16, 0, 14),
                    child: Column(
                      children: [
                        Row(
                          children: [
                            _stat(context, rawi.deathAh.isEmpty ? '—' : rawi.deathYear, t('DIED (H)', 'WAFAT (H)')),
                            _sep(context),
                            _stat(context, formatNumber(rawi.counts), t('NARRATIONS', 'RIWAYAT')),
                          ],
                        ),
                        // The level label runs long, so it gets its own line
                        // instead of a third of the strip: label left, value right.
                        if (rawi.level.isNotEmpty) ...[
                          const SizedBox(height: 13),
                          Container(height: 1, margin: const EdgeInsets.symmetric(horizontal: 16), color: p.border),
                          const SizedBox(height: 11),
                          Padding(
                            padding: const EdgeInsets.symmetric(horizontal: 16),
                            child: Row(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(t('LEVEL', 'TARAF'), style: HText.labelSm.copyWith(color: p.textMuted, fontSize: 8)),
                                const SizedBox(width: 14),
                                Expanded(
                                  child: Text(
                                    rawi.levelText,
                                    textAlign: TextAlign.right,
                                    style: HText.bodySm.copyWith(color: p.emerald, fontWeight: FontWeight.w600, fontSize: 12, height: 1.35),
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ],
                      ],
                    ),
                  ),
                  const SizedBox(height: 16),
                  CardSurface(
                    padding: const EdgeInsets.fromLTRB(16, 15, 16, 15),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        SectionLabel(icon: Icons.badge_outlined, text: t('REGISTRY RECORD', 'CATATAN REGISTRI')),
                        const SizedBox(height: 12),
                        _field(context, t('Full name', 'Nama lengkap', lang), name),
                        if (rawi.nameId.isNotEmpty && rawi.nameId != name) _field(context, t('Malay name', 'Nama Melayu', lang), rawi.nameId),
                        if (rawi.kunyah.isNotEmpty) _field(context, t('Kunyah', 'Kunyah', lang), rawi.kunyah),
                        if (rawi.residence.isNotEmpty) _field(context, t('Residence', 'Domisili', lang), rawi.residence),
                        if (rawi.deathAh.isNotEmpty) _field(context, t('Death year', 'Tahun wafat', lang), rawi.deathYear),
                        if (rawi.level.isNotEmpty) _field(context, t('Level', 'Taraf', lang), rawi.levelText),
                        _field(context, t('Registry id', 'ID registri', lang), rawi.id),
                      ],
                    ),
                  ),
                  const SizedBox(height: 16),
                  PrimaryButton(
                    label: t('Find hadith through this narrator', 'Cari hadis melalui perawi ini', lang),
                    icon: Icons.search_rounded,
                    onTap: () => Navigator.of(context).push(MaterialPageRoute(builder: (_) => SearchPage(initialQuery: name))),
                  ),
                  const SizedBox(height: 12),
                  Text(
                    t(
                      'Narrator records are drawn from the lidwa registry used by the hadeeth.id web edition. Biographical detail is limited to what the registry carries.',
                      'Catatan perawi diambil dari registri lidwa yang dipakai edisi web hadeeth.id. Detail biografi terbatas pada yang tersedia di registri.',
                      lang,
                    ),
                    style: HText.bodySm.copyWith(color: p.textMuted, height: 1.5),
                  ),
                ],
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
      child: Column(
        children: [
          Text(value, style: HText.h3.copyWith(color: p.textPrimary, fontSize: 16), textAlign: TextAlign.center, maxLines: 1, overflow: TextOverflow.ellipsis),
          const SizedBox(height: 3),
          Text(label, style: HText.labelSm.copyWith(color: p.textMuted, fontSize: 8), textAlign: TextAlign.center),
        ],
      ),
    );
  }

  Widget _sep(BuildContext context) {
    return Container(width: 1, height: 30, color: context.p.border);
  }

  Widget _field(BuildContext context, String label, String value) {
    final p = context.p;
    return Padding(
      padding: const EdgeInsets.only(bottom: 11),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(width: 104, child: Text(label, style: HText.labelSm.copyWith(color: p.textMuted, fontSize: 10))),
          Expanded(child: Text(value, style: HText.bodySm.copyWith(color: p.textPrimary))),
        ],
      ),
    );
  }
}

class ScholarsPage extends StatefulWidget {
  const ScholarsPage({super.key});

  @override
  State<ScholarsPage> createState() => _ScholarsPageState();
}

class _ScholarsPageState extends State<ScholarsPage> {
  List<Rawi> _rawis = [];
  bool _loading = true;
  double _progress = 0;
  String _query = '';
  final _controller = TextEditingController();

  @override
  void initState() {
    super.initState();
    _load();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  Future<void> _load() async {
    try {
      final list = await context.read<HadeethRepository>().rawis(onProgress: (v) {
        if (mounted) setState(() => _progress = v);
      });
      if (!mounted) return;
      setState(() {
        _rawis = list;
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
    final q = _query.toLowerCase();
    final filtered = q.isEmpty
        ? _rawis.take(60).toList()
        : _rawis
            .where((r) => r.nameEn.toLowerCase().contains(q) || r.nameId.toLowerCase().contains(q) || r.nameAr.contains(_query))
            .take(120)
            .toList();

    return Scaffold(
      body: SafeArea(
        bottom: false,
        child: Column(
          children: [
            PageHeader(
              title: t('Narrators', 'Perawi', lang),
              subtitle: '${formatNumber(_rawis.length)} ${t('REGISTERED TRANSMITTERS', 'PERAWI TERDAFTAR')}',
              showLogo: false,
              leading: const BackButton2(),
            ),
            Padding(
              padding: const EdgeInsets.fromLTRB(16, 12, 16, 8),
              child: TextField(
                controller: _controller,
                onChanged: (v) => setState(() => _query = v),
                style: HText.bodySm.copyWith(color: p.textPrimary),
                decoration: InputDecoration(
                  isDense: true,
                  hintText: t('Search narrator by name…', 'Cari perawi berdasarkan nama…', lang),
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
            ),
            Expanded(
              child: _loading
                  ? Center(
                      child: Column(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          SizedBox(width: 150, child: LinearProgressIndicator(value: _progress == 0 ? null : _progress, minHeight: 4, color: p.emerald, backgroundColor: p.surfaceHigh)),
                          const SizedBox(height: 12),
                          Text(t('Loading narrator registry…', 'Memuat registri perawi…', lang), style: HText.bodySm.copyWith(color: p.textMuted)),
                        ],
                      ),
                    )
                  : filtered.isEmpty
                      ? EmptyState(icon: Icons.person_search_outlined, title: t('No narrator found', 'Perawi tidak ditemukan', lang), message: t('Try a shorter name fragment.', 'Coba potongan nama yang lebih pendek.', lang))
                      : ListView.builder(
                          padding: const EdgeInsets.fromLTRB(16, 6, 16, 24),
                          itemCount: filtered.length,
                          itemBuilder: (context, i) {
                            final r = filtered[i];
                            return Padding(
                              padding: const EdgeInsets.only(bottom: 9),
                              child: CardSurface(
                                onTap: () => Navigator.of(context).push(MaterialPageRoute(builder: (_) => ScholarPage(rawi: r))),
                                padding: const EdgeInsets.symmetric(horizontal: 13, vertical: 11),
                                child: Row(
                                  children: [
                                    Container(
                                      width: 36,
                                      height: 36,
                                      decoration: BoxDecoration(color: p.surfaceLow, shape: BoxShape.circle, border: Border.all(color: p.border)),
                                      alignment: Alignment.center,
                                      child: Text(r.initial, style: HText.label.copyWith(color: p.emerald, fontSize: 11)),
                                    ),
                                    const SizedBox(width: 11),
                                    Expanded(
                                      child: Column(
                                        crossAxisAlignment: CrossAxisAlignment.start,
                                        children: [
                                          Text(r.name(lang), style: HText.bodySm.copyWith(color: p.textPrimary, fontWeight: FontWeight.w600), maxLines: 1, overflow: TextOverflow.ellipsis),
                                          const SizedBox(height: 2),
                                          Text(
                                            [
                                              if (r.deathAh.isNotEmpty) '${t('d.', 'w.')} ${r.deathYear}',
                                              if (r.residence.isNotEmpty) r.residence,
                                              if (r.counts > 0) '${formatNumber(r.counts)} ${t('riwayat', 'riwayat', lang)}',
                                            ].join('  •  '),
                                            style: HText.labelSm.copyWith(color: p.textMuted, fontSize: 9.5),
                                            maxLines: 1,
                                            overflow: TextOverflow.ellipsis,
                                          ),
                                        ],
                                      ),
                                    ),
                                    Icon(Icons.chevron_right_rounded, size: 18, color: p.outline),
                                  ],
                                ),
                              ),
                            );
                          },
                        ),
            ),
          ],
        ),
      ),
    );
  }
}

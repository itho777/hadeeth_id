import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../data/hadeeth_repository.dart';
import '../models.dart';
import '../state/app_state.dart';
import '../theme.dart';
import 'scholar_page.dart';
import 'topic_detail_page.dart';
import 'widgets.dart';

class TopicsPage extends StatefulWidget {
  const TopicsPage({super.key});

  @override
  State<TopicsPage> createState() => _TopicsPageState();
}

class _TopicsPageState extends State<TopicsPage> {
  late final Future<List<Topic>> _topics;
  final _controller = TextEditingController();
  String _query = '';

  @override
  void initState() {
    super.initState();
    _topics = context.read<HadeethRepository>().topics();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final p = context.p;
    final lang = context.watch<AppState>().lang;
    return Scaffold(
      body: SafeArea(
        bottom: false,
        child: Column(
          children: [
            PageHeader(
              title: t('Topics & Concepts', 'Tema & Konsep', lang),
              subtitle: t('THEMATIC INDEX ACROSS ALL COLLECTIONS', 'INDEKS TEMATIK LINTAS KOLEKSI'),
              actions: [
                IconPill(
                  icon: Icons.groups_outlined,
                  tooltip: t('Narrators', 'Perawi', lang),
                  onTap: () => Navigator.of(context).push(MaterialPageRoute(builder: (_) => const ScholarsPage())),
                ),
              ],
            ),
            Padding(
              padding: const EdgeInsets.fromLTRB(16, 12, 16, 6),
              child: TextField(
                controller: _controller,
                onChanged: (v) => setState(() => _query = v.toLowerCase()),
                style: HText.bodySm.copyWith(color: p.textPrimary),
                decoration: InputDecoration(
                  isDense: true,
                  hintText: t('Filter topics…', 'Saring tema…', lang),
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
              child: FutureBuilder<List<Topic>>(
                future: _topics,
                builder: (context, snap) {
                  if (!snap.hasData) return const LoadingBlock(message: 'Loading topics…');
                  final all = snap.data!;
                  final list = _query.isEmpty ? all : all.where((t0) => t0.name('en').toLowerCase().contains(_query) || t0.name('id').toLowerCase().contains(_query)).toList();
                  if (list.isEmpty) {
                    return EmptyState(icon: Icons.search_off_rounded, title: t('No topic found', 'Tema tidak ditemukan', lang), message: t('Try another keyword.', 'Coba kata kunci lain.', lang));
                  }
                  return ListView(
                    padding: const EdgeInsets.fromLTRB(16, 10, 16, 26),
                    children: [
                      for (var i = 0; i < list.length; i += 2)
                        Padding(
                          padding: const EdgeInsets.only(bottom: 10),
                          child: Row(
                            children: [
                              Expanded(child: _card(context, list[i], lang)),
                              const SizedBox(width: 10),
                              Expanded(child: i + 1 < list.length ? _card(context, list[i + 1], lang) : const SizedBox.shrink()),
                            ],
                          ),
                        ),
                      const SizedBox(height: 10),
                      CardSurface(
                        onTap: () => Navigator.of(context).push(MaterialPageRoute(builder: (_) => const ScholarsPage())),
                        child: Row(
                          children: [
                            Icon(Icons.groups_outlined, size: 20, color: p.gold),
                            const SizedBox(width: 12),
                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(t('Narrator registry', 'Registri perawi', lang), style: HText.h3.copyWith(color: p.textPrimary, fontSize: 14)),
                                  const SizedBox(height: 2),
                                  Text(t('Search 14,000+ transmitters', 'Telusuri 14.000+ perawi', lang), style: HText.labelSm.copyWith(color: p.textMuted, fontSize: 10)),
                                ],
                              ),
                            ),
                            Icon(Icons.chevron_right_rounded, size: 18, color: p.outline),
                          ],
                        ),
                      ),
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

  Widget _card(BuildContext context, Topic topic, String lang) {
    final p = context.p;
    return CardSurface(
      onTap: () => Navigator.of(context).push(MaterialPageRoute(builder: (_) => TopicDetailPage(topic: topic))),
      padding: const EdgeInsets.all(14),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                width: 34,
                height: 34,
                decoration: BoxDecoration(color: p.dark ? Brand.emeraldBright.withValues(alpha: 0.14) : Brand.emerald.withValues(alpha: 0.09), borderRadius: BorderRadius.circular(10)),
                child: Icon(topic.icon, size: 18, color: p.emerald),
              ),
              const Spacer(),
              Text('${topic.id}'.padLeft(2, '0'), style: HText.labelSm.copyWith(color: p.textMuted, fontSize: 9)),
            ],
          ),
          const SizedBox(height: 12),
          Text(topic.name(lang), style: HText.h3.copyWith(fontSize: 13.5, color: p.textPrimary), maxLines: 2, overflow: TextOverflow.ellipsis),
          const SizedBox(height: 3),
          Directionality(
            textDirection: TextDirection.rtl,
            child: Text(topic.nameAr, style: HText.arabic(15).copyWith(color: p.gold), maxLines: 1, overflow: TextOverflow.ellipsis),
          ),
          const SizedBox(height: 12),
          Text('${formatNumber(topic.count)} ${t('hadiths', 'hadis', lang)}', style: HText.labelSm.copyWith(color: p.emerald, fontSize: 10)),
        ],
      ),
    );
  }
}

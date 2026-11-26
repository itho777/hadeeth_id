import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:provider/provider.dart';

import '../data/hadeeth_repository.dart';
import '../data/prepared_answers.dart';
import '../models.dart';
import '../state/app_state.dart';
import '../state/nav_controller.dart';
import '../theme.dart';
import 'widgets.dart';
import 'chapters_page.dart';
import 'hadith_detail_page.dart';
import 'search_page.dart';
import 'scholar_page.dart';
import 'settings_page.dart';
import 'topic_detail_page.dart';

class HomePage extends StatefulWidget {
  const HomePage({super.key});

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  late final Future<List<Book>> _books;
  late final Future<Hadith?> _hotd;
  late final Future<List<Topic>> _topics;

  @override
  void initState() {
    super.initState();
    final repo = context.read<HadeethRepository>();
    _books = repo.books();
    _hotd = repo.hadithOfTheDay();
    _topics = repo.topics();
  }

  void _openChat(String prompt) => context.read<NavController>().go(3, prompt: prompt);

  @override
  Widget build(BuildContext context) {
    final p = context.p;
    final state = context.watch<AppState>();
    final lang = state.lang;
    final dates = todayDates(lang);

    return Scaffold(
      body: SafeArea(
        bottom: false,
        child: SingleChildScrollView(
          padding: const EdgeInsets.fromLTRB(16, 14, 16, 28),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              _buildHeader(context, state, lang),
              const SizedBox(height: 20),
              Text(t('Assalamu\'alaikum', 'Assalamu\'alaikum', lang), style: HText.h1.copyWith(color: p.textPrimary)),
              const SizedBox(height: 4),
              Row(
                children: [
                  Icon(Icons.calendar_today_outlined, size: 12, color: p.textMuted),
                  const SizedBox(width: 6),
                  Expanded(
                    child: Text(
                      '${dates.hijri}  •  ${dates.gregorian}',
                      style: HText.bodySm.copyWith(color: p.textMuted, height: 1.35),
                      maxLines: 2,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 16),

              // Search entry point, same tiers as the web search box.
              GestureDetector(
                onTap: () => Navigator.of(context).push(MaterialPageRoute(builder: (_) => const SearchPage())),
                child: Container(
                  padding: const EdgeInsets.symmetric(horizontal: 15, vertical: 14),
                  decoration: BoxDecoration(
                    color: p.card,
                    borderRadius: BorderRadius.circular(16),
                    border: Border.all(color: p.border),
                    boxShadow: [BoxShadow(color: Colors.black.withValues(alpha: p.dark ? 0.2 : 0.03), blurRadius: 14, offset: const Offset(0, 5))],
                  ),
                  child: Row(
                    children: [
                      Icon(Icons.search_rounded, size: 21, color: p.gold),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Text(
                          t('Search hadith by meaning, narrator, or number…', 'Cari hadis berdasarkan makna, perawi, atau nomor…', lang),
                          style: HText.bodySm.copyWith(color: p.textMuted),
                        ),
                      ),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 7, vertical: 3),
                        decoration: BoxDecoration(color: p.surfaceLow, borderRadius: BorderRadius.circular(7)),
                        child: Text('AI', style: HText.labelSm.copyWith(color: p.emerald)),
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 12),
              SingleChildScrollView(
                scrollDirection: Axis.horizontal,
                child: Row(
                  children: [
                    ChipButton(
                      label: t('All collections', 'Semua koleksi', lang),
                      selected: true,
                      onTap: () => Navigator.of(context).push(MaterialPageRoute(builder: (_) => const SearchPage(initialQuery: ''))),
                    ),
                    const SizedBox(width: 8),
                    ChipButton(
                      label: t('Sahih only', 'Hanya sahih', lang),
                      selected: false,
                      onTap: () => Navigator.of(context).push(MaterialPageRoute(builder: (_) => const SearchPage(onlySahih: true))),
                    ),
                    const SizedBox(width: 8),
                    ChipButton(
                      label: t('By topic', 'Berdasarkan tema', lang),
                      selected: false,
                      onTap: () => context.read<NavController>().go(2),
                    ),
                    const SizedBox(width: 8),
                    ChipButton(
                      label: t('Narrators', 'Perawi', lang),
                      selected: false,
                      onTap: () => Navigator.of(context).push(MaterialPageRoute(builder: (_) => const ScholarsPage())),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 26),

              const SectionLabel(icon: Icons.auto_stories_outlined, text: 'HADITH OF THE DAY / HADIS HARI INI'),
              const SizedBox(height: 10),
              FutureBuilder<Hadith?>(
                future: _hotd,
                builder: (context, snap) {
                  if (!snap.hasData) return const CardSurface(child: LoadingBlock(message: 'Loading hadith of the day…'));
                  final h = snap.data;
                  if (h == null) return CardSurface(child: Text(t('Hadith unavailable.', 'Hadis belum dapat dimuat.', lang), style: HText.bodySm));
                  return _hotdCard(context, h, lang, state);
                },
              ),
              const SizedBox(height: 26),

              if (state.lastRead.isNotEmpty) ...[
                const SectionLabel(icon: Icons.bookmark_border, text: 'CONTINUE READING / LANJUTKAN BACA'),
                const SizedBox(height: 10),
                _continueCard(context, state, lang),
                const SizedBox(height: 26),
              ],

              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Expanded(
                    child: SectionLabel(
                      icon: Icons.menu_book_outlined,
                      text: t('KUTUBUT TIS\'AH', 'KUTUBUT TIS\'AH'),
                    ),
                  ),
                  GestureDetector(
                    onTap: () => context.read<NavController>().go(1),
                    child: Text(t('View all →', 'Lihat semua →', lang), style: HText.labelSm.copyWith(color: p.emerald, fontSize: 11)),
                  ),
                ],
              ),
              const SizedBox(height: 4),
              Text(
                t('The nine canonical compilations', 'Sembilan kitab hadis utama', lang),
                style: HText.bodySm.copyWith(color: p.textMuted),
              ),
              const SizedBox(height: 12),
              FutureBuilder<List<Book>>(
                future: _books,
                builder: (context, snap) {
                  if (!snap.hasData) {
                    return const CardSurface(child: LoadingBlock(message: 'Loading collections…'));
                  }
                  final core = snap.data!.where((b) => b.isCore).toList();
                  return Column(
                    children: [
                      for (var i = 0; i < core.length; i += 2)
                        Padding(
                          padding: const EdgeInsets.only(bottom: 10),
                          child: Row(
                            children: [
                              Expanded(child: _coreBookCard(context, core[i], i + 1, lang)),
                              const SizedBox(width: 10),
                              Expanded(
                                child: i + 1 < core.length
                                    ? _coreBookCard(context, core[i + 1], i + 2, lang)
                                    : const SizedBox.shrink(),
                              ),
                            ],
                          ),
                        ),
                    ],
                  );
                },
              ),
              const SizedBox(height: 18),

              _askAiCard(context, lang),
              const SizedBox(height: 26),

              const SectionLabel(icon: Icons.explore_outlined, text: 'TOPICS & CONCEPTS / TEMA'),
              const SizedBox(height: 10),
              FutureBuilder<List<Topic>>(
                future: _topics,
                builder: (context, snap) {
                  if (!snap.hasData) return const CardSurface(child: LoadingBlock(message: 'Loading topics…'));
                  final topics = snap.data!.take(4).toList();
                  return Column(
                    children: [
                      for (var i = 0; i < topics.length; i += 2)
                        Padding(
                          padding: const EdgeInsets.only(bottom: 10),
                          child: Row(
                            children: [
                              Expanded(child: _topicCard(context, topics[i], lang)),
                              const SizedBox(width: 10),
                              Expanded(
                                child: i + 1 < topics.length ? _topicCard(context, topics[i + 1], lang) : const SizedBox.shrink(),
                              ),
                            ],
                          ),
                        ),
                    ],
                  );
                },
              ),
              const SizedBox(height: 12),
              SecondaryButton(
                label: t('Browse all topics', 'Jelajahi semua tema', lang),
                icon: Icons.arrow_forward_rounded,
                expand: true,
                onTap: () => context.read<NavController>().go(2),
              ),
              const SizedBox(height: 26),

              FutureBuilder<List<Book>>(
                future: _books,
                builder: (context, snap) {
                  final count = snap.data?.fold<int>(0, (sum, b) => sum + b.totalHadiths) ?? 0;
                  if (count == 0) return const SizedBox.shrink();
                  return CardSurface(
                    padding: const EdgeInsets.all(18),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        SectionLabel(icon: Icons.account_balance_outlined, text: t('THE ARCHIVE', 'ARSIP')),
                        const SizedBox(height: 10),
                        Text(
                          '${formatNumber(count)} ${t('authenticated narrations', 'riwayat hadis terverifikasi', lang)}',
                          style: HText.h2.copyWith(color: p.textPrimary),
                        ),
                        const SizedBox(height: 8),
                        Text(
                          t('Read with full isnad, scholarly grading and cross-references — directly from the hadeeth.id source files.', 'Baca dengan sanad lengkap, penilaian ulama, dan takhrij lintas kitab — langsung dari sumber data hadeeth.id.', lang),
                          style: HText.bodySm.copyWith(color: p.textMuted),
                        ),
                      ],
                    ),
                  );
                },
              ),
              const SizedBox(height: 24),
              Text(
                '© 2026 hadeeth.id — Digital Hadith Manuscript Preservation',
                style: HText.bodySm.copyWith(color: p.textMuted, fontSize: 10.5),
                textAlign: TextAlign.center,
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildHeader(BuildContext context, AppState state, String lang) {
    final p = context.p;
    return Row(
      children: [
        const BrandLogo(height: 38),
        const SizedBox(width: 10),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              RichText(
                text: TextSpan(
                  children: [
                    TextSpan(text: 'hadeeth', style: HText.h3.copyWith(color: p.textPrimary)),
                    TextSpan(text: '.id', style: HText.h3.copyWith(color: p.gold)),
                  ],
                ),
              ),
              Text(t('DIGITAL HADITH ARCHIVE', 'ARSIP HADIS DIGITAL', lang), style: HText.labelSm.copyWith(color: p.textMuted, fontSize: 8.5)),
            ],
          ),
        ),
        LangToggle(lang: lang, onChanged: (v) => state.setLang(v)),
        const SizedBox(width: 6),
        IconPill(
          icon: context.isDark ? Icons.light_mode_outlined : Icons.dark_mode_outlined,
          tooltip: t('Toggle theme', 'Ubah tema', lang),
          onTap: () => state.toggleTheme(context.isDark),
        ),
        const SizedBox(width: 6),
        IconPill(
          icon: Icons.settings_outlined,
          tooltip: t('Settings', 'Pengaturan', lang),
          onTap: () => Navigator.of(context).push(MaterialPageRoute(builder: (_) => const SettingsPage())),
        ),
      ],
    );
  }

  Widget _hotdCard(BuildContext context, Hadith h, String lang, AppState state) {
    final p = context.p;
    final translation = state.translationMode == 'en' && h.textEn.isNotEmpty ? h.textEn : h.translation('id');
    return CardSurface(
      padding: const EdgeInsets.fromLTRB(17, 16, 17, 15),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Row(
            children: [
              Container(width: 3, height: 17, decoration: BoxDecoration(color: p.gold, borderRadius: BorderRadius.circular(3))),
              const SizedBox(width: 9),
              Expanded(child: Text('HADITH OF THE DAY', style: HText.label.copyWith(color: p.gold))),
              GradeBadge(label: h.grade.isNotEmpty ? h.grade : 'Hadith', tier: h.tier, small: true),
            ],
          ),
          const SizedBox(height: 16),
          ArabicBlock(text: h.textAr, size: state.arabicSize - 3),
          const SizedBox(height: 14),
          Divider(color: p.divider, height: 1),
          const SizedBox(height: 12),
          Text(translation, style: HText.body.copyWith(color: p.textSecondary), maxLines: 5, overflow: TextOverflow.ellipsis),
          const SizedBox(height: 14),
          Row(
            children: [
              Expanded(
                child: Text(
                  '${_bookName(h.bookId)} • #${h.number}',
                  style: HText.labelSm.copyWith(color: p.textMuted),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
              ),
              IconButton(
                tooltip: t('Copy', 'Salin', lang),
                icon: Icon(Icons.copy_all_outlined, size: 17, color: p.textMuted),
                onPressed: () {
                  Clipboard.setData(ClipboardData(text: '${h.textAr}\n\n$translation\n\n${_bookName(h.bookId)} #${h.number}'));
                  showSnack(context, t('Hadith copied', 'Hadis disalin', lang));
                },
              ),
            ],
          ),
          const SizedBox(height: 2),
          GestureDetector(
            onTap: () => Navigator.of(context).push(MaterialPageRoute(builder: (_) => HadithDetailPage(bookId: h.bookId, number: h.number))),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Text(t('Read full context & sanad', 'Baca konteks & sanad lengkap', lang), style: HText.labelSm.copyWith(color: p.emerald, fontSize: 11)),
                const SizedBox(width: 4),
                Icon(Icons.arrow_forward_rounded, size: 14, color: p.emerald),
              ],
            ),
          ),
        ],
      ),
    );
  }

  String _bookName(String id) {
    switch (id) {
      case 'bukhari': return 'Sahih al-Bukhari';
      case 'muslim': return 'Sahih Muslim';
      default: return id;
    }
  }

  Widget _continueCard(BuildContext context, AppState state, String lang) {
    final p = context.p;
    final lr = state.lastRead.values.reduce((a, b) => a.at.isAfter(b.at) ? a : b);
    return CardSurface(
      onTap: () => Navigator.of(context).push(MaterialPageRoute(builder: (_) => HadithDetailPage(bookId: lr.bookId, number: lr.number))),
      child: Column(
        children: [
          Row(
            children: [
              Container(
                width: 38,
                height: 38,
                decoration: BoxDecoration(color: p.dark ? Brand.emeraldBright.withValues(alpha: 0.16) : Brand.emerald.withValues(alpha: 0.10), borderRadius: BorderRadius.circular(11)),
                child: Icon(Icons.menu_book_outlined, color: p.emerald, size: 19),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(lr.bookTitle, style: HText.h3.copyWith(color: p.textPrimary, fontSize: 15)),
                    const SizedBox(height: 3),
                    Text('${lr.chapter} • ${t('Hadith', 'Hadis', lang)} #${lr.number}', style: HText.bodySm.copyWith(color: p.textMuted)),
                  ],
                ),
              ),
              Icon(Icons.arrow_forward_ios_rounded, size: 15, color: p.emerald),
            ],
          ),
          const SizedBox(height: 15),
          ClipRRect(
            borderRadius: BorderRadius.circular(4),
            child: LinearProgressIndicator(
              value: 0.35,
              minHeight: 4,
              backgroundColor: p.surfaceHigh,
              color: p.dark ? Brand.emeraldBright : Brand.emerald,
            ),
          ),
          const SizedBox(height: 8),
          Row(
            children: [
              Text(formatWhen(lr.at, lang), style: HText.labelSm.copyWith(color: p.textMuted)),
              const Spacer(),
              Text(t('Resume', 'Lanjutkan', lang), style: HText.labelSm.copyWith(color: p.emerald)),
            ],
          ),
        ],
      ),
    );
  }

  Widget _coreBookCard(BuildContext context, Book book, int rank, String lang) {
    final p = context.p;
    return CardSurface(
      onTap: () => Navigator.of(context).push(MaterialPageRoute(builder: (_) => ChaptersPage(book: book))),
      padding: const EdgeInsets.fromLTRB(13, 14, 13, 12),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                width: 25,
                height: 25,
                decoration: BoxDecoration(
                  color: p.dark ? Brand.emeraldBright.withValues(alpha: 0.15) : Brand.emerald.withValues(alpha: 0.10),
                  borderRadius: BorderRadius.circular(7),
                ),
                alignment: Alignment.center,
                child: Text(rank.toString().padLeft(2, '0'), style: HText.labelSm.copyWith(fontSize: 9, color: p.emerald)),
              ),
              const Spacer(),
              GradeBadge(label: t('Sahih', 'Sahih', lang), tier: 'sahih', small: true),
            ],
          ),
          const SizedBox(height: 14),
          Text(book.title(lang), style: HText.h3.copyWith(fontSize: 14.5, color: p.textPrimary), maxLines: 2, overflow: TextOverflow.ellipsis),
          const SizedBox(height: 5),
          Text(book.author(lang), style: HText.bodySm.copyWith(color: p.textMuted, fontSize: 11), maxLines: 1, overflow: TextOverflow.ellipsis),
          const SizedBox(height: 12),
          Row(
            children: [
              Text('${formatNumber(book.totalHadiths)} ${t('hadiths', 'hadis', lang)}', style: HText.labelSm.copyWith(color: p.textSecondary, fontSize: 10)),
              const Spacer(),
              Icon(Icons.arrow_forward_rounded, size: 15, color: p.emerald),
            ],
          ),
        ],
      ),
    );
  }

  Widget _askAiCard(BuildContext context, String lang) {
    final p = context.p;
    // Home samples must be questions with a prepared answer too, or the user
    // taps a card and waits 20 s for Razi to say it lacks context.
    final samples = homeSamples(lang, wibDayNumber());
    return Container(
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: p.dark
              ? [const Color(0xFF0B3529), const Color(0xFF06231B)]
              : [const Color(0xFF083326), const Color(0xFF0F4C3A)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(18),
        border: Border.all(color: Brand.emeraldBright.withValues(alpha: 0.35)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              ClipRRect(
                borderRadius: BorderRadius.circular(999),
                child: Image.asset('assets/images/razi-avatar.jpg', width: 40, height: 40, fit: BoxFit.cover),
              ),
              const SizedBox(width: 10),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(t('AI ASSISTANT', 'ASISTEN AI', lang), style: HText.labelSm.copyWith(color: Brand.goldLight)),
                    const SizedBox(height: 3),
                    Text(t('Ask Razi', 'Tanya Razi', lang), style: HText.h3.copyWith(color: Colors.white)),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Text(
            t(
              'Razi has read every chain in this archive. Ask about a narration, a narrator, or how two isnād compare — each answer names its book and number.',
              'Razi sudah membaca seluruh sanad di arsip ini. Tanyakan riwayat, perawi, atau perbandingan dua sanad — tiap jawaban menyebut kitab dan nomornya.',
              lang,
            ),
            style: HText.bodySm.copyWith(color: Colors.white.withValues(alpha: 0.82)),
          ),
          const SizedBox(height: 14),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: [
              for (final s in samples)
                GestureDetector(
                  onTap: () => _openChat(s),
                  child: Container(
                    padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                    decoration: BoxDecoration(color: Colors.white.withValues(alpha: 0.10), borderRadius: BorderRadius.circular(999), border: Border.all(color: Colors.white.withValues(alpha: 0.18))),
                    child: Text(s, style: HText.bodySm.copyWith(color: Colors.white, fontSize: 11)),
                  ),
                ),
            ],
          ),
          const SizedBox(height: 16),
          GestureDetector(
            onTap: () => _openChat(''),
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
              decoration: BoxDecoration(color: Brand.goldSoft, borderRadius: BorderRadius.circular(12)),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text(t('Start chat', 'Mulai chat', lang), style: HText.label.copyWith(color: const Color(0xFF261900))),
                  const SizedBox(width: 6),
                  const Icon(Icons.arrow_forward_rounded, size: 14, color: Color(0xFF261900)),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _topicCard(BuildContext context, Topic topic, String lang) {
    final p = context.p;
    return CardSurface(
      onTap: () => Navigator.of(context).push(MaterialPageRoute(builder: (_) => TopicDetailPage(topic: topic))),
      padding: const EdgeInsets.all(14),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            width: 34,
            height: 34,
            decoration: BoxDecoration(color: p.dark ? Brand.emeraldBright.withValues(alpha: 0.15) : Brand.emerald.withValues(alpha: 0.09), borderRadius: BorderRadius.circular(10)),
            child: Icon(topic.icon, size: 18, color: p.emerald),
          ),
          const SizedBox(height: 12),
          Text(topic.name(lang), style: HText.h3.copyWith(fontSize: 14, color: p.textPrimary), maxLines: 2, overflow: TextOverflow.ellipsis),
          const SizedBox(height: 2),
          Directionality(
            textDirection: TextDirection.rtl,
            child: Text(topic.nameAr, style: HText.arabic(14).copyWith(color: p.gold), maxLines: 1, overflow: TextOverflow.ellipsis),
          ),
          const SizedBox(height: 12),
          Text('${formatNumber(topic.count)} ${t('hadiths', 'hadis', lang)}', style: HText.labelSm.copyWith(color: p.textMuted, fontSize: 10)),
        ],
      ),
    );
  }
}

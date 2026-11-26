import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_markdown/flutter_markdown.dart';
import 'package:provider/provider.dart';
import 'package:url_launcher/url_launcher.dart';

import '../data/razi_service.dart';
import '../data/prepared_answers.dart';
import '../models.dart';
import '../state/app_state.dart';
import '../state/nav_controller.dart';
import '../theme.dart';
import 'hadith_detail_page.dart';
import 'widgets.dart';

class ChatPage extends StatefulWidget {
  /// The prepared answers are normally read from the bundled asset. Tests can
  /// pass the same map in directly, since `rootBundle` has no assets in a
  /// widget test.
  const ChatPage({super.key, this.preparedAnswers});

  final Map<String, String>? preparedAnswers;

  @override
  State<ChatPage> createState() => _ChatPageState();
}

class _ChatPageState extends State<ChatPage> {
  final List<ChatMessage> _messages = [];
  final TextEditingController _input = TextEditingController();
  final ScrollController _scroll = ScrollController();
  final FocusNode _focus = FocusNode();
  bool _sending = false;
  String? _pendingPrompt;
  int _seedOffset = 0;

  /// Verified answers to the ten starter questions, shipped as an asset. A tap
  /// on those cards replies from this map instead of waiting out a model call —
  /// they are questions we chose, so the answers are ones we already have.
  Map<String, String> _seeds = const {};

  @override
  void initState() {
    super.initState();
    if (widget.preparedAnswers != null) {
      _seeds = widget.preparedAnswers!;
    } else {
      _loadSeeds();
    }
  }

  Future<void> _loadSeeds() async {
    try {
      final raw = await rootBundle.loadString('assets/data/razi_seeds.json');
      final map = parsePreparedAnswers(raw);
      if (mounted && map.isNotEmpty) setState(() => _seeds = map);
    } catch (_) {
      // Optional asset: without it every prompt simply goes to Razi.
    }
  }

  /// Consume a prompt handed over by another tab. Deferred to after the frame:
  /// clearing it inside didChangeDependencies called notifyListeners() while the
  /// shell was mid-build, which is what left the AI tab stuck taking taps.
  void _takePrompt(String prompt) {
    if (!mounted) return;
    context.read<NavController>().takePrompt();
    setState(() => _pendingPrompt = null);
    if (prompt.trim().isNotEmpty) {
      _askSeed(prompt, context.read<AppState>().lang);
    }
  }

  /// A starter question with a prepared answer appears instantly.
  void _askSeed(String question, String lang) {
    final cached = _seeds['$lang|$question'];
    if (cached != null) {
      _showPrepared(question, cached);
      return;
    }
    if (_seeds.isEmpty) {
      // First launch: the asset may still be loading. Retry once before
      // spending a 20 s Razi call on a question we already have an answer for.
      _loadSeeds().then((_) {
        if (!mounted) return;
        final retry = _seeds['$lang|$question'];
        if (retry != null) {
          _showPrepared(question, retry);
        } else {
          _send(question);
        }
      });
      return;
    }
    _send(question);
  }

  void _showPrepared(String question, String reply) {
    setState(() {
      _messages.add(ChatMessage(role: 'user', text: question, at: DateTime.now()));
      _messages.add(ChatMessage(role: 'assistant', text: reply, at: DateTime.now()));
    });
    _scrollToEnd();
  }

  @override
  void dispose() {
    _input.dispose();
    _scroll.dispose();
    _focus.dispose();
    super.dispose();
  }

  Future<void> _send([String? preset]) async {
    final text = (preset ?? _input.text).trim();
    if (text.isEmpty || _sending) return;
    final lang = context.read<AppState>().lang;
    setState(() {
      _messages.add(ChatMessage(role: 'user', text: text, at: DateTime.now()));
      _sending = true;
    });
    _input.clear();
    _scrollToEnd();
    try {
      final reply = await context.read<RaziService>().ask(text, lang: lang);
      if (!mounted) return;
      setState(() {
        _messages.add(ChatMessage(role: 'assistant', text: reply, at: DateTime.now()));
        _sending = false;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _messages.add(ChatMessage(
          role: 'assistant',
          text: lang == 'id'
              ? 'Maaf, Razi tidak dapat dihubungi sekarang. Periksa koneksi lalu coba lagi.'
              : 'Razi could not be reached right now. Check your connection and try again.',
          at: DateTime.now(),
        ));
        _sending = false;
      });
    }
    _scrollToEnd();
  }

  void _scrollToEnd() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (!_scroll.hasClients) return;
      _scroll.animateTo(_scroll.position.maxScrollExtent + 120, duration: const Duration(milliseconds: 260), curve: Curves.easeOut);
    });
  }

  void _newChat() {
    context.read<RaziService>().reset();
    setState(() => _messages.clear());
  }

  @override
  Widget build(BuildContext context) {
    final lang = context.watch<AppState>().lang;
    final pending = context.watch<NavController>().chatPrompt;
    if (pending != null && pending != _pendingPrompt) {
      _pendingPrompt = pending;
      WidgetsBinding.instance.addPostFrameCallback((_) {
        if (mounted) _takePrompt(pending);
      });
    }
    return Scaffold(
      body: SafeArea(
        bottom: false,
        child: Column(
          children: [
            _header(context, lang),
            Expanded(
              child: _messages.isEmpty
                  ? _intro(context, lang)
                  : ListView.builder(
                      controller: _scroll,
                      padding: const EdgeInsets.fromLTRB(16, 14, 16, 16),
                      itemCount: _messages.length + (_sending ? 1 : 0),
                      itemBuilder: (context, i) {
                        if (i >= _messages.length) return _typing(context, lang);
                        return _bubble(context, _messages[i], lang);
                      },
                    ),
            ),
            _composer(context, lang),
          ],
        ),
      ),
    );
  }

  Widget _header(BuildContext context, String lang) {
    final p = context.p;
    return Container(
      padding: const EdgeInsets.fromLTRB(16, 12, 16, 14),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: p.dark ? [const Color(0xFF0B3529), const Color(0xFF0A1220)] : [const Color(0xFF083326), const Color(0xFF001932)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        border: Border(bottom: BorderSide(color: Brand.goldLight.withValues(alpha: 0.2))),
      ),
      child: Row(
        children: [
          GestureDetector(
            onTap: () {
              final nav = context.read<NavController>();
              if (!nav.back()) nav.go(0, remember: false);
            },
            child: Container(
              width: 34,
              height: 34,
              margin: const EdgeInsets.only(right: 11),
              decoration: BoxDecoration(color: Colors.white.withValues(alpha: 0.10), borderRadius: BorderRadius.circular(10), border: Border.all(color: Colors.white.withValues(alpha: 0.16))),
              child: const Icon(Icons.close_rounded, size: 19, color: Colors.white),
            ),
          ),
          ClipRRect(
            borderRadius: BorderRadius.circular(999),
            child: Image.asset('assets/images/razi-avatar.jpg', width: 42, height: 42, fit: BoxFit.cover),
          ),
          const SizedBox(width: 11),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('Razi', style: HText.h3.copyWith(color: Colors.white, fontSize: 16)),
                const SizedBox(height: 2),
                Row(
                  children: [
                    Container(width: 6, height: 6, decoration: const BoxDecoration(color: Brand.emeraldBright, shape: BoxShape.circle)),
                    const SizedBox(width: 5),
                    Expanded(
                      child: Text(
                        t(
                          'AI hadith assistant',
                          'Asisten hadis AI',
                          lang,
                        ),
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                        style: HText.labelSm.copyWith(color: Colors.white.withValues(alpha: 0.65), fontSize: 9.5),
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
          const SizedBox(width: 8),
          GestureDetector(
            onTap: _newChat,
            child: Container(
              width: 34,
              height: 34,
              decoration: BoxDecoration(color: Colors.white.withValues(alpha: 0.10), borderRadius: BorderRadius.circular(10), border: Border.all(color: Colors.white.withValues(alpha: 0.16))),
              child: const Icon(Icons.add_comment_outlined, size: 16, color: Colors.white),
            ),
          ),
        ],
      ),
    );
  }

  Widget _intro(BuildContext context, String lang) {
    final p = context.p;
    final prompts = preparedWindow(lang, wibDayNumber(), _seedOffset);
    return ListView(
      padding: const EdgeInsets.fromLTRB(18, 22, 18, 20),
      children: [
        Text(t("Assalamu'alaikum — I'm Razi", "Assalamu'alaikum — saya Razi", lang), style: HText.h1.copyWith(color: p.textPrimary, fontSize: 24)),
        const SizedBox(height: 8),
        Text(
          t(
            'I read the same collections you do — 28 kutub with isnād, grading and narrator biographies. Each answer names its book and number so you can check it.',
            'Saya membaca koleksi yang sama — 28 kitab dengan sanad, derajat, dan biografi perawi. Tiap jawaban menyebut kitab dan nomornya supaya bisa Anda periksa.',
            lang,
          ),
          style: HText.bodySm.copyWith(color: p.textMuted, height: 1.55),
        ),
        const SizedBox(height: 18),
        Row(
          children: [
            Text(
              t('PREPARED ANSWERS', 'JAWABAN SIAP', lang),
              style: HText.labelSm.copyWith(color: p.gold, fontSize: 9.5),
            ),
            const SizedBox(width: 8),
            Expanded(child: Divider(color: p.divider, height: 1)),
          ],
        ),
        const SizedBox(height: 12),
        for (final s in prompts)
          Padding(
            padding: const EdgeInsets.only(bottom: 9),
            child: CardSurface(
              onTap: () => _askSeed(s, lang),
              padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 13),
              child: Row(
                children: [
                  Icon(Icons.chat_bubble_outline_rounded, size: 15, color: p.gold),
                  const SizedBox(width: 10),
                  Expanded(child: Text(s, style: HText.bodySm.copyWith(color: p.textPrimary))),
                  Icon(Icons.arrow_forward_rounded, size: 14, color: p.emerald),
                ],
              ),
            ),
          ),
        const SizedBox(height: 2),
        Center(
          child: TextButton.icon(
            onPressed: () => setState(() => _seedOffset += 4),
            icon: Icon(Icons.refresh_rounded, size: 14, color: p.emerald),
            label: Text(t('More questions', 'Pertanyaan lain', lang),
                style: HText.labelSm.copyWith(color: p.emerald, fontSize: 11)),
          ),
        ),
        const SizedBox(height: 6),
        Row(
          children: [
            Icon(Icons.info_outline_rounded, size: 13, color: p.textMuted),
            const SizedBox(width: 6),
            Expanded(
              child: Text(
                t('Prepared answers cite the collection shown. Verify wording against the source.', 'Jawaban siap menyebut koleksi yang dirujuk. Periksa redaksi terhadap sumbernya.', lang),
                style: HText.labelSm.copyWith(color: p.textMuted, fontSize: 9.5, height: 1.4),
              ),
            ),
          ],
        ),
      ],
    );
  }

  Widget _bubble(BuildContext context, ChatMessage m, String lang) {
    final p = context.p;
    final isUser = m.role == 'user';
    if (isUser) {
      return Align(
        alignment: Alignment.centerRight,
        child: Container(
          margin: const EdgeInsets.only(bottom: 12, left: 40),
          padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 11),
          decoration: BoxDecoration(
            color: p.dark ? Brand.emeraldBright : Brand.ink,
            borderRadius: const BorderRadius.only(topLeft: Radius.circular(16), topRight: Radius.circular(16), bottomLeft: Radius.circular(16), bottomRight: Radius.circular(4)),
          ),
          child: Text(m.text, style: HText.bodySm.copyWith(color: p.dark ? Brand.darkCanvas : Colors.white, height: 1.5)),
        ),
      );
    }
    return Padding(
      padding: const EdgeInsets.only(bottom: 14, right: 18),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          ClipRRect(
            borderRadius: BorderRadius.circular(999),
            child: Image.asset('assets/images/razi-avatar.jpg', width: 28, height: 28, fit: BoxFit.cover),
          ),
          const SizedBox(width: 9),
          Expanded(
            child: Container(
              padding: const EdgeInsets.fromLTRB(14, 12, 14, 12),
              decoration: BoxDecoration(
                color: p.card,
                borderRadius: const BorderRadius.only(topLeft: Radius.circular(4), topRight: Radius.circular(16), bottomLeft: Radius.circular(16), bottomRight: Radius.circular(16)),
                border: Border.all(color: p.border),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  MarkdownBody(
                    data: m.text,
                    selectable: true,
                    onTapLink: (text, href, title) => _openLink(href),
                    styleSheet: MarkdownStyleSheet(
                      p: HText.bodySm.copyWith(color: p.textSecondary, height: 1.6),
                      h1: HText.h3.copyWith(color: p.textPrimary),
                      h2: HText.h3.copyWith(color: p.textPrimary, fontSize: 15),
                      h3: HText.h3.copyWith(color: p.textPrimary, fontSize: 14),
                      listBullet: HText.bodySm.copyWith(color: p.textSecondary, height: 1.6),
                      strong: HText.bodySm.copyWith(color: p.textPrimary, fontWeight: FontWeight.w700),
                      em: HText.bodySm.copyWith(color: p.textSecondary, fontStyle: FontStyle.italic),
                      blockquote: HText.bodySm.copyWith(color: p.textMuted, fontStyle: FontStyle.italic),
                      blockquoteDecoration: BoxDecoration(border: Border(left: BorderSide(color: p.gold, width: 2.5))),
                      blockquotePadding: const EdgeInsets.only(left: 10),
                      code: HText.bodySm.copyWith(color: p.emerald, fontFamily: 'monospace'),
                      a: HText.bodySm.copyWith(color: p.emerald, decoration: TextDecoration.underline),
                    ),
                  ),
                  const SizedBox(height: 6),
                  Row(
                    children: [
                      GestureDetector(
                        onTap: () {
                          Clipboard.setData(ClipboardData(text: m.text));
                          showSnack(context, t('Copied', 'Disalin', lang));
                        },
                        child: Icon(Icons.copy_all_outlined, size: 14, color: p.textMuted),
                      ),
                      const Spacer(),
                      Text('RAZI', style: HText.labelSm.copyWith(color: p.textMuted, fontSize: 8)),
                    ],
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _typing(BuildContext context, String lang) {
    final p = context.p;
    return Padding(
      padding: const EdgeInsets.only(bottom: 14, left: 2),
      child: Row(
        children: [
          ClipRRect(
            borderRadius: BorderRadius.circular(999),
            child: Image.asset('assets/images/razi-avatar.jpg', width: 28, height: 28, fit: BoxFit.cover),
          ),
          const SizedBox(width: 9),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
            decoration: BoxDecoration(color: p.card, borderRadius: BorderRadius.circular(14), border: Border.all(color: p.border)),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                SizedBox(width: 13, height: 13, child: CircularProgressIndicator(strokeWidth: 1.8, color: p.emerald)),
                const SizedBox(width: 9),
                Text(t('Razi is checking the collections…', 'Razi memeriksa koleksi…', lang), style: HText.labelSm.copyWith(color: p.textMuted, fontSize: 10)),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _composer(BuildContext context, String lang) {
    final p = context.p;
    return Container(
      padding: EdgeInsets.fromLTRB(12, 9, 12, 9 + MediaQuery.of(context).padding.bottom),
      decoration: BoxDecoration(color: p.card, border: Border(top: BorderSide(color: p.border))),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.end,
        children: [
          Expanded(
            child: TextField(
              controller: _input,
              focusNode: _focus,
              minLines: 1,
              maxLines: 4,
              textCapitalization: TextCapitalization.sentences,
              onSubmitted: (_) => _send(),
              style: HText.bodySm.copyWith(color: p.textPrimary),
              decoration: InputDecoration(
                isDense: true,
                hintText: t('Ask about a hadith, narrator or chain…', 'Tanyakan hadis, perawi, atau sanad…', lang),
                hintStyle: HText.bodySm.copyWith(color: p.textMuted, fontSize: 12),
                filled: true,
                fillColor: p.surfaceLow,
                contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(22), borderSide: BorderSide(color: p.border)),
                enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(22), borderSide: BorderSide(color: p.border)),
                focusedBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(22), borderSide: BorderSide(color: p.emerald)),
              ),
            ),
          ),
          const SizedBox(width: 8),
          GestureDetector(
            onTap: _sending ? null : () => _send(),
            child: Container(
              width: 42,
              height: 42,
              decoration: BoxDecoration(
                color: _sending ? p.surfaceHigh : (p.dark ? Brand.emeraldBright : Brand.ink),
                shape: BoxShape.circle,
              ),
              child: Icon(Icons.arrow_upward_rounded, size: 19, color: _sending ? p.textMuted : (p.dark ? Brand.darkCanvas : Colors.white)),
            ),
          ),
        ],
      ),
    );
  }

  Future<void> _openLink(String? href) async {
    if (href == null) return;
    final uri = Uri.tryParse(href);
    if (uri == null) return;
    final book = uri.queryParameters['book'];
    final id = uri.queryParameters['id'] ?? uri.queryParameters['number'];
    if (uri.path.contains('hadith') && book != null && id != null) {
      if (!mounted) return;
      Navigator.of(context).push(MaterialPageRoute(builder: (_) => HadithDetailPage(bookId: book, number: id)));
      return;
    }
    final absolute = uri.hasScheme ? uri : Uri.parse('https://hadeeth.id/${href.replaceFirst(RegExp(r'^/+'), '')}');
    await launchUrl(absolute, mode: LaunchMode.externalApplication);
  }
}

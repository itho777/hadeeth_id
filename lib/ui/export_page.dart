import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:provider/provider.dart';
import 'package:share_plus/share_plus.dart';

import '../models.dart';
import '../state/app_state.dart';
import '../theme.dart';
import 'widgets.dart';

class ExportPage extends StatefulWidget {
  const ExportPage({super.key, this.hadith, this.bookTitle, this.bookmarks});

  final Hadith? hadith;
  final String? bookTitle;
  final List<Bookmark>? bookmarks;

  @override
  State<ExportPage> createState() => _ExportPageState();
}

class _ExportPageState extends State<ExportPage> {
  String _style = 'chicago';

  static const _styles = {
    'chicago': 'Chicago',
    'apa': 'APA 7',
    'mla': 'MLA 9',
    'bibtex': 'BibTeX',
  };

  List<({String title, String number, String bookId, String grade, String translation})> get _entries {
    final h = widget.hadith;
    if (h != null) {
      return [(
        title: widget.bookTitle ?? h.bookId,
        number: h.number,
        bookId: h.bookId,
        grade: h.grade,
        translation: widget.bookTitle == null ? h.translation('id') : h.translation('en'),
      )];
    }
    return (widget.bookmarks ?? const [])
        .map((b) => (title: b.bookTitle, number: b.number, bookId: b.bookId, grade: b.grade, translation: b.translation))
        .toList();
  }

  String _cite(String style, ({String title, String number, String bookId, String grade, String translation}) e) {
    final url = 'https://hadeeth.id/hadith.html?book=${e.bookId}&id=${e.number}';
    final title = e.title;
    final number = e.number;
    switch (style) {
      case 'apa':
        return '$title. (n.d.). Hadith $number [${e.grade.isEmpty ? 'Hadith' : e.grade}]. hadeeth.id. $url';
      case 'mla':
        return '"$title, Hadith $number." hadeeth.id, $url. Accessed ${_accessed()}.';
      case 'bibtex':
        return '@misc{hadeeth_${e.bookId}_$number,\n  title  = {$title, Hadith $number},\n  note   = {${e.grade}},\n  url    = {$url},\n  year   = {2026}\n}';
      default:
        return '$title, Hadith $number (${e.grade.isEmpty ? 'hadeeth.id' : e.grade}), accessed ${_accessed()}, $url.';
    }
  }

  String _accessed() {
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    final now = DateTime.now();
    return '${now.day} ${months[now.month - 1]} ${now.year}';
  }

  String get _output {
    final entries = _entries;
    if (_style == 'bibtex') return entries.map((e) => _cite('bibtex', e)).join('\n\n');
    return entries.asMap().entries.map((it) {
      final cite = _cite(_style, it.value);
      return _style == 'chicago' && entries.length > 1 ? '${it.key + 1}. $cite' : cite;
    }).join('\n\n');
  }

  @override
  Widget build(BuildContext context) {
    final p = context.p;
    final lang = context.watch<AppState>().lang;
    final entries = _entries;

    return Scaffold(
      body: SafeArea(
        bottom: false,
        child: Column(
          children: [
            PageHeader(
              title: t('Export citations', 'Ekspor kutipan', lang),
              subtitle: '${entries.length} ${t('RECORD(S)', 'REKAMAN')}',
              showLogo: false,
              leading: const BackButton2(),
            ),
            Expanded(
              child: ListView(
                padding: const EdgeInsets.fromLTRB(16, 16, 16, 24),
                children: [
                  SectionLabel(icon: Icons.style_outlined, text: t('CITATION STYLE', 'GAYA KUTIPAN')),
                  const SizedBox(height: 10),
                  Wrap(
                    spacing: 8,
                    children: [
                      for (final entry in _styles.entries)
                        ChipButton(label: entry.value, selected: _style == entry.key, onTap: () => setState(() => _style = entry.key)),
                    ],
                  ),
                  const SizedBox(height: 20),
                  SectionLabel(icon: Icons.article_outlined, text: t('PREVIEW', 'PRATINJAU')),
                  const SizedBox(height: 10),
                  Container(
                    width: double.infinity,
                    padding: const EdgeInsets.all(15),
                    decoration: BoxDecoration(
                      color: p.dark ? Colors.black.withValues(alpha: 0.35) : p.surfaceLow,
                      borderRadius: BorderRadius.circular(14),
                      border: Border.all(color: p.border),
                    ),
                    child: SelectableText(
                      _output,
                      style: HText.bodySm.copyWith(
                        color: p.textPrimary,
                        fontFamily: 'monospace',
                        fontSize: 11.5,
                        height: 1.6,
                      ),
                    ),
                  ),
                  const SizedBox(height: 18),
                  PrimaryButton(
                    label: t('Copy citation', 'Salin kutipan', lang),
                    icon: Icons.copy_all_outlined,
                    onTap: () {
                      Clipboard.setData(ClipboardData(text: _output));
                      showSnack(context, t('Citation copied', 'Kutipan disalin', lang));
                    },
                  ),
                  const SizedBox(height: 10),
                  SecondaryButton(
                    label: t('Share citation', 'Bagikan kutipan', lang),
                    icon: Icons.ios_share_rounded,
                    expand: true,
                    onTap: () => Share.share(_output, subject: t('Hadith citation', 'Kutipan hadis', lang)),
                  ),
                  const SizedBox(height: 20),
                  Text(
                    t(
                      'Citations follow the reference format used by hadeeth.id. Verify publisher-specific conventions with your institution before submission.',
                      'Kutipan mengikuti format rujukan hadeeth.id. Verifikasi konvensi institusi Anda sebelum pengumpulan.',
                      lang,
                    ),
                    style: HText.labelSm.copyWith(color: p.textMuted, fontSize: 10, height: 1.5),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

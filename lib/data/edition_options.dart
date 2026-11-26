import '../models.dart';

String normaliseEditionText(String s) =>
    s.replaceAll(RegExp(r'\s+'), ' ').trim().toLowerCase();

/// One alternative edition offered by the selector on the hadith page.
class EditionOption {
  EditionOption({required this.lang, required this.source, required this.text});

  final String lang;
  final String source;
  final String text;

  String get key => '$lang|$source|${text.length}:${text.hashCode}';

  /// Languages the page has no tab for sort first, so a Malay or Urdu edition
  /// surfaces above a second Indonesian source.
  int get rank => const {'id': 1, 'en': 2}[lang] ?? 0;

  String get label {
    const names = {
      'id': 'Indonesia',
      'en': 'English',
      'ar': 'Arabic',
      'ms': 'Melayu',
      'ur': 'Urdu',
      'tr': 'Türkçe',
      'fr': 'Français',
    };
    final language = names[lang] ?? lang.toUpperCase();
    return source.isEmpty ? language : '$language · ${source.toUpperCase()}';
  }
}

/// Editions that add something the page does not already show. Arabic is
/// skipped because the matn sits at the top of the card, and any text equal to
/// the ID/EN tab body is skipped because it would be a second copy of the same
/// words under a different label.
List<EditionOption> editionOptions(Hadith h) {
  final shown = <String>{normaliseEditionText(h.textId), normaliseEditionText(h.textEn)}..remove('');
  final seen = <String>{};
  final out = <EditionOption>[];
  h.otherTexts.forEach((langKey, list) {
    final lang = langKey.toLowerCase();
    if (lang == 'ar') return;
    for (final ed in list) {
      final text = (ed['text'] ?? '').trim();
      if (text.isEmpty) continue;
      final normalised = normaliseEditionText(text);
      if (shown.contains(normalised) || !seen.add('$lang|$normalised')) continue;
      out.add(EditionOption(lang: lang, source: (ed['source'] ?? '').trim(), text: text));
    }
  });
  out.sort((a, b) {
    final byRank = a.rank.compareTo(b.rank);
    if (byRank != 0) return byRank;
    final byLang = a.lang.compareTo(b.lang);
    return byLang != 0 ? byLang : a.source.compareTo(b.source);
  });
  return out;
}

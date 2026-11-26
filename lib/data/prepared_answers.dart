import 'dart:convert';

/// The ten starter questions shipped with verified answers in
/// `assets/data/razi_seeds.json`. Both languages carry the same ten topics.
const List<String> preparedQuestionsEn = [
  'What does the hadith about intentions say?',
  'Can you walk me through the isnad of the hadith about intentions?',
  'Which hadith warns about riba?',
  'What are the major sins according to hadith?',
  'What hadith says about truthfulness?',
  'Which hadith stresses honouring parents?',
  'What is the reward for praying in congregation?',
  'What hadith teaches good treatment of neighbours?',
  'When does Ramadan fasting start and end according to hadith?',
  'What hadith explains lawful, unlawful and doubtful matters?',
];

const List<String> preparedQuestionsId = [
  'Apa isi hadis tentang niat?',
  'Bagaimana sanad hadis tentang niat?',
  'Hadis apa yang memperingatkan tentang riba?',
  'Apa saja dosa besar menurut hadis?',
  'Apa hadis tentang kejujuran?',
  'Hadis apa tentang berbakti kepada orang tua?',
  'Apa pahala salat berjamaah?',
  'Apa hadis tentang bertetangga dengan baik?',
  'Kapan puasa Ramadan dimulai dan diakhiri menurut hadis?',
  'Apa hadis tentang halal, haram, dan syubhat?',
];

List<String> preparedQuestions(String lang) =>
    lang == 'id' ? preparedQuestionsId : preparedQuestionsEn;

/// WIB calendar day. Shared with Hadith of the Day so both rotations turn at
/// the same midnight rather than at UTC.
int wibDayNumber([DateTime? now]) {
  final wib = (now ?? DateTime.now()).toUtc().add(const Duration(hours: 7));
  return DateTime.utc(wib.year, wib.month, wib.day).millisecondsSinceEpoch ~/
      86400000;
}

/// Four of the ten questions, window starting at `day * 4 + offset`. The day
/// changes the set; "more questions" advances the offset so all ten are
/// reachable without waiting for tomorrow.
List<String> preparedWindow(String lang, int day, int offset, {int size = 4}) {
  final all = preparedQuestions(lang);
  final start = ((day * size) + offset) % all.length;
  return List.generate(size, (i) => all[(start + i) % all.length]);
}

/// Two questions for the home AI card. Offset 8 keeps them different from the
/// first cards on the chat screen while staying inside the ten prepared ones.
List<String> homeSamples(String lang, int day) =>
    preparedWindow(lang, day, 8).take(2).toList();

Map<String, String> parsePreparedAnswers(String raw) {
  final data = jsonDecode(raw) as Map<String, dynamic>;
  final map = <String, String>{};
  for (final value in data.values) {
    if (value is! Map) continue;
    final lang = '${value['lang'] ?? ''}';
    final question = '${value['question'] ?? ''}';
    final reply = '${value['reply'] ?? ''}';
    if (question.isNotEmpty && reply.isNotEmpty) map['$lang|$question'] = reply;
  }
  return map;
}

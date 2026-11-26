import 'dart:convert';

import 'package:flutter/material.dart';

/// Letters that carry no identity in an Arabic-derived name, so a monogram made
/// from the last word of "Sahih al-Bukhari" is a B and not an A.
const _nameNoise = {'al', 'el', 'as', 'ash', 'ad', 'ibn', 'bin', 'binti', 'bint', 'abu', 'abd', 'imam', 'the', 'of'};

/// The lidwa registry packs the Arabic spelling of a name into the same field
/// as its transliteration — 40% of `rawis.ndjson` rows look like
/// `"al-Muttalib bin 'Abdullah … المطلب بن عبد الله …"`. Rendered in the Latin
/// face those tail characters come out as tofu boxes, so the two scripts are
/// split once, at parse time, and each is drawn in its own font.
final RegExp _arabicRun = RegExp(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]');

/// Latin part of a mixed registry string, whitespace collapsed.
String latinOf(String s) => s
    .replaceAll(_arabicRun, ' ')
    .replaceAll(RegExp(r'\s+'), ' ')
    .trim()
    // A transliteration that lost its Arabic often trails a lone "(" or "'".
    .replaceAll(RegExp(r'[\s(\[]+$'), '')
    .trim();

/// Arabic part of a mixed registry string, Arabic characters only.
String arabicOf(String s) {
  final buffer = StringBuffer();
  var inRun = false;
  for (final rune in s.runes) {
    final char = String.fromCharCode(rune);
    final isArabic = _arabicRun.hasMatch(char) || (inRun && char == ' ');
    if (isArabic) {
      buffer.write(char);
      inRun = true;
    } else {
      inRun = false;
    }
  }
  return buffer.toString().replaceAll(RegExp(r'\s+'), ' ').trim();
}

String nameMonogram(String name, String fallbackId) {
  final parts = name.trim().split(RegExp(r'[\s\-–—]+')).where((s) => s.isNotEmpty).toList();
  for (final part in parts.reversed) {
    // Latin only: an Arabic token has no glyph in the display face and would
    // draw a box in the avatar instead of a letter.
    final token = part.replaceAll(RegExp(r'[^A-Za-z]'), '');
    if (token.length < 2) continue;
    if (_nameNoise.contains(token.toLowerCase())) continue;
    return token.substring(0, 1).toUpperCase();
  }
  final id = fallbackId.trim();
  return id.isEmpty ? '?' : id.substring(0, 1).toUpperCase();
}

int _asInt(dynamic v, [int fallback = 0]) {
  if (v == null) return fallback;
  if (v is int) return v;
  if (v is num) return v.toInt();
  return int.tryParse(v.toString()) ?? fallback;
}

String _asString(dynamic v, [String fallback = '']) {
  if (v == null) return fallback;
  return v.toString();
}

/// The registry's ten classifications, keyed by `book_type_ar`. These are the
/// only categories the app offers anywhere — the Kutub filter, the admin
/// console's book list and the download screen all read this same map.
const Map<String, String> bookClassLatin = {
  'الصحيح': 'Sahih',
  'السنن': 'Sunan',
  'الجامع': "Jami'",
  'المسند': 'Musnad',
  'الموطأ': 'Muwatta',
  'المستدرك': 'Mustadrak',
  'المعجم': "Mu'jam",
  'أحكام': 'Ahkam',
  'جوامع الكلم': "Jawami' al-Kalim",
  'متنوع': 'Mutanawwi',
};

/// Filter order: the two Sahih collections, then the Sunan family, then the
/// rest, matching how the registry orders its own catalogue.
const List<String> bookClassOrder = [
  'الصحيح',
  'الجامع',
  'السنن',
  'المسند',
  'الموطأ',
  'المستدرك',
  'المعجم',
  'أحكام',
  'جوامع الكلم',
  'متنوع',
];

class Book {
  Book({
    required this.id,
    required this.titleAr,
    required this.titleEn,
    required this.titleId,
    required this.authorAr,
    required this.authorEn,
    required this.authorId,
    required this.deathYearAh,
    required this.totalHadiths,
    required this.totalChapters,
    required this.gradeSummary,
    required this.orderIndex,
    required this.bookTypeAr,
    required this.editions,
  });

  final String id;
  final String titleAr;
  final String titleEn;
  final String titleId;
  final String authorAr;
  final String authorEn;
  final String authorId;
  final int deathYearAh;
  final int totalHadiths;
  final int totalChapters;
  final String gradeSummary;
  final int orderIndex;
  final String bookTypeAr;
  final List<String> editions;

  String title(String lang) => lang == 'ar' ? titleAr : (lang == 'id' ? titleId : titleEn);
  String author(String lang) => lang == 'ar' ? authorAr : (lang == 'id' ? authorId : authorEn);

  bool get isCore => const {
        'bukhari', 'muslim', 'abudawud', 'tirmidhi', 'nasai',
        'ibnmajah', 'malik', 'darimi', 'ahmad',
      }.contains(id);

  bool get isSunan => bookClass == 'السنن';

  /// The registry's own classification. Bukhari and Muslim carry `الجامع`,
  /// not `الصحيح` — classification and authenticity are different axes, so this
  /// is deliberately not derived from `gradeSummary`.
  String get bookClass => bookTypeAr.isEmpty ? 'متنوع' : bookTypeAr;

  String classLabel(String lang) =>
      lang == 'ar' ? bookClass : (bookClassLatin[bookClass] ?? bookClass);

  /// Authenticity, not classification. The Hadith of the Day pool uses this.
  bool get isSahih => gradeSummary.contains('صحيح') && !gradeSummary.contains('Varies');

  String get monogram => nameMonogram(titleEn, id);

  factory Book.fromJson(Map<String, dynamic> j) => Book(
        id: _asString(j['id']),
        titleAr: _asString(j['title_ar']),
        titleEn: _asString(j['title_en'], _asString(j['id'])),
        titleId: _asString(j['title_id'], _asString(j['title_en'])),
        authorAr: _asString(j['author_ar']),
        authorEn: _asString(j['author_en']),
        authorId: _asString(j['author_id'], _asString(j['author_en'])),
        deathYearAh: _asInt(j['death_year_ah']),
        totalHadiths: _asInt(j['total_hadiths'], _asInt(j['hadiths_count'])),
        totalChapters: _asInt(j['total_chapters']),
        gradeSummary: _asString(j['grade_summary']),
        orderIndex: _asInt(j['order_index']),
        bookTypeAr: _asString(j['book_type_ar']),
        editions: (j['editions'] as List?)?.map((e) => e.toString()).toList() ?? const [],
      );
}

class Chapter {
  Chapter({
    required this.bookId,
    required this.id,
    required this.number,
    required this.titleId,
    required this.titleEn,
    required this.titleAr,
    required this.hadithStart,
    required this.hadithEnd,
    required this.hadithCount,
  });

  final String bookId;
  final String id;
  final int number;
  final String titleId;
  final String titleEn;
  final String titleAr;
  final int hadithStart;
  final int hadithEnd;
  final int hadithCount;

  String title(String lang) => lang == 'ar' ? titleAr : (lang == 'id' ? titleId : titleEn);

  factory Chapter.fromJson(Map<String, dynamic> j) => Chapter(
        bookId: _asString(j['book_id']),
        id: _asString(j['id']),
        number: _asInt(j['chapter_number']),
        titleId: _asString(j['title_id']),
        titleEn: _asString(j['title_en'], _asString(j['title_id'])),
        titleAr: _asString(j['title_ar']),
        hadithStart: _asInt(j['hadith_start']),
        hadithEnd: _asInt(j['hadith_end']),
        hadithCount: _asInt(j['hadith_count']),
      );
}

class RawiRef {
  RawiRef({required this.name, required this.id, this.rank = 0, this.tags = const []});

  final String name;
  final String id;
  final int rank;
  final List<String> tags;

  factory RawiRef.fromJson(Map<String, dynamic> j) {
    final raw = _asString(j['name'] ?? j['name_en']);
    final latin = latinOf(raw);
    return RawiRef(
      // Chain names are mixed-script in the registry; the Latin face can only
      // draw the transliteration.
      name: latin.isNotEmpty ? latin : raw,
      id: _asString(j['id']),
      rank: _asInt(j['rank']),
      tags: (j['tags'] as List?)?.map((e) => e.toString()).toList() ?? const [],
    );
  }
}

class Grading {
  Grading({required this.source, required this.sourceLabel, required this.by, required this.grade});

  final String source;
  final String sourceLabel;
  final String by;
  final String grade;

  factory Grading.fromJson(Map<String, dynamic> j) => Grading(
        source: _asString(j['src']),
        sourceLabel: _asString(j['src_label'], _asString(j['src'])),
        by: _asString(j['by']),
        grade: _asString(j['grade']),
      );
}

class Hadith {
  Hadith({
    required this.id,
    required this.bookId,
    required this.number,
    required this.lidwaIds,
    required this.textAr,
    required this.textId,
    required this.textEn,
    required this.rawis,
    required this.grade,
    required this.gradeId,
    required this.status,
    required this.elevation,
    required this.gradings,
    required this.chapterId,
    required this.otherTexts,
  });

  final String id;
  final String bookId;
  final String number;
  final List<String> lidwaIds;
  final String textAr;
  final String textId;
  final String textEn;
  final List<RawiRef> rawis;
  final String grade;
  final String gradeId;
  final String status;
  final String elevation;
  final List<Grading> gradings;
  final String chapterId;
  final Map<String, List<Map<String, String>>> otherTexts;

  String get key => '$bookId:$number';

  String translation(String lang) {
    if (lang == 'id') return textId.isNotEmpty ? textId : textEn;
    return textEn.isNotEmpty ? textEn : textId;
  }

  bool get hasArabic => textAr.trim().isNotEmpty;

  String get translationEnOrId => textEn.isNotEmpty ? textEn : textId;

  /// Grade tier used for the badge colour.
  String get tier {
    final g = '${grade.isNotEmpty ? grade : ''} ${gradeId.isNotEmpty ? gradeId : ''}'.toLowerCase();
    if (g.contains('shahih') || g.contains('sahih') || g.contains('صحيح')) return 'sahih';
    if (g.contains('hasan') || g.contains('حسن')) return 'hasan';
    if (g.contains('dhaif') || g.contains('daif') || g.contains('ضعيف')) return 'daif';
    return 'unknown';
  }

  factory Hadith.fromJson(Map<String, dynamic> j, {String? bookIdFallback}) {
    final other = <String, List<Map<String, String>>>{};
    final tr = j['translations'];
    if (tr is Map) {
      tr.forEach((lang, list) {
        if (list is List) {
          other[lang.toString()] = list
              .whereType<Map>()
              .map((e) => {
                    'source': _asString(e['source']),
                    'text': _asString(e['text']),
                  })
              .where((e) => (e['text'] ?? '').isNotEmpty)
              .toList();
        }
      });
    }
    final lidwa = j['lidwa_id'];
    final lidwaIds = lidwa is List ? lidwa.map((e) => e.toString()).toList() : (lidwa == null || lidwa.toString().isEmpty ? <String>[] : [lidwa.toString()]);
    return Hadith(
      id: _asString(j['id']),
      bookId: _asString(j['book'], bookIdFallback ?? ''),
      number: _asString(j['hadith_number'], _asString(j['id'])),
      lidwaIds: lidwaIds,
      textAr: _asString(j['text_ar'], _asString(j['text_ar_plain'])),
      textId: _asString(j['text_id']),
      textEn: _asString(j['text_en']),
      rawis: (j['rawis'] as List?)?.whereType<Map>().map((e) => RawiRef.fromJson(e.cast<String, dynamic>())).toList() ?? const [],
      grade: _asString(j['grade']),
      gradeId: _asString(j['grade_id'], _asString(j['grade'])),
      status: _asString(j['status']),
      elevation: _asString(j['elevation']),
      gradings: (j['gradings'] as List?)?.whereType<Map>().map((e) => Grading.fromJson(e.cast<String, dynamic>())).toList() ?? const [],
      chapterId: _asString(j['chapter_id']),
      otherTexts: other,
    );
  }

  Map<String, dynamic> toJson() => {
        'id': id,
        'book': bookId,
        'hadith_number': number,
        'lidwa_id': lidwaIds,
        'text_ar': textAr,
        'text_id': textId,
        'text_en': textEn,
        'rawis': rawis.map((r) => {'name': r.name, 'id': r.id}).toList(),
        'grade': grade,
        'grade_id': gradeId,
        'status': status,
        'elevation': elevation,
        'gradings': gradings.map((g) => {'src': g.source, 'src_label': g.sourceLabel, 'by': g.by, 'grade': g.grade}).toList(),
        'chapter_id': chapterId,
      };
}

class Rawi {
  Rawi({
    required this.id,
    required this.nameAr,
    required this.nameEn,
    required this.nameId,
    required this.kunyah,
    required this.residence,
    required this.deathAh,
    required this.role,
    required this.roleId,
    required this.grade,
    required this.counts,
  });

  final String id;
  final String nameAr;
  final String nameEn;
  final String nameId;
  final String kunyah;
  final String residence;
  final String deathAh;
  final String role;
  final String roleId;
  final String grade;
  final int counts;

  String name(String lang) => lang == 'ar' ? nameAr : (lang == 'id' ? nameId : nameEn);

  /// Narrator level (tabaqah). The lidwa registry stores it in `grade`
  /// ("Follower(Tabi') [4th generation]"); a few records carry a `role` label.
  String get level => role.isNotEmpty ? role : grade;

  /// `level` with the registry's own "Level:" prefix dropped, for the rows that
  /// already print a LEVEL label of their own.
  String get levelText => level.replaceFirst(RegExp(r'^level\s*:\s*', caseSensitive: false), '');

  /// Death year with a single Hijri marker, whichever way the registry wrote it.
  String get deathYear => deathAh.isEmpty ? '' : (deathAh.toUpperCase().endsWith('H') ? deathAh : '$deathAh H');

  String get initial => nameMonogram(nameEn, id);

  factory Rawi.fromJson(Map<String, dynamic> j) {
    final rawEn = _asString(j['en']);
    final rawAr = _asString(j['ar']);
    final rawId = _asString(j['id']);
    // Registry fields are mixed-script; keep the Latin spelling in the Latin
    // fields and the Arabic spelling in `nameAr`.
    final latinEn = latinOf(rawEn);
    final latinAr = latinOf(rawAr);
    final arabicAr = arabicOf(rawAr).isNotEmpty ? arabicOf(rawAr) : arabicOf(rawEn);
    return Rawi(
      id: _asString(j['rawi_id'] ?? j['id']),
      nameAr: arabicAr,
      nameEn: latinEn.isNotEmpty ? latinEn : latinAr,
      nameId: latinOf(rawId).isNotEmpty ? latinOf(rawId) : (latinEn.isNotEmpty ? latinEn : latinAr),
      kunyah: _asString(j['kunyah']),
      residence: _asString(j['residence']),
      deathAh: _asString(j['death_ah']),
      role: _asString(j['role']),
      roleId: _asString(j['roleId'], _asString(j['role'])),
      grade: _asString(j['grade']),
      counts: _asInt(j['counts']),
    );
  }
}

class Topic {
  Topic({required this.id, required this.nameEn, required this.nameId, required this.count});

  final int id;
  final String nameEn;
  final String nameId;
  final int count;

  String name(String lang) => lang == 'id' ? nameId : nameEn;

  /// Arabic label for the fourteen lidwa top-level topics.
  static const arabic = <int, String>{
    1: 'الإيمان',
    2: 'العلم',
    3: 'الأمم السابقة',
    4: 'السيرة النبوية',
    5: 'القرآن',
    6: 'الأخلاق والآداب',
    7: 'العبادات',
    8: 'الطعام والشراب',
    9: 'اللباس والزينة',
    10: 'الأحوال الشخصية',
    11: 'المعاملات',
    12: 'الأقضية والأحكام',
    13: 'الجرائم والحدود',
    14: 'الجهاد',
  };

  String get nameAr => arabic[id] ?? '';

  IconData get icon => switch (id) {
        1 => Icons.shield_outlined,
        2 => Icons.school_outlined,
        3 => Icons.public_outlined,
        4 => Icons.menu_book_outlined,
        5 => Icons.auto_stories_outlined,
        6 => Icons.favorite_border,
        7 => Icons.mosque_outlined,
        8 => Icons.restaurant_outlined,
        9 => Icons.checkroom_outlined,
        10 => Icons.person_outline,
        11 => Icons.storefront_outlined,
        12 => Icons.gavel_outlined,
        13 => Icons.report_gmailerrorred_outlined,
        _ => Icons.military_tech_outlined,
      };

  factory Topic.fromJson(Map<String, dynamic> j) => Topic(
        id: _asInt(j['id']),
        nameEn: _asString(j['name_en']),
        nameId: _asString(j['name_id'], _asString(j['name_en'])),
        count: _asInt(j['hadith_count']),
      );
}

class TopicEntry {
  TopicEntry({required this.topicId, required this.bookId, required this.numbers});

  final int topicId;
  final String bookId;
  final List<String> numbers;

  factory TopicEntry.fromJson(Map<String, dynamic> j) => TopicEntry(
        topicId: _asInt(j['t']),
        bookId: _asString(j['b']),
        numbers: (j['n'] as List?)?.map((e) => e.toString()).toList() ?? const [],
      );
}

class SearchHit {
  SearchHit({
    required this.id,
    required this.bookId,
    required this.bookName,
    required this.number,
    required this.arabic,
    required this.translation,
    required this.english,
    required this.grade,
    required this.source,
  });

  final String id;
  final String bookId;
  final String bookName;
  final String number;
  final String arabic;
  final String translation;
  final String english;
  final String grade;
  final String source;

  factory SearchHit.fromMeili(Map<String, dynamic> j) => SearchHit(
        id: _asString(j['id']),
        bookId: _asString(j['collection']),
        bookName: _asString(j['book_title_en'], _asString(j['book_title_id'], _asString(j['collection']))),
        number: _asString(j['hadith_number']),
        arabic: _asString(j['text_ar']),
        translation: _asString(j['text_id'], _asString(j['text_en'])),
        english: _asString(j['text_en']),
        grade: _asString(j['grade']),
        source: _asString(j['source_label']),
      );
}

class SearchResultSet {
  SearchResultSet({required this.hits, required this.method, required this.engine, required this.fellBack});

  final List<SearchHit> hits;
  final String method;
  final String engine;
  final bool fellBack;
}

class Bookmark {
  Bookmark({
    required this.bookId,
    required this.bookTitle,
    required this.number,
    required this.arabic,
    required this.translation,
    required this.grade,
    required this.note,
    required this.collection,
    required this.savedAt,
  });

  final String bookId;
  final String bookTitle;
  final String number;
  final String arabic;
  final String translation;
  final String grade;
  String note;
  String collection;
  final DateTime savedAt;

  String get key => '$bookId:$number';

  Map<String, dynamic> toJson() => {
        'book_id': bookId,
        'book_title': bookTitle,
        'number': number,
        'arabic': arabic,
        'translation': translation,
        'grade': grade,
        'note': note,
        'collection': collection,
        'saved_at': savedAt.toIso8601String(),
      };

  factory Bookmark.fromJson(Map<String, dynamic> j) => Bookmark(
        bookId: _asString(j['book_id']),
        bookTitle: _asString(j['book_title']),
        number: _asString(j['number']),
        arabic: _asString(j['arabic']),
        translation: _asString(j['translation']),
        grade: _asString(j['grade']),
        note: _asString(j['note']),
        collection: _asString(j['collection'], 'Unsorted'),
        savedAt: DateTime.tryParse(_asString(j['saved_at'])) ?? DateTime.now(),
      );
}

class LastRead {
  LastRead({required this.bookId, required this.bookTitle, required this.number, required this.chapter, required this.at});

  final String bookId;
  final String bookTitle;
  final String number;
  final String chapter;
  final DateTime at;

  Map<String, dynamic> toJson() => {
        'book_id': bookId,
        'book_title': bookTitle,
        'number': number,
        'chapter': chapter,
        'at': at.toIso8601String(),
      };

  factory LastRead.fromJson(Map<String, dynamic> j) => LastRead(
        bookId: _asString(j['book_id']),
        bookTitle: _asString(j['book_title']),
        number: _asString(j['number']),
        chapter: _asString(j['chapter']),
        at: DateTime.tryParse(_asString(j['at'])) ?? DateTime.now(),
      );
}

class DownloadInfo {
  DownloadInfo({required this.bookId, required this.title, required this.bytes, required this.at});

  final String bookId;
  final String title;
  final int bytes;
  final DateTime at;

  Map<String, dynamic> toJson() => {'book_id': bookId, 'title': title, 'bytes': bytes, 'at': at.toIso8601String()};

  factory DownloadInfo.fromJson(Map<String, dynamic> j) => DownloadInfo(
        bookId: _asString(j['book_id']),
        title: _asString(j['title']),
        bytes: _asInt(j['bytes']),
        at: DateTime.tryParse(_asString(j['at'])) ?? DateTime.now(),
      );
}

class ChatMessage {
  ChatMessage({required this.role, required this.text, required this.at});

  final String role; // user | assistant
  final String text;
  final DateTime at;

  Map<String, dynamic> toJson() => {'role': role, 'text': text, 'at': at.toIso8601String()};

  factory ChatMessage.fromJson(Map<String, dynamic> j) => ChatMessage(
        role: _asString(j['role'], 'assistant'),
        text: _asString(j['text']),
        at: DateTime.tryParse(_asString(j['at'])) ?? DateTime.now(),
      );
}

List<dynamic> parseNdjson(String text) {
  final out = <dynamic>[];
  for (final line in const LineSplitter().convert(text)) {
    final t = line.trim();
    if (t.isEmpty) continue;
    try {
      out.add(jsonDecode(t));
    } catch (_) {
      // A byte-range slice can clip the first or last line; skip fragments.
    }
  }
  return out;
}

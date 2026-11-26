import 'dart:async';

import '../models.dart';
import 'auth_service.dart';
import 'local_store.dart';
import 'r2_client.dart';

class IndexEntry {
  IndexEntry({
    required this.i,
    required this.id,
    required this.n,
    required this.start,
    required this.end,
    required this.chapter,
    required this.lidwa,
    required this.raw,
  });

  final int i;
  final String id;
  final String n;
  final int start;
  final int end;
  final String? chapter;
  final List<String> lidwa;
  final Map<String, dynamic> raw;

  bool matches(String needle) {
    if (n == needle || id == needle) return true;
    return lidwa.any((l) => l == needle);
  }

  factory IndexEntry.fromJson(Map<String, dynamic> j) {
    final l = j['l'];
    final lidwa = l is List ? l.map((e) => e.toString()).toList() : (l == null ? <String>[] : [l.toString()]);
    return IndexEntry(
      i: (j['i'] as num?)?.toInt() ?? 0,
      id: '${j['id'] ?? ''}',
      n: '${j['n'] ?? j['id'] ?? ''}',
      start: (j['s'] as num?)?.toInt() ?? 0,
      end: (j['e'] as num?)?.toInt() ?? 0,
      chapter: j['c']?.toString(),
      lidwa: lidwa,
      raw: j,
    );
  }
}

/// Reader repository. Everything resolves against the same R2 contract the web
/// app uses (`api/<book>_index.ndjson` + byte ranges into `api/<book>.ndjson`),
/// with the local offline mirror taking precedence when a book is downloaded.
class HadeethRepository {
  HadeethRepository({R2Client? remote, LocalStore? local})
      : remote = remote ?? R2Client(),
        local = local ?? LocalStore.instance;

  final R2Client remote;
  final LocalStore local;

  final Set<String> downloaded = <String>{};
  bool preferOffline = true;

  List<Book>? _books;
  final Map<String, List<Chapter>> _chapters = {};
  final Map<String, List<IndexEntry>> _index = {};
  List<Topic>? _topics;
  List<TopicEntry>? _topicIndex;
  List<Rawi>? _rawis;
  Map<String, Rawi>? _rawiById;

  static String indexPath(String book) => 'api/${book}_index.ndjson';
  static String rowsPath(String book) => 'api/$book.ndjson';
  static String chaptersPath(String book) => 'chapters/$book.ndjson';

  Future<String?> _read(String path, {int? start, int? end}) async {
    final offline = local.has(path);
    if (preferOffline && await offline) {
      return start == null ? local.readFull(path) : local.readRange(path, start, end!);
    }
    try {
      return start == null ? await remote.fetchText(path) : await remote.fetchRange(path, start, end!);
    } catch (_) {
      // Last chance: a partially downloaded book still answers from disk.
      if (await offline) {
        return start == null ? local.readFull(path) : local.readRange(path, start, end!);
      }
      return null;
    }
  }

  Future<List<Book>> books({bool refresh = false}) async {
    if (_books != null && !refresh) return _books!;
    final rows = await remote.fetchNdjson('books.ndjson');
    final list = rows.map(Book.fromJson).toList()..sort((a, b) => a.orderIndex.compareTo(b.orderIndex));
    if (list.isNotEmpty) _books = list;
    return _books ?? list;
  }

  Future<Book?> book(String id) async {
    final all = await books();
    for (final b in all) {
      if (b.id == id) return b;
    }
    return null;
  }

  Future<List<Chapter>> chapters(String bookId, {bool refresh = false}) async {
    if (_chapters.containsKey(bookId) && !refresh) return _chapters[bookId]!;
    final text = await _read(chaptersPath(bookId), start: null);
    final Iterable<Map<String, dynamic>> rows =
        text == null ? const [] : parseNdjson(text).whereType<Map>().map((e) => e.cast<String, dynamic>());
    final list = rows.map(Chapter.fromJson).toList();
    _chapters[bookId] = list;
    return list;
  }

  Future<List<IndexEntry>> index(String bookId, {bool refresh = false}) async {
    if (_index.containsKey(bookId) && !refresh) return _index[bookId]!;
    final text = await _read(indexPath(bookId));
    if (text == null) return <IndexEntry>[];
    final list = parseNdjson(text).whereType<Map>().map((e) => IndexEntry.fromJson(e.cast<String, dynamic>())).toList();
    _index[bookId] = list;
    return list;
  }

  IndexEntry? _findEntry(List<IndexEntry> idx, String number) {
    for (final e in idx) {
      if (e.lidwa.any((l) => l == number)) return e;
    }
    for (final e in idx) {
      if (e.n == number) return e;
    }
    for (final e in idx) {
      if (e.id == number) return e;
    }
    return null;
  }

  Future<Hadith?> getHadith(String bookId, String number) async {
    final idx = await index(bookId);
    if (idx.isEmpty) return null;
    final entry = _findEntry(idx, number);
    if (entry == null) return null;
    final text = await _read(rowsPath(bookId), start: entry.start, end: entry.end);
    if (text == null) return null;
    final rows = parseNdjson(text).whereType<Map>().map((e) => e.cast<String, dynamic>()).toList();
    if (rows.isEmpty) return null;
    Map<String, dynamic>? pick;
    for (final r in rows) {
      final n = '${r['hadith_number'] ?? r['id']}';
      if (n == number || '${r['id']}' == number) {
        pick = r;
        break;
      }
    }
    pick ??= rows.first;
    return Hadith.fromJson(pick, bookIdFallback: bookId);
  }

  /// Load every row of a book (full download / offline bootstrap).
  Future<List<Hadith>> allHadiths(String bookId) async {
    final text = await _read(rowsPath(bookId));
    if (text == null) return const [];
    return parseNdjson(text)
        .whereType<Map>()
        .map((e) => Hadith.fromJson(e.cast<String, dynamic>(), bookIdFallback: bookId))
        .toList();
  }

  Future<List<Hadith>> chapterHadiths(String bookId, Chapter chapter) async {
    final idx = await index(bookId);
    final num = '${chapter.number}';
    var entries = idx.where((e) => e.chapter == num).toList();
    if (entries.isEmpty) entries = idx.where((e) => e.chapter == chapter.id).toList();
    if (entries.isEmpty) {
      entries = idx.where((e) => e.i >= chapter.hadithStart && e.i <= chapter.hadithEnd).toList();
    }
    if (entries.isEmpty) return const [];
    return _fetchEntries(bookId, entries);
  }

  /// Sequential reading page for a whole book, used by "Read sequential".
  Future<List<Hadith>> page(String bookId, {int offset = 0, int limit = 10}) async {
    final idx = await index(bookId);
    if (idx.isEmpty) return const [];
    final slice = idx.skip(offset).take(limit).toList();
    return _fetchEntries(bookId, slice);
  }

  Future<List<Hadith>> hadithsByNumbers(String bookId, List<String> numbers) async {
    if (numbers.isEmpty) return const [];
    final idx = await index(bookId);
    final wanted = numbers.toSet();
    final entries = <IndexEntry>[];
    for (final n in wanted) {
      final e = _findEntry(idx, n);
      if (e != null) entries.add(e);
    }
    entries.sort((a, b) => a.start.compareTo(b.start));
    return _fetchEntries(bookId, entries);
  }

  Future<List<Hadith>> _fetchEntries(String bookId, List<IndexEntry> entries) async {
    final runs = <List<int>>[];
    for (final e in entries) {
      if (runs.isNotEmpty && e.start == runs.last[1] + 1) {
        runs.last[1] = e.end;
      } else {
        runs.add([e.start, e.end]);
      }
    }
    final byNumber = <String, Hadith>{};
    for (final run in runs) {
      final text = await _read(rowsPath(bookId), start: run[0], end: run[1]);
      if (text == null) continue;
      for (final row in parseNdjson(text).whereType<Map>()) {
        final h = Hadith.fromJson(row.cast<String, dynamic>(), bookIdFallback: bookId);
        byNumber['${h.number}|${h.id}'] = h;
      }
    }
    final out = <Hadith>[];
    for (final e in entries) {
      Hadith? hit;
      for (final h in byNumber.values) {
        if (h.number == e.n || h.id == e.id) {
          hit = h;
          break;
        }
      }
      if (hit != null && !out.any((x) => x.number == hit!.number)) out.add(hit);
    }
    out.sort((a, b) {
      final ai = entries.indexWhere((e) => e.n == a.number || e.id == a.id);
      final bi = entries.indexWhere((e) => e.n == b.number || e.id == b.id);
      return ai.compareTo(bi);
    });
    return out;
  }

  Future<List<IndexEntry>> neighbours(String bookId, String number) async {
    final idx = await index(bookId);
    final pos = idx.indexWhere((e) => e.matches(number) && (e.n == number || e.lidwa.contains(number) || e.id == number));
    if (pos < 0) return const [];
    final out = <IndexEntry>[];
    if (pos > 0) out.add(idx[pos - 1]);
    if (pos < idx.length - 1) out.add(idx[pos + 1]);
    return out;
  }

  Future<int> positionOf(String bookId, String number) async {
    final idx = await index(bookId);
    return idx.indexWhere((e) => e.n == number || e.id == number || e.lidwa.contains(number));
  }

  Future<List<Topic>> topics() async {
    if (_topics != null) return _topics!;
    final rows = await remote.fetchNdjson('topics.ndjson');
    _topics = rows.map(Topic.fromJson).toList()..sort((a, b) => a.id.compareTo(b.id));
    return _topics!;
  }

  Future<List<TopicEntry>> topicIndex() async {
    if (_topicIndex != null) return _topicIndex!;
    final rows = await remote.fetchNdjson('topics_index.ndjson');
    _topicIndex = rows.map(TopicEntry.fromJson).toList();
    return _topicIndex!;
  }

  Future<List<Rawi>> rawis({void Function(double progress)? onProgress}) async {
    if (_rawis != null) return _rawis!;
    onProgress?.call(0.1);
    final rows = await remote.fetchNdjson('rawis/rawis.ndjson', timeout: const Duration(seconds: 40));
    onProgress?.call(0.9);
    _rawis = rows.map(Rawi.fromJson).where((r) => r.nameEn.isNotEmpty).toList();
    _rawiById = {for (final r in _rawis!) r.id: r};
    onProgress?.call(1);
    return _rawis!;
  }

  Future<Rawi?> rawi(String id) async {
    if (_rawiById == null) await rawis();
    return _rawiById?[id];
  }

  Future<Map<String, Rawi>> rawisByIds(Iterable<String> ids) async {
    if (_rawiById == null) await rawis();
    return {for (final id in ids) if (_rawiById!.containsKey(id)) id: _rawiById![id]!};
  }

  /// Hadith-of-the-Day pin. Supabase `hotd_overrides` is the admin source of
  /// truth; the CDN `hotd.ndjson` line stays as an offline fallback. Both are
  /// read-only for anon, so a signed-out reader still sees the same pick.
  Future<(String, String)?> hotdPin() async {
    final live = await _supabasePin();
    if (live != null) return live;
    final text = await _read('hotd.ndjson');
    if (text == null) return null;
    for (final row in parseNdjson(text)) {
      if (row is! Map) continue;
      final book = '${row['book'] ?? ''}'.trim();
      final id = '${row['id'] ?? row['hadith'] ?? ''}'.trim();
      if (book.isNotEmpty && id.isNotEmpty) return (book, id);
    }
    return null;
  }

  Future<(String, String)?> _supabasePin() async {
    final client = AuthService.instance.client;
    if (client == null) return null;
    try {
      final rows = await client
          .rpc('get_hotd_override')
          .timeout(const Duration(seconds: 8));
      if (rows is List) {
        for (final row in rows.whereType<Map>()) {
          final book = '${row['book_id'] ?? ''}'.trim();
          final id = '${row['hadith_number'] ?? ''}'.trim();
          if (book.isNotEmpty && id.isNotEmpty) return (book, id);
        }
      }
    } catch (_) {
      // Offline or RPC unavailable: fall through to the CDN line.
    }
    return null;
  }

  /// Hadith of the Day. An admin pin wins; otherwise the pick is deterministic
  /// for the WIB calendar day over the sahih-graded collections, so every device
  /// shows the same narration and it rolls at midnight without a server call.
  Future<Hadith?> hadithOfTheDay() async {
    final pin = await hotdPin();
    if (pin != null) {
      final pinned = await getHadith(pin.$1, pin.$2);
      if (pinned != null) return pinned;
    }
    final pool = (await books()).where((b) => b.isSahih && b.totalHadiths > 0).toList();
    if (pool.isEmpty) return getHadith('bukhari', '1');
    final wib = DateTime.now().toUtc().add(const Duration(hours: 7));
    final day = DateTime.utc(wib.year, wib.month, wib.day).millisecondsSinceEpoch ~/ 86400000;
    final book = pool[day % pool.length];
    final start = (day * 2654435761) % book.totalHadiths + 1;
    // These collections are graded sahih end to end. Non-core rows often have
    // no per-hadith grade, so 'unknown' is acceptable here; a recorded weak
    // grade is not. Walk forward a few rows to skip the latter.
    for (var step = 0; step < 8; step++) {
      final h = await getHadith(book.id, '${start + step}');
      if (h == null) break;
      if (h.tier == 'sahih' || h.tier == 'unknown') return h;
    }
    return getHadith('bukhari', '1');
  }

  /// Fetch syarah/commentary for a hadith from R2.
  /// Path: data/commentaries/{book}_{number}.json
  Future<Syarah?> getSyarah(String bookId, String number) async {
    final path = 'data/commentaries/${bookId}_${number}.json';
    final res = await remote.searchText(path);
    if (res == null) return null;
    return Syarah.fromJson(res);
  }
}

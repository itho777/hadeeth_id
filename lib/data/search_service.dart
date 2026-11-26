import 'dart:convert';

import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:http/http.dart' as http;

import '../models.dart';
import 'hadeeth_repository.dart';

/// Search tiers.
///
/// 1. `semantic` — `POST https://hadeeth.id/api/search`, the Cloudflare AI +
///    pgvector endpoint behind the web search box. Answers with ids plus a
///    similarity score, so hits are hydrated from the CDN afterwards.
/// 2. `keyword` — the Meilisearch index behind the web edition's keyword tier.
///    Only used when a key is supplied at build time, because the deployed web
///    build cannot reach [1]: the API answers with a pinned
///    `Access-Control-Allow-Origin: https://hadeeth.id` header, so a browser on
///    any other origin is blocked, while the Android app has no CORS at all.
///
///      flutter build web --dart-define=MEILI_KEY=<key>
///
/// 3. `offline` — local scan over downloaded collections, no network, no key.
class SearchService {
  SearchService({http.Client? client, String? meiliKey})
      : _client = client ?? http.Client(),
        _meiliKey = meiliKey ?? const String.fromEnvironment('MEILI_KEY');

  final http.Client _client;
  final String _meiliKey;

  static const _semanticUrl = 'https://hadeeth.id/api/search';
  static const _meiliUrl = 'https://meili-handoff-router.irianto-suryoputro.workers.dev/indexes/hadiths/search';

  bool get _canMeili => _meiliKey.isNotEmpty;

  Future<List<SearchHit>> semantic(String query, {String bookFilter = 'all', int limit = 20}) async {
    final body = jsonEncode({'q': query, 'book': bookFilter, 'limit': limit.clamp(1, 20)});
    final res = await _client
        .post(Uri.parse(_semanticUrl), headers: const {'Content-Type': 'application/json'}, body: body)
        .timeout(const Duration(seconds: 25));
    if (res.statusCode != 200) throw Exception('Search HTTP ${res.statusCode}');
    final data = jsonDecode(utf8.decode(res.bodyBytes)) as Map<String, dynamic>;
    final results = (data['results'] as List?) ?? const [];
    if (results.isEmpty) {
      final err = data['aiError'] ?? data['rpcError'];
      if (err != null) throw Exception(err.toString());
      return const [];
    }
    // The endpoint answers with ids plus a similarity score; matn and grade are
    // resolved later from the CDN by the search page.
    return results.whereType<Map>().map((r) {
      final j = r.cast<String, dynamic>();
      final bookId = _str(j['book_id']);
      return SearchHit(
        id: _str(j['id']),
        bookId: bookId,
        bookName: _str(j['book_title_en']).isNotEmpty ? _str(j['book_title_en']) : bookId.toUpperCase(),
        number: _str(j['hadith_number']),
        arabic: _str(j['text_ar']),
        translation: _str(j['text_id']).isNotEmpty ? _str(j['text_id']) : _str(j['text_en']),
        english: _str(j['text_en']),
        grade: _str(j['grade']),
        source: 'semantic',
      );
    }).toList();
  }

  /// Meilisearch keyword tier. Documents come back whole, so no hydration step.
  Future<List<SearchHit>> meili(String query, {String bookFilter = 'all', int limit = 20}) async {
    if (!_canMeili) throw StateError('meili key not configured');
    final payload = <String, dynamic>{'q': query, 'limit': limit.clamp(1, 50)};
    if (bookFilter != 'all') payload['filter'] = 'collection = "$bookFilter"';
    final res = await _client
        .post(
          Uri.parse(_meiliUrl),
          headers: {'Content-Type': 'application/json', 'Authorization': 'Bearer $_meiliKey'},
          body: jsonEncode(payload),
        )
        .timeout(const Duration(seconds: 20));
    if (res.statusCode != 200) throw Exception('Keyword HTTP ${res.statusCode}');
    final data = jsonDecode(utf8.decode(res.bodyBytes)) as Map<String, dynamic>;
    final hits = (data['hits'] as List?) ?? const [];
    return hits.whereType<Map>().map((r) {
      final j = r.cast<String, dynamic>();
      final bookId = _str(j['collection']).isNotEmpty ? _str(j['collection']) : _str(j['source']);
      final en = _str(j['book_title_en']);
      final id = _str(j['book_title_id']);
      return SearchHit(
        id: _str(j['id']),
        bookId: bookId,
        bookName: en.isNotEmpty ? en : (id.isNotEmpty ? id : bookId.toUpperCase()),
        number: _str(j['hadith_number']),
        arabic: _str(j['text_ar']),
        translation: _str(j['text_id']).isNotEmpty ? _str(j['text_id']) : _str(j['text_en']),
        english: _str(j['text_en']),
        grade: _str(j['grade']),
        source: 'keyword',
      );
    }).toList();
  }

  /// Exact substring search across downloaded collections only.
  Future<List<SearchHit>> keyword(HadeethRepository repo, String query, {String bookFilter = 'all', int limit = 30}) async {
    final q = query.trim().toLowerCase();
    if (q.length < 3) return const [];
    final out = <SearchHit>[];
    final ids = bookFilter == 'all' ? repo.downloaded.toList() : [if (repo.downloaded.contains(bookFilter)) bookFilter];
    for (final bookId in ids) {
      final book = await repo.book(bookId);
      final rows = await repo.allHadiths(bookId);
      for (final h in rows) {
        final haystack = '${h.textAr} ${h.textId} ${h.textEn} ${h.number}'.toLowerCase();
        if (!haystack.contains(q)) continue;
        out.add(SearchHit(
          id: h.id,
          bookId: h.bookId,
          bookName: book?.titleEn ?? bookId,
          number: h.number,
          arabic: h.textAr,
          translation: h.translationEnOrId,
          english: h.textEn,
          grade: h.grade,
          source: 'offline',
        ));
        if (out.length >= limit) return out;
      }
    }
    return out;
  }

  Future<SearchResultSet> search({
    required String query,
    required HadeethRepository repo,
    String bookFilter = 'all',
    int limit = 20,
    String method = 'semantic',
  }) async {
    if (method == 'offline') {
      final hits = await keyword(repo, query, bookFilter: bookFilter, limit: limit);
      return SearchResultSet(hits: hits, method: 'offline', engine: 'Offline', fellBack: false);
    }

    // A browser cannot reach the semantic endpoint cross-origin, so on web the
    // keyword index is the primary tier.
    if (kIsWeb && _canMeili) {
      try {
        final hits = await meili(query, bookFilter: bookFilter, limit: limit);
        return SearchResultSet(hits: hits, method: 'keyword', engine: 'Meilisearch', fellBack: false);
      } catch (_) {/* fall through to the semantic tier */}
    }

    try {
      final hits = await semantic(query, bookFilter: bookFilter, limit: limit);
      return SearchResultSet(hits: hits, method: 'semantic', engine: 'Cloudflare AI', fellBack: false);
    } catch (e) {
      if (_canMeili) {
        try {
          final hits = await meili(query, bookFilter: bookFilter, limit: limit);
          return SearchResultSet(hits: hits, method: 'keyword', engine: 'Meilisearch', fellBack: true);
        } catch (_) {/* report the first failure */}
      }
      if (repo.downloaded.isNotEmpty) {
        try {
          final hits = await keyword(repo, query, bookFilter: bookFilter, limit: limit);
          return SearchResultSet(hits: hits, method: 'offline', engine: 'Offline', fellBack: true);
        } catch (_) {/* report the first failure */}
      }
      return SearchResultSet(hits: const [], method: 'error', engine: e.toString(), fellBack: false);
    }
  }

  String _str(dynamic v) => v == null ? '' : v.toString();
}

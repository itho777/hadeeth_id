import 'dart:convert';

import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;

/// Opt-in network smoke test. Runs against the live hadeeth.id endpoints from a
/// real browser engine (`flutter test --platform chrome`) so CORS is enforced
/// exactly as it will be in the deployed web build.
///
///   flutter test --platform chrome --dart-define=LIVE=true test/live_network_test.dart
const bool kLive = bool.fromEnvironment('LIVE');

void main() {
  const jsonHeaders = {'Content-Type': 'application/json'};

  test('CDN book index is reachable and parses', () async {
    if (!kLive) return;
    final res = await http.get(Uri.parse('https://cdn.hadeeth.id/books.ndjson'));
    expect(res.statusCode, 200);
    final rows = const LineSplitter()
        .convert(utf8.decode(res.bodyBytes))
        .where((l) => l.trim().isNotEmpty)
        .map((l) => jsonDecode(l) as Map<String, dynamic>)
        .toList();
    expect(rows.length, greaterThanOrEqualTo(9));
    expect(rows.any((r) => r['id'] == 'bukhari'), isTrue);
  }, timeout: const Timeout(Duration(seconds: 60)));

  test('search API answers cross-origin with ids', () async {
    if (!kLive) return;
    final res = await http.post(
      Uri.parse('https://hadeeth.id/api/search'),
      headers: jsonHeaders,
      body: jsonEncode({'q': 'niat dan amal', 'book': 'all', 'limit': 2}),
    );
    expect(res.statusCode, 200);
    final data = jsonDecode(utf8.decode(res.bodyBytes)) as Map<String, dynamic>;
    final results = data['results'] as List? ?? const [];
    expect(results, isNotEmpty);
    expect((results.first as Map)['book_id'], isNotNull);
  }, timeout: const Timeout(Duration(seconds: 90)));

  test('Razi scholar API answers cross-origin', () async {
    if (!kLive) return;
    final res = await http.post(
      Uri.parse('https://razi.hadeeth.id/api/chat'),
      headers: jsonHeaders,
      body: jsonEncode({'message': 'Apa hadis tentang niat?', 'lang': 'id'}),
    );
    expect(res.statusCode, 200);
    expect(utf8.decode(res.bodyBytes).trim(), isNotEmpty);
  }, timeout: const Timeout(Duration(seconds: 120)));
}

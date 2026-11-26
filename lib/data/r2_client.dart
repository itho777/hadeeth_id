import 'dart:async';
import 'dart:convert';

import 'package:http/http.dart' as http;

import '../models.dart';

/// Thin client over the hadeeth.id R2 bucket. The reader path is the same one
/// the web app uses: an NDJSON offset index plus one HTTP Range request per
/// contiguous run, because the bucket answers 206 with CORS open.
class R2Client {
  R2Client({http.Client? client}) : _client = client ?? http.Client();

  static const String baseUrl = 'https://cdn.hadeeth.id';
  static const String devFallback = 'https://pub-075ac3f4a31e4e85a876c26c815ae93d.r2.dev';

  final http.Client _client;
  final Map<String, List<Map<String, dynamic>>> _ndjsonCache = {};
  final Map<String, String> _textCache = {};

  void clearCache() {
    _ndjsonCache.clear();
    _textCache.clear();
  }

  Future<http.Response> _send(String url, {Map<String, String>? headers, Duration timeout = const Duration(seconds: 20)}) {
    return _client.get(Uri.parse(url), headers: headers).timeout(timeout);
  }

  Future<http.Response?> _get(String path, {Map<String, String>? headers, Duration timeout = const Duration(seconds: 20)}) async {
    for (final origin in [baseUrl, devFallback]) {
      try {
        final res = await _send('$origin/$path', headers: headers, timeout: timeout);
        if (res.statusCode == 200 || res.statusCode == 206) return res;
      } catch (_) {
        // try the mirror
      }
    }
    return null;
  }

  Future<String?> fetchText(String path, {Duration timeout = const Duration(seconds: 25)}) async {
    if (_textCache.containsKey(path)) return _textCache[path];
    final res = await _get(path, timeout: timeout);
    if (res == null) return null;
    final text = utf8.decode(res.bodyBytes, allowMalformed: true);
    _textCache[path] = text;
    return text;
  }

  Future<List<Map<String, dynamic>>> fetchNdjson(String path, {bool cache = true, Duration timeout = const Duration(seconds: 25)}) async {
    if (cache && _ndjsonCache.containsKey(path)) return _ndjsonCache[path]!;
    final text = await fetchText(path, timeout: timeout);
    if (text == null) return const [];
    final rows = parseNdjson(text).whereType<Map>().map((e) => e.cast<String, dynamic>()).toList();
    if (cache) _ndjsonCache[path] = rows;
    return rows;
  }

  /// Byte range read. Returns the decoded slice; callers parse NDJSON rows.
  Future<String> fetchRange(String path, int start, int end, {Duration timeout = const Duration(seconds: 20)}) async {
    final res = await _get(path, headers: {'Range': 'bytes=$start-$end'}, timeout: timeout);
    if (res == null) throw Exception('Range request failed for $path');
    final bytes = res.bodyBytes;
    if (res.statusCode == 200) {
      final from = start.clamp(0, bytes.length);
      final to = (end + 1).clamp(from, bytes.length);
      return utf8.decode(bytes.sublist(from, to), allowMalformed: true);
    }
    return utf8.decode(bytes, allowMalformed: true);
  }

  Future<Map<String, dynamic>?> searchText(String path) async {
    final text = await fetchText(path);
    if (text == null) return null;
    try {
      final decoded = jsonDecode(text);
      return decoded is Map<String, dynamic> ? decoded : null;
    } catch (_) {
      return null;
    }
  }
}

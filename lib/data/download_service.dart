import 'dart:io';

import 'package:http/http.dart' as http;

import '../data/local_store.dart';
import '../data/r2_client.dart';
import '../models.dart';

class DownloadService {
  DownloadService({http.Client? client}) : _client = client ?? http.Client();

  final http.Client _client;
  final LocalStore _store = LocalStore.instance;

  static const files = ['api/_ID__index.ndjson', 'chapters/_ID_.ndjson', 'api/_ID_.ndjson'];

  Future<DownloadInfo> downloadBook(Book book, {void Function(double)? onProgress}) async {
    final plan = <String, String>{
      'api/${book.id}_index.ndjson': '${R2Client.baseUrl}/api/${book.id}_index.ndjson',
      'chapters/${book.id}.ndjson': '${R2Client.baseUrl}/chapters/${book.id}.ndjson',
      'api/${book.id}.ndjson': '${R2Client.baseUrl}/api/${book.id}.ndjson',
    };

    // The row file is by far the largest, so weight the bar by bytes when the
    // CDN reports content-length; otherwise fall back to equal thirds.
    final weights = {'api/${book.id}_index.ndjson': 0.02, 'chapters/${book.id}.ndjson': 0.01, 'api/${book.id}.ndjson': 0.97};

    var totalWritten = 0;
    var doneShare = 0.0;
    for (final entry in plan.entries) {
      final path = entry.key;
      final url = entry.value;
      final file = await _store.file(path);
      await file.parent.create(recursive: true);

      final request = http.Request('GET', Uri.parse(url));
      final response = await _client.send(request).timeout(const Duration(seconds: 90));
      if (response.statusCode != 200 && response.statusCode != 206) {
        throw Exception('Download failed for $path (HTTP ${response.statusCode})');
      }
      final expected = response.contentLength ?? 0;
      final sink = file.openWrite();
      var received = 0;
      try {
        await for (final chunk in response.stream) {
          sink.add(chunk);
          received += chunk.length;
          totalWritten += chunk.length;
          final fileShare = expected > 0 ? (received / expected).clamp(0.0, 1.0) : 0.0;
          onProgress?.call((doneShare + fileShare * weights[path]!).clamp(0.0, 1.0));
        }
      } finally {
        await sink.flush();
        await sink.close();
      }
      doneShare += weights[path]!;
      onProgress?.call(doneShare.clamp(0.0, 1.0));
    }

    onProgress?.call(1);
    return DownloadInfo(bookId: book.id, title: book.titleEn, bytes: totalWritten, at: DateTime.now());
  }

  Future<void> deleteBook(String bookId) async {
    await _store.deleteBook(bookId);
  }

  Future<int> storageBytes() => _store.totalBytes();

  Future<bool> isComplete(String bookId) async {
    for (final path in LocalStore.bookPaths(bookId)) {
      final f = await _store.file(path);
      if (!await f.exists() || await f.length() == 0) return false;
    }
    return true;
  }

  Future<List<String>> downloadedBooks() async {
    final r = await _store.root();
    final apiDir = Directory('${r.path}${Platform.pathSeparator}api');
    if (!await apiDir.exists()) return const [];
    final out = <String>[];
    await for (final e in apiDir.list()) {
      if (e is File) {
        final name = e.uri.pathSegments.last;
        if (name.endsWith('.ndjson') && !name.endsWith('_index.ndjson')) {
          final id = name.substring(0, name.length - '.ndjson'.length);
          if (await isComplete(id)) out.add(id);
        }
      }
    }
    out.sort();
    return out;
  }
}

import 'dart:convert';
import 'dart:io';

import 'package:path_provider/path_provider.dart';

/// Offline mirror of the R2 key layout. A downloaded book keeps exactly the
/// three files the reader needs — the row file, its byte-offset index and the
/// chapter list — so an offline lookup goes through the same range maths as the
/// online one instead of a second parser.
class LocalStore {
  LocalStore._();
  static final LocalStore instance = LocalStore._();

  /// Test seam: bind the mirror to a plain directory so widget tests do not
  /// need the `path_provider` platform channel.
  LocalStore.at(Directory dir) : _root = dir;

  Directory? _root;

  Future<Directory> root() async {
    if (_root != null) return _root!;
    final base = await getApplicationSupportDirectory();
    final dir = Directory('${base.path}${Platform.pathSeparator}hadeeth_offline');
    if (!await dir.exists()) await dir.create(recursive: true);
    _root = dir;
    return dir;
  }

  Future<File> file(String path) async {
    final r = await root();
    final f = File('${r.path}${Platform.pathSeparator}${path.replaceAll('/', Platform.pathSeparator)}');
    return f;
  }

  Future<bool> has(String path) async => (await file(path)).exists();

  Future<String?> readFull(String path) async {
    final f = await file(path);
    if (!await f.exists()) return null;
    return f.readAsString();
  }

  Future<String?> readRange(String path, int start, int end) async {
    final f = await file(path);
    if (!await f.exists()) return null;
    final raf = await f.open();
    try {
      final length = await f.length();
      if (start >= length) return null;
      await raf.setPosition(start);
      final count = (end - start + 1).clamp(0, length - start);
      final bytes = await raf.read(count);
      return utf8.decode(bytes, allowMalformed: true);
    } finally {
      await raf.close();
    }
  }

  Future<int> write(String path, List<int> bytes) async {
    final f = await file(path);
    await f.parent.create(recursive: true);
    await f.writeAsBytes(bytes, flush: true);
    return bytes.length;
  }

  Future<int> bookSize(String bookId) async {
    var total = 0;
    for (final p in bookPaths(bookId)) {
      final f = await file(p);
      if (await f.exists()) total += await f.length();
    }
    return total;
  }

  Future<void> deleteBook(String bookId) async {
    for (final p in bookPaths(bookId)) {
      final f = await file(p);
      if (await f.exists()) await f.delete();
    }
  }

  static List<String> bookPaths(String bookId) => [
        'api/$bookId.ndjson',
        'api/${bookId}_index.ndjson',
        'chapters/$bookId.ndjson',
      ];

  Future<int> totalBytes() async {
    final r = await root();
    var total = 0;
    await for (final e in r.list(recursive: true)) {
      if (e is File) total += await e.length();
    }
    return total;
  }
}

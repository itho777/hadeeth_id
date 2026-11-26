import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';

import '../models.dart';

class AppState extends ChangeNotifier {
  AppState();

  static const _kTheme = 'theme_mode';
  static const _kLang = 'lang';
  static const _kArabic = 'arabic_size';
  static const _kShowTrans = 'show_translation';
  static const _kTransMode = 'translation_mode';
  static const _kBookmarks = 'bookmarks_v1';
  static const _kCollections = 'collections_v1';
  static const _kLastRead = 'last_read_v1';
  static const _kDownloads = 'downloads_v1';
  static const _kReads = 'reads_v1';
  static const _kPreferOffline = 'prefer_offline';
  static const _kOnboarded = 'onboarded_v1';

  SharedPreferences? _prefs;

  ThemeMode themeMode = ThemeMode.system;
  String lang = 'id';
  double arabicSize = 27;
  bool showTranslation = true;
  String translationMode = 'id'; // id | en | both
  bool preferOffline = true;
  bool onboarded = false;

  Map<String, LastRead> lastRead = {};
  List<Bookmark> bookmarks = [];
  List<String> collections = ['Unsorted', 'Study', 'Fiqh', 'Akhlaq'];
  Map<String, DownloadInfo> downloads = {};
  int readsToday = 0;
  String readsDate = '';

  List<Bookmark> get sortedBookmarks => List<Bookmark>.from(bookmarks)..sort((a, b) => b.savedAt.compareTo(a.savedAt));

  /// Wired by SyncService once the reader signs in. Null keeps the app local.
  void Function(Bookmark bookmark, bool removed)? onBookmarkChange;
  void Function(LastRead read)? onProgressChange;
  void Function(String lang)? onLanguageChange;

  bool isBookmarked(String bookId, String number) => bookmarks.any((b) => b.key == '$bookId:$number');

  Future<void> init() async {
    _prefs = await SharedPreferences.getInstance();
    final p = _prefs!;
    themeMode = switch (p.getString(_kTheme)) {
      'light' => ThemeMode.light,
      'dark' => ThemeMode.dark,
      _ => ThemeMode.system,
    };
    lang = p.getString(_kLang) ?? 'id';
    arabicSize = p.getDouble(_kArabic) ?? 27;
    showTranslation = p.getBool(_kShowTrans) ?? true;
    translationMode = p.getString(_kTransMode) ?? 'id';
    preferOffline = p.getBool(_kPreferOffline) ?? true;
    onboarded = p.getBool(_kOnboarded) ?? false;
    readsDate = p.getString('${_kReads}_date') ?? '';
    readsToday = p.getInt(_kReads) ?? 0;
    _normaliseReadsDate();

    final bm = p.getString(_kBookmarks);
    if (bm != null && bm.isNotEmpty) {
      try {
        bookmarks = (jsonDecode(bm) as List).whereType<Map>().map((e) => Bookmark.fromJson(e.cast<String, dynamic>())).toList();
      } catch (_) {}
    }
    final cols = p.getString(_kCollections);
    if (cols != null && cols.isNotEmpty) {
      try {
        collections = (jsonDecode(cols) as List).map((e) => e.toString()).toList();
      } catch (_) {}
    }
    if (!collections.contains('Unsorted')) collections.insert(0, 'Unsorted');

    final lr = p.getString(_kLastRead);
    if (lr != null && lr.isNotEmpty) {
      try {
        final map = jsonDecode(lr) as Map<String, dynamic>;
        lastRead = map.map((k, v) => MapEntry(k, LastRead.fromJson(v as Map<String, dynamic>)));
      } catch (_) {}
    }
    final dl = p.getString(_kDownloads);
    if (dl != null && dl.isNotEmpty) {
      try {
        final list = (jsonDecode(dl) as List).whereType<Map>();
        downloads = {for (final e in list) (e['book_id'] ?? '').toString(): DownloadInfo.fromJson(e.cast<String, dynamic>())};
      } catch (_) {}
    }
    notifyListeners();
  }

  void _normaliseReadsDate() {
    final today = DateTime.now().toIso8601String().substring(0, 10);
    if (readsDate != today) {
      readsDate = today;
      readsToday = 0;
      _prefs?.setString('${_kReads}_date', today);
      _prefs?.setInt(_kReads, 0);
    }
  }

  Future<void> _save(String key, Object? value) async {
    final p = _prefs;
    if (p == null) return;
    if (value == null) {
      await p.remove(key);
    } else if (value is String) {
      await p.setString(key, value);
    } else if (value is bool) {
      await p.setBool(key, value);
    } else if (value is double) {
      await p.setDouble(key, value);
    } else if (value is int) {
      await p.setInt(key, value);
    }
  }

  Future<void> setThemeMode(ThemeMode mode) async {
    themeMode = mode;
    await _save(_kTheme, mode.name);
    notifyListeners();
  }

  Future<void> toggleTheme(bool dark) async => setThemeMode(dark ? ThemeMode.light : ThemeMode.dark);

  Future<void> setLang(String value) async {
    lang = value;
    await _save(_kLang, value);
    onLanguageChange?.call(value);
    notifyListeners();
  }

  Future<void> setArabicSize(double value) async {
    arabicSize = value.clamp(18, 44);
    await _save(_kArabic, arabicSize);
    notifyListeners();
  }

  Future<void> setShowTranslation(bool value) async {
    showTranslation = value;
    await _save(_kShowTrans, value);
    notifyListeners();
  }

  Future<void> setTranslationMode(String value) async {
    translationMode = value;
    await _save(_kTransMode, value);
    notifyListeners();
  }

  Future<void> setPreferOffline(bool value) async {
    preferOffline = value;
    await _save(_kPreferOffline, value);
    notifyListeners();
  }

  Future<void> setOnboarded(bool value) async {
    onboarded = value;
    await _save(_kOnboarded, value);
    notifyListeners();
  }

  Future<void> recordRead(String bookId, String bookTitle, String number, String chapter) async {
    _normaliseReadsDate();
    lastRead[bookId] = LastRead(bookId: bookId, bookTitle: bookTitle, number: number, chapter: chapter, at: DateTime.now());
    readsToday += 1;
    await _save(_kLastRead, jsonEncode(lastRead.map((k, v) => MapEntry(k, v.toJson()))));
    await _save(_kReads, readsToday);
    onProgressChange?.call(lastRead[bookId]!);
    notifyListeners();
  }

  Future<bool> toggleBookmark({
    required String bookId,
    required String bookTitle,
    required String number,
    required String arabic,
    required String translation,
    required String grade,
    String collection = 'Unsorted',
  }) async {
    final key = '$bookId:$number';
    final existing = bookmarks.indexWhere((b) => b.key == key);
    if (existing >= 0) {
      final removed = bookmarks.removeAt(existing);
      await _persistBookmarks();
      onBookmarkChange?.call(removed, true);
      return false;
    }
    bookmarks.add(Bookmark(
      bookId: bookId,
      bookTitle: bookTitle,
      number: number,
      arabic: arabic,
      translation: translation,
      grade: grade,
      note: '',
      collection: collection,
      savedAt: DateTime.now(),
    ));
    await _persistBookmarks();
    onBookmarkChange?.call(bookmarks.last, false);
    return true;
  }

  Future<void> updateNote(String key, String note) async {
    final i = bookmarks.indexWhere((b) => b.key == key);
    if (i < 0) return;
    bookmarks[i].note = note;
    await _persistBookmarks();
    onBookmarkChange?.call(bookmarks[i], false);
  }

  Future<void> moveToCollection(String key, String collection) async {
    final i = bookmarks.indexWhere((b) => b.key == key);
    if (i < 0) return;
    bookmarks[i].collection = collection;
    await _persistBookmarks();
    onBookmarkChange?.call(bookmarks[i], false);
  }

  Future<void> removeBookmark(String key) async {
    final i = bookmarks.indexWhere((b) => b.key == key);
    if (i < 0) return;
    final removed = bookmarks.removeAt(i);
    await _persistBookmarks();
    onBookmarkChange?.call(removed, true);
  }

  Future<void> addCollection(String name) async {
    final trimmed = name.trim();
    if (trimmed.isEmpty || collections.contains(trimmed)) return;
    collections.add(trimmed);
    await _save(_kCollections, jsonEncode(collections));
    notifyListeners();
  }

  Future<void> _persistBookmarks() async {
    await _save(_kBookmarks, jsonEncode(bookmarks.map((b) => b.toJson()).toList()));
    notifyListeners();
  }

  /// Merge the signed-in account's copy into local state. Newest write wins per
  /// key; nothing is deleted locally because another device may not have it yet.
  Future<void> applyRemote({
    required List<Bookmark> remoteBookmarks,
    required Map<String, LastRead> remoteProgress,
  }) async {
    final byKey = {for (final b in bookmarks) b.key: b};
    for (final remote in remoteBookmarks) {
      final local = byKey[remote.key];
      if (local == null || remote.savedAt.isAfter(local.savedAt)) {
        byKey[remote.key] = remote;
      }
    }
    bookmarks = byKey.values.toList();
    for (final entry in remoteProgress.entries) {
      final local = lastRead[entry.key];
      if (local == null || entry.value.at.isAfter(local.at)) {
        lastRead[entry.key] = entry.value;
      }
    }
    await _save(_kBookmarks, jsonEncode(bookmarks.map((b) => b.toJson()).toList()));
    await _save(_kLastRead, jsonEncode(lastRead.map((k, v) => MapEntry(k, v.toJson()))));
    notifyListeners();
  }

  Future<void> setDownload(DownloadInfo info) async {
    downloads[info.bookId] = info;
    await _save(_kDownloads, jsonEncode(downloads.values.map((d) => d.toJson()).toList()));
    notifyListeners();
  }

  Future<void> removeDownload(String bookId) async {
    downloads.remove(bookId);
    await _save(_kDownloads, jsonEncode(downloads.values.map((d) => d.toJson()).toList()));
    notifyListeners();
  }

  int get downloadBytes => downloads.values.fold(0, (sum, d) => sum + d.bytes);

  Future<void> resetSettings() async {
    themeMode = ThemeMode.system;
    lang = 'id';
    arabicSize = 27;
    showTranslation = true;
    translationMode = 'id';
    preferOffline = true;
    await _save(_kTheme, ThemeMode.system.name);
    await _save(_kLang, 'id');
    await _save(_kArabic, 27.0);
    await _save(_kShowTrans, true);
    await _save(_kTransMode, 'id');
    await _save(_kPreferOffline, true);
    notifyListeners();
  }
}

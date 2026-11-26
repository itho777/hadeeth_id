import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

import '../models.dart';
import '../state/app_state.dart';
import 'auth_service.dart';

/// Local-first sync: every read and bookmark is written to disk first, then
/// mirrored to Supabase when the reader is signed in. Signing in pulls the
/// cloud copy, merges it into local state (newest `saved_at` / `read_at` wins),
/// and pushes the merged result back so a second device catches up.
class SyncService extends ChangeNotifier {
  SyncService._();

  static final SyncService instance = SyncService._();

  AppState? _state;
  bool _syncing = false;
  DateTime? _lastSynced;
  String? _error;
  Timer? _debounce;

  bool get syncing => _syncing;
  DateTime? get lastSynced => _lastSynced;
  String? get error => _error;
  bool get active => AuthService.instance.signedIn;

  SupabaseClient get _db => Supabase.instance.client;
  String? get _uid => _db.auth.currentUser?.id;

  /// Called once from main(); wires local mutations to the cloud mirror.
  void bind(AppState state) {
    _state = state;
    state.onBookmarkChange = _pushBookmark;
    state.onProgressChange = _pushProgress;
    state.onLanguageChange = (lang) => pushProfile(preferredLanguage: lang);
    AuthService.instance.addListener(_onAuthChanged);
    if (AuthService.instance.signedIn) unawaited(pull());
  }

  void _onAuthChanged() {
    if (AuthService.instance.signedIn) {
      unawaited(pull());
    } else {
      _lastSynced = null;
      _error = null;
      notifyListeners();
    }
  }

  /// Pull the account copy, merge into local state, then mirror the merge back.
  Future<void> pull() async {
    final state = _state;
    final uid = _uid;
    if (state == null || uid == null || _syncing) return;
    _syncing = true;
    _error = null;
    notifyListeners();
    try {
      final profile = await _db.from('profiles').select().eq('id', uid).maybeSingle();
      final rows = await _db.from('bookmarks').select().eq('user_id', uid);
      final progress = await _db.from('reading_progress').select().eq('user_id', uid);

      final remoteBookmarks = (rows as List)
          .whereType<Map>()
          .map((r) => _bookmarkFromRow(r.cast<String, dynamic>()))
          .toList();
      final remoteProgress = <String, LastRead>{};
      for (final r in (progress as List).whereType<Map>()) {
        final lr = _progressFromRow(r.cast<String, dynamic>());
        remoteProgress[lr.bookId] = lr;
      }
      await state.applyRemote(remoteBookmarks: remoteBookmarks, remoteProgress: remoteProgress);

      // Mirror the merge so this device's offline reads reach the other side.
      if (state.bookmarks.isNotEmpty) {
        await _db.from('bookmarks').upsert(
              state.bookmarks.map(_bookmarkRow).toList(),
              onConflict: 'user_id,book_id,hadith_number',
            );
      }
      if (state.lastRead.isNotEmpty) {
        await _db.from('reading_progress').upsert(
              state.lastRead.values.map(_progressRow).toList(),
              onConflict: 'user_id,book_id',
            );
      }
      if (profile != null) {
        _displayName = '${profile['display_name'] ?? ''}'.trim();
        _avatarUrl = '${profile['avatar_url'] ?? ''}'.trim();
      }
      _lastSynced = DateTime.now();
    } catch (e) {
      _error = '$e';
    } finally {
      _syncing = false;
      notifyListeners();
    }
  }

  String? _displayName;
  String? _avatarUrl;
  String? get displayName => (_displayName?.isEmpty ?? true) ? null : _displayName;
  String? get avatarUrl => (_avatarUrl?.isEmpty ?? true) ? null : _avatarUrl;

  Future<void> _pushBookmark(Bookmark bookmark, bool removed) async {
    final uid = _uid;
    if (uid == null) return;
    try {
      if (removed) {
        await _db.from('bookmarks').delete().match({
          'user_id': uid,
          'book_id': bookmark.bookId,
          'hadith_number': bookmark.number,
        });
      } else {
        await _db.from('bookmarks').upsert(
              _bookmarkRow(bookmark),
              onConflict: 'user_id,book_id,hadith_number',
            );
      }
      _lastSynced = DateTime.now();
      _error = null;
    } catch (e) {
      _error = '$e';
    }
    notifyListeners();
  }

  Future<void> _pushProgress(LastRead read) async {
    final uid = _uid;
    if (uid == null) return;
    try {
      await _db.from('reading_progress').upsert(
            _progressRow(read),
            onConflict: 'user_id,book_id',
          );
      _lastSynced = DateTime.now();
      _error = null;
    } catch (e) {
      _error = '$e';
    }
    notifyListeners();
  }

  /// Debounced profile write; language changes fire often, so batch them.
  void pushProfile({String? displayName, String? preferredLanguage}) {
    _debounce?.cancel();
    _debounce = Timer(const Duration(milliseconds: 700), () async {
      final uid = _uid;
      if (uid == null) return;
      try {
        await _db.from('profiles').upsert({
          'id': uid,
          if (displayName != null) 'display_name': displayName,
          if (preferredLanguage != null) 'preferred_language': preferredLanguage,
          'updated_at': DateTime.now().toUtc().toIso8601String(),
        });
      } catch (e) {
        _error = '$e';
        notifyListeners();
      }
    });
  }

  Map<String, dynamic> _bookmarkRow(Bookmark b) => {
        'user_id': _uid,
        'book_id': b.bookId,
        'hadith_number': b.number,
        'book_title': b.bookTitle,
        'arabic': b.arabic,
        'translation': b.translation,
        'grade': b.grade,
        'note': b.note,
        'collection': b.collection,
        'saved_at': b.savedAt.toUtc().toIso8601String(),
      };

  Map<String, dynamic> _progressRow(LastRead r) => {
        'user_id': _uid,
        'book_id': r.bookId,
        'hadith_number': r.number,
        'book_title': r.bookTitle,
        'chapter': r.chapter,
        'read_at': r.at.toUtc().toIso8601String(),
      };

  Bookmark _bookmarkFromRow(Map<String, dynamic> r) => Bookmark(
        bookId: '${r['book_id'] ?? ''}',
        bookTitle: '${r['book_title'] ?? ''}',
        number: '${r['hadith_number'] ?? ''}',
        arabic: '${r['arabic'] ?? ''}',
        translation: '${r['translation'] ?? ''}',
        grade: '${r['grade'] ?? ''}',
        note: '${r['note'] ?? ''}',
        collection: '${r['collection'] ?? 'Unsorted'}',
        savedAt: DateTime.tryParse('${r['saved_at']}')?.toLocal() ?? DateTime.now(),
      );

  LastRead _progressFromRow(Map<String, dynamic> r) => LastRead(
        bookId: '${r['book_id'] ?? ''}',
        bookTitle: '${r['book_title'] ?? ''}',
        number: '${r['hadith_number'] ?? ''}',
        chapter: '${r['chapter'] ?? ''}',
        at: DateTime.tryParse('${r['read_at']}')?.toLocal() ?? DateTime.now(),
      );

  @override
  void dispose() {
    _debounce?.cancel();
    AuthService.instance.removeListener(_onAuthChanged);
    super.dispose();
  }
}

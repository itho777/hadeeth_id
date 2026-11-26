import 'dart:io';

import 'package:flutter_test/flutter_test.dart';

import 'package:hadeeth_id_mobile/data/hadeeth_repository.dart';
import 'package:hadeeth_id_mobile/data/local_store.dart';
import 'package:hadeeth_id_mobile/data/razi_service.dart';
import 'package:hadeeth_id_mobile/data/r2_client.dart';
import 'package:hadeeth_id_mobile/data/search_service.dart';

/// Opt-in run against production from the app's own code paths — no stubs.
///
///   flutter test --dart-define=LIVE=true test/live_services_test.dart
const bool kLive = bool.fromEnvironment('LIVE');

void main() {
  HadeethRepository liveRepo() => HadeethRepository(
        remote: R2Client(),
        local: LocalStore.at(Directory.systemTemp.createTempSync('hadeeth_live_')),
      );

  test('repository parses books, chapters and a matn row from the CDN', () async {
    if (!kLive) return;
    final repo = liveRepo();
    final books = await repo.books();
    expect(books.length, greaterThanOrEqualTo(9));
    final bukhari = books.firstWhere((b) => b.id == 'bukhari');
    expect(bukhari.totalHadiths, greaterThan(7000));

    final chapters = await repo.chapters('bukhari');
    expect(chapters, isNotEmpty);

    final h = await repo.getHadith('bukhari', '1');
    expect(h, isNotNull);
    expect(h!.textAr.trim(), isNotEmpty);
    expect(h.textEn.toLowerCase(), contains('intention'));
  }, timeout: const Timeout(Duration(minutes: 3)));

  test('semantic search returns hydratable ids from production', () async {
    if (!kLive) return;
    final hits = await SearchService().semantic('niat dan amal', limit: 3);
    expect(hits, isNotEmpty);
    final first = hits.first;
    expect(first.bookId, isNotEmpty);
    expect(first.number, isNotEmpty);
    final row = await liveRepo().getHadith(first.bookId, first.number);
    expect(row, isNotNull, reason: 'every semantic hit must resolve to a CDN row');
    expect(row!.textAr.trim(), isNotEmpty);
  }, timeout: const Timeout(Duration(minutes: 3)));

  test('Razi answers a hadith question', () async {
    if (!kLive) return;
    final reply = await RaziService().ask('Apa hadis tentang niat?', lang: 'id');
    expect(reply.trim().length, greaterThan(40));
  }, timeout: const Timeout(Duration(minutes: 3)));
}

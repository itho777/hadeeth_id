import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:hadeeth_id_mobile/data/auth_service.dart';
import 'package:hadeeth_id_mobile/ui/books_page.dart';
import 'package:hadeeth_id_mobile/ui/chat_page.dart';
import 'package:hadeeth_id_mobile/ui/hadith_detail_page.dart';
import 'package:hadeeth_id_mobile/ui/home_page.dart';
import 'package:hadeeth_id_mobile/ui/privacy_page.dart';
import 'package:hadeeth_id_mobile/ui/profile_page.dart';
import 'package:hadeeth_id_mobile/ui/saved_page.dart';
import 'package:hadeeth_id_mobile/ui/scholar_page.dart';
import 'package:hadeeth_id_mobile/ui/search_page.dart';
import 'package:hadeeth_id_mobile/ui/sanad_page.dart';
import 'package:hadeeth_id_mobile/ui/settings_page.dart';
import 'package:hadeeth_id_mobile/ui/sources_page.dart';
import 'package:hadeeth_id_mobile/ui/topics_page.dart';

import 'app_test.dart' as h;

/// Renders each screen at phone size and writes a PNG under `test/goldens/`.
/// Run with:
///
///   flutter test --update-goldens test/golden_test.dart
///
/// The PNGs are a visual check of the real widgets against the captured CDN
/// fixtures — not an assertion pass, so they are refreshed on demand only.
Future<void> _loadFonts() async {
  Future<void> load(String family, List<String> files) async {
    final loader = FontLoader(family);
    for (final f in files) {
      final bytes = File('assets/fonts/$f').readAsBytesSync();
      loader.addFont(Future.value(ByteData.view(bytes.buffer)));
    }
    await loader.load();
  }

  await load('Amiri', ['Amiri-Regular.ttf', 'Amiri-Bold.ttf']);
  await load('PlusJakartaSans', [
    'PlusJakartaSans-Regular.ttf',
    'PlusJakartaSans-Medium.ttf',
    'PlusJakartaSans-SemiBold.ttf',
    'PlusJakartaSans-Bold.ttf',
  ]);
}

void main() {
  setUpAll(() async {
    await _loadFonts();
  });

  Future<void> shot(WidgetTester tester, String name, Widget page, {bool dark = false}) async {
    tester.view.physicalSize = const Size(1170, 2532);
    tester.view.devicePixelRatio = 3.0;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);
    await tester.pumpWidget(h.harness(h.fixtureRepo(), page, dark: dark));
    await h.settle(tester, rounds: 14);
    await expectLater(find.byType(MaterialApp), matchesGoldenFile('goldens/$name.png'));
  }

  testWidgets('home', (t) => shot(t, 'home', const HomePage()));
  testWidgets('books', (t) => shot(t, 'books', const BooksPage()));
  testWidgets('topics', (t) => shot(t, 'topics', const TopicsPage()));
  testWidgets('search', (t) => shot(t, 'search', const SearchPage(initialQuery: 'niat')));
  testWidgets('settings', (t) => shot(t, 'settings', const SettingsPage()));
  testWidgets('sources', (t) => shot(t, 'sources', const SourcesPage()));
  testWidgets('privacy', (t) => shot(t, 'privacy', const PrivacyPage()));
  testWidgets('profile', (t) => shot(t, 'profile', const ProfilePage()));
  testWidgets('profile with sign-in', (t) async {
    AuthService.instance.debugConfigure();
    addTearDown(AuthService.instance.debugReset);
    await shot(t, 'profile_login', const ProfilePage());
  });
  testWidgets('saved', (t) => shot(t, 'saved', const SavedPage()));
  testWidgets('chat', (t) => shot(t, 'chat', const ChatPage()));
  testWidgets('hadith detail', (t) => shot(t, 'hadith_detail', const HadithDetailPage(bookId: 'bukhari', number: '1')));
  testWidgets('home dark', (t) => shot(t, 'home_dark', const HomePage(), dark: true));
  testWidgets('hadith detail dark', (t) => shot(t, 'hadith_detail_dark', const HadithDetailPage(bookId: 'bukhari', number: '1'), dark: true));

  // Sanad + narrator profile carry the longest labels in the app (a full
  // narrator name beside a tabaqah level), so they get their own shots. The
  // data load runs inside runAsync: the CDN client arms request timeouts, and
  // a fake-async test zone never lets those timers fire.
  testWidgets('sanad', (t) async {
    final hadith = await t.runAsync(() => h.fixtureRepo().getHadith('bukhari', '1'));
    await shot(t, 'sanad', SanadPage(hadith: hadith!, bookTitle: 'Sahih al-Bukhari'));
  });

  testWidgets('narrator profile', (t) async {
    final rawis = await t.runAsync(() => h.fixtureRepo().rawis());
    final longest = rawis!.reduce((a, b) => a.nameEn.length >= b.nameEn.length ? a : b);
    await shot(t, 'narrator', ScholarPage(rawi: longest, fallbackName: longest.nameEn));
  });
}

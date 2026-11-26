import 'dart:convert';
import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_markdown/flutter_markdown.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:provider/provider.dart';

import 'package:hadeeth_id_mobile/data/download_service.dart';
import 'package:hadeeth_id_mobile/data/edition_options.dart';
import 'package:hadeeth_id_mobile/data/hadeeth_repository.dart';
import 'package:hadeeth_id_mobile/data/local_store.dart';
import 'package:hadeeth_id_mobile/data/prepared_answers.dart';
import 'package:hadeeth_id_mobile/data/r2_client.dart';
import 'package:hadeeth_id_mobile/data/razi_service.dart';
import 'package:hadeeth_id_mobile/data/search_service.dart';
import 'package:hadeeth_id_mobile/models.dart';
import 'package:hadeeth_id_mobile/state/app_state.dart';
import 'package:hadeeth_id_mobile/state/nav_controller.dart';
import 'package:hadeeth_id_mobile/theme.dart';
import 'package:hadeeth_id_mobile/ui/app_shell.dart';
import 'package:hadeeth_id_mobile/ui/books_page.dart';
import 'package:hadeeth_id_mobile/ui/chat_page.dart';
import 'package:hadeeth_id_mobile/ui/hadith_detail_page.dart';
import 'package:hadeeth_id_mobile/ui/hadith_list_page.dart';
import 'package:hadeeth_id_mobile/ui/home_page.dart';
import 'package:hadeeth_id_mobile/data/auth_service.dart';
import 'package:hadeeth_id_mobile/ui/login_page.dart';
import 'package:hadeeth_id_mobile/ui/profile_page.dart';
import 'package:hadeeth_id_mobile/ui/search_page.dart';
import 'package:hadeeth_id_mobile/ui/settings_page.dart';
import 'package:hadeeth_id_mobile/ui/widgets.dart';

/// Serves the real cdn.hadeeth.id files captured under `test/fixtures`, so every
/// assertion below runs against production data shapes rather than stubs.
http.Client fixtureClient({bool hotdPin = true}) {
  String read(String name) => File('test/fixtures/$name').readAsStringSync();

  final files = {
    'books.ndjson': read('books.ndjson'),
    'chapters/bukhari.ndjson': read('chapters_bukhari.ndjson'),
    'api/bukhari_index.ndjson': read('bukhari_index.ndjson'),
    'topics.ndjson': read('topics.ndjson'),
    'rawis/rawis.ndjson': read('rawis.ndjson'),
    // An admin pin is one line on the CDN. The unpinned case serves an empty
    // file, so the daily pick has to stand on its own.
    'hotd.ndjson': hotdPin ? '{"book":"bukhari","id":"1"}' : '',
  };
  final rows = read('bukhari_rows.ndjson');

  return MockClient((request) async {
    final url = request.url;
    // The keyword index the web build falls back to. Documents come back whole,
    // exactly like the live Meilisearch response captured from the worker.
    if (url.host.contains('meili-handoff-router')) {
      return http.Response(
        jsonEncode({
          'hits': [
            {
              'id': 'lidwa__bukhari__1',
              'collection': 'bukhari',
              'book_title_en': 'Sahih al-Bukhari',
              'hadith_number': '1',
              'text_ar': 'إنما الأعمال بالنيات',
              'text_id': 'Sesungguhnya amal itu tergantung niatnya.',
              'text_en': 'Actions are but by intention.',
              'grade': 'Sahih',
            },
          ],
        }),
        200,
        headers: {'content-type': 'application/json'},
      );
    }
    if (url.path.endsWith('/api/search')) {
      return http.Response(
        jsonEncode({
          'results': [
            // Production returns ids plus a similarity score only — no matn,
            // no grade — so the page has to hydrate each hit from the CDN.
            {
              'id': 'lidwa__bukhari__1',
              'book_id': 'bukhari',
              'hadith_number': '1',
              'similarity': 0.83,
            },
          ],
        }),
        200,
        headers: {'content-type': 'application/json'},
      );
    }
    for (final entry in files.entries) {
      if (url.path.endsWith('/${entry.key}')) {
        return http.Response.bytes(utf8.encode(entry.value), 200);
      }
    }
    if (url.path.endsWith('/api/bukhari.ndjson')) {
      return http.Response.bytes(
        utf8.encode(rows),
        request.headers['Range'] != null ? 206 : 200,
      );
    }
    return http.Response('not found: ${url.path}', 404);
  });
}

HadeethRepository fixtureRepo({bool hotdPin = true}) => HadeethRepository(
  remote: R2Client(client: fixtureClient(hotdPin: hotdPin)),
  local: LocalStore.at(Directory.systemTemp.createTempSync('hadeeth_repo_')),
);

/// Harakat and tatweel differ between the fixture and hand-written literals, so
/// comparisons strip them first.
String ar(String s) =>
    s.replaceAll(RegExp(r'[\u064B-\u0652\u0670\u0640\u06D6-\u06ED]'), '');

AppState englishState() => AppState()..lang = 'en';

Widget harness(HadeethRepository repo, Widget child, {bool dark = false}) {
  // Pages outside AppShell fall back to the shared language default; keep the
  // harness in step with the AppState it wires up.
  setActiveLang('en');
  return MultiProvider(
    providers: [
      ChangeNotifierProvider<AppState>.value(value: englishState()),
      ChangeNotifierProvider<NavController>(create: (_) => NavController()),
      Provider<HadeethRepository>.value(value: repo),
      Provider<DownloadService>(
        create: (_) => DownloadService(client: fixtureClient()),
      ),
      Provider<SearchService>(
        create: (_) => SearchService(client: fixtureClient()),
      ),
      Provider<RaziService>(
        create: (_) => RaziService(client: fixtureClient()),
      ),
    ],
    child: MaterialApp(
      theme: buildTheme(HP.light),
      darkTheme: buildTheme(HP.darkPalette),
      themeMode: dark ? ThemeMode.dark : ThemeMode.light,
      debugShowCheckedModeBanner: false,
      home: child,
    ),
  );
}

/// Widget tests run on a fake clock, so real file and HTTP futures only land
/// inside `runAsync`. Yield to the real event loop, then pump a few frames.
Future<void> settle(WidgetTester tester, {int rounds = 8}) async {
  for (var i = 0; i < rounds; i++) {
    await tester.runAsync(
      () => Future<void>.delayed(const Duration(milliseconds: 120)),
    );
    await tester.pump(const Duration(milliseconds: 60));
  }
}

void main() {
  test('hadith of the day honours the admin pin on the CDN', () async {
    final h = await fixtureRepo().hadithOfTheDay();
    expect(h, isNotNull);
    expect(h!.bookId, 'bukhari');
    expect(h.number, '1');
    expect(h.tier, 'sahih');
  });

  test('hadith of the day stays sahih and stable when no pin exists', () async {
    final repo = fixtureRepo(hotdPin: false);
    final first = await repo.hadithOfTheDay();
    final second = await repo.hadithOfTheDay();
    expect(first, isNotNull);
    expect(first!.tier, 'sahih');
    expect(second!.id, first.id, reason: 'one pick per day, not per tap');
  });

  test(
    'repository reads the production index, chapter table and a matn row',
    () async {
      final repo = fixtureRepo();
      final books = await repo.books();
      expect(books, isNotEmpty);

      final bukhari = books.firstWhere((b) => b.id == 'bukhari');
      expect(bukhari.totalHadiths, greaterThan(7000));
      expect(bukhari.titleEn.toLowerCase(), contains('bukhari'));

      final chapters = await repo.chapters('bukhari');
      expect(chapters.length, 97);

      final entries = await repo.index('bukhari');
      expect(entries.length, 7008);
      expect(entries.first.matches('1'), isTrue);

      final hadith = await repo.getHadith('bukhari', '1');
      expect(hadith, isNotNull);
      expect(ar(hadith!.textAr), contains(ar('إنما الأعمال بالنيات')));
      expect(hadith.translation('id'), isNotEmpty);
      expect(hadith.rawis, isNotEmpty);
    },
  );

  test('semantic search parses the ids-only production response', () async {
    final hits = await SearchService(client: fixtureClient()).semantic('niat');
    expect(hits, hasLength(1));
    expect(hits.first.bookId, 'bukhari');
    expect(hits.first.number, '1');
    expect(hits.first.arabic, isEmpty, reason: 'production carries no matn');
    expect(hits.first.source, 'semantic');
  });

  test('chapter scoping returns only that chapter\'s rows', () async {
    final repo = fixtureRepo();
    final chapters = await repo.chapters('bukhari');
    final first = chapters.first;
    final rows = await repo.chapterHadiths('bukhari', first);
    expect(rows, isNotEmpty);
  });

  test('keyword tier reads whole Meilisearch documents', () async {
    final svc = SearchService(client: fixtureClient(), meiliKey: 'test-key');
    final hits = await svc.meili('niat');
    expect(hits, hasLength(1));
    expect(hits.first.bookId, 'bukhari');
    expect(hits.first.bookName, 'Sahih al-Bukhari');
    expect(hits.first.arabic, contains('الأعمال'));
    expect(hits.first.grade, 'Sahih');
    expect(hits.first.source, 'keyword');
  });

  test(
    'search falls back to the keyword index when the semantic API refuses',
    () async {
      // 403 stands in for the pinned Access-Control-Allow-Origin that blocks a
      // browser origin; the service must not surface an empty page for it.
      final client = MockClient((req) async {
        if (req.url.host == 'hadeeth.id') return http.Response('blocked', 403);
        if (req.url.host.contains('meili-handoff-router')) {
          return http.Response.bytes(
            utf8.encode(
              jsonEncode({
                'hits': [
                  {
                    'id': 'lidwa__bukhari__1',
                    'collection': 'bukhari',
                    'hadith_number': '1',
                    'text_ar': 'إنما الأعمال بالنيات',
                    'text_id': 'Amal tergantung niat',
                    'grade': 'Sahih',
                  },
                ],
              }),
            ),
            200,
          );
        }
        throw StateError('unexpected ${req.url}');
      });
      final set = await SearchService(
        client: client,
        meiliKey: 'test-key',
      ).search(query: 'niat', repo: fixtureRepo());
      expect(set.method, 'keyword');
      expect(set.fellBack, isTrue);
      expect(set.hits.single.bookId, 'bukhari');
    },
  );

  testWidgets('home renders the archive counter once collections load', (
    tester,
  ) async {
    await tester.pumpWidget(harness(fixtureRepo(), const HomePage()));
    await settle(tester);
    expect(find.textContaining('KUTUBUT').evaluate().isNotEmpty, isTrue);
    expect(
      find.textContaining('Sahih al-Bukhari').evaluate().isNotEmpty,
      isTrue,
      reason: 'collection cards require books.ndjson to have parsed',
    );
  });

  testWidgets('books page lists the nine collections from books.ndjson', (
    tester,
  ) async {
    await tester.pumpWidget(harness(fixtureRepo(), const BooksPage()));
    await settle(tester);
    expect(find.textContaining('Bukhari').evaluate().isNotEmpty, isTrue);
  });

  testWidgets('hadith detail renders the Arabic matn from the CDN row', (
    tester,
  ) async {
    await tester.pumpWidget(
      harness(
        fixtureRepo(),
        const HadithDetailPage(bookId: 'bukhari', number: '1'),
      ),
    );
    await settle(tester, rounds: 12);
    final arabicOnScreen = tester
        .widgetList<Text>(find.byType(Text))
        .any((w) => ar(w.data ?? '').contains(ar('إنما الأعمال بالنيات')));
    expect(
      arabicOnScreen,
      isTrue,
      reason: 'matn must come from the CDN row file',
    );
    // The row's other editions are the same Arabic and the same ID/EN bodies the
    // tabs already show, so the duplicate "other editions" block must be gone.
    expect(find.textContaining('Edisi lain'), findsNothing);
    expect(find.textContaining('Other editions'), findsNothing);
  });

  testWidgets('hadith list renders rows for the first chapter', (tester) async {
    final repo = fixtureRepo();
    Book? book;
    Chapter? chapter;
    await tester.runAsync(() async {
      book = (await repo.books()).firstWhere((b) => b.id == 'bukhari');
      chapter = (await repo.chapters('bukhari')).first;
    });
    await tester.pumpWidget(
      harness(repo, HadithListPage(book: book!, chapter: chapter)),
    );
    await settle(tester, rounds: 12);
    expect(find.byType(ListView).evaluate().isNotEmpty, isTrue);
  });

  testWidgets(
    'search page hydrates an ids-only hit into matn and translation',
    (tester) async {
      await tester.pumpWidget(
        harness(fixtureRepo(), const SearchPage(initialQuery: 'niat')),
      );
      await settle(tester, rounds: 16);
      final texts = tester
          .widgetList<Text>(find.byType(Text))
          .map((w) => ar(w.data ?? ''))
          .join(' ');
      expect(
        texts.contains(ar('إنما الأعمال بالنيات')),
        isTrue,
        reason: 'matn must be pulled from the CDN row file for an ids-only hit',
      );
      expect(
        texts.contains('reward of deeds depends upon the intentions'),
        isTrue,
        reason:
            'translation must follow the matn from the same row (en locale)',
      );
    },
  );

  test('dark palette is pinned to the exact hadeeth.id ink colours', () {
    // Values lifted from js/theme.js + the Tailwind token map in index.html:
    // body ink-black #0D0D10, header #10141A, card #1E293B, inset #0F172A,
    // border #334155, accent #10B981.
    const expected = {
      'canvas': 0xFF0D0D10,
      'nav': 0xFF10141A,
      'card': 0xFF1E293B,
      'panel': 0xFF0F172A,
      'border': 0xFF334155,
      'emerald': 0xFF10B981,
      'text': 0xFFF8FAFC,
    };
    final p = HP.darkPalette;
    expect(p.dark, isTrue);
    expect(Brand.darkCanvas.toARGB32(), expected['canvas']);
    expect(Brand.darkNav.toARGB32(), expected['nav']);
    expect(Brand.darkCard.toARGB32(), expected['card']);
    expect(Brand.darkPanel.toARGB32(), expected['panel']);
    expect(Brand.darkBorder.toARGB32(), expected['border']);
    expect(Brand.emeraldBright.toARGB32(), expected['emerald']);
    expect(Brand.darkText.toARGB32(), expected['text']);
    expect(p.canvas.toARGB32(), expected['canvas']);
    expect(p.emerald.toARGB32(), expected['emerald']);
    expect(buildTheme(p).brightness, Brightness.dark);
  });

  testWidgets('starter questions answer instantly from the prepared cache', (
    t,
  ) async {
    final seeds = parsePreparedAnswers(
      File('assets/data/razi_seeds.json').readAsStringSync(),
    );
    await t.pumpWidget(
      harness(fixtureRepo(), ChatPage(preparedAnswers: seeds)),
    );
    await settle(t, rounds: 2);
    final day = wibDayNumber();
    final firstWindow = preparedWindow('en', day, 0);
    expect(find.text(firstWindow.first), findsOneWidget);

    // "More questions" advances the window so all ten are reachable today.
    await t.tap(find.text('More questions'));
    await t.pumpAndSettle();
    final nextWindow = preparedWindow('en', day, 4);
    expect(find.text(nextWindow.first), findsOneWidget);
    expect(find.text(firstWindow.first), findsNothing);

    await t.tap(find.text(nextWindow.first));
    await t.pumpAndSettle();
    expect(find.byType(MarkdownBody), findsOneWidget);
    expect(find.textContaining('could not be reached'), findsNothing);
  });

  test('all ten starter questions have a verified answer in both languages', () {
    final seeds = parsePreparedAnswers(
      File('assets/data/razi_seeds.json').readAsStringSync(),
    );
    expect(seeds.length, 20);
    for (final q in preparedQuestionsEn) {
      expect(
        seeds.containsKey('en|$q'),
        isTrue,
        reason: 'missing EN answer for $q',
      );
    }
    for (final q in preparedQuestionsId) {
      expect(
        seeds.containsKey('id|$q'),
        isTrue,
        reason: 'missing ID answer for $q',
      );
    }
    // A hadith question must be answered from a hadith, not with Qur'an verses.
    final riba = seeds['en|Which hadith warns about riba?']!;
    expect(riba, contains('Sahih Muslim 2995'));
    expect(riba, contains('Shahih'));
    final isnad =
        seeds['en|Can you walk me through the isnad of the hadith about intentions?']!;
    expect(isnad, contains('mutashil'));
    expect(isnad, contains('Umar bin al-Khattab'));
  });

  test('the starter window rotates per WIB day and covers all ten', () {
    final day = wibDayNumber(DateTime.utc(2026, 11, 25, 17)); // 00:00 WIB
    expect(
      preparedWindow('en', day, 0),
      isNot(preparedWindow('en', day + 1, 0)),
    );
    final seen = <String>{};
    for (var offset = 0; offset < 12; offset += 4) {
      seen.addAll(preparedWindow('en', day, offset));
    }
    expect(seen.length, 10);
  });

  test('edition selector drops Arabic and anything the tabs already show', () {
    final h = Hadith.fromJson({
      'book': 'bukhari',
      'hadith_number': '7',
      'text_ar': 'النص العربي',
      'text_id': 'Isi terjemahan Indonesia',
      'text_en': 'English translation body',
      'translations': {
        'ar': [
          {'source': 'lidwa', 'text': 'النص العربي'},
        ],
        'id': [
          {'source': 'lidwa', 'text': 'Isi terjemahan Indonesia'},
          {'source': 'fawaz', 'text': 'Versi Indonesia yang berbeda'},
        ],
        'en': [
          {'source': 'fawaz', 'text': 'English translation body'},
        ],
        'ms': [
          {'source': 'xyz', 'text': 'Terjemahan Melayu'},
        ],
      },
    }, bookIdFallback: 'bukhari');
    final options = editionOptions(h);
    expect(options.map((e) => e.lang), ['ms', 'id']);
    expect(options.map((e) => e.text), [
      'Terjemahan Melayu',
      'Versi Indonesia yang berbeda',
    ]);
    expect(options.first.label, 'Melayu · XYZ');
    expect(options.any((e) => e.lang == 'ar'), isFalse);
    expect(options.any((e) => e.text == 'Isi terjemahan Indonesia'), isFalse);
  });

  test('a row whose other editions only repeat the tabs offers none', () {
    final row =
        jsonDecode(
              File('test/fixtures/bukhari_rows.ndjson').readAsLinesSync().first,
            )
            as Map<String, dynamic>;
    expect(editionOptions(Hadith.fromJson(row)), isEmpty);
  });

  test('home AI samples are drawn from the answered set', () {
    final seeds = parsePreparedAnswers(
      File('assets/data/razi_seeds.json').readAsStringSync(),
    );
    final day = wibDayNumber(DateTime.utc(2026, 11, 25, 17));
    for (final lang in ['en', 'id']) {
      final samples = homeSamples(lang, day);
      expect(samples.length, 2);
      for (final q in samples) {
        expect(
          seeds.containsKey('$lang|$q'),
          isTrue,
          reason: 'home chip without an answer: $q',
        );
      }
    }
  });

  testWidgets('AI tab can be left with a single tap', (t) async {
    await t.pumpWidget(harness(fixtureRepo(), const AppShell()));
    await settle(t, rounds: 4);
    final bar = find.byType(NavigationBar);
    await t.tap(find.descendant(of: bar, matching: find.text('Razi')));
    await t.pumpAndSettle();
    expect(t.widget<NavigationBar>(bar).selectedIndex, 3);
    await t.tap(find.descendant(of: bar, matching: find.text('Books')));
    await t.pumpAndSettle();
    expect(t.widget<NavigationBar>(bar).selectedIndex, 1);
  });

  testWidgets('the last tab is the profile and it carries bookmarks', (
    t,
  ) async {
    await t.pumpWidget(harness(fixtureRepo(), const AppShell()));
    await settle(t, rounds: 4);
    final bar = find.byType(NavigationBar);
    expect(
      find.descendant(of: bar, matching: find.text('Saved')),
      findsNothing,
    );
    await t.tap(find.descendant(of: bar, matching: find.text('Profile')));
    await t.pumpAndSettle();
    expect(t.widget<NavigationBar>(bar).selectedIndex, 4);
    expect(find.text('BOOKMARKS'), findsOneWidget);
    expect(find.text('Manage bookmarks'), findsOneWidget);
  });

  testWidgets('settings offers the support and legal pages', (t) async {
    await t.pumpWidget(harness(fixtureRepo(), const SettingsPage()));
    await settle(t, rounds: 4);
    expect(find.text('Profile'), findsOneWidget);
    // The support rows sit below the fold; a ListView only builds what it shows.
    for (var i = 0; i < 3; i++) {
      await t.drag(find.byType(ListView).first, const Offset(0, -500));
      await t.pumpAndSettle();
    }
    expect(find.text('Data sources & credits'), findsOneWidget);
    expect(find.text('Privacy policy'), findsOneWidget);
    expect(find.text('Support this project'), findsOneWidget);

    await t.tap(find.text('Data sources & credits'));
    await t.pumpAndSettle();
    expect(find.textContaining('28 collections'), findsWidgets);
    expect(find.textContaining('never overwritten'), findsOneWidget);
  });

  test('back walks the tab trail and refuses once it runs out', () {
    final nav = NavController();
    nav.go(3);
    nav.go(1);
    expect(nav.back(), isTrue);
    expect(nav.tab, 3);
    expect(nav.back(), isTrue);
    expect(nav.tab, 0);
    expect(nav.back(), isFalse);
    expect(nav.tab, 0);
  });

  testWidgets('the shell traps the system back gesture', (t) async {
    await t.pumpWidget(harness(fixtureRepo(), const AppShell()));
    await settle(t, rounds: 4);
    // `find.byType(PopScope)` does not match a generic instantiation, so match
    // on the interface instead.
    final scope =
        t.widgetList(find.byWidgetPredicate((w) => w is PopScope)).single
            as PopScope;
    expect(scope.canPop, isFalse, reason: 'back is handled, never auto-popped');
  });

  test(
    'account merge keeps the newest copy of each bookmark and read mark',
    () async {
      final state = AppState();
      state.bookmarks = [
        Bookmark(
          bookId: 'bukhari',
          bookTitle: 'Sahih al-Bukhari',
          number: '1',
          arabic: 'ar',
          translation: 'local',
          grade: 'Sahih',
          note: 'local note',
          collection: 'Unsorted',
          savedAt: DateTime.utc(2026, 11, 20),
        ),
      ];
      state.lastRead['bukhari'] = LastRead(
        bookId: 'bukhari',
        bookTitle: 'Sahih al-Bukhari',
        number: '1',
        chapter: 'Revelation',
        at: DateTime.utc(2026, 11, 21),
      );

      await state.applyRemote(
        remoteBookmarks: [
          Bookmark(
            bookId: 'bukhari',
            bookTitle: 'Sahih al-Bukhari',
            number: '1',
            arabic: 'ar',
            translation: 'cloud',
            grade: 'Sahih',
            note: 'cloud note',
            collection: 'Study',
            savedAt: DateTime.utc(2026, 11, 22),
          ),
          Bookmark(
            bookId: 'muslim',
            bookTitle: 'Sahih Muslim',
            number: '5',
            arabic: 'ar',
            translation: 'other device',
            grade: 'Sahih',
            note: '',
            collection: 'Unsorted',
            savedAt: DateTime.utc(2026, 11, 19),
          ),
        ],
        remoteProgress: {
          // Older than the local mark, so it must not overwrite it.
          'bukhari': LastRead(
            bookId: 'bukhari',
            bookTitle: 'Sahih al-Bukhari',
            number: '9',
            chapter: 'Old',
            at: DateTime.utc(2026, 11, 1),
          ),
          'muslim': LastRead(
            bookId: 'muslim',
            bookTitle: 'Sahih Muslim',
            number: '5',
            chapter: 'Faith',
            at: DateTime.utc(2026, 11, 23),
          ),
        },
      );

      expect(state.bookmarks, hasLength(2));
      final bukhari = state.bookmarks.firstWhere((b) => b.key == 'bukhari:1');
      expect(bukhari.note, 'cloud note', reason: 'newer saved_at wins');
      expect(
        state.lastRead['bukhari']!.number,
        '1',
        reason: 'older cloud mark loses',
      );
      expect(
        state.lastRead['muslim']!.number,
        '5',
        reason: 'new device is adopted',
      );
    },
  );

  test('native OAuth callback is a constant scheme URL', () {
    expect(AuthService.oauthRedirect(), 'com.hadeeth.id://login-callback');
    expect(AuthService.oauthRedirect().contains('?'), isFalse);
  });

  testWidgets('login page offers email, password and Google', (t) async {
    await t.pumpWidget(harness(fixtureRepo(), const LoginPage()));
    await t.pumpAndSettle();
    expect(find.widgetWithText(TextField, 'Email'), findsOneWidget);
    expect(find.widgetWithText(TextField, 'Password'), findsOneWidget);
    expect(find.text('Continue with Google'), findsOneWidget);
    expect(find.text('Sign in'), findsWidgets);
    await t.tap(find.text('No account yet? Register'));
    await t.pumpAndSettle();
    expect(find.text('Create account'), findsWidgets);
  });

  testWidgets('profile offers sign-in when the build has a key', (t) async {
    AuthService.instance.debugConfigure();
    addTearDown(AuthService.instance.debugReset);
    await t.pumpWidget(harness(fixtureRepo(), const ProfilePage()));
    await settle(t, rounds: 6);
    expect(find.text('Sign in or register'), findsOneWidget);
    await t.tap(find.text('Sign in or register'));
    await settle(t, rounds: 6);
    expect(find.text('Continue with Google'), findsOneWidget);
    expect(find.text('Email'), findsOneWidget);
  });
}

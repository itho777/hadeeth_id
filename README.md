# hadeeth.id — mobile edition

Flutter client for [hadeeth.id](https://hadeeth.id), the digital hadith manuscript
encyclopedia. Android is the target platform; a web build exists for previewing the same
widgets in a browser.

Built from the Stitch mobile mockups (`Downloads/stitch_hadith_mobile_encyclopedia_app`),
with two deliberate departures per the brief:

- **Logo and AI avatar are the real ones** from the web repo (`assets/images/logo_light.jpg`,
  `logo_dark.jpg`, `logo_mono.jpg`, `razi-avatar.jpg`); no placeholder art survives.
- **Dark mode uses the exact hadeeth.id palette**, values taken from `js/theme.js` and the
  Tailwind token map in `index.html` — body `#0D0D10`, header `#10141A`, card `#1E293B`,
  inset `#0F172A`, border `#334155`, accent `#10B981`, text `#F8FAFC / #D1D5DB / #9CA3AF`.
  Light mode stays close to Stitch (manuscript paper `#FDFBF7`, ink `#001932`).

## Screens

| Screen | File | Web equivalent |
| --- | --- | --- |
| Home / discovery | `lib/ui/home_page.dart` | `index.html` |
| Collections (Kutub) | `lib/ui/books_page.dart` | `books.html` |
| Chapters | `lib/ui/chapters_page.dart` | `kitab.html` |
| Hadith list | `lib/ui/hadith_list_page.dart` | chapter view |
| Hadith detail | `lib/ui/hadith_detail_page.dart` | `hadith.html` |
| Sanad chain | `lib/ui/sanad_page.dart` | `hadith.html#sanad` |
| Narrator profile | `lib/ui/scholar_page.dart` | `scholars.html` |
| Topics | `lib/ui/topics_page.dart`, `topic_detail_page.dart` | `topics.html` |
| Search | `lib/ui/search_page.dart` | search box on every page |
| Ask Razi (AI) | `lib/ui/chat_page.dart` | `js/razi-chat.js` widget |
| Saved / markah | `lib/ui/saved_page.dart` | bookmark drawer |
| Downloads | `lib/ui/downloads_page.dart` | — (offline reading is mobile-only) |
| Data sources & credits | `lib/ui/sources_page.dart` | `docs.html` |
| Privacy policy | `lib/ui/privacy_page.dart` | `privacy.html` |
| Profile | `lib/ui/profile_page.dart` | `profile.html` |
| Sign in / register | `lib/ui/login_page.dart` | `login.html` |
| Donation sheet | `lib/ui/donate_sheet.dart` | tafseer.id donation modal |
| Settings | `lib/ui/settings_page.dart` | theme + language controls |

## Data path

No new backend. The app reads exactly what the web edition reads:

- `https://cdn.hadeeth.id/books.ndjson`, `topics.ndjson`, `chapters/<book>.ndjson`,
  `api/<book>_index.ndjson`, `api/<book>.ndjson` (range-requestable, used for single rows),
  `rawis/rawis.ndjson`, `rawis/profiles_index.ndjson`, `rawis/profiles.ndjson`.
- `POST https://hadeeth.id/api/search` — Cloudflare AI + pgvector. Answers with ids and a
  similarity score only, so each hit is hydrated from its CDN row.
- `POST https://razi.hadeeth.id/api/chat` — Razi, grounded in the archive.

Search tiers, in order (`lib/data/search_service.dart`):

1. **Cloudflare AI semantic** — the web endpoint. Works on Android, which has no CORS.
2. **Meilisearch keyword** — only when `MEILI_KEY` is supplied at build time. Needed for the
   web build, because `hadeeth.id/api/search` pins `Access-Control-Allow-Origin:
   https://hadeeth.id`, so a browser on any other origin is refused while the keyword
   worker answers `*`.
3. **Offline keyword** — substring scan over downloaded collections, no network.

`MEILI_KEY` is never committed; pass it at build time:

```bash
flutter build web --release --dart-define=MEILI_KEY=<key>
```

Offline reading: a download stores the book index, its chapter table and its row file under
the app documents directory (`lib/data/local_store.dart`), and the repository prefers that
mirror when `preferOffline` is on.

## Build and run

```bash
flutter pub get
flutter run -d chrome                      # preview
flutter build apk --release --dart-define=SUPABASE_ANON_KEY=<key>   # Android artifact
flutter build web --release --dart-define=SUPABASE_ANON_KEY=<key>   # web artifact
```

Without `SUPABASE_ANON_KEY` the app builds and runs exactly as before: local-only, no login
UI. The anon key is public by design but is never committed; it reaches the app only through
the build define. Release APK: `build/app/outputs/flutter-apk/app-release.apk`.

## Account and sync

- `lib/data/auth_service.dart` — Supabase Auth: email/password sign-in and registration plus
  Google OAuth. Session persists across launches; `AuthService.instance.email` drives the
  Profile and Settings rows.
- `lib/data/sync_service.dart` — local-first mirror. Bookmark and last-read writes go to disk
  first, then to `bookmarks` / `reading_progress` when signed in. Signing in pulls the account
  copy, merges it (newest `saved_at` / `read_at` wins), then pushes the merged result, so two
  devices converge without losing offline work. Language changes debounce into
  `profiles.preferred_language`.
- The bottom bar's fifth tab is Profile, not Saved. Profile carries the account card,
  reading stats, the three most recent bookmarks and a `Manage bookmarks` row that opens
  the full saved library (search, collections, export).
- Google returns to `com.hadeeth.id://login-callback` (intent filter in
  `android/app/src/main/AndroidManifest.xml`). Supabase must list that URL — and
  the trailing-slash form — under Auth → URL Configuration → Redirect URLs. If it
  is not listed, Supabase silently uses `site_url`, so the browser finishes on
  `https://hadeeth.id` instead of returning to the app. Native sign-in forces
  `LaunchMode.externalApplication`; the web build uses its own origin.

## Tests

```bash
flutter test                                            # 51 tests, fixtures in test/fixtures
flutter test --update-goldens test/golden_test.dart     # regenerate test/goldens/*.png
flutter test --dart-define=LIVE=true test/live_services_test.dart   # hits production
```

- `test/app_test.dart` — repository parsing, chapter scoping, ids-only search hydration,
  Meilisearch tier, fallback chain, and every screen rendered against captured CDN files
  (`test/fixtures/`), plus a palette assertion that pins the dark tokens.
- `test/golden_test.dart` — phone-size PNGs of each screen in both themes, rendered with the
  real Amiri and Plus Jakarta Sans fonts.
- `test/live_services_test.dart` — opt-in run against the live CDN, search API and Razi.
- `test/live_network_test.dart` — opt-in CORS check; run it with `--platform chrome` on a
  host where a headless Chromium can start.

## Hadith of the day and prepared answers

- **Hadith of the day** (`lib/data/hadeeth_repository.dart`): the admin pin now lives in
  Supabase `hotd_overrides`, read through the anon `get_hotd_override()` RPC, so one save in
  `https://hadeeth.id/admin.html` reaches every client. The CDN line
  `https://cdn.hadeeth.id/hotd.ndjson` remains as an offline fallback. Without a pin the pick
  is deterministic on the WIB calendar day — seeded from the date, drawn from the sahih-graded
  collections only — so every device shows the same narration and it rolls at midnight with
  no round trip.
- **Prepared answers** (`assets/data/razi_seeds.json`, authored in `tool/gen_prepared_answers.py`):
  ten popular starter questions, each with an English and an Indonesian answer, all twenty
  written against a row read from the CDN (reference, grade and wording from that row — not
  model output). The intro shows four at a time; the window rotates with the WIB day and
  "More questions" advances it, so the same three cards are not the only thing on screen.
  The home AI card draws its two sample chips from the same ten (`homeSamples`), so a chip on
  the dashboard also answers instantly instead of calling Razi.
  The bridge-side cache for both web and mobile is described in `tool/SERVER_WORK.md`, with
  `tool/razi_seed_cache.js` and `tool/seed_answers.json` ready to drop in.
- **Other editions are a selector, not a list** (`lib/data/edition_options.dart`): the detail page
  shows ID and EN tabs, and any further edition sits behind a dropdown that lists only entries
  the tabs do not already show — Arabic is dropped (the matn is at the top) and any text equal
  to the ID/EN body is dropped, so nothing is printed twice. Labels read `Language · SOURCE`;
  one edition is displayed at a time, and the section disappears when only duplicates remain.
- **Book classification** comes from the registry's own `book_type_ar` — Jami', Sunan, Musnad,
  Muwatta, Sahih, Mustadrak, Mu'jam, Ahkam, Jawami' al-Kalim, Mutanawwi' — used by the Kutub
  filter and nowhere else. Authenticity (sahih/da'if) stays a separate axis.

## Known limits

- No Android AVD on the build machine, so the APK was compiled but not launched on an
  emulator; the widget tests and goldens are the rendering evidence.
- Google sign-in on Android needs `com.hadeeth.id://login-callback` in the Supabase redirect
  allowlist; email/password works without it. Email sign-up obeys the project's confirmation
  setting, so a new account may have to confirm the address before the first sign-in.
- The web build's semantic search needs `MEILI_KEY` (see above). Without it, search falls
  back to downloaded collections.
- `flutter test --platform chrome` could not launch a headless browser here, so the CORS
  behaviour was verified with `curl` against the live endpoints instead.
- Narrator biography is limited to what the lidwa registry carries; there is no
  independent biographical dataset in the archive.

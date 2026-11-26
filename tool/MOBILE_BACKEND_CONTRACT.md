# Mobile backend contract — hadeeth.id

The mobile app and the web app share one Supabase project. Supabase stores
**only user state and editorial pins**. The hadith corpus stays on the R2 CDN;
do not copy 118k rows into Postgres.

| Item | Value |
|---|---|
| Project ref | `idokyspokenbmzoegahq` |
| URL | `https://idokyspokenbmzoegahq.supabase.co` |
| Schema migration | `G:/hadeeth_id/supabase/migrations/20261125000000_mobile_sync_and_hotd.sql` |
| Web sync implementation | `G:/hadeeth_id/js/user-sync.js` |
| Runtime key | anon key only. Never ship the service-role key. |

Google OAuth is enabled on the project (`/auth/v1/settings` returns
`"google": true`). Apple is not enabled yet.

## Tables

### `profiles`
`id uuid` (auth user id, PK), `display_name`, `avatar_url`,
`preferred_language` (`id`/`en`), `updated_at`.

### `bookmarks`
Primary key `(user_id, book_id, hadith_number)`. Columns:
`book_id`, `hadith_number`, `book_title`, `arabic`, `translation`, `grade`,
`note`, `collection`, `saved_at`.

### `reading_progress`
Primary key `(user_id, book_id)`. Columns:
`book_id`, `hadith_number`, `book_title`, `chapter`, `read_at`.

### `hotd_overrides`, `hotd_settings`
One manual Hadith-of-the-Day pin per WIB day, plus the auto-rotate switch.
Public read; writes require an admin email in `admin_users`. RLS enforces it.

## Hadith of the Day

Read the manual pin first:

```dart
final rows = await Supabase.instance.client.rpc(
  'get_hotd_override',
  params: {'p_day': '2026-11-25'}, // omit for today in WIB
);
final pin = (rows as List).isNotEmpty ? rows.first as Map<String, dynamic> : null;
```

If there is no pin and `hotd_settings.auto_rotate` is true, use the existing
`HadithRepository.hadithOfTheDay()` logic: it deterministically selects from
the sahih-pure collections in `books.ndjson` using the WIB day number. No
scheduled job and no database copy of the corpus are involved.

## Auth + sync rules

```dart
await Supabase.initialize(url: supabaseUrl, anonKey: anonKey);
await Supabase.instance.client.auth.signInWithOAuth(
  OAuthProvider.google,
  redirectTo: 'hadeethid://login-callback',
);
```

Register `hadeethid://login-callback` in the Android/iOS manifest and add it to
Supabase Auth → URL Configuration.

1. After sign-in, pull `profiles`, `bookmarks`, and `reading_progress` for
   `auth.uid()`.
2. Merge locally with last-write-wins on `saved_at` / `read_at`.
3. Push with `upsert` and the composite conflict target:
   `bookmarks` → `user_id,book_id,hadith_number`;
   `reading_progress` → `user_id,book_id`.
4. Keep an offline queue in local storage; reading never waits on a sync.
5. The web implementation of the same rules is `G:/hadeeth_id/js/user-sync.js`.

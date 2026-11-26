-- Canonical schema now lives in the web repo:
--   G:/hadeeth_id/supabase/migrations/20261125000000_mobile_sync_and_hotd.sql
-- Apply that file once; it contains these user tables plus HOTD and the
-- content mirror. This copy only creates the user-owned subset and is kept so
-- the mobile repo can be worked on without the web checkout.
-- After this runs, both the web app and the mobile app can sync using the
-- public anon key — no service key is needed at runtime.

create table if not exists public.profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  display_name text,
  avatar_url text,
  preferred_language text not null default 'id',
  updated_at timestamptz not null default now()
);

create table if not exists public.bookmarks (
  user_id uuid not null references auth.users(id) on delete cascade,
  book_id text not null,
  hadith_number text not null,
  book_title text not null default '',
  arabic text not null default '',
  translation text not null default '',
  grade text not null default '',
  note text not null default '',
  collection text not null default 'Unsorted',
  saved_at timestamptz not null default now(),
  primary key (user_id, book_id, hadith_number)
);

create table if not exists public.reading_progress (
  user_id uuid not null references auth.users(id) on delete cascade,
  book_id text not null,
  hadith_number text not null,
  book_title text not null default '',
  chapter text not null default '',
  read_at timestamptz not null default now(),
  primary key (user_id, book_id)
);

alter table public.profiles enable row level security;
alter table public.bookmarks enable row level security;
alter table public.reading_progress enable row level security;

drop policy if exists "own profile" on public.profiles;
create policy "own profile" on public.profiles
  for all using (auth.uid() = id) with check (auth.uid() = id);

drop policy if exists "own bookmarks" on public.bookmarks;
create policy "own bookmarks" on public.bookmarks
  for all using (auth.uid() = user_id) with check (auth.uid() = user_id);

drop policy if exists "own reading progress" on public.reading_progress;
create policy "own reading progress" on public.reading_progress
  for all using (auth.uid() = user_id) with check (auth.uid() = user_id);

create index if not exists bookmarks_user_saved_idx
  on public.bookmarks (user_id, saved_at desc);

create or replace function public.handle_new_user()
returns trigger language plpgsql security definer set search_path = public as $$
begin
  insert into public.profiles (id, display_name, avatar_url)
  values (
    new.id,
    coalesce(new.raw_user_meta_data ->> 'full_name', new.raw_user_meta_data ->> 'name', split_part(new.email, '@', 1)),
    new.raw_user_meta_data ->> 'avatar_url'
  )
  on conflict (id) do nothing;
  return new;
end $$;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute function public.handle_new_user();

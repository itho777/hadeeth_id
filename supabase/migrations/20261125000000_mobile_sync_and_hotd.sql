-- hadeeth.id Supabase schema: user data + shared Hadith-of-the-Day pins.
-- No hadith corpus is copied here. The R2/CDN NDJSON files remain the content
-- source of truth; Supabase stores only account state and editor overrides.
-- Apply in the Supabase SQL editor or through the Management API. Re-runnable.

-- ---------------------------------------------------------------- user data
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

create index if not exists bookmarks_user_saved_idx
  on public.bookmarks (user_id, saved_at desc);

-- ---------------------------------------------------------------- admin gate
create table if not exists public.admin_users (
  email text primary key,
  created_at timestamptz not null default now()
);
insert into public.admin_users (email) values
  ('admin@hadeeth.id'), ('info@hadeeth.id')
on conflict (email) do nothing;

create or replace function public.is_hadeeth_admin()
returns boolean language sql stable security definer
set search_path = public, pg_temp as $$
  select exists (
    select 1 from public.admin_users a
    where lower(a.email) = lower(coalesce(auth.jwt() ->> 'email', ''))
  );
$$;
revoke all on function public.is_hadeeth_admin() from public;
grant execute on function public.is_hadeeth_admin() to anon, authenticated, service_role;

-- ------------------------------------------------------------ hadith of day
-- One manual pin per WIB calendar day. When absent, the web and mobile clients
-- derive the same sahih pick locally from the CDN payload; no content table and
-- no nightly cron are needed.
create table if not exists public.hotd_overrides (
  day date primary key,
  book_id text not null,
  hadith_number text not null,
  note text not null default '',
  set_by uuid references auth.users(id) on delete set null,
  created_at timestamptz not null default now()
);

create table if not exists public.hotd_settings (
  singleton boolean primary key default true check (singleton),
  auto_rotate boolean not null default true,
  updated_at timestamptz not null default now()
);
insert into public.hotd_settings (singleton, auto_rotate)
values (true, true) on conflict (singleton) do nothing;

create or replace function public.get_hotd_override(p_day date default null)
returns table (day date, book_id text, hadith_number text, note text, source text)
language sql stable security definer
set search_path = public, pg_temp as $$
  select o.day, o.book_id, o.hadith_number, o.note, 'manual'::text
  from public.hotd_overrides o
  where o.day = coalesce(p_day, (now() at time zone 'Asia/Jakarta')::date);
$$;
revoke all on function public.get_hotd_override(date) from public;
grant execute on function public.get_hotd_override(date) to anon, authenticated, service_role;

-- ------------------------------------------------------------------ RLS
alter table public.profiles enable row level security;
alter table public.bookmarks enable row level security;
alter table public.reading_progress enable row level security;
alter table public.admin_users enable row level security;
alter table public.hotd_overrides enable row level security;
alter table public.hotd_settings enable row level security;

drop policy if exists "own profile" on public.profiles;
create policy "own profile" on public.profiles
  for all using (auth.uid() = id) with check (auth.uid() = id);

drop policy if exists "own bookmarks" on public.bookmarks;
create policy "own bookmarks" on public.bookmarks
  for all using (auth.uid() = user_id) with check (auth.uid() = user_id);

drop policy if exists "own reading progress" on public.reading_progress;
create policy "own reading progress" on public.reading_progress
  for all using (auth.uid() = user_id) with check (auth.uid() = user_id);

drop policy if exists "public hotd overrides" on public.hotd_overrides;
create policy "public hotd overrides" on public.hotd_overrides
  for select using (true);
drop policy if exists "admin writes hotd overrides" on public.hotd_overrides;
create policy "admin writes hotd overrides" on public.hotd_overrides
  for all using (public.is_hadeeth_admin()) with check (public.is_hadeeth_admin());

drop policy if exists "public hotd settings" on public.hotd_settings;
create policy "public hotd settings" on public.hotd_settings
  for select using (true);
drop policy if exists "admin writes hotd settings" on public.hotd_settings;
create policy "admin writes hotd settings" on public.hotd_settings
  for all using (public.is_hadeeth_admin()) with check (public.is_hadeeth_admin());

-- ---------------------------------------------------------- profile trigger
create or replace function public.handle_new_user()
returns trigger language plpgsql security definer set search_path = public as $$
begin
  insert into public.profiles (id, display_name, avatar_url)
  values (
    new.id,
    coalesce(new.raw_user_meta_data ->> 'full_name',
             new.raw_user_meta_data ->> 'name',
             split_part(coalesce(new.email, ''), '@', 1)),
    new.raw_user_meta_data ->> 'avatar_url'
  )
  on conflict (id) do nothing;
  return new;
end $$;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute function public.handle_new_user();
